from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Callable, Optional
from zipfile import ZipFile

from loguru import logger

from fused._global_api import get_api
from fused.models._codegen import MetaJson
from fused.models.api import UdfJobStepConfig
from fused.models.udf import (
    AnyBaseUdf,
    Udf,
    load_udf_from_response_data,
)

from .._str_utils import is_uuid
from ._impl._context_impl import context_get_user_email

try:
    from cachetools import TTLCache, cached

    memoize_cache = cached(TTLCache(maxsize=10240, ttl=60))
    logger.debug("cachetools TTL memoize cache initialized")
except ImportError:
    from functools import lru_cache

    # Number of entries to store
    memoize_cache = lru_cache(maxsize=1024)
    logger.debug("lru memoize cache initialized")


def get_step_config_from_server(
    email_or_handle: Optional[str],
    slug: str,
    cache_key: Any,
    _is_public: bool = False,
    import_udf_globals: bool = True,
) -> UdfJobStepConfig:
    logger.info(f"Requesting {email_or_handle=} {slug=}")
    # cache_key is unused
    api = get_api()
    if _is_public:
        obj = api._get_public_udf(slug)
    else:
        obj = api._get_udf(email_or_handle, slug)
    udf = load_udf_from_response_data(
        obj, context={"import_globals": import_udf_globals}
    )

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


def load_udf_from_fused(
    email_or_handle_or_id: str,
    id: str | None = None,
    *,
    cache_key: Any = None,
    import_globals: bool | None = None,
) -> AnyBaseUdf:
    """
    Download the code of a UDF, to be run inline.

    Args:
        email_or_handle_or_id: Email or handle of the UDF's owner, or name of the UDF to import.
        id: Name of the UDF to import. If only the first argument is provided, the current user's email will be used.

    Keyword args:
        cache_key: Additional cache key for busting the UDF cache
    """
    if id is None and not is_uuid(email_or_handle_or_id):
        id = email_or_handle_or_id
        try:
            email_or_handle = context_get_user_email()
        except Exception as e:
            raise ValueError(
                "could not detect user ID from context, please specify the UDF as 'user@example.com' (or 'user'), 'udf_name'."
            ) from e
    else:
        email_or_handle = email_or_handle_or_id
    step_config = get_step_config_from_server(
        email_or_handle=email_or_handle,
        slug=id,
        cache_key=cache_key,
        import_udf_globals=import_globals,
    )

    return step_config.udf


async def get_step_config_from_server_async(
    email_or_handle: Optional[str],
    slug: str,
    cache_key: Any,
    _is_public: bool = False,
    import_udf_globals: bool = True,
) -> UdfJobStepConfig:
    """Async version of get_step_config_from_server that uses async HTTP requests"""
    api = get_api()
    if _is_public:
        obj = api._get_public_udf(slug)
    else:
        obj = await api._get_udf_async(email_or_handle, slug)

    udf = load_udf_from_response_data(
        obj, context={"import_globals": import_udf_globals}
    )
    return UdfJobStepConfig(udf=udf)


async def load_udf_from_fused_async(
    email_or_handle_or_id: str,
    id: str | None = None,
    *,
    cache_key: Any = None,
    import_globals: bool | None = None,
) -> AnyBaseUdf:
    """
    Asynchronously download the code of a UDF, to be run inline.

    This is the async version of load_udf_from_fused that uses async HTTP requests
    to avoid blocking the event loop during UDF metadata fetching.

    Args:
        email_or_handle_or_id: Email or handle of the UDF's owner, or name of the UDF to import.
        id: Name of the UDF to import. If only the first argument is provided, the current user's email will be used.

    Keyword args:
        cache_key: Additional cache key for busting the UDF cache
        import_globals: Whether to import globals from the UDF context
    """
    if id is None and not is_uuid(email_or_handle_or_id):
        id = email_or_handle_or_id
        try:
            from fused.core._impl._context_impl import context_get_user_email_async

            email_or_handle = await context_get_user_email_async()
        except Exception as e:
            raise ValueError(
                "could not detect user ID from context, please specify the UDF as 'user@example.com' (or 'user'), 'udf_name'."
            ) from e
    else:
        email_or_handle = email_or_handle_or_id

    step_config = await get_step_config_from_server_async(
        email_or_handle=email_or_handle,
        slug=id,
        cache_key=cache_key,
        import_udf_globals=import_globals,
    )
    return step_config.udf


@memoize_cache
def _get_github_udf_from_server(
    url: str, *, cache_key: Any = None, import_globals: bool | None = None
) -> AnyBaseUdf:
    logger.info(f"Requesting {url=}")
    # cache_key is unused
    api = get_api(credentials_needed=False)
    obj = api._get_code_by_url(url)
    udf = load_udf_from_response_data(obj, context={"import_globals": import_globals})
    return udf


def load_udf_from_github(
    url: str, *, cache_key: Any = None, import_globals: bool | None = None
) -> AnyBaseUdf:
    """
    Download the code of a UDF, to be run inline.

    Args:
        email_or_id: Email of the UDF's owner, or name of the UDF to import.
        id: Name of the UDF to import. If only the first argument is provided, the current user's email will be used.

    Keyword args:
        cache_key: Additional cache key for busting the UDF cache
    """
    return _get_github_udf_from_server(
        url=url, cache_key=cache_key, import_globals=import_globals
    )


def load_udf_from_shared_token(
    token: str, import_globals: bool | None = None
) -> AnyBaseUdf:
    """
    Download the code of a UDF from a shared token

    Args:
        token: the shared token for a UDF

    Raises:
        requests.HTTPError if the token is for a UDF that is not owned by the current user
    """
    api = get_api(credentials_needed=False)
    obj = api._get_udf_by_token(token)
    udf = load_udf_from_response_data(obj, context={"import_globals": import_globals})
    return udf


def _get_entrypoint_of_code(code: str):
    """
    Returns the name of the function decorated with '@fused.udf' in the provided code.
    If multiple functions are decorated with '@fused.udf', use "udf" as the entrypoint.
    """
    found_udf_names: list[str] = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    is_fused_udf = False
                    actual_decorator = decorator
                    # If the decorator is called (e.g., @fused.udf(arg=...)),
                    # the node is ast.Call, and the actual decorator is in .func
                    if isinstance(decorator, ast.Call):
                        actual_decorator = decorator.func

                    # Check for @fused.udf (Attribute)
                    if isinstance(actual_decorator, ast.Attribute):
                        if (
                            isinstance(actual_decorator.value, ast.Name)
                            and actual_decorator.value.id == "fused"
                            and actual_decorator.attr == "udf"
                        ):
                            is_fused_udf = True
                    # Check for @udf (Name, assuming `from fused import udf`)
                    elif (
                        isinstance(actual_decorator, ast.Name)
                        and actual_decorator.id == "udf"
                    ):
                        is_fused_udf = True

                    if is_fused_udf:
                        found_udf_names.append(node.name)
                        break  # Only need to find one relevant decorator per function

    except SyntaxError as e:
        raise ValueError(f"Invalid Python code provided: {e}") from e

    if not found_udf_names:
        raise ValueError(
            "No function decorated with '@fused.udf' found in the provided code."
        )
    elif len(found_udf_names) == 1:
        return found_udf_names[0]
    elif len(found_udf_names) > 1:
        if "udf" not in found_udf_names:
            raise ValueError(
                f"Multiple functions decorated with '@fused.udf' found: {', '.join(found_udf_names)}. "
                "Please provide code with only one decorated UDF."
            )
        else:
            return "udf"


def load_udf_from_code(
    code: str, name: Optional[str] = None, import_globals: bool | None = None
) -> Udf:
    """
    Load a UDF from raw code.

    """
    udf_entrypoint_name = _get_entrypoint_of_code(code)

    data = {
        "name": name or udf_entrypoint_name,  # Use found name as default
        "entrypoint": udf_entrypoint_name,  # Use found name as entrypoint
        "type": "geopandas_v2",
        "code": code,
    }
    return Udf.model_validate(
        data, context={"import_globals": import_globals, "load_parameter_list": True}
    )


def load_udf_from_file(path: Path, import_globals: bool | None = None) -> Udf:
    """
    Load a UDF from a python file

    Args:
        path : pathlib.Path
    """
    code = path.read_bytes().decode("utf8")
    udf_entrypoint_name = _get_entrypoint_of_code(code)

    data = {
        "name": path.stem,
        "entrypoint": udf_entrypoint_name,
        "type": "geopandas_v2",
        "code": code,
    }
    return Udf.model_validate(
        data, context={"import_globals": import_globals, "load_parameter_list": True}
    )


def _get_udf_from_directory(
    load_callback: Callable[[str], bytes], import_globals: bool | None = None
) -> Udf:
    meta_contents = json.loads(load_callback("meta.json"))
    meta = MetaJson.model_validate(meta_contents)

    if len(meta.job_config.steps) != 1:
        raise ValueError(
            f"meta.json is not in expected format: {len(meta.job_config.steps)=}"
        )

    if meta.job_config.steps[0]["type"] != "udf":
        raise ValueError(
            f'meta.json is not in expected format: {meta.job_config.steps[0]["type"]=}'
        )

    # Load the source code into the UDF model
    udf_dict = meta.job_config.steps[0]["udf"]
    source_file_name = udf_dict["source"]

    code = load_callback(source_file_name).decode("utf-8")
    udf_dict["code"] = code
    del udf_dict["source"]

    # Do the same for headers
    for header_dict in udf_dict["headers"]:
        header_source_file_name = header_dict.get("source_file")
        if header_source_file_name:
            del header_dict["source_file"]
            header_code = load_callback(header_source_file_name).decode("utf-8")
            header_dict["source_code"] = header_code

    return Udf.model_validate(
        udf_dict,
        context={"import_globals": import_globals, "load_parameter_list": True},
    )


def load_udf_from_directory(
    path: Path, import_globals: bool | None = None
) -> AnyBaseUdf:
    """
    Load a UDF from a python file

    Args:
        path : pathlib.Path
    """

    def _load_file(name: str) -> bytes:
        file_path = path / name
        if not file_path.exists():
            raise ValueError(
                f"Expected a file to be at {repr(file_path)}. Is this the right directory to load from?"
            )

        return file_path.read_bytes()

    return _get_udf_from_directory(
        load_callback=_load_file, import_globals=import_globals
    )


def load_udf_from_zip(path: Path, import_globals: bool | None = None) -> AnyBaseUdf:
    """
    Load a UDF from a python file

    Args:
        path : pathlib.Path
    """
    with ZipFile(path) as zf:
        return _get_udf_from_directory(
            load_callback=lambda f: zf.read(f), import_globals=import_globals
        )
