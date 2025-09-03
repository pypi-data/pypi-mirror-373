from typing import Literal

from fused._options import options as OPTIONS
from fused._udf.context import get_global_context


def make_realtime_url(client_id: str | None) -> str:
    context = get_global_context()

    if client_id is None and context is not None:
        client_id = context.realtime_client_id

    if client_id is None:
        client_id = OPTIONS.realtime_client_id

    if client_id is None:
        raise ValueError(
            "Failed to detect realtime client ID (context is "
            "not configured with client ID)"
        )

    return f"{OPTIONS.base_url}/realtime/{client_id}"


def make_shared_realtime_url(id: str) -> str:
    return f"{OPTIONS.base_url}/realtime-shared/{id}"


def get_recursion_factor() -> int:
    context = get_global_context()

    recursion_factor = context.recursion_factor
    if recursion_factor is None:
        recursion_factor = 1
    if recursion_factor > OPTIONS.max_recursion_factor:
        raise ValueError(
            f"Recursion factor {recursion_factor} exceeds maximum {OPTIONS.max_recursion_factor}"
        )

    return recursion_factor + 1


def default_run_engine() -> Literal["remote", "local"]:
    if OPTIONS.default_udf_run_engine is not None:
        return OPTIONS.default_udf_run_engine
    return "remote"
