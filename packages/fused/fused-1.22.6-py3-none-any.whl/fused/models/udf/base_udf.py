from __future__ import annotations

import ast
import difflib
import json
import re
import warnings
from contextlib import ExitStack
from copy import deepcopy
from enum import Enum
from functools import cached_property
from io import IOBase
from pathlib import PurePath
from textwrap import dedent, indent
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Literal,
    Sequence,
)

import requests
from loguru import logger
from pydantic import (
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
)
from pydantic_core.core_schema import ValidationInfo
from requests import HTTPError
from typing_extensions import Self, override

from fused._formatter.udf import fused_header_repr, fused_udf_repr
from fused._options import options as OPTIONS
from fused.models.base import FusedBaseModel, UserMetadataType
from fused.models.udf.header import Header
from fused.warnings import (
    FusedDeprecationWarning,
    FusedImportWarning,
    FusedUdfWarning,
    FusedWarning,
)

from .._codegen import (
    extract_parameters,
    stringify_headers,
    stringify_named_params,
    structure_params,
)
from .._inplace import _maybe_inplace

if TYPE_CHECKING:
    from fused.models.api import UdfAccessToken, UdfAccessTokenList
    from fused.models.api._cronjob import CronJob, CronJobSequence

from fused._global_api import get_api

METADATA_FUSED_ID = "fused:id"
METADATA_FUSED_DESCRIPTION = "fused:description"
METADATA_FUSED_SLUG = "fused:slug"
METADATA_FUSED_EXPLORER_TAB = "fused:explorerTab"


class HeaderSequence(RootModel[Sequence[Header]]):
    def _repr_html_(self) -> str:
        return fused_header_repr(self)

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, item, value):
        self.root[item] = value

    def __len__(self):
        return len(self.root)


class AttrDict(dict):
    """Dictionary where keys can also be accessed as attributes"""

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            if __name in self:
                return self[__name]
            else:
                raise

    def __dir__(self) -> Iterable[str]:
        return self.keys()


class CompiledAttrs(AttrDict):
    """Dictionary that stores compiled values where keys can also be accessed as attributes"""

    def __init__(self, header: Header = None, do_import: bool = False):
        self.do_import = do_import
        self.header = None
        if header:
            self.header = header
            if do_import:
                from fused._udf.state import noop_decorators_context

                with noop_decorators_context(True):
                    super().__init__(header._exec())

    def _do_import(self):
        from fused._udf.state import noop_decorators_context

        with noop_decorators_context(True):
            self.update(self.header._exec())

    def __deepcopy__(self, memo=None):
        # Deepcopy can happen when pydantic model_copy(deep=True) is called on UDF through _maybe_inplace
        # Note: IPython added additional values to __builtins__ globals which caused further issues during this process.
        cls = type(self)
        return cls(deepcopy(self.header, memo), self.do_import)


class UdfType(str, Enum):
    GEOPANDAS_V2 = "geopandas_v2"


class BaseUdf(FusedBaseModel):
    name: str | None = None
    type: Literal[UdfType.GEOPANDAS_V2]
    code: str
    headers: HeaderSequence | Sequence[Header] = Field(default_factory=list)
    metadata: UserMetadataType = None
    _globals: CompiledAttrs | None = None
    import_globals: bool = Field(default=True, exclude=True)
    _import_global_status: tuple[bool, str] | None = None

    @model_validator(mode="after")
    def _process_import(self, info: ValidationInfo) -> Self:
        self.import_globals = (
            info.context["import_globals"]
            if info.context and info.context.get("import_globals") is not None
            else self.import_globals
        )
        if not OPTIONS.never_import and self.import_globals:
            # This is to work around initializing EMPTY_UDF
            self._globals = CompiledAttrs()
            if self.code:
                with ExitStack() as stack:
                    if self.headers is not None:
                        for header in self.headers:
                            stack.enter_context(header._register_custom_finder())

                    module_name = f"{self.name or 'udf'}"
                    try:
                        self._globals = CompiledAttrs(
                            Header(
                                module_name=module_name,
                                source_code=self.code,
                                source_file=f"{module_name}.py",
                            ),
                            not OPTIONS.never_import,
                        )
                        self._import_global_status = (True, "")
                    except Exception as e:
                        self._import_global_status = (False, str(e))
                        warnings.warn(
                            f"Error importing globals for {self.name}: {str(e)}. "
                            f"Globals defined in the UDF's context will not be exposed as attributes on the UDF "
                            f"object - To disable importing UDF's globals, specify 'import_globals=False' or set "
                            f"fused.options.never_import = True to disable this globally.",
                            FusedImportWarning,
                        )

        return self

    def do_import_globals(self):
        self._globals._do_import()

    def __deepcopy__(self, memo=None):
        # deep copying the utils module might fail (in pickling)
        try:
            del self._cached_utils
        except AttributeError:
            pass
        return super().__deepcopy__(memo)

    def __eq__(self, other):
        # Quick check of equality by only checking types and public variables.
        # Pydantic __eq__ compare private attributes which fails existing equality checks.

        if not isinstance(other, self.__class__):
            return NotImplemented

        # Only compare public attributes as _globals contains un-comparable values.
        return self.__dict__ == other.__dict__

    def __getattr__(self, item: str):
        # Any private attribute access gets passed here (pydantic behavior)
        # Attribute access for those not found on the model also gets passed here (python behavior)

        method_attrs = {"utils", "_cached_utils"}
        # Ensure we prioritize access to the model's private attributes and method attributes
        if item in (self.__private_attributes__.keys() | method_attrs):
            return super().__getattr__(item)

        # This access takes advantage of the above private attributes check or else we'd be in an infinite loop.
        _g = self._globals
        if _g is None:
            raise AttributeError(
                "Accessing attributes on this UDF was disabled when it was loaded."
            )
        try:
            return getattr(_g, item)
        except AttributeError:
            successful, msg = self._import_global_status
            if not successful:
                raise AttributeError(f"UDF's globals failed to import: {msg}")
            raise AttributeError(
                f"{self.__class__.__name__!r} object has no attribute {item!r}"
            )

    @override
    def __repr_args__(self):
        # Pydantic uses this to build the value of __repr_str__
        metadata = self.metadata or {}
        yield "id", metadata.get("fused:id")
        yield "name", self.name
        yield "description", metadata.get("fused:description")
        catalog_url = self.catalog_url
        if catalog_url:
            yield "catalog_url", catalog_url

        # Define the metadata keys to potentially include
        optional_metadata_keys = {
            "fused:udfType": "udf_type",
            "fused:slug": "slug",
            "fused:gitRepo": "git_repo",
            "fused:gitLastModified": "last_modified",
        }

        for meta_key, repr_key in optional_metadata_keys.items():
            value = metadata.get(meta_key)
            if value:
                yield repr_key, value

        yield "code", self.code

    @override
    def __repr__(self) -> str:
        args_str = self.__repr_str__(",\n  ")
        return f"{self.__repr_name__()}(\n  {args_str}\n)"

    @override
    def __str__(self) -> str:
        return self.__repr__()

    @field_validator("headers", mode="before")
    @classmethod
    def _process_headers(cls, headers):
        processed_headers = []
        if headers is not None:
            for header in headers:
                if isinstance(header, str):
                    module_name = PurePath(header).name.split(".", maxsplit=1)[0]
                    processed_headers.append(
                        Header.from_code(module_name=module_name, source_file=header)
                    )
                elif (
                    isinstance(header, dict)
                    and header.get("source_file")
                    and not header.get("source_code")
                ):  # headers = {'source_file': 'header.py', 'module_name': 'header'}
                    source_file = header["source_file"]
                    module_name = header.get(
                        "module_name",
                        PurePath(source_file).name.split(".", maxsplit=1)[0],
                    )
                    processed_headers.append(
                        Header.from_code(
                            module_name=module_name,
                            source_file=source_file,
                        )
                    )
                else:
                    processed_headers.append(header)

        return processed_headers

    @field_validator("code", mode="before")
    @classmethod
    def _udf_is_str(cls, v):
        if isinstance(v, IOBase):
            # Handle passing in a file as the code
            v.seek(0)
            data = v.read()
            if isinstance(data, str):
                return data
            elif isinstance(data, bytes):
                return data.decode("utf-8")
            else:
                raise ValueError("Expected string or bytes from the file")

        return v

    @field_validator("code", mode="after")
    @classmethod
    def _code_valid_max_cache_age(cls, code: str):
        # Regex to find @fused.udf decorator and capture the cache_max_age value
        # It handles single or double quotes and optional spacing.
        # re.DOTALL allows '.' to match newline characters if the decorator spans multiple lines.
        match: re.Match[str] | None = re.search(
            r"@fused\.udf\(.*?cache_max_age\s*=\s*[\"']([^\"']+)['\"].*?\)",
            code,
            re.DOTALL,
        )

        if match:
            cache_age_str = match.group(1)
            # validate the cache_age_str to check it follows the standard format
            valid_value = re.match(r"(\d+)([smhd])$", cache_age_str.strip().lower())
            if not valid_value:
                raise ValueError(
                    f"Invalid `cache_max_age` parameter '{cache_age_str}': Use a number followed by one of 's' (seconds), 'm' (minutes), 'h' (hours), or 'd' (days)."
                )

        return code

    @classmethod
    def from_gist(cls, gist_id: str):
        """Create a Udf from a GitHub gist."""
        # TODO: if a versioned gist, taking the last / won't work as that will be the
        # version, not the gist id.
        if "/" in gist_id:
            gist_id = gist_id.split("/")[-1]

        url = f"https://api.github.com/gists/{gist_id}"
        r = requests.get(url, timeout=OPTIONS.request_timeout)
        r.raise_for_status()

        files: dict = r.json()["files"]

        obj = {}
        # TODO: Update expected files schema
        assert "code.py" in files.keys()
        assert "parameters.json" in files.keys()

        obj["code"] = _fetch_gist_content(files, "code.py")

        parameters_text = _fetch_gist_content(files, "parameters.json")
        parameters = json.loads(parameters_text)
        obj.update(parameters)

        return cls.model_validate(obj)

    # TODO: Rename to to_fused when deprecated features in existing to_fused are removed
    def _to_fused_v2(
        self,
        overwrite: bool | None = None,
    ):
        """
        Save this UDF on the Fused service.

        Args:
            overwrite: If True, overwrite existing remote UDF with the UDF object.
        """
        api = get_api()
        self_id = self._get_metadata_safe(METADATA_FUSED_ID)
        remote_udf = self._maybe_udf_by_name(self.name)
        backend_id = self_id
        old_metadata = None
        if remote_udf:
            remote_id = remote_udf._get_metadata_safe(METADATA_FUSED_ID)
            # Handle legacy use case of default overwriting if same udf
            if self_id == remote_id and overwrite is None:
                overwrite = True
            if overwrite:
                backend_id = remote_id
        else:
            # If the UDF does not exist, we need to save it as new
            if backend_id is not None:
                if overwrite:
                    warnings.warn(
                        "UDF does not exist on Fused. Saving as new UDF.",
                        FusedUdfWarning,
                        stacklevel=2,
                    )
                    # Try deleting the UDF by id if it exists before saving as new - fine if it doesn't exist.
                    try:
                        self.delete_saved()
                    except Exception as e:
                        # Using logger since we don't want to show this to the user by default.
                        logger.warning(
                            f"Failed to delete existing UDF with {id=}. {e}",
                            exc_info=True,
                        )
                backend_id = None

        # Ensures some metadata values are not serialized as it can lead to stale data upon loading.
        if self.metadata:
            old_metadata = self.metadata.copy() if self.metadata else {}
            self._delete_metadata_safe(METADATA_FUSED_ID)
            self._delete_metadata_safe(METADATA_FUSED_SLUG)

        try:
            result = api.save_udf(udf=self, slug=self.name, id=backend_id)
        except HTTPError as e:
            # If already exists:
            if e.response.status_code == 409:
                diff_lines = difflib.unified_diff(
                    (remote_udf.code + "\n").splitlines(keepends=True),
                    (self.code + "\n").splitlines(keepends=True),
                    fromfile="remote",
                    tofile="local",
                )
                raise ValueError(
                    f"{e.args[0]['detail']}. A diff of the code has been provided. Use overwrite=True if you want to replace the remote UDF with the local one.\n\n"
                    + "".join(diff_lines)
                )
            if old_metadata:
                self.metadata = old_metadata
            raise

        new_id = result["id"]
        self._set_metadata_safe(METADATA_FUSED_ID, new_id)
        self._set_metadata_safe(METADATA_FUSED_SLUG, self.name)
        return self

    def to_fused(
        self,
        overwrite: bool | None = None,
        **kwargs: dict[str, Any],
    ):
        """
        Save this UDF on the Fused service.

        Args:
            overwrite: If True, overwrite existing remote UDF with the UDF object.
        """

        # Deprecated parameters
        slug = kwargs.get("slug", ...)
        over_id = kwargs.get("over_id")
        as_new = kwargs.get("as_new")
        inplace = kwargs.get("inplace", True)

        if slug is not Ellipsis:
            warnings.warn(
                "'slug' parameter is deprecated. The name of the UDF will be used to generate the slug.",
                FusedDeprecationWarning,
                stacklevel=2,
            )

        if over_id:
            warnings.warn(
                "'over_id' parameter is deprecated.",
                FusedDeprecationWarning,
                stacklevel=2,
            )
        if as_new:
            warnings.warn(
                "'as_new' parameter is deprecated.",
                FusedDeprecationWarning,
                stacklevel=2,
            )

        if inplace is False:
            warnings.warn(
                "'inplace' parameter is deprecated.",
                FusedDeprecationWarning,
                stacklevel=2,
            )

        # New Flow
        if not any((slug is not Ellipsis, over_id, as_new, inplace is False)):
            return self._to_fused_v2(overwrite)

        backend_id = (
            str(over_id) if over_id else self._get_metadata_safe(METADATA_FUSED_ID)
        )
        if backend_id is None or as_new:
            assert as_new is not False, (
                "Cannot detect ID to save over, so as_new cannot be False."
            )
            backend_id = None

        ret = _maybe_inplace(self, inplace)

        if slug is Ellipsis:
            # If the user didn't specify a name to save as, determine the name
            # to save as here.
            slug = ret._get_metadata_safe(METADATA_FUSED_SLUG)
            if not slug:
                # No metadata-determined name, so use the regular name of the
                # UDF.
                slug = ret.name

        if slug and slug != ret.name:
            # If we are setting the name of the UDF, it is important to set the
            # name on the UDF body itself, because that is what Workbench will read
            ret.name = slug

        api = get_api()
        result = api.save_udf(
            udf=ret,
            slug=slug,
            id=backend_id,
        )
        new_id = result["id"]

        ret._set_metadata_safe(METADATA_FUSED_ID, new_id)
        ret._set_metadata_safe(METADATA_FUSED_SLUG, slug)
        return ret

    def _maybe_udf_by_name(self, slug: str):
        from .udf import load_udf_from_response_data

        api = get_api()
        try:
            remote_udf_data = api._get_udf(slug)
        except HTTPError:
            return None

        udf = load_udf_from_response_data(remote_udf_data)
        return udf

    def delete_saved(self, inplace: bool = True):
        from fused._global_api import get_api

        backend_id = self._get_metadata_safe(METADATA_FUSED_ID)
        if backend_id is None:
            raise ValueError("No saved UDF ID found in metadata.")

        api = get_api()
        api.delete_saved_udf(
            id=backend_id,
        )

        ret = _maybe_inplace(self, inplace)
        # ret.metadata must be non None because we read the backend ID from there
        ret.metadata.pop(METADATA_FUSED_ID)
        return ret

    def delete_cache(self):
        backend_id = self._get_metadata_safe(METADATA_FUSED_ID)
        if backend_id is None:
            raise ValueError("No saved UDF ID found in metadata.")

        api = get_api()
        api.delete_cache(backend_id)

        return self

    def create_access_token(
        self,
        *,
        client_id: str | Ellipsis | None = ...,
        public_read: bool | None = None,
        access_scope: str | None = None,
        cache: bool = True,
        metadata_json: dict[str, Any] | None = None,
        enabled: bool = True,
    ) -> UdfAccessToken:
        from fused._global_api import get_api

        # If there is a backend ID, locate this UDF by the backend ID rather than by its name
        backend_id = self._get_metadata_safe(METADATA_FUSED_ID)
        if backend_id is None:
            raise ValueError(
                "No saved UDF ID found in metadata. Save the UDF to Fused first with `.to_fused` and then create the access token."
            )

        api = get_api()
        return api.create_udf_access_token(
            udf_id=backend_id,
            client_id=client_id,
            public_read=public_read,
            access_scope=access_scope,
            cache=cache,
            metadata_json=metadata_json,
            enabled=enabled,
        )

    def get_access_tokens(self) -> UdfAccessTokenList:
        from fused._global_api import get_api
        from fused.models.api import UdfAccessTokenList

        # If there is a backend ID, locate this UDF by the backend ID rather than by its name
        backend_id = self._get_metadata_safe(METADATA_FUSED_ID)
        assert backend_id is not None, (
            "No saved UDF ID found in metadata. Save the UDF to Fused first with `.to_fused` and then create the access token."
        )

        api = get_api()
        all_tokens = api.get_udf_access_tokens(max_requests=None)

        return UdfAccessTokenList(
            [token for token in all_tokens if token.udf_id == backend_id]
        )

    def schedule(
        self,
        minute: list[int] | int,
        hour: list[int] | int,
        day_of_month: list[int] | int | None = None,
        month: list[int] | int | None = None,
        day_of_week: list[int] | int | None = None,
        udf_args: dict[str, Any] | None = None,
        enabled: bool = True,
        _create_udf: bool = True,
        **kwargs,
    ) -> "CronJob":
        """Schedule this UDF to run on a cron schedule.

        Args:
            minute: The minute to run the UDF on.
            hour: The hour to run the UDF on.
            day_of_month: The day of the month to run the UDF on. (Default every day)
            month: The month to run the UDF on. (Default every month)
            day_of_week: The day of the week to run the UDF on. (Default every day)
            udf_args: The arguments to pass to the UDF. (Default None)
            enabled: Whether the cron job is enabled. (Default True)
            _create_udf: Save the UDF to Fused before creating the CronJob. (Default True)
        """
        from fused.models.api._cronjob import CronJob

        return CronJob.from_udf(
            self,
            minute,
            hour,
            day_of_month,
            month,
            day_of_week,
            udf_args,
            enabled,
            _create_udf=_create_udf,
            **kwargs,
        )

    def get_schedule(self) -> "CronJobSequence":
        """Retrieve any scheduled runs of this UDF"""
        backend_id = self._get_metadata_safe(METADATA_FUSED_ID)
        if backend_id is None:
            raise ValueError("No saved UDF ID found in metadata.")

        return get_api().get_cronjobs_for_udf(backend_id)

    def _repr_html_(self) -> str:
        return fused_udf_repr(self)

    def _get_metadata_safe(self, key: str, default: Any | None = None) -> str | None:
        if self.metadata is not None:
            return self.metadata.get(key, default)
        else:
            return None

    def _set_metadata_safe(self, key: str, value: Any):
        if self.metadata is None:
            self.metadata = {}

        self.metadata[key] = value

    def _delete_metadata_safe(self, key: str):
        try:
            del self.metadata[key]
        except KeyError:
            pass

    def _generate_code(
        self, include_imports=True, headerfile=False
    ) -> tuple[str, Sequence[str]]:
        def _extract_fn(src: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
            # TODO: handle Header objects in header param
            parsed_ast = ast.parse(src)

            # Find all function definitions in the AST
            function_defs = [
                node
                for node in ast.walk(parsed_ast)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

            # first function (assume it's the target function)
            return function_defs[0]

        def _extract_fn_body(
            function_def: ast.FunctionDef | ast.AsyncFunctionDef, src: str
        ) -> str:
            target_function_body = function_def.body
            # Reconstruct the source code of the function body
            line_start = target_function_body[0].lineno - 1
            line_end = target_function_body[-1].end_lineno
            target_function_body_lines = [
                line for line in src.splitlines()[line_start:line_end]
            ]
            target_function_body_str = "\n".join(target_function_body_lines)

            return target_function_body_str

        # Derive parameters
        positional_parameters, named_parameters = extract_parameters(self.code)

        _params_fn_original = positional_parameters + stringify_named_params(
            named_parameters
        )
        # String: Imports
        str_imports = (
            "\n".join(
                [
                    "import fused",
                    "from fused.models.udf import Header",
                ]
            )
            + "\n\n"
        )
        # String: UDF header - Replace Header with file reference
        header_files = []
        processed_headers = []
        # TODO: do this conversion as part of header attribute
        for header in self.headers:
            if isinstance(header, Header):
                if headerfile:
                    filename = header.module_name + ".py"
                    processed_headers.append(filename)

                else:
                    processed_headers.append(header)
                # Create a file magic string
                header_files.append(header._generate_cell_code())

            else:
                processed_headers.append(header)

        _headers = (
            stringify_headers(processed_headers) if headerfile else processed_headers
        )
        params_decorator = [f"\n    headers={_headers}\n"]
        str_udf_header = (
            f"@fused.udf({structure_params(params_decorator, separator=',')})"
        )
        # String: Function header
        fn = _extract_fn(self.code)
        str_async = "async " if isinstance(fn, ast.AsyncFunctionDef) else ""
        str_fn_header = f"{str_async}def {self.entrypoint}({structure_params(_params_fn_original)}):"
        # String: Function body
        str_fn_body = dedent(_extract_fn_body(fn, src=self.code))

        str_udf = f"""
{str_udf_header}
{str_fn_header}
{indent(str_fn_body, " " * 4)}
"""
        if include_imports:
            str_udf = str_imports + str_udf
        return str_udf.strip("\n"), header_files

    def render(self):
        from IPython import get_ipython

        # Get the current IPython instance.
        ipython = get_ipython()
        if ipython is None:
            raise RuntimeError("This function can only be used in a Jupyter Notebook.")

        # Generate code string and spl into lines.
        code = self._generate_code()[0].strip()

        transformed = ipython.input_transformer_manager.transform_cell(code)
        # Set the content of the subsequent cell with.
        ipython.set_next_input(transformed)

    @property
    def utils(self):
        return self._cached_utils

    @cached_property
    def _cached_utils(self):
        if len(self.headers) == 0:
            raise ValueError("UDF does not have a utils module")
        if len(self.headers) > 1:
            raise ValueError("UDF has multiple header modules")
        if self.headers[0].module_name != "utils":
            warnings.warn(
                FusedWarning(
                    f"Accessing header module {self.headers[0].module_name} under the name utils"
                )
            )
        # TODO: Even though this might have already been evaluated, we have to evaluate it again now
        # It is at least cached

        vals = self.headers[0]._exec()
        vals["_udf"] = self

        return AttrDict(vals)

    @property
    def catalog_url(self) -> str | None:
        """Returns the link to open this UDF in the Workbench Catalog, or None if the UDF is not saved."""
        udf_id = self._get_metadata_safe("fused:id")
        if udf_id:
            return f"http://{OPTIONS.base_url.split('/')[2]}/workbench/catalog/{self.name}-{udf_id}"
        else:
            return None

    model_config = ConfigDict(exclude={"utils"})

    def __getstate__(self):
        # Pickling the utils will fail (module is not pickleable)
        try:
            del self._cached_utils
        except AttributeError:
            pass

        state = super().__getstate__()
        # Remove the _globals and _nested_callable attributes from the state
        # (modules and inline functions are not pickleable)
        state["__pydantic_private__"].pop("_globals", None)
        state["__pydantic_private__"].pop("_nested_callable", None)
        return state

    def __setstate__(self, state):
        super().__setstate__(state)
        # Recreate the _globals and _nested_callable attributes
        self._globals = None
        self._nested_callable = None
        # validate to ensure we run _process_import
        self.model_validate(self)


def _fetch_gist_content(gist_files_dict: dict, fname: str) -> str:
    gist_data = gist_files_dict[fname]

    if gist_data["truncated"]:
        full_url = gist_data["raw_url"]
        full_r = requests.get(full_url, timeout=OPTIONS.request_timeout)
        full_r.raise_for_status()
        return full_r.text
    else:
        return gist_data["content"]
