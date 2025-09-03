from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests
from pydantic import BaseModel, ConfigDict

from fused._formatter.formatter_eval_result import fused_eval_result_repr
from fused.models.udf import AnyBaseUdf


class CacheSources(str, Enum):
    MEMORY = "memory"
    OBJECT_STORAGE = "object_storage"


@dataclass
class CacheStatus:
    is_cached: bool
    cache_source: CacheSources


def is_response_cached(r: requests.Response) -> CacheStatus:
    # Metadata is always persisted from original call and its cache=True value indicates that the UDF result was saved
    # in object storage, but doesn't tell us if the invocation was cached or regenerated and saved. Therefore, we read
    # the headers set by entities that know, either fused server or the cache proxy.
    from_cached_storage = r.headers.get("x-fused-cached") is not None
    from_cached_proxy = r.headers.get("x-cache", "").lower() == "hit"
    is_cached = from_cached_storage or from_cached_proxy

    if from_cached_proxy:
        cache_source = CacheSources.MEMORY
    elif from_cached_storage:
        cache_source = CacheSources.OBJECT_STORAGE
    else:
        cache_source = None

    return CacheStatus(is_cached=is_cached, cache_source=cache_source)


class UdfEvaluationResult(BaseModel):
    data: Any = None

    udf: AnyBaseUdf | None = None

    time_taken_seconds: float

    stdout: str | None = None
    stderr: str | None = None
    has_exception: bool = False
    exception_class: str | None = None
    error_message: str | None = None
    error_lineno: int | None = None
    error_type: str | None = None

    # TODO: Maybe update to one field cache_status: Optional[CacheStatus] = None ?
    is_cached: bool = False
    cache_source: CacheSources | None = None

    def _repr_html_(self) -> str:
        return fused_eval_result_repr(self)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class MultiUdfEvaluationResult(BaseModel):
    udf_results: list[UdfEvaluationResult | Any]

    def _repr_html_(self) -> str:
        # Aggregate reprs
        result_reprs = [
            udf_result._repr_html_()
            if hasattr(udf_result, "_repr_html_")
            else repr(udf_result)
            for udf_result in self.udf_results
        ]
        return "<br><br>".join(result_reprs)

    model_config = ConfigDict(arbitrary_types_allowed=True)
