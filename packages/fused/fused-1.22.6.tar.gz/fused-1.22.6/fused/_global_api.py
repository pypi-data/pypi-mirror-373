from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fused.api import FusedAPI, FusedDockerAPI


API: FusedAPI | FusedDockerAPI | None = None

# We expect this to be set after import
API_CLASS: type[FusedAPI] | None = None


def get_api(**api_kwargs) -> FusedAPI | FusedDockerAPI:
    global API
    if API is not None:
        return API

    if API_CLASS is not None:
        API = API_CLASS(**api_kwargs)
        return API

    raise ValueError("Internal error: Global API_CLASS was not set.")


def set_api(api: FusedAPI | FusedDockerAPI) -> None:
    global API
    API = api


def set_api_class(api_class: type[FusedAPI]) -> None:
    global API_CLASS
    API_CLASS = api_class


def reset_api():
    global API
    API = None
