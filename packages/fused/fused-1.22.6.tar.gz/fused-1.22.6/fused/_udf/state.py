from __future__ import annotations

import contextlib
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fused.models.udf import AnyBaseUdf


noop_decorators: ContextVar[bool] = ContextVar("noop_decorator", default=False)
decorator_src_override: ContextVar[str | None] = ContextVar(
    "decorator_src_override", default=None
)
decorator_udf_override: ContextVar[AnyBaseUdf | None] = ContextVar(
    "decorator_udf_override", default=None
)

decorator_import_globals_disabled: ContextVar[bool | None] = ContextVar(
    "decorator_import_globals_override", default=None
)


@contextmanager
def noop_decorators_context(val: bool):
    token = noop_decorators.set(val)
    try:
        yield token
    finally:
        noop_decorators.reset(token)


# Provides the UDF's code to the fused.udf decorator via the global context (above).
#
# Injecting the UDF code back inside the run function.
@contextmanager
def decorator_src_override_context(val: str):
    token = decorator_src_override.set(val)
    try:
        yield token
    finally:
        decorator_src_override.reset(token)


@contextmanager
def decorator_udf_override_context(udf: AnyBaseUdf):
    token = decorator_udf_override.set(udf)
    try:
        yield token
    finally:
        decorator_udf_override.reset(token)


@contextmanager
def decorator_import_globals_disable_context():
    token = decorator_import_globals_disabled.set(True)
    try:
        yield token
    finally:
        decorator_import_globals_disabled.reset(token)


class StdStreamProxy:
    """Act as a proxy for a target stream to prevent it from being closed unexpectedly"""

    def __init__(self, target: str):
        self._target = target
        self._stream = getattr(sys, target)

    # Forward all non-overridden methods
    def __getattr__(self, item):
        return getattr(self._stream, item)

    # To mitigate UDF crashes, we prevent close from operating on the stream. We ensure that anything left in the buffer
    # is flushed.
    def close(self):
        self.flush()

    def get_stream(self):
        return self._stream

    def __enter__(self):
        setattr(sys, self._target, self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        setattr(sys, self._target, self._stream)


@contextlib.contextmanager
def _isolate_streams():
    # We proxy all streams, including the dunder variants, to ensure none are closed within UDF code
    with (
        StdStreamProxy("stdin") as stdin_proxy,
        StdStreamProxy("__stdin__") as __stdin_proxy,
        StdStreamProxy("stdout") as stdout_proxy,
        StdStreamProxy("__stdout__") as __stdout_proxy,
        StdStreamProxy("stderr") as stderr_proxy,
        StdStreamProxy("__stderr__") as __stderr_proxy,
    ):
        yield (
            stdin_proxy,
            __stdin_proxy,
            stdout_proxy,
            __stdout_proxy,
            stderr_proxy,
            __stderr_proxy,
        )
