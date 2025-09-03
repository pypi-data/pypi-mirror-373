from pathlib import Path
from typing import Any, Union

import requests

from fused.models.api.udf_access_token import is_udf_token
from fused.models.udf import AnyBaseUdf

from .core import (
    load_udf_from_code,
    load_udf_from_directory,
    load_udf_from_file,
    load_udf_from_fused,
    load_udf_from_fused_async,
    load_udf_from_github,
    load_udf_from_shared_token,
    load_udf_from_zip,
)


def load(
    url_or_udf: Union[str, Path],
    /,
    *,
    cache_key: Any = None,
    import_globals: bool = True,
) -> AnyBaseUdf:
    """
    Loads a UDF from various sources including GitHub URLs,
    and a Fused platform-specific identifier.

    This function supports loading UDFs from a GitHub repository URL, or a Fused
    platform-specific identifier composed of an email and UDF name. It intelligently
    determines the source type based on the format of the input and retrieves the UDF
    accordingly.

    Args:
        url_or_udf: A string representing the location of the UDF, or the raw code of the UDF.
            The location can be a GitHub URL starting with "https://github.com",
            a Fused platform-specific identifier in the format "email/udf_name",
            or a local file path pointing to a Python file.
        cache_key: An optional key used for caching the loaded UDF. If provided, the function
            will attempt to load the UDF from cache using this key before attempting to
            load it from the specified source. Defaults to None, indicating no caching.
        import_globals: Expose the globals defined in the UDF's context as attributes on the UDF object (default True).
            This requires executing the code of the UDF. To globally configure this behavior, use `fused.options.never_import`.

    Returns:
        AnyBaseUdf: An instance of the loaded UDF.

    Raises:
        ValueError: If the URL or Fused platform-specific identifier format is incorrect or
            cannot be parsed.
        Exception: For errors related to network issues, file access permissions, or other
            unforeseen errors during the loading process.

    Examples:
        Load a UDF from a GitHub URL:
        ```py
        udf = fused.load("https://github.com/fusedio/udfs/tree/main/public/REM_with_HyRiver/")
        ```

        Load a UDF using a Fused platform-specific identifier:
        ```py
        udf = fused.load("username@fused.io/REM_with_HyRiver")
        ```
    """
    # NOTE: Order matters
    if str(url_or_udf).startswith("https://github.com"):
        return load_udf_from_github(
            url_or_udf, cache_key=cache_key, import_globals=import_globals
        )

    if isinstance(url_or_udf, str) and "\n" in url_or_udf:
        # if there are newlines, assume this is raw code
        return load_udf_from_code(url_or_udf, import_globals=import_globals)

    path = Path(url_or_udf)

    if path.suffix == ".py":
        return load_udf_from_file(path, import_globals=import_globals)

    if path.suffix == ".zip":
        return load_udf_from_zip(path, import_globals=import_globals)

    if path.is_dir():  # Non-existant paths will be false
        return load_udf_from_directory(path, import_globals=import_globals)

    if isinstance(url_or_udf, str):
        if is_udf_token(url_or_udf):
            try:
                return load_udf_from_shared_token(
                    url_or_udf, import_globals=import_globals
                )
            except requests.HTTPError:
                raise ValueError(
                    "It looks like you tried to load a UDF from a shared token "
                    "without having access to the source code. "
                    "You may want to call `run` instead of `load`."
                )

        # remaining cases: assume UDF name or user/name
        parts = url_or_udf.split("/", maxsplit=1)
        if len(parts) == 2:
            email_or_handle, udf_name = parts
            return load_udf_from_fused(
                email_or_handle,
                udf_name,
                cache_key=cache_key,
                import_globals=import_globals,
            )
        elif len(parts) == 1:
            udf_name = parts[0]
            return load_udf_from_fused(
                udf_name, cache_key=cache_key, import_globals=import_globals
            )

    if not path.exists():
        raise FileNotFoundError(str(path))

    else:
        raise ValueError(
            f"Ambiguous file detected {path}. Ensure file exists and has an extension."
        )


async def load_async(
    url_or_udf: Union[str, Path],
    /,
    *,
    cache_key: Any = None,
    import_globals: bool = True,
) -> AnyBaseUdf:
    """
    Asynchronously loads a UDF from various sources including GitHub URLs,
    and a Fused platform-specific identifier.

    This is the async-optimized version of fused.load() that uses async HTTP requests
    to avoid blocking the event loop during UDF metadata fetching.

    Args:
        url_or_udf: A string representing the location of the UDF, or the raw code of the UDF.
        cache_key: An optional key used for caching the loaded UDF.
        import_globals: Expose the globals defined in the UDF's context as attributes on the UDF object.

    Returns:
        AnyBaseUdf: An instance of the loaded UDF.

    Examples:
        Load a UDF asynchronously:
        ```py
        udf = await fused.load_async("username@fused.io/my_udf_name")
        ```

        Use in parameter validation:
        ```py
        if not isinstance(udf, Udf):
            udf = await fused.load_async(udf)
        ```
    """
    # NOTE: Order matters - same logic as sync version but with async calls where needed
    if str(url_or_udf).startswith("https://github.com"):
        # TODO: Make async
        return load_udf_from_github(
            url_or_udf, cache_key=cache_key, import_globals=import_globals
        )

    if isinstance(url_or_udf, str) and "\n" in url_or_udf:
        # TODO: Make async?
        return load_udf_from_code(url_or_udf, import_globals=import_globals)

    path = Path(url_or_udf)

    if path.suffix == ".py":
        # TODO: Make async
        return load_udf_from_file(path, import_globals=import_globals)

    if path.suffix == ".zip":
        # TODO: Make async
        return load_udf_from_zip(path, import_globals=import_globals)

    if path.is_dir():
        # TODO: Make async
        return load_udf_from_directory(path, import_globals=import_globals)

    if isinstance(url_or_udf, str):
        if is_udf_token(url_or_udf):
            try:
                # TODO: Make async
                return load_udf_from_shared_token(
                    url_or_udf, import_globals=import_globals
                )
            except requests.HTTPError:
                raise ValueError(
                    "It looks like you tried to load a UDF from a shared token "
                    "without having access to the source code. "
                    "You may want to call `run` instead of `load`."
                )

        parts = url_or_udf.split("/", maxsplit=1)
        if len(parts) == 2:
            email_or_handle, udf_name = parts
            return await load_udf_from_fused_async(
                email_or_handle,
                udf_name,
                cache_key=cache_key,
                import_globals=import_globals,
            )
        elif len(parts) == 1:
            udf_name = parts[0]
            return await load_udf_from_fused_async(
                udf_name, cache_key=cache_key, import_globals=import_globals
            )

    if not path.exists():
        raise FileNotFoundError(str(path))

    else:
        raise ValueError(
            f"Ambiguous file detected {path}. Ensure file exists and has an extension."
        )
