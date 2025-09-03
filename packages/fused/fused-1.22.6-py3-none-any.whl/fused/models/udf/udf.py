from __future__ import annotations

import ast
import warnings
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Iterable,
    Literal,
    Sequence,
    overload,
)

from pydantic import Field, PrivateAttr, RootModel, model_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated, Self, override

from fused.models.udf.base_udf import (
    METADATA_FUSED_ID,
    METADATA_FUSED_SLUG,
    BaseUdf,
    UdfType,
)
from fused.warnings import FusedUdfWarning

from .._inplace import _maybe_inplace

if TYPE_CHECKING:
    from fused.models.api.job import UdfJobStepConfig
    from fused.models.udf._eval_result import UdfEvaluationResult


class Udf(BaseUdf):
    """A user-defined function that operates on [`geopandas.GeoDataFrame`s][geopandas.GeoDataFrame]."""

    type: Literal[UdfType.GEOPANDAS_V2] = UdfType.GEOPANDAS_V2

    entrypoint: str
    """Name of the function within the code to invoke."""

    cache_max_age: int | None = None
    """The maximum age when returning a result from the cache."""

    instance_type: str | None = None
    """The instance type to run this UDF on by default, if not specified in
    `fused.run()`, e.g., "batch".
    """

    parameters: dict[str, Any] = Field(default_factory=dict)
    """Parameters to pass into the entrypoint."""

    _parameter_list: Sequence[str] | None = PrivateAttr(None)
    _parameter_has_kwargs: bool | None = PrivateAttr(None)
    original_headers: str | None = None

    _nested_callable = PrivateAttr(None)  # TODO : Find out type

    @model_validator(mode="after")
    # TODO: Maybe use this by default instead of _extract_parameter_list(inspect.signature) in _udf_internal?
    def _set_parameter_list(self, info: ValidationInfo) -> Self:
        load_parameter_list = (
            info.context["load_parameter_list"]
            if info.context and info.context.get("load_parameter_list") is not None
            else False
        )
        if load_parameter_list:
            params = self._detect_parameters(self.code)
            _parameter_list, _parameter_has_kwargs = params

            self._parameter_list = _parameter_list
            self._parameter_has_kwargs = _parameter_has_kwargs

        return self

    def _detect_parameters(self, src: str) -> tuple[list[str], bool]:
        # Originally from fused/_udf/load.py
        # Note: Removed default type parsing because using AST is high maintenance to cover all scenarios.

        try:
            parsed_ast = ast.parse(src)
        except SyntaxError:
            parsed_ast = ast.parse(repr(src))

        # Find and extract parameters
        params = []
        has_kwargs = False
        for node in ast.walk(parsed_ast):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == self.entrypoint
            ):
                for arg in node.args.args:
                    params.append(arg.arg)

                if node.args.kwarg:
                    has_kwargs = True
                break

        return params, has_kwargs

    def _with_udf_entrypoint(self) -> Self:
        """
        If the entrypoint is not "udf", replace it back to "udf" using AST manipulation.
        If a function named "udf" already exists, it will be renamed to "udf_updated".
        """
        target_new_name = "udf"
        if self.entrypoint == target_new_name:
            return self

        udf = self.model_copy()

        try:
            # Parse the code into an AST
            tree = ast.parse(udf.code, type_comments=True)

            # Rename existing udf -> udf_old
            visitor1 = RenameFunctionVisitor(
                old_name=target_new_name,
                new_name=f"{target_new_name}_old",
            )
            updated_tree = visitor1.visit(tree)

            # Rename the entrypoint -> udf
            visitor2 = RenameFunctionVisitor(
                old_name=self.entrypoint,
                new_name=target_new_name,
            )
            updated_tree = visitor2.visit(updated_tree)

            # Check if the original entrypoint function definition was found in the second pass
            if not visitor2.found_definition:
                raise ValueError(
                    f"Could not find the specified entrypoint function definition '{self.entrypoint}' in the UDF code."
                )

            # Ensure line numbers and column offsets are correct
            ast.fix_missing_locations(updated_tree)

            # Convert the potentially modified AST back to code
            udf.code = ast.unparse(updated_tree)
            udf.entrypoint = target_new_name

        except Exception as e:
            # Catch parsing, visiting, or unparsing errors
            raise RuntimeError(f"Failed to update entrypoint of UDF: {e}") from e

        return udf

    def set_parameters(
        self,
        parameters: dict[str, Any],
        replace_parameters: bool = False,
        inplace: bool = False,
    ) -> Udf:
        """Set the parameters on this UDF.

        Args:
            parameters: The new parameters dictionary.
            replace_parameters: If True, unset any parameters not in the parameters argument. Defaults to False.
            inplace: If True, modify this object. If False, return a new object. Defaults to True.
        """
        ret = _maybe_inplace(self, inplace)
        new_parameters = (
            parameters
            if replace_parameters
            else {
                **ret.parameters,
                **parameters,
            }
        )
        ret.parameters = new_parameters
        return ret

    def eval_schema(self, inplace: bool = False) -> Udf:
        """Reload the schema saved in the code of the UDF.

        Note that this will evaluate the UDF function.

        Args:
            inplace: If True, update this UDF object. Otherwise return a new UDF object (default).
        """
        from fused._udf.execute_v2 import execute_for_decorator

        new_udf = execute_for_decorator(self)
        assert isinstance(new_udf, Udf), f"UDF has unexpected type: {type(new_udf)}"
        ret = _maybe_inplace(self, inplace)
        ret._parameter_list = new_udf._parameter_list
        ret._parameter_has_kwargs = new_udf._parameter_has_kwargs
        return ret

    def run_local(
        self,
        *,
        inplace: bool = False,
        validate_imports: bool | None = None,
        **kwargs,
    ) -> UdfEvaluationResult:
        """Evaluate this UDF against a sample.

        Args:
            inplace: If True, update this UDF object with schema information. (default)
        """
        from fused._udf.execute_v2 import execute_against_sample

        ret = _maybe_inplace(self, inplace)
        return execute_against_sample(
            udf=ret,
            input=[],
            validate_imports=validate_imports,
            **kwargs,
        )

    def to_file(self, where: str | Path | BinaryIO, *, overwrite: bool = False):
        """Write the UDF to disk or the specified file-like object.

        The UDF will be written as a Zip file.

        Args:
            where: A path to a file or a file-like object.

        Keyword Args:
            overwrite: If true, overwriting is allowed.
        """
        updated_udf = self._with_udf_entrypoint()
        job = updated_udf()
        job.export(where, how="zip", overwrite=overwrite)

    def to_directory(self, where: str | Path | None = None, *, overwrite: bool = False):
        """Write the UDF to disk as a directory (folder).

        Args:
            where: A path to a directory. If not provided, uses the UDF function name.

        Keyword Args:
            overwrite: If true, overwriting is allowed.
        """
        updated_udf = self._with_udf_entrypoint()
        job = updated_udf()
        where = where or self.name
        job.export(where, how="local", overwrite=overwrite)

    # List of data input is passed - run that
    @overload
    def __call__(self, *, arg_list: Iterable[Any], **kwargs) -> UdfJobStepConfig: ...

    # Nothing is passed - run the UDF once
    @overload
    def __call__(self, *, arg_list: None = None, **kwargs) -> UdfJobStepConfig: ...

    def __call__(
        self, *, arg_list: Iterable[Any] | None = None, **kwargs
    ) -> UdfJobStepConfig:
        """Create a job from this UDF.

        Args:
            arg_list: A list of records to pass in to the UDF as input.
        """
        # cyclic dependency if imported at top-level
        from fused.models.api.job import UdfJobStepConfig

        with_params = self.model_copy()
        # TODO: Consider using with_parameters here, and validating that "context" and other reserved parameter names are not being passed.
        new_parameters = {**kwargs}
        if new_parameters:
            with_params.parameters = new_parameters

        if arg_list is not None and not len(arg_list):
            warnings.warn(
                FusedUdfWarning(
                    "An empty `arg_list` was passed in, no calls to the UDF will be made."
                )
            )

        return UdfJobStepConfig(
            udf=with_params,
            input=arg_list,
        )


EMPTY_UDF = Udf(name="EMPTY_UDF", code="", entrypoint="")

AnyBaseUdf = Annotated[Udf, Field(..., discriminator="type")]


class RootAnyBaseUdf(RootModel[AnyBaseUdf]):
    pass


def load_udf_from_response_data(data: dict, context=None) -> RootAnyBaseUdf:
    """Return a UDF from an HTTP response body, adding in metadata if necessary"""

    if context is None:
        context = {}

    # Always generate parameter list during deserialization
    if "load_parameter_list" not in context:
        context["load_parameter_list"] = True

    udf = RootAnyBaseUdf.model_validate_json(data["udf_body"], context=context).root
    # Restore metadata fields if they were not already present
    if not udf._get_metadata_safe(METADATA_FUSED_ID) and "id" in data:
        udf._set_metadata_safe(METADATA_FUSED_ID, data["id"])
    if not udf._get_metadata_safe(METADATA_FUSED_SLUG) and "slug" in data:
        udf._set_metadata_safe(METADATA_FUSED_SLUG, data["slug"])
    return udf


# Helper class for AST transformation
class RenameFunctionVisitor(ast.NodeTransformer):
    """
    AST visitor to rename a top level function definition AND its usages (ast.Name in calls/loads).
    """

    def __init__(self, old_name: str, new_name: str):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name
        self.found_definition = False  # Track if the definition was found

    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.name == self.old_name:
            if self.found_definition:
                warnings.warn(
                    f"Found multiple definitions of entrypoint function '{self.old_name}'"
                )
            node.name = self.new_name
            self.found_definition = True
        # Continue visiting other nodes
        return self.generic_visit(node)

    @override
    def visit_Name(self, node: ast.Name) -> ast.AST:
        # Rename names used in a 'load' context (i.e., references/calls)
        if node.id == self.old_name and isinstance(node.ctx, ast.Load):
            node.id = self.new_name
        return node  # Return the node itself (potentially modified)
