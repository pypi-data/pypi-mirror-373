# TODO: This file is no longer the most recent -- use fused.core.run_* instead
# This file is only for running non-saved (code included) UDFs
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pyarrow as pa
from loguru import logger

from fused._options import options as OPTIONS
from fused._request import default_retry_strategy, session_with_retries
from fused.api.api import FusedAPI, resolve_udf_server_url
from fused.core._realtime_ops import (
    _process_response,
    _process_response_async,
    serialize_realtime_params,
)
from fused.models import AnyJobStepConfig
from fused.models.udf._eval_result import UdfEvaluationResult

from ..core._impl._realtime_ops_impl import get_recursion_factor
from ..core._realtime_ops import _realtime_raise_for_status_async

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd


def run_tile(
    x: float,
    y: float,
    z: float,
    data: None | (pd.DataFrame | gpd.GeoDataFrame | pa.Table | str | Path | Any) = None,
    step_config: AnyJobStepConfig | None = None,
    params: dict[str, str] | None = None,
    *,
    print_time: bool = False,
    client_id: str | None = None,
    cache_max_age: int | None = None,
    dtype_out_vector: str | None = None,
    dtype_out_raster: str | None = None,
    _profile: bool = False,
    run_id: str | None = None,
) -> UdfEvaluationResult:  # TODO: return png
    time_start = time.perf_counter()
    # We need to get the auth headers from the FusedAPI. Don't enable set_global_api
    # to avoid messing up the user's environment.
    api = FusedAPI(set_global_api=False)

    udf_server_url = resolve_udf_server_url(client_id)

    assert step_config is not None
    # Apply parameters, if we want to step_config that's returned to have this,
    # overwrite step_config.
    step_config_with_params = step_config.set_udf(
        udf=step_config.udf, parameters=serialize_realtime_params(params)
    )

    url = f"{udf_server_url}/api/v1/run/udf/tiles/{z}/{x}/{y}"

    # Headers
    recursion_factor = get_recursion_factor()
    headers = api._generate_headers(
        {
            "Content-Type": "application/json",
            **(OPTIONS.default_run_headers or {}),
        }
    )
    headers["Fused-Recursion"] = f"{recursion_factor}"

    # Payload
    post_attr_json = {
        "data_left": data,
        "data_right": None,
        "step_config": step_config_with_params.model_dump_json(),
        "dtype_in": "json",
        # TODO remove dtype_out
        "dtype_out_vector": dtype_out_vector or OPTIONS.default_dtype_out_vector,
        "dtype_out_raster": dtype_out_raster or OPTIONS.default_dtype_out_raster,
        "profile": _profile,
    }

    # Params
    req_params = {
        **({"cache_max_age": int(cache_max_age)} if cache_max_age is not None else {}),
    }

    # Make request
    start = time.time()

    with session_with_retries() as session:
        r = session.post(
            url=url,
            params=req_params,
            json=post_attr_json,
            headers=headers,
            timeout=OPTIONS.run_timeout,
        )

    end = time.time()
    if print_time:
        logger.info(f"Time in request: {end - start}")

    time_end = time.perf_counter()
    time_taken_seconds = time_end - time_start

    return _process_response(
        r,
        step_config=step_config_with_params,
        time_taken_seconds=time_taken_seconds,
        profile=_profile,
    )


def run(
    step_config: AnyJobStepConfig | None = None,
    params: dict[str, str] | None = None,
    *,
    print_time: bool = False,
    read_options: dict | None = None,
    client_id: str | None = None,
    cache_max_age: int | None = None,
    dtype_out_vector: str | None = None,
    dtype_out_raster: str | None = None,
    _profile: bool = False,
    run_id: str | None = None,
    use_sse: bool = False,
) -> pd.DataFrame:
    """Run a UDF.

    Args:
        step_config: AnyJobStepConfig.
        params: Additional parameters to pass to the UDF. Must be JSON serializable.

    Keyword Args:
        print_time: If True, print the amount of time taken in the request.
        read_options: If not None, options for reading `df` that will be passed to GeoPandas.
    """
    # TODO: This function is too complicated

    time_start = time.perf_counter()
    # We need to get the auth headers from the FusedAPI. Don't enable set_global_api
    # to avoid messing up the user's environment.
    api = FusedAPI(set_global_api=False)

    udf_server_url = resolve_udf_server_url(client_id)

    assert step_config is not None
    # Apply parameters, if we want to step_config that's returned to have this,
    # overwrite step_config.
    step_config_with_params = step_config.set_udf(
        udf=step_config.udf, parameters=serialize_realtime_params(params)
    )

    # Note: Custom UDF uses the json POST attribute.
    url = f"{udf_server_url}/api/v1/run/udf"
    if use_sse:
        url += "/sse"

    # This is the body for when step_config_with_params.type == "udf".
    body = {
        "data_left": None,
        "step_config": step_config_with_params.model_dump_json(),
        "dtype_in": "json",
        # TODO remove dtype_out
        "dtype_out_vector": dtype_out_vector or OPTIONS.default_dtype_out_vector,
        "dtype_out_raster": dtype_out_raster or OPTIONS.default_dtype_out_raster,
        "profile": _profile,
    }

    method = "POST"
    post_attr_json = body

    recursion_factor = get_recursion_factor()
    post_attr_headers = api._generate_headers(
        {
            "Content-Type": "application/json",
            **(OPTIONS.default_run_headers or {}),
        }
    )
    post_attr_headers["Fused-Recursion"] = f"{recursion_factor}"
    if run_id is not None:
        post_attr_headers["Fused-Run-Id"] = run_id

    req_params = {
        **({"cache_max_age": int(cache_max_age)} if cache_max_age is not None else {}),
    }

    if use_sse:
        # Make request
        start = time.time()

        import httpx

        with httpx.stream(
            method,
            url,
            params=req_params,
            json=post_attr_json,
            headers=post_attr_headers,
            timeout=OPTIONS.run_timeout,
        ) as r:
            end = time.time()
            logger.info(f"{run_id=} | Time in initial request: {end - start}")

            # Process SSE response
            assert r.headers.get("content-type", "").startswith("text/event-stream")
            accumulated_data = []
            headers_data = None
            next_event_data = None
            status_code = r.status_code
            for line_str in r.iter_lines():
                logger.debug(f"{run_id=} | SSE line: {line_str}")  # Debugging output
                if line_str:
                    # line_str = line.decode("utf-8")
                    if line_str.startswith("event: end"):
                        break  # End of stream
                    elif line_str.startswith("event"):
                        next_event_data = line_str[
                            6:
                        ].strip()  # Remove 'event: ' prefix
                    elif line_str.startswith("data:"):
                        data = line_str[5:].strip()  # Remove 'data: ' prefix
                        if next_event_data == "headers":
                            headers_data = json.loads(data)
                        elif next_event_data == "status":
                            status_code = int(data)
                        elif next_event_data == "data":
                            if data:
                                accumulated_data.append(data.encode("utf-8"))
                        next_event_data = None

        end2 = time.time()
        logger.info(f"{run_id=} | Time in full request: {end2 - start}")

        # Create a mock response object with the accumulated data
        class MockResponse:
            def __init__(self, content, headers, status_code=200):
                self.content = content
                self.status_code = status_code
                self.headers = headers

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP {self.status_code}")

        combined_data = b"".join(accumulated_data)
        mock_response = MockResponse(
            combined_data, headers=headers_data, status_code=status_code
        )

        time_end = time.perf_counter()
        time_taken_seconds = time_end - time_start

        return _process_response(
            mock_response,
            step_config=step_config_with_params,
            time_taken_seconds=time_taken_seconds,
            profile=_profile,
        )

    # Make request
    start = time.time()

    with session_with_retries() as session:
        logger.debug(f"{run_id=} | Starting request")
        r = session.request(
            method=method,
            url=url,
            params=req_params,
            json=post_attr_json,
            headers=post_attr_headers,
            timeout=OPTIONS.run_timeout,
        )

    end = time.time()
    logger.info(f"{run_id=} | Time in request: {end - start}")

    time_end = time.perf_counter()
    time_taken_seconds = time_end - time_start

    return _process_response(
        r,
        step_config=step_config_with_params,
        time_taken_seconds=time_taken_seconds,
        profile=_profile,
    )


def run_polling(
    step_config: AnyJobStepConfig | None = None,
    params: dict[str, str] | None = None,
    *,
    print_time: bool = False,
    read_options: dict | None = None,
    client_id: str | None = None,
    cache_max_age: int | None = None,
    dtype_out_vector: str | None = None,
    dtype_out_raster: str | None = None,
    _profile: bool = False,
    run_id: str | None = None,
) -> UdfEvaluationResult:
    time_start = time.perf_counter()
    # We need to get the auth headers from the FusedAPI. Don't enable set_global_api
    # to avoid messing up the user's environment.
    api = FusedAPI(set_global_api=False)

    udf_server_url = resolve_udf_server_url(client_id)

    assert step_config is not None
    # Apply parameters, if we want to step_config that's returned to have this,
    # overwrite step_config.
    step_config_with_params = step_config.set_udf(
        udf=step_config.udf, parameters=serialize_realtime_params(params)
    )

    # Note: Custom UDF uses the json POST attribute.
    url = f"{udf_server_url}/api/v1/run/udf/start"

    # This is the body for when step_config_with_params.type == "udf".
    body = {
        "data_left": None,
        "step_config": step_config_with_params.model_dump_json(),
        "dtype_in": "json",
        # TODO remove dtype_out
        "dtype_out_vector": dtype_out_vector or OPTIONS.default_dtype_out_vector,
        "dtype_out_raster": dtype_out_raster or OPTIONS.default_dtype_out_raster,
        "profile": _profile,
    }

    method = "POST"
    post_attr_json = body

    recursion_factor = get_recursion_factor()
    post_attr_headers = api._generate_headers(
        {
            "Content-Type": "application/json",
            **(OPTIONS.default_run_headers or {}),
        }
    )
    post_attr_headers["Fused-Recursion"] = f"{recursion_factor}"
    if run_id is not None:
        post_attr_headers["Fused-Run-Id"] = run_id

    req_params = {
        **({"cache_max_age": int(cache_max_age)} if cache_max_age is not None else {}),
    }

    # Make request
    start = time.time()

    # use request_timeout instead of run_timeout since the request does not
    # connect for the entirety of the UDF run
    # set a higher timeout for PR dev envs
    timeout = (
        OPTIONS.request_timeout
        if "dev" not in OPTIONS.base_url
        else OPTIONS.request_timeout_dev
    )

    with session_with_retries() as session:
        logger.debug(f"{run_id=} | Starting request")
        r = session.request(
            method=method,
            url=url,
            params=req_params,
            json=post_attr_json,
            headers=post_attr_headers,
            timeout=timeout,
        )

        if r.status_code == 202:
            logger.debug(f"{run_id=} | Start polling")

            n_retries = 0
            while (time.time() - start) < OPTIONS.run_timeout:
                r = session.get(
                    f"{udf_server_url}/api/v1/run/udf/get/{run_id}",
                    headers=post_attr_headers,
                    timeout=timeout,
                )
                if r.status_code != 202:
                    break
                if n_retries > 1:
                    time.sleep(1)
                n_retries += 1

    if r.status_code == 202:
        # TODO: Add a better error message
        raise Exception(f"UDF run {run_id} timed out")

    end = time.time()
    logger.info(f"{run_id=} | Time in request: {end - start}")

    time_end = time.perf_counter()
    time_taken_seconds = time_end - time_start

    return _process_response(
        r,
        step_config=step_config_with_params,
        time_taken_seconds=time_taken_seconds,
        profile=_profile,
    )


async def run_tile_async(
    x: float,
    y: float,
    z: float,
    step_config: AnyJobStepConfig | None = None,
    params: dict[str, str] | None = None,
    *,
    print_time: bool = False,
    client_id: str | None = None,
    cache_max_age: int | None = None,
    dtype_out_vector: str | None = None,
    dtype_out_raster: str | None = None,
    run_id: str | None = None,
) -> UdfEvaluationResult:  # TODO: return png
    time_start = time.perf_counter()
    # We need to get the auth headers from the FusedAPI. Don't enable set_global_api
    # to avoid messing up the user's environment.
    api = FusedAPI(set_global_api=False)

    udf_server_url = resolve_udf_server_url(client_id)

    assert step_config is not None
    # Apply parameters, if we want to step_config that's returned to have this,
    # overwrite step_config.
    step_config_with_params = step_config.set_udf(
        udf=step_config.udf, parameters=serialize_realtime_params(params)
    )

    url = f"{udf_server_url}/api/v1/run/udf/tiles/{z}/{x}/{y}"

    # Headers
    recursion_factor = get_recursion_factor()
    headers = api._generate_headers(
        {
            "Content-Type": "application/json",
            **(OPTIONS.default_run_headers or {}),
        }
    )
    headers["Fused-Recursion"] = f"{recursion_factor}"

    # Payload
    post_attr_json = {
        "data_left": None,
        "data_right": None,
        "step_config": step_config_with_params.model_dump_json(),
        "dtype_in": "json",
        # TODO remove dtype_out
        "dtype_out_vector": dtype_out_vector or OPTIONS.default_dtype_out_vector,
        "dtype_out_raster": dtype_out_raster or OPTIONS.default_dtype_out_raster,
    }

    # Params
    req_params = {
        **({"cache_max_age": int(cache_max_age)} if cache_max_age is not None else {}),
    }

    # Make request
    start = time.time()

    if OPTIONS.pyodide_async_requests:
        import pyodide.http
        import yarl

        url_with_params = yarl.URL(url, encoded=True).with_query(req_params)
        r = await pyodide.http.pyfetch(
            str(url_with_params),
            method="POST",
            headers=headers,
            body=json.dumps(post_attr_json),
            # TODO: timeout
        )
        end = time.time()
        if print_time:
            logger.info(f"Time in request: {end - start}")
        time_end = time.perf_counter()
        time_taken_seconds = time_end - time_start

        return await _process_response_async(
            r,
            step_config=step_config_with_params,
            time_taken_seconds=time_taken_seconds,
        )
    else:
        from fused.core._realtime_ops import _get_shared_session

        # Use shared session for connection pooling and reuse
        session = await _get_shared_session()
        async with session.post(
            url=url,
            params=req_params,
            json=post_attr_json,
            headers=headers,
            retry=default_retry_strategy,
            # TODO: timeout
        ) as r:
            end = time.time()
            if print_time:
                logger.info(f"Time in request: {end - start}")

            time_end = time.perf_counter()
            time_taken_seconds = time_end - time_start

            return await _process_response_async(
                r,
                step_config=step_config_with_params,
                time_taken_seconds=time_taken_seconds,
            )


async def run_async(
    step_config: AnyJobStepConfig | None = None,
    params: dict[str, str] | None = None,
    *,
    print_time: bool = False,
    client_id: str | None = None,
    cache_max_age: int | None = None,
    dtype_out_vector: str | None = None,
    dtype_out_raster: str | None = None,
    run_id: str | None = None,
) -> UdfEvaluationResult:
    """Run a UDF over a DataFrame.

    Args:
        step_config: AnyJobStepConfig.
        params: Additional parameters to pass to the UDF. Must be JSON serializable.

    Keyword Args:
        print_time: If True, print the amount of time taken in the request.
    """
    # TODO: This function is too complicated

    time_start = time.perf_counter()
    # We need to get the auth headers from the FusedAPI. Don't enable set_global_api
    # to avoid messing up the user's environment.
    api = FusedAPI(set_global_api=False)

    udf_server_url = resolve_udf_server_url(client_id)

    assert step_config is not None
    # Apply parameters, if we want to step_config that's returned to have this,
    # overwrite step_config.
    step_config_with_params = step_config.set_udf(
        udf=step_config.udf, parameters=serialize_realtime_params(params)
    )

    # Note: Custom UDF uses the json POST attribute.
    url = f"{udf_server_url}/api/v1/run/udf"

    # This is the body for when step_config_with_params.type == "udf".
    body = {
        "data_left": None,
        "step_config": step_config_with_params.model_dump_json(),
        "dtype_in": "json",
        # TODO remove dtype_out
        "dtype_out_vector": dtype_out_vector or OPTIONS.default_dtype_out_vector,
        "dtype_out_raster": dtype_out_raster or OPTIONS.default_dtype_out_raster,
    }

    post_attr_json = body

    recursion_factor = get_recursion_factor()
    post_attr_headers = api._generate_headers(
        {
            "Content-Type": "application/json",
            **(OPTIONS.default_run_headers or {}),
        }
    )
    post_attr_headers["Fused-Recursion"] = f"{recursion_factor}"

    req_params = {
        **({"cache_max_age": int(cache_max_age)} if cache_max_age is not None else {}),
    }
    # Make request
    start = time.time()

    if OPTIONS.pyodide_async_requests:
        import pyodide.http
        import yarl

        url_with_params = yarl.URL(url, encoded=True).with_query(req_params)
        r = await pyodide.http.pyfetch(
            str(url_with_params),
            method="POST",
            headers=post_attr_headers,
            body=json.dumps(post_attr_json),
            # TODO: timeout
        )
        end = time.time()
        if print_time:
            logger.info(f"Time in request: {end - start}")

        await _realtime_raise_for_status_async(r)
        time_end = time.perf_counter()
        time_taken_seconds = time_end - time_start

        response = await _process_response_async(
            r,
            step_config=step_config_with_params,
            time_taken_seconds=time_taken_seconds,
        )
    else:
        from fused.core._realtime_ops import _get_shared_session

        # Use shared session for connection pooling and reuse
        # TODO: Retry mechanism
        session = await _get_shared_session()
        async with session.post(
            url=url,
            params=req_params,
            json=post_attr_json,
            headers=post_attr_headers,
            # TODO: timeout
        ) as r:
            end = time.time()
            if print_time:
                logger.info(f"Time in request: {end - start}")

            await _realtime_raise_for_status_async(r)
            time_end = time.perf_counter()
            time_taken_seconds = time_end - time_start

            response = await _process_response_async(
                r,
                step_config=step_config_with_params,
                time_taken_seconds=time_taken_seconds,
            )
    return response
