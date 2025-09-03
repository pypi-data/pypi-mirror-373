from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import requests
from loguru import logger

from fused._options import StorageStr, _get_data_dir
from fused._options import options as OPTIONS
from fused.core._impl._context_impl import context_in_batch, context_in_realtime

if TYPE_CHECKING:
    import fsspec


def data_path(storage: StorageStr = "auto") -> Path:
    if storage != "auto":
        return _get_data_dir(storage)
    return OPTIONS.data_directory


def filesystem(protocol: str, **storage_options) -> fsspec.AbstractFileSystem:
    """Get an fsspec filesystem for the given protocol.

    Args:
        protocol: Protocol part of the URL, such as "s3" or "gs".
        storage_options: Additional arguments to pass to the storage backend.

    Returns:
        An fsspec AbstractFileSystem.
    """

    import fsspec

    return fsspec.filesystem(protocol, **storage_options)


def _download_requests(url: str) -> bytes:
    # this function is shared
    response = requests.get(url, headers={"User-Agent": ""})
    response.raise_for_status()
    return response.content


def _download_signed(url: str) -> bytes:
    from fused.api._public_api import get_api

    api = get_api()
    return _download_requests(api.sign_url(url))


def _download_object(protocol: str, url: str) -> bytes:
    """

    Args:
        protocol: Protocol part of the URL, such as "s3" or "gs".
        url: Object URL with or without the protocol.

    Returns:
        The object's content in bytes
    """
    # Local needs to use signed URL to impersonal remote IAM role to download the file while remote can assume it has
    # direct access to S3 resources due to its IAM role.
    if not context_in_realtime() and not context_in_batch():
        logger.debug("Trying a signed URL")
        try:
            return _download_signed(url)
        except Exception as e:
            logger.debug(str(e))

    fs = filesystem(protocol)
    with fs.open(url, "rb") as f:
        return f.read()
