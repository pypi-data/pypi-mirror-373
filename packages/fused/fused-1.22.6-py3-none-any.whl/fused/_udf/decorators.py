import ast
import inspect
import re
import warnings
from datetime import timedelta
from textwrap import dedent
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    get_type_hints,
)

from fused._udf.state import (
    decorator_import_globals_disabled,
    decorator_src_override,
    decorator_udf_override,
    noop_decorators,
)
from fused.models.request import WHITELISTED_INSTANCE_TYPES_values
from fused.models.udf import Header, Udf
from fused.warnings import (
    FusedIgnoredWarning,
    FusedPythonVersionWarning,
    FusedUdfWarning,
)

RESERVED_UDF_PARAMETERS = {
    "self",
    "arg_list",
    "output_table",
}
"""Set of UDF parameter names that should not be used because they will cause conflicts
when instantiating the UDF to a job."""

UDF_RUN_KWARGS = {"x", "y", "z"}
"""Set of UDF keyword arguments that are also parameters to udf.run(), which would cause the
user's UDF arguments to be clobbered."""


def _extract_parameter_list(
    func: Callable, num_positional_args: int
) -> Tuple[List[str], bool]:
    parameter_list: List[str] = []
    has_kwargs = False
    xyz_reserved_seen: Set = set()

    signature = inspect.signature(func)
    for param_idx, param in enumerate(signature.parameters.values()):
        # Don't check certain
        is_reserved_positional_param = (param_idx == 0 and param.name == "dataset") or (
            param_idx == 1 and param.name == "right"
        )
        if param.name in RESERVED_UDF_PARAMETERS and not is_reserved_positional_param:
            warnings.warn(
                FusedUdfWarning(
                    f'Parameter named "{param}" is reserved and may cause conflicts. If you want to set the Fused option with the same name, provide it when instantiating the UDF but not in the parameter list.'
                )
            )

        if param.kind == inspect.Parameter.VAR_KEYWORD:
            has_kwargs = True

        if (
            param.kind
            in [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]
            and param.name in UDF_RUN_KWARGS
        ):
            xyz_reserved_seen.add(param.name)

        # TODO decide if we want to restrict this to certain keyword names
        # # Special bbox types are reserved exclusively for the 'bbox' parameter
        # if (
        #     param.name != BBOX_NAME
        #     and param.annotation in EXPECTED_UDF_KWARG_TYPES[BBOX_NAME]
        # ):
        #     warnings.warn(
        #         FusedUdfWarning(
        #             f'Parameter "{param}" specifies a valid Fused geometry type, but only the parameter named "{BBOX_NAME}" will receive geometry from the runtime.'
        #         )
        #     )

        if param_idx < num_positional_args:
            # This is one of the first args for getting the input data
            continue

        if param.kind in [
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.VAR_POSITIONAL,
        ]:
            warnings.warn(
                FusedUdfWarning(
                    f"Positional-only argument (name {param.name}, kind {param.kind}) cannot be specified in UDFs"
                )
            )
        elif param.kind != inspect.Parameter.VAR_KEYWORD:
            # Must be a keyword only parameter
            # This parameter must be specified: if param.default is not inspect._empty:
            # TODO: This parameter_list is not used at all, instead the signature is called below.
            parameter_list.append(param.name)

    if len(xyz_reserved_seen) == 3:
        warnings.warn(
            FusedIgnoredWarning(
                f"Parameters named 'x', 'y' and 'z' for UDF '{func.__name__}' are "
                "reserved and will be clobbered when passing all three of them "
                "to fused.run() at the same time."
            )
        )

    return list(signature.parameters.keys()), has_kwargs


def _parse_ttl(ttl: Optional[Union[str, int]], cache: bool = True) -> Optional[int]:
    if ttl is None:
        if not cache:
            return 0
        return None
    elif not cache:
        raise ValueError("Cannot specify both `cache_max_age` and `cache=False`")

    if ttl == 0 or (isinstance(ttl, str) and ttl.strip() == "0"):
        return 0

    if isinstance(ttl, int):
        ttl = f"{ttl}s"

    quantifier = re.match(r"(\d+)([smhd])$", ttl.strip().lower())
    if not quantifier:
        raise ValueError(
            "Invalid `cache_max_age` parameter: Use a number followed by one of 's' (seconds), 'm' (minutes), 'h' (hours), or 'd' (days)."
        )

    value, unit = int(quantifier.group(1)), quantifier.group(2)
    delta_map = {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
    }
    return int(delta_map[unit].total_seconds())


def _validate_instance_type(instance_type: Optional[str]) -> Optional[str]:
    if instance_type is None:
        return None

    if (
        instance_type not in ("realtime", "small", "medium", "large")
        and instance_type not in WHITELISTED_INSTANCE_TYPES_values
    ):
        raise ValueError(
            "Invalid instance type specified. Must be 'realtime', 'small', "
            "'medium', 'large', or one of the whitelisted instance types "
            f"({WHITELISTED_INSTANCE_TYPES_values})."
        )

    return instance_type


# Note: If the signature of this function changes, the signature of the
# specialized versions of it below must also change. This pattern is used
# so that the internal function can be reused (pass in different _udf_cls),
# but the type hinting in e.g. VS Code is correct. Importantly, this type
# hinting includes the keyword parameters. Otherwise the way to express
# the type to VS Code is either not possible or too complicated.
def _udf_internal(
    fn: Optional[Callable] = None,
    *,
    _udf_cls: type[Udf],
    _num_positional_args: int,
    name: Union[str, None] = None,
    cache_max_age: Optional[str] = None,
    instance_type: Optional[str] = None,
    default_parameters: Optional[Dict[str, Any]] = None,
    headers: Optional[Sequence[Union[str, Header]]] = None,
):
    def _internal_decorator_wrapper(func):
        if noop_decorators.get():
            return func

        entrypoint = func.__name__
        fn_name = name or entrypoint

        _src = decorator_src_override.get() or inspect.getsource(func)
        _src = dedent(_src)
        # src = _strip_decorators(_src)
        _src, original_headers = _strip_decorator_params(_src, cache_max_age)
        _src = _add_type_annotation_imports(_src, func)

        src = _src

        parameter_list, parameter_has_kwargs = _extract_parameter_list(
            func, num_positional_args=_num_positional_args
        )

        resolved_headers = headers
        override_udf = decorator_udf_override.get()
        if override_udf and override_udf.headers:
            # model_dump is needed because the headers are really the wrong type
            resolved_headers = [h.model_dump() for h in override_udf.headers]

        import_globals_disabled = decorator_import_globals_disabled.get()
        import_globals = False if import_globals_disabled else True

        new_udf = _udf_cls(
            code=src.strip("\n"),
            name=fn_name,
            entrypoint=entrypoint,
            cache_max_age=_parse_ttl(cache_max_age),
            instance_type=_validate_instance_type(instance_type),
            parameters=default_parameters or {},
            headers=resolved_headers,
            original_headers=original_headers,
            import_globals=import_globals,
        )
        new_udf._parameter_list = parameter_list
        new_udf._parameter_has_kwargs = parameter_has_kwargs
        new_udf._nested_callable = func
        return new_udf

    if fn is not None:
        return _internal_decorator_wrapper(fn)
    else:
        return _internal_decorator_wrapper


# Specializations of _udf_internal. Note we return Callable so that type hinting
# is right when using "@fused.udf()" -- but this does mean it's wrong when
# using "@fused.udf".
def udf(
    fn: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    cache_max_age: Optional[str] = None,
    instance_type: Optional[str] = None,
    default_parameters: Optional[Dict[str, Any]] = None,
    headers: Optional[Sequence[Union[str, Header]]] = None,
    **kwargs: dict[str, Any],
) -> Callable[..., Udf]:
    """A decorator that transforms a function into a Fused UDF.

    Args:
        name: The name of the UDF object. Defaults to the name of the function.
        cache_max_age: The maximum age when returning a result from the cache.
        instance_type: The default type of instance to use for remote execution
           ('realtime' or 'batch').
        default_parameters: Parameters to embed in the UDF object, separately from the arguments
            list of the function. Defaults to None for empty parameters.
        headers: A list of files to include as modules when running the UDF. For example,
            when specifying `headers=['my_header.py']`, inside the UDF function it may be
            referenced as:

            ```py
            import my_header
            my_header.my_function()
            ```

            Defaults to None for no headers.

    Returns:
        A callable that represents the transformed UDF. This callable can be used
        within GeoPandas workflows to apply the defined operation on geospatial data.

    Examples:
        To create a simple UDF that calls a utility function to calculate the area of geometries in a GeoDataFrame:

        ```py
        @fused.udf
        def udf(bbox, table_path="s3://fused-asset/infra/building_msft_us"):
            ...
            gdf = table_to_tile(bbox, table=table_path)
            return gdf
        ```
    """
    if kwargs.get("schema") is not None:
        warnings.warn(
            FusedUdfWarning(
                "The `schema` parameter is deprecated and will be removed in a future version."
            )
        )

    return _udf_internal(
        fn=fn,
        _udf_cls=Udf,
        _num_positional_args=2,
        name=name,
        cache_max_age=cache_max_age,
        instance_type=instance_type,
        default_parameters=default_parameters,
        headers=headers,
    )


def _strip_decorator_params(src: str, cache_max_age=None) -> str:
    """Remove all parameter from decorator declaration."""
    # TODO: use ast by line number to not use ast.unparse

    # TODO: This requires Python 3.9 because ast.unparse was exposed in that release.
    # https://docs.python.org/3/whatsnew/3.9.html#ast We may be able to backport it?
    if not hasattr(ast, "unparse"):
        warnings.warn(
            FusedPythonVersionWarning(
                "Decorators will not be removed from UDF source because ast.unparse is not available in this version of Python"
            )
        )
        return src, ""

    tree = ast.parse(src)

    original_headers = ""
    changes_made = False

    def remove_params_from_decorator(node):
        nonlocal changes_made
        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.value.id == "fused"
                and node.func.attr == "udf"
            ):
                keywords = []
                for each_keyword in node.keywords:
                    if each_keyword.arg == "headers":
                        nonlocal original_headers
                        original_headers = ast.unparse(each_keyword.value)
                        changes_made = True
                    elif each_keyword.arg == "cache_max_age":
                        # if cache_max_age was passed as a variable, replace with its literal
                        if not isinstance(each_keyword.value, ast.Constant):
                            each_keyword.value = ast.Constant(value=cache_max_age)
                        changes_made = True
                        keywords.append(each_keyword)
                node.keywords = keywords
        return node

    # Remove parameters from the fused decorator definition
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            new_decorators = []
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    new_decorators.append(remove_params_from_decorator(decorator))
                else:
                    new_decorators.append(decorator)

    if changes_made:
        modified_src = ast.unparse(tree)

        return modified_src, original_headers
    else:
        # Avoid unparsing if not absolutely necessary. This is because of e.g.
        # PEP 701 causing differences between Python 3.11/3.12 rendering of f-strings.
        return src, ""


def _add_type_annotation_imports(src: str, func) -> str:
    """Add import statements for type annotations.

    Currently this function only specifically handles pandas.DataFrame
    and geopandas.GeoDataFrame in the annotations (and other built-ins
    will work fine anyway).
    """

    # TODO replace this with inspect.get_annotations when dropping Python 3.9 support
    try:
        type_hints = get_type_hints(func)
    except NameError:
        # if the type hints cannot be retrieved (eg strings), return the original source
        # see https://github.com/fusedlabs/application/pull/3744
        return src

    # check the function arguments for annotations using pandas/geopandas
    annotations = {}
    for param, annot in type_hints.items():
        if annot.__module__ not in ("builtins", "fused"):
            annotations[param] = annot

    if not annotations:
        return src

    # walk the ast tree to find the exact syntax used in the type annotations
    # to generate the correct imports
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_args = node.args
            break

    imports = []

    for arg in func_args.args:
        if arg.arg in annotations:
            obj = annotations[arg.arg]

            if isinstance(arg.annotation, ast.Name):
                name = arg.annotation.id
                if name == obj.__name__:
                    imports.append(f"from {obj.__module__} import {name}")
                else:
                    imports.append(
                        f"from {obj.__module__} import {obj.__name__} as {name}"
                    )
            elif isinstance(arg.annotation, ast.Attribute):
                if isinstance(arg.annotation.value, ast.Name):
                    name = arg.annotation.value.id
                    if name == obj.__module__:
                        imports.append(f"import {obj.__module__}")
                    else:
                        top_level = obj.__module__.split(".")[0]
                        if name == top_level:
                            imports.append(f"import {top_level}")
                        else:
                            imports.append(f"import {top_level} as {name}")

    if imports:
        src = "\n".join(imports) + "\n\n" + src

    return src
