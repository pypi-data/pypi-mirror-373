from __future__ import annotations

from fused._udf.context import get_global_context


def context_get_user_email() -> str:
    context = get_global_context()
    assert context is not None, "context is unexpectedly None"
    assert hasattr(context, "user_email"), (
        "could not detect user ID from context, please specify the UDF as 'user@example.com', 'udf_name'."
    )
    return context.user_email


async def context_get_user_email_async() -> str:
    context = get_global_context()
    assert context is not None, "context is unexpectedly None"
    assert hasattr(context, "user_email_async"), (
        "could not detect user ID from context, please specify the UDF as 'user@example.com/udf_name'."
    )
    return await context.user_email_async()


def context_get_auth_header(*, missing_ok: bool = False) -> dict[str, str]:
    context = get_global_context()
    if not context:
        raise ValueError("missing global context")

    return context.auth_header(missing_ok=missing_ok)


def context_get_auth_scheme_and_token() -> tuple[str, str] | None:
    context = get_global_context()
    if not context:
        return None

    if context.auth_scheme and context.auth_token:
        return (context.auth_scheme, context.auth_token)
    return None


def context_in_realtime():
    context = get_global_context()
    return context.in_realtime


def context_in_batch():
    context = get_global_context()
    return context.in_batch
