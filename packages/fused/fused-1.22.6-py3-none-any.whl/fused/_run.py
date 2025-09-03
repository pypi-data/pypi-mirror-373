import asyncio
import sys
import time
import uuid
import warnings
from concurrent.futures import CancelledError
from dataclasses import dataclass
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Dict,
    Literal,
    Optional,
    Union,
    overload,
)

from fused._options import options as OPTIONS

from . import load_async

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd
    import xarray as xr

from loguru import logger

from fused._load_udf import load
from fused._udf.decorators import _parse_ttl
from fused.models.api import UdfAccessToken, UdfJobStepConfig
from fused.models.api.udf_access_token import is_udf_token
from fused.models.request import (
    WHITELISTED_INSTANCE_TYPES,
    WHITELISTED_INSTANCE_TYPES_values,
)
from fused.models.udf import Udf
from fused.models.udf._eval_result import UdfEvaluationResult
from fused.types import UdfRuntimeError, UdfSerializationError, UdfTimeoutError
from fused.warnings import FusedDeprecationWarning, FusedIgnoredWarning, FusedWarning

from .core import (
    run_shared_file,
    run_shared_file_async,
    run_shared_tile,
    run_shared_tile_async,
)
from .core._impl._realtime_ops_impl import default_run_engine

ResultType = Union["xr.Dataset", "pd.DataFrame", "gpd.GeoDataFrame"]

InstanceType = Literal[
    "realtime", "small", "medium", "large", WHITELISTED_INSTANCE_TYPES
]


RUN_KWARGS = {
    "x",
    "y",
    "z",
    "sync",
    "engine",
    "type",
    "max_retry",
    "cache_max_age",
    "cache",
    "verbose",
    "parameters",
    "_return_response",
    "_profile",
    "_use_sse",
    "_use_polling",
}


@dataclass
class ResolvedTokenBasedUdf:
    """Represents a UDF resolved as a token for remote execution."""

    token: str
    storage_type: Literal["token"] = "token"
    udf: str = ""  # token string

    def __post_init__(self):
        if not self.udf:
            self.udf = self.token


@dataclass
class ResolvedLocalJobStepUdf:
    """Represents a UDF resolved as a local job step."""

    job_step: UdfJobStepConfig
    udf: Udf
    storage_type: Literal["local_job_step"] = "local_job_step"


ResolvedUdf = Union[ResolvedTokenBasedUdf, ResolvedLocalJobStepUdf]


async def resolve_udf_async(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken],
    engine: str,
    is_token: bool,
) -> ResolvedUdf:
    """
    Async version of resolve_udf that handles I/O operations without blocking.

    Resolve UDF input into standardized components, handling all loading scenarios.

    Args:
        udf: The UDF to resolve
        engine: Execution engine (used for local loading decisions)
        is_token: Whether the UDF is a token

    Returns:
        UdfResolution object containing resolved UDF information
    """

    if udf is None:
        raise ValueError("No UDF specified")

    elif is_token:
        # Handle local engine loading for tokens
        token = udf if isinstance(udf, str) else udf.token
        if engine == "local":
            job_step, loaded_udf = await _load_udf_and_setup_job_step_async(token)
            return ResolvedLocalJobStepUdf(job_step=job_step, udf=loaded_udf)
        else:
            return ResolvedTokenBasedUdf(token=token)

    elif isinstance(udf, Udf):
        job_step = UdfJobStepConfig(udf=udf)
        return ResolvedLocalJobStepUdf(job_step=job_step, udf=udf)

    elif isinstance(udf, str):
        job_step, loaded_udf = await _load_udf_and_setup_job_step_async(udf)
        return ResolvedLocalJobStepUdf(job_step=job_step, udf=loaded_udf)

    else:
        raise TypeError(
            "Could not detect UDF from first parameter. It should be a string or Udf object."
        )


def resolve_udf(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken],
    engine: str,
    is_token: bool,
) -> ResolvedUdf:
    """
    Resolve UDF input into standardized components, handling all loading scenarios.

    Args:
        udf: The UDF to resolve
        engine: Execution engine (used for local loading decisions)
        is_token: Whether the UDF is a token

    Returns:
        UdfResolution object containing resolved UDF information
    """
    if udf is None:
        raise ValueError("No UDF specified")

    elif is_token:
        # Handle local engine loading for tokens
        token = udf if isinstance(udf, str) else udf.token
        if engine == "local":
            job_step, loaded_udf = _load_udf_and_setup_job_step(token)
            return ResolvedLocalJobStepUdf(job_step=job_step, udf=loaded_udf)
        else:
            return ResolvedTokenBasedUdf(token=token)

    elif isinstance(udf, Udf):
        job_step = UdfJobStepConfig(udf=udf)
        return ResolvedLocalJobStepUdf(job_step=job_step, udf=udf)

    elif isinstance(udf, str):
        job_step, loaded_udf = _load_udf_and_setup_job_step(udf)
        return ResolvedLocalJobStepUdf(job_step=job_step, udf=loaded_udf)

    else:
        raise TypeError(
            "Could not detect UDF from first parameter. It should be a string or Udf object."
        )


def _load_udf_and_setup_job_step(udf_source: str) -> tuple[UdfJobStepConfig, Udf]:
    """Helper to load UDF and create job step configuration."""
    try:
        loaded_udf = load(udf_source)
    except Exception as exc:
        raise ValueError(
            "Could not load UDF. Make sure the UDF is available locally when "
            'using `engine="local"`.\n'
            f'Error loading the UDF: "{exc}"'
        )

    job_step = UdfJobStepConfig(udf=loaded_udf)
    return job_step, loaded_udf


async def _load_udf_and_setup_job_step_async(
    udf_source: str,
) -> tuple[UdfJobStepConfig, Udf]:
    """Async helper to load UDF and create job step configuration."""

    try:
        loaded_udf = await load_async(udf_source)
    except Exception as exc:
        raise ValueError(
            "Could not load UDF. Make sure the UDF is available locally when "
            'using `engine="local"`.\n'
            f'Error loading the UDF: "{exc}"'
        )

    job_step = UdfJobStepConfig(udf=loaded_udf)
    return job_step, loaded_udf


def _create_local_params(
    local_tile_bbox: Optional["gpd.GeoDataFrame"],
    cache_max_age: Optional[int],
    _return_response: Optional[bool],
    parameters: Dict[str, Any],
    include_bbox: bool = True,
) -> Dict[str, Any]:
    """Helper to create common local execution parameters."""
    params = {
        "cache_max_age": cache_max_age,
        "_return_response": _return_response,
        **parameters,
    }
    if include_bbox:
        # For tile operations, include the bbox as first positional arg
        return {"bbox": local_tile_bbox, **params}
    return params


def _resolve_engine(
    engine: Optional[Literal["remote", "local"]],
    is_token: bool,
    instance_type: Optional[str],
) -> Literal["remote", "local"]:
    """Determine the execution engine based on parameters and storage type."""
    if engine == "realtime":
        engine = "remote"
    elif engine is None:
        if is_token:
            engine = "remote"
        else:
            engine = default_run_engine()
    elif engine not in ("local", "remote"):
        raise ValueError("Invalid engine specified. Must be 'local' or 'remote'.")

    if instance_type is not None:
        if engine == "local":
            raise ValueError(
                "Specifying an instance type is only supported for the 'remote' engine."
            )
        if (
            instance_type not in ("realtime", "small", "medium", "large")
            and instance_type not in WHITELISTED_INSTANCE_TYPES_values
        ):
            raise ValueError(
                "Invalid instance type specified. Must be 'realtime', 'small', "
                "'medium', 'large', or one of the whitelisted instance types "
                f"({WHITELISTED_INSTANCE_TYPES_values})."
            )

    return engine


def _resolve_instance_type(
    instance_type: Optional[str], resolved_udf: ResolvedUdf
) -> str:
    # if not specified in run(), use the default defined on the UDF
    if instance_type is None and resolved_udf.storage_type == "local_job_step":
        instance_type = resolved_udf.udf.instance_type

    if instance_type is None:
        # TODO potentially allow to override the default instance type with an option?
        instance_type = "realtime"

    if resolved_udf.storage_type == "token" and instance_type != "realtime":
        # TODO we could in theory allow to run shared tokens that can be loaded
        # locally, or support this on the server side
        raise ValueError(
            "UDF shared tokens can only be run with the 'realtime' instance type"
        )

    return instance_type


def _process_tile_coordinates(
    x: Optional[int],
    y: Optional[int],
    z: Optional[int],
    type: Optional[Literal["tile", "file"]],
    kw_parameters: Dict[str, Any],
) -> tuple[Optional["gpd.GeoDataFrame"], bool, Optional[Literal["tile", "file"]]]:
    """Process tile coordinates and determine execution type."""
    from fused._optional_deps import HAS_GEOPANDAS, HAS_MERCANTILE, HAS_SHAPELY

    local_tile_bbox: Optional["gpd.GeoDataFrame"] = None
    xyz_ignored = False

    if x is not None and y is not None and z is not None:
        if HAS_MERCANTILE and HAS_GEOPANDAS and HAS_SHAPELY:
            import geopandas as gpd
            import mercantile
            import shapely

            tile_bounds = mercantile.bounds(x, y, z)
            local_tile_bbox = gpd.GeoDataFrame(
                {"x": [x], "y": [y], "z": [z]},
                geometry=[shapely.box(*tile_bounds)],
                crs=4326,
            )
        else:
            xyz_ignored = True

    if x is not None and y is not None and z is not None:
        if type != "tile":
            if type is None:
                # by default we still interpret x/y/z (if all passed) as a tile run
                type = "tile"
            else:
                kw_parameters["x"] = x
                kw_parameters["y"] = y
                kw_parameters["z"] = z
    else:
        if type is None:
            type = "file"
        elif type != "file":
            raise ValueError(
                "x, y, z not specified but type is 'tile', which is an invalid configuration. You must specify x, y, and z."
            )
        if x is not None:
            kw_parameters["x"] = x
        if y is not None:
            kw_parameters["y"] = y
        if z is not None:
            kw_parameters["z"] = z

    return local_tile_bbox, xyz_ignored, type


def _process_parameters(
    parameters: Optional[Dict[str, Any]],
    kw_parameters: Dict[str, Any],
    udf: Union[str, Udf],
    type: Optional[Literal["tile", "file"]],
    _ignore_unknown_arguments: bool,
) -> tuple[Dict[str, Any], bool]:
    """Process and validate parameters."""
    verbose = kw_parameters.get("verbose", None)
    if verbose is None:
        verbose = OPTIONS.verbose_udf_runs

    merged_parameters = {
        **kw_parameters,
        **(parameters if parameters is not None else {}),
    }

    # Raise an error if passing a different argument than those expected from
    # the union of the UDF own parameters and the run() function parameters
    if merged_parameters and not _ignore_unknown_arguments:
        if isinstance(udf, Udf) and udf._parameter_list:
            udf_kwargs = set(udf._parameter_list)
            allowed_kwargs = udf_kwargs.union(
                RUN_KWARGS if type == "tile" else RUN_KWARGS - {"x", "y", "z"}
            )
            kw_params = set(merged_parameters.keys())

            if not kw_params.issubset(allowed_kwargs) and not udf._parameter_has_kwargs:
                unexpected_args = kw_params - allowed_kwargs
                raise TypeError(
                    f"{udf.entrypoint}() got unexpected keyword argument '{unexpected_args.pop()}'"
                )

    return merged_parameters, verbose


def _create_execution_function(
    dispatch_params: tuple,
    udf_resolution: ResolvedUdf,
    x: Optional[int],
    y: Optional[int],
    z: Optional[int],
    cache_max_age: Optional[int],
    local_tile_bbox: Optional["gpd.GeoDataFrame"],
    _return_response: Optional[bool],
    parameters: Dict[str, Any],
    run_id: str,
) -> Callable:
    """Create the appropriate execution function based on dispatch parameters."""
    exec_type, storage_type, engine, instance_type = dispatch_params

    # Prepare parameter sets
    tile_params = {
        "x": x,
        "y": y,
        "z": z,
        "cache_max_age": cache_max_age,
        "_run_id": run_id,
        **parameters,
    }
    file_params = {
        "cache_max_age": cache_max_age,
        "_run_id": run_id,
        **parameters,
    }

    # Shared UDF token
    if storage_type == "token":
        assert engine == "remote"
        assert isinstance(udf_resolution, ResolvedTokenBasedUdf)
        if exec_type == "tile":
            return partial(run_shared_tile, udf_resolution.token, **tile_params)
        else:  # file
            return partial(run_shared_file, udf_resolution.token, **file_params)

    # Local job step
    elif storage_type == "local_job_step":
        assert isinstance(udf_resolution, ResolvedLocalJobStepUdf)
        job_step = udf_resolution.job_step
        if engine == "remote" and instance_type == "realtime":
            if exec_type == "tile":
                return lambda: job_step._run_tile(**tile_params)
            else:  # file
                # Async file doesn't use cache_max_age for some reason
                return lambda: job_step._run_file(**file_params)
        elif engine == "remote":  # one of the batch instance types
            return lambda: job_step.set_udf(
                job_step.udf, parameters=parameters
            )._run_batch(instance_type=instance_type)
        else:  # local engine
            if exec_type == "tile":
                local_params = _create_local_params(
                    local_tile_bbox,
                    cache_max_age,
                    _return_response,
                    parameters,
                    include_bbox=True,
                )
                return lambda: job_step._run_local(
                    local_tile_bbox,
                    **{k: v for k, v in local_params.items() if k != "bbox"},
                )
            else:  # file
                local_params = _create_local_params(
                    local_tile_bbox,
                    cache_max_age,
                    _return_response,
                    parameters,
                    include_bbox=False,
                )
                return lambda: job_step._run_local(**local_params)

    else:
        # in theory we should never get here
        raise ValueError(f"Call type is not yet implemented: {dispatch_params}")


def _create_execution_function_async(
    dispatch_params: tuple,
    udf_resolution: ResolvedUdf,
    x: Optional[int],
    y: Optional[int],
    z: Optional[int],
    cache_max_age: Optional[int],
    local_tile_bbox: Optional["gpd.GeoDataFrame"],
    _return_response: Optional[bool],
    parameters: Dict[str, Any],
    run_id: str,
) -> Callable:
    """Create the appropriate async execution function based on dispatch parameters."""
    exec_type, storage_type, engine, instance_type = dispatch_params

    # Prepare parameter sets
    tile_params = {
        "x": x,
        "y": y,
        "z": z,
        "cache_max_age": cache_max_age,
        "_run_id": run_id,
        **parameters,
    }
    file_params = {
        "cache_max_age": cache_max_age,
        "_run_id": run_id,
        **parameters,
    }

    # Shared UDF token
    if storage_type == "token":
        assert engine == "remote"
        assert isinstance(udf_resolution, ResolvedTokenBasedUdf)
        if exec_type == "tile":
            return partial(run_shared_tile_async, udf_resolution.token, **tile_params)
        else:  # file
            return partial(run_shared_file_async, udf_resolution.token, **file_params)

    # Local job step
    elif storage_type == "local_job_step":
        assert isinstance(udf_resolution, ResolvedLocalJobStepUdf)
        job_step = udf_resolution.job_step
        if engine == "remote" and instance_type == "realtime":
            if exec_type == "tile":
                return lambda: job_step._run_tile_async(**tile_params)
            else:  # file
                return lambda: job_step._run_file_async(**file_params)
        elif engine == "remote":  # one of the batch instance types

            async def _async_batch():
                return job_step.set_udf(job_step.udf, parameters=parameters)._run_batch(
                    instance_type=instance_type
                )

            return _async_batch
        else:  # local engine
            # Local execution is inherently sync, so we wrap it in an async function
            if exec_type == "tile":
                local_params = _create_local_params(
                    local_tile_bbox,
                    cache_max_age,
                    _return_response,
                    parameters,
                    include_bbox=True,
                )

                async def _async_tile_local():
                    return job_step._run_local(
                        local_tile_bbox,
                        **{k: v for k, v in local_params.items() if k != "bbox"},
                    )

                return _async_tile_local
            else:  # file
                local_params = _create_local_params(
                    local_tile_bbox,
                    cache_max_age,
                    _return_response,
                    parameters,
                    include_bbox=False,
                )

                async def _async_file_local():
                    return job_step._run_local(**local_params)

                return _async_file_local

    else:
        raise ValueError(f"Call type is not yet implemented: {dispatch_params}")


async def _execute_with_retry_async(
    fn: Callable[[], Awaitable[Any]],
    max_retry: int,
    _cancel_callback: Callable[[], bool] | None,
    _return_response: bool,
    verbose: bool,
) -> Any:
    """Run `fn` with exponential backoff.

    Cancels immediately if `_cancel_callback` returns True. Returns the
    `_process_result` of `fn()`; raises the last error after retries.
    """

    n_retries = 0
    while n_retries <= max_retry:
        cancel_requested = _cancel_callback is not None and _cancel_callback()
        try:
            if cancel_requested:
                raise CancelledError("Cancel requested")

            udf_eval_result = await fn()
            # Nested and remote UDF calls will return UdfEvaluationResult.
            # merge the stdout/stderr from fused.run() into running environment,
            # then return the UdfEvaluationResult object.
            return _process_result(udf_eval_result, _return_response, verbose)
        except Exception as exc:
            if (
                isinstance(
                    exc, (UdfSerializationError, UdfRuntimeError, CancelledError)
                )
                or n_retries >= max_retry
            ):
                raise

            delay = OPTIONS.request_retry_base_delay * (2**n_retries)
            n_retries += 1
            warnings.warn(
                f"UDF execution failed, retrying in {delay} seconds (error: {exc})",
                FusedWarning,
            )

            await asyncio.sleep(delay)


def _execute_with_retry(
    fn: Callable[[], Any],
    max_retry: int,
    _cancel_callback: Callable[[], bool] | None,
    _return_response: bool,
    verbose: bool,
) -> Any:
    """Run `fn` with exponential backoff.

    Cancels immediately if `_cancel_callback` returns True. Returns the
    `_process_result` of `fn()`; raises the last error after retries.
    """
    n_retries = 0
    while n_retries <= max_retry:
        cancel_requested = _cancel_callback is not None and _cancel_callback()
        try:
            if cancel_requested:
                raise CancelledError("Cancel requested")
            udf_eval_result = fn()

            # Nested and remote UDF calls will return UdfEvaluationResult.
            # merge the stdout/stderr from fused.run() into running environment,
            # then return the UdfEvaluationResult object.
            return _process_result(udf_eval_result, _return_response, verbose)

        except Exception as exc:
            if (
                isinstance(
                    exc, (UdfSerializationError, UdfRuntimeError, CancelledError)
                )
                or n_retries >= max_retry
            ):
                raise

            delay = OPTIONS.request_retry_base_delay * (2**n_retries)
            n_retries += 1
            warnings.warn(
                f"UDF execution failed, retrying in {delay} seconds (error: {exc})",
                FusedWarning,
            )

            time.sleep(delay)


def _process_result(udf_eval_result, _return_response: Optional[bool], verbose: bool):
    """Process the UDF execution result and handle output."""
    # Nested and remote UDF calls will return UdfEvaluationResult.
    # merge the stdout/stderr from fused.run() into running environment,
    # then return the UdfEvaluationResult object.

    if _return_response:
        return udf_eval_result
    if isinstance(udf_eval_result, UdfEvaluationResult):
        has_error = udf_eval_result.has_exception
        if udf_eval_result.stdout and (verbose or has_error):
            sys.stdout.write(udf_eval_result.stdout)
        if udf_eval_result.stderr and (verbose or has_error):
            sys.stderr.write(udf_eval_result.stderr)
        if udf_eval_result.is_cached:
            if verbose:
                sys.stdout.write("Cached UDF result returned.\n")
            logger.info(f"Cache source: {udf_eval_result.cache_source.value}")
        if udf_eval_result.error_message is not None:
            if udf_eval_result.error_type == "serialization_error":
                raise UdfSerializationError(udf_eval_result.error_message)
            elif udf_eval_result.error_type == "timeout_error":
                raise UdfTimeoutError(udf_eval_result.error_message)
            raise UdfRuntimeError(
                udf_eval_result.error_message,
                child_exception_class=udf_eval_result.exception_class,
            )
        sys.stderr.flush()
        return udf_eval_result.data

    return udf_eval_result


@overload
def run(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: Literal[True] = True,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[
        Literal["realtime", "batch", WHITELISTED_INSTANCE_TYPES]
    ] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Literal[False] = False,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> ResultType: ...


@overload
def run(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: Literal[True] = True,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[InstanceType] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Literal[True] = True,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> UdfEvaluationResult: ...


@overload
def run(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: Literal[False] = False,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[InstanceType] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Literal[False] = False,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> Coroutine[ResultType, None, None]: ...


def run(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    sync: bool = True,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[InstanceType] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Optional[bool] = False,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> Union[
    ResultType,
    Coroutine[ResultType, None, None],
    UdfEvaluationResult,
    Coroutine[UdfEvaluationResult, None, None],
]:
    """
    Executes a user-defined function (UDF) with various execution and input options.

    This function supports executing UDFs in different environments (local or remote),
    with different types of inputs (tile coordinates, geographical bounding boxes, etc.), and
    allows for both synchronous and asynchronous execution. It dynamically determines the execution
    path based on the provided parameters.

    Args:
        udf (str, Udf or UdfJobStepConfig): the UDF to execute.
            The UDF can be specified in several ways:
            - A string representing a UDF name or UDF shared token.
            - A UDF object.
            - A UdfJobStepConfig object for detailed execution configuration.
        x, y, z: Tile coordinates for tile-based UDF execution.
        sync: If True, execute the UDF synchronously. If False, execute asynchronously.
        engine: The execution engine to use ('remote' or 'local').
        instance_type: The type of instance to use for remote execution ('realtime',
            or 'small', 'medium', 'large' or one of the whitelisted instance types).
            If not specified, gets the default from the UDF (if specified in the
            ``@fused.udf()`` decorator, and the UDF is not run as a shared token),
            or otherwise defaults to 'realtime'.
        type: The type of UDF execution ('tile' or 'file').
        max_retry: The maximum number of retries to attempt if the UDF fails.
            By default does not retry.
        cache_max_age: The maximum age when returning a result from the cache.
            Supported units are seconds (s), minutes (m), hours (h), and days (d) (e.g. “48h”, “10s”, etc.).
            Default is `None` so a UDF run with `fused.run()` will follow `cache_max_age` defined in `@fused.udf()` unless this value is changed.
        cache: Set to False as a shortcut for `cache_max_age='0s'` to disable caching.
        verbose: Set to False to suppress any print statements from the UDF.
        parameters: Additional parameters to pass to the UDF.
        **kw_parameters: Additional parameters to pass to the UDF.

    Raises:
        ValueError: If the UDF is not specified or is specified in more than one way.
        TypeError: If the first parameter is not of an expected type.
        Warning: Various warnings are issued for ignored parameters based on the execution path chosen.

    Returns:
        The result of the UDF execution, which varies based on the UDF and execution path.

    Examples:
        Run a UDF saved in the Fused system:
        ```py
        fused.run("username@fused.io/my_udf_name")
        ```

        Run a UDF saved in GitHub:
        ```py
        loaded_udf = fused.load("https://github.com/fusedio/udfs/tree/main/public/Building_Tile_Example")
        fused.run(loaded_udf, bbox=bbox)
        ```

        Run a UDF saved in a local directory:
        ```py
        loaded_udf = fused.load("/Users/local/dir/Building_Tile_Example")
        fused.run(loaded_udf, bbox=bbox)
        ```

    Note:
        This function dynamically determines the execution path and parameters based on the inputs.
        It is designed to be flexible and support various UDF execution scenarios.
    """
    if sync is False:
        warnings.warn(
            "sync=False' parameter is deprecated, use 'run_async()' instead of 'run()'",
            FusedDeprecationWarning,
        )

        async def _r():
            return await run_async(
                udf,
                x=x,
                y=y,
                z=z,
                sync=sync,
                engine=engine,
                type=type,
                max_retry=max_retry,
                cache_max_age=cache_max_age,
                parameters=parameters,
                _return_response=_return_response,
                _ignore_unknown_arguments=_ignore_unknown_arguments,
                _cancel_callback=_cancel_callback,
                **kw_parameters,
            )

        return _r()

    run_id = str(uuid.uuid4())
    logger.debug(f"Running UDF with {run_id=}")

    # Determine execution engine first (needed for UDF resolution)
    is_token = (isinstance(udf, str) and is_udf_token(udf)) or isinstance(
        udf, UdfAccessToken
    )
    engine = _resolve_engine(engine, is_token, instance_type)

    # Resolve UDF and get all configuration
    resolved_udf = resolve_udf(udf, engine, is_token)
    instance_type = _resolve_instance_type(instance_type, resolved_udf)

    # Process tile coordinates and determine execution type
    local_tile_bbox, xyz_ignored, type = _process_tile_coordinates(
        x, y, z, type, kw_parameters
    )

    # Process and validate parameters
    parameters, verbose = _process_parameters(
        parameters, kw_parameters, resolved_udf.udf, type, _ignore_unknown_arguments
    )

    # Parsed cache TTL
    cache_max_age = _parse_ttl(cache_max_age, cache)

    # Create and execute the function
    dispatch_params = (
        type,
        resolved_udf.storage_type,
        engine,
        instance_type,
    )

    fn = _create_execution_function(
        dispatch_params,
        resolved_udf,
        x,
        y,
        z,
        cache_max_age,
        local_tile_bbox,
        _return_response,
        parameters,
        run_id,
    )

    if xyz_ignored and engine == "local":
        # This warning doesn't matter on realtime because we will just put the x/y/z into the URL
        warnings.warn(
            FusedIgnoredWarning(
                "x, y, z arguments will be ignored because the following packages were not all found: mercantile shapely geopandas"
            ),
        )

    return _execute_with_retry(
        fn, max_retry, _cancel_callback, _return_response, verbose
    )


@overload
async def run_async(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[InstanceType] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Literal[False] = False,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> ResultType: ...


@overload
async def run_async(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[InstanceType] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Literal[True] = True,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> UdfEvaluationResult: ...


async def run_async(
    udf: Union[str, None, UdfJobStepConfig, Udf, UdfAccessToken] = None,
    *,
    x: Optional[int] = None,
    y: Optional[int] = None,
    z: Optional[int] = None,
    engine: Optional[Literal["remote", "local"]] = None,
    instance_type: Optional[InstanceType] = None,
    type: Optional[Literal["tile", "file"]] = None,
    max_retry: int = 0,
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
    _return_response: Optional[bool] = False,
    _ignore_unknown_arguments: bool = False,
    _cancel_callback: Callable[[], bool] | None = None,
    **kw_parameters,
) -> Union[ResultType, UdfEvaluationResult]:
    """
    Async version of run() that executes a user-defined function (UDF) asynchronously.

    This function provides the same functionality as run() but with async execution.
    It supports executing UDFs in different environments (local or remote),
    with different types of inputs (tile coordinates, geographical bounding boxes, etc.).

    Args:
        udf (str, Udf or UdfJobStepConfig): the UDF to execute.
            The UDF can be specified in several ways:
            - A string representing a UDF name or UDF shared token.
            - A UDF object.
            - A UdfJobStepConfig object for detailed execution configuration.
        x, y, z: Tile coordinates for tile-based UDF execution.
        engine: The execution engine to use ('remote' or 'local').
        instance_type: The type of instance to use for remote execution ('realtime',
            or 'small', 'medium', 'large' or one of the whitelisted instance types).
            If not specified, gets the default from the UDF (if specified in the
            ``@fused.udf()`` decorator, and the UDF is not run as a shared token),
            or otherwise defaults to 'realtime'.
        type: The type of UDF execution ('tile' or 'file').
        max_retry: The maximum number of retries to attempt if the UDF fails.
            By default does not retry.
        cache_max_age: The maximum age when returning a result from the cache.
            Supported units are seconds (s), minutes (m), hours (h), and days (d) (e.g. "48h", "10s", etc.).
            Default is `None` so a UDF run with `fused.run_async()` will follow `cache_max_age` defined in `@fused.udf()` unless this value is changed.
        cache: Set to False as a shortcut for `cache_max_age='0s'` to disable caching.
        verbose: Set to False to suppress any print statements from the UDF.
        parameters: Additional parameters to pass to the UDF.
        **kw_parameters: Additional parameters to pass to the UDF.

    Raises:
        ValueError: If the UDF is not specified or is specified in more than one way.
        TypeError: If the first parameter is not of an expected type.
        Warning: Various warnings are issued for ignored parameters based on the execution path chosen.

    Returns:
        The result of the UDF execution, which varies based on the UDF and execution path.

    Examples:
        Run a UDF saved in the Fused system asynchronously:
        ```py
        result = await fused.run_async("username@fused.io/my_udf_name")
        ```

        Run a UDF saved in GitHub asynchronously:
        ```py
        loaded_udf = fused.load("https://github.com/fusedio/udfs/tree/main/public/Building_Tile_Example")
        result = await fused.run_async(loaded_udf, bbox=bbox)
        ```

        Run a UDF saved in a local directory asynchronously:
        ```py
        loaded_udf = fused.load("/Users/local/dir/Building_Tile_Example")
        result = await fused.run_async(loaded_udf, bbox=bbox)
        ```

    Note:
        This function always executes asynchronously. For synchronous execution, use run().
        It uses the same parameter validation and UDF resolution logic as run().
    """
    run_id = str(uuid.uuid4())

    # Determine execution engine first (needed for UDF resolution)
    is_token = (isinstance(udf, str) and is_udf_token(udf)) or isinstance(
        udf, UdfAccessToken
    )
    engine = _resolve_engine(engine, is_token, instance_type)

    # Resolve UDF and get all configuration
    resolved_udf = await resolve_udf_async(udf, engine, is_token)
    instance_type = _resolve_instance_type(instance_type, resolved_udf)

    # Process tile coordinates and determine execution type
    local_tile_bbox, xyz_ignored, type = _process_tile_coordinates(
        x, y, z, type, kw_parameters
    )

    # Process and validate parameters
    parameters, verbose = _process_parameters(
        parameters, kw_parameters, resolved_udf.udf, type, _ignore_unknown_arguments
    )

    # Parsed cache TTL
    cache_max_age = _parse_ttl(cache_max_age, cache)

    dispatch_params = (
        type,
        resolved_udf.storage_type,
        engine,
        instance_type,
    )

    fn = _create_execution_function_async(
        dispatch_params,
        resolved_udf,
        x,
        y,
        z,
        cache_max_age,
        local_tile_bbox,
        _return_response,
        parameters,
        run_id,
    )

    if xyz_ignored and engine == "local":
        # This warning doesn't matter on realtime because we will just put the x/y/z into the URL
        warnings.warn(
            FusedIgnoredWarning(
                "x, y, z arguments will be ignored because the following packages were not all found: mercantile shapely geopandas"
            ),
        )

    return await _execute_with_retry_async(
        fn, max_retry, _cancel_callback, _return_response, verbose
    )
