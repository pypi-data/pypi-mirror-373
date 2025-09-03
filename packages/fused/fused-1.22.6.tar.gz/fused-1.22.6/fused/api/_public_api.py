from __future__ import annotations

import io
import os
import warnings
from datetime import timedelta
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Literal,
    overload,
)

from fused._global_api import get_api
from fused._optional_deps import HAS_PANDAS, PD_DATAFRAME
from fused._options import options as OPTIONS
from fused._secrets import secrets
from fused.models.api import ListDetails
from fused.models.api._cronjob import CronJob
from fused.models.internal import Jobs
from fused.models.internal.job import CoerceableToJobId, RunResponse
from fused.models.udf import BaseUdf
from fused.models.udf._eval_result import UdfEvaluationResult
from fused.warnings import FusedTypeWarning

if TYPE_CHECKING:
    import geopandas as gpd
    import pandas as pd


def job_get_logs(
    job: CoerceableToJobId,
    since_ms: int | None = None,
) -> list[Any]:
    """Fetch logs for a job

    Args:
        job: the identifier of a job or a `RunResponse` object.
        since_ms: Timestamp, in milliseconds since epoch, to get logs for. Defaults to None for all logs.

    Returns:
        Log messages for the given job.
    """
    api = get_api()
    return api.get_logs(job=job, since_ms=since_ms)


def job_print_logs(
    job: CoerceableToJobId,
    since_ms: int | None = None,
    file: IO | None = None,
) -> None:
    """Fetch and print logs for a job

    Args:
        job: the identifier of a job or a `RunResponse` object.
        since_ms: Timestamp, in milliseconds since epoch, to get logs for. Defaults to None for all logs.
        file: Where to print logs to. Defaults to sys.stdout.

    Returns:
        None
    """
    job = RunResponse.from_job_id(job)
    job.print_logs(since_ms=since_ms, file=file)


def job_tail_logs(
    job: CoerceableToJobId,
    refresh_seconds: float = 1,
    sample_logs: bool = True,
    timeout: float | None = None,
):
    """Continuously print logs for a job

    Args:
        job: the identifier of a job or a `RunResponse` object.
        refresh_seconds: how frequently, in seconds, to check for new logs. Defaults to 1.
        sample_logs: if true, print out only a sample of logs. Defaults to True.
        timeout: if not None, how long to continue tailing logs for. Defaults to None for indefinite.
    """
    api = get_api()
    return api.tail_logs(
        job=job,
        refresh_seconds=refresh_seconds,
        sample_logs=sample_logs,
        timeout=timeout,
    )


def job_get_status(job: CoerceableToJobId) -> RunResponse:
    """Fetch the status of a running job

    Args:
        job: the identifier of a job or a `RunResponse` object.

    Returns:
        The status of the given job.
    """
    api = get_api()
    return api.get_status(job=job)


def job_cancel(job: CoerceableToJobId) -> RunResponse:
    """Cancel an existing job

    Args:
        job: the identifier of a job or a `RunResponse` object.

    Returns:
        A new job object.
    """
    api = get_api()
    return api.cancel_job(job=job)


def job_get_exec_time(job: CoerceableToJobId) -> timedelta:
    """Determine the execution time of this job, using the logs.

    Returns:
        Time the job took. If the job is in progress, time from first to last log message is returned.
    """
    job = RunResponse.from_job_id(job)
    return job.get_exec_time()


def job_wait_for_job(
    job: CoerceableToJobId,
    poll_interval_seconds: float = 5,
    timeout: float | None = None,
) -> RunResponse:
    """Block the Python kernel until this job has finished

    Args:
        poll_interval_seconds: How often (in seconds) to poll for status updates. Defaults to 5.
        timeout: The length of time in seconds to wait for the job. Defaults to None.

    Raises:
        TimeoutError: if waiting for the job timed out.

    Returns:
        The status of the given job.
    """
    api = get_api()
    return api.wait_for_job(
        job,
        poll_interval_seconds=poll_interval_seconds,
        timeout=timeout,
    )


def job_wait_for_results(
    job: CoerceableToJobId,
    poll_interval_seconds: float = 5,
    timeout: float | None = None,
) -> list[UdfEvaluationResult]:
    job_response = job_get_status(job=job)
    return job_response.wait_for_job(
        poll_interval_seconds=poll_interval_seconds, timeout=timeout
    ).get_results()


def job_get_results(job: CoerceableToJobId) -> list[Any]:
    return job_get_status(job=job).get_results()


def whoami():
    """
    Returns information on the currently logged in user
    """
    api = get_api()
    return api._whoami()


def delete(
    path: str,
    max_deletion_depth: int | Literal["unlimited"] = 3,
) -> bool:
    """Delete the files at the path.

    Args:
        path: Directory or file to delete, like `fd://my-old-table/`
        max_deletion_depth: If set (defaults to 3), the maximum depth the operation will recurse to.
                            This option is to help avoid accidentally deleting more data that intended.
                            Pass `"unlimited"` for unlimited.


    Examples:
        ```python
        fused.api.delete("fd://bucket-name/deprecated_table/")
        ```
    """
    api = get_api()
    return api.delete(path, max_deletion_depth=max_deletion_depth)


@overload
def list(path: str, *, details: Literal[False] = False) -> list[str]: ...


@overload
def list(path: str, *, details: Literal[True]) -> list[ListDetails]: ...


def list(path: str, *, details: bool = False) -> list[str] | list[ListDetails]:
    """List the files at the path.

    Args:
        path: Parent directory URL, like `fd://bucket-name/`
        details: If True, return additional metadata about each record.

    Returns:
        A list of paths as URLs, or as metadata objects.

    Examples:
        ```python
        fused.api.list("fd://bucket-name/")
        ```
    """
    api = get_api(credentials_needed=False)
    return api.list(path, details=details)


def get(path: str) -> bytes:
    """Download the contents at the path to memory.

    Args:
        path: URL to a file, like `fd://bucket-name/file.parquet`

    Returns:
        bytes of the file

    Examples:
        ```python
        fused.api.get("fd://bucket-name/file.parquet")
        ```
    """
    api = get_api(credentials_needed=False)
    return api.get(path)


def download(path: str, local_path: str | Path) -> None:
    """Download the contents at the path to disk.

    Args:
        path: URL to a file, like `fd://bucket-name/file.parquet`
        local_path: Path to a local file.
    """
    api = get_api(credentials_needed=False)
    api.download(path, local_path=local_path)


def upload(
    local_path: str | Path | bytes | BinaryIO | pd.DataFrame | gpd.GeoDataFrame,
    remote_path: str,
    timeout: float | None = None,
) -> None:
    """Upload local file to S3.

    Args:
        local_path: Either a path to a local file (`str`, `Path`), a (Geo)DataFrame
                    (which will get uploaded as Parquet file), or the contents to upload.
                    Any string will be treated as a Path, if you wish to upload the contents of
                    the string, first encode it: `s.encode("utf-8")`
        remote_path: URL to upload to, like `fd://new-file.txt`
        timeout: Optional timeout in seconds for the upload (will default to `OPTIONS.request_timeout` if not specified).

    Examples:
        To upload a local json file to your Fused-managed S3 bucket:
        ```py
        fused.api.upload("my_file.json", "fd://my_bucket/my_file.json")
        ```
    """
    api = get_api()
    if isinstance(local_path, str):
        # We assume any string being passed in is a path, rather than the contents
        # to upload.
        local_path = Path(local_path)
        if not local_path.exists():
            warnings.warn(
                FusedTypeWarning(
                    '`local_path` is being treated as a path but it does not exist. If you wish to upload the contents of the string, encode it to bytes first with `.encode("utf-8")'
                )
            )
    if isinstance(local_path, Path):
        file_name = local_path.name
        if remote_path.endswith("/"):  # Remote path has a directory-like structure
            remote_path += file_name

        data = local_path.read_bytes()
    elif HAS_PANDAS and isinstance(local_path, PD_DATAFRAME):
        data = io.BytesIO()
        local_path.to_parquet(data)
        data.seek(0)
    else:
        data = local_path

    api.upload(path=remote_path, data=data, timeout=timeout)


def sign_url(path: str) -> str:
    """Create a signed URL to access the path.

    This function may not check that the file represented by the path exists.

    Args:
        path: URL to a file, like `fd://bucket-name/file.parquet`

    Returns:
        HTTPS URL to access the file using signed access.

    Examples:
        ```python
        fused.api.sign_url("fd://bucket-name/table_directory/file.parquet")
        ```
    """
    api = get_api()
    return api.sign_url(path)


def sign_url_prefix(path: str) -> dict[str, str]:
    """Create signed URLs to access all blobs under the path.

    Args:
        path: URL to a prefix, like `fd://bucket-name/some_directory/`

    Returns:
        Dictionary mapping from blob store key to signed HTTPS URL.

    Examples:
        ```python
        fused.api.sign_url_prefix("fd://bucket-name/table_directory/")
        ```
    """
    api = get_api()
    return api.sign_url_prefix(path)


def get_jobs(
    n: int = 5,
    *,
    skip: int = 0,
    per_request: int = 25,
    max_requests: int | None = None,
) -> Jobs:
    """Get the job history.

    Args:
        n: The number of jobs to fetch. Defaults to 5.

    Keyword Args:
        skip: Where in the job history to begin. Defaults to 0, which retrieves the most recent job.
        per_request: Number of jobs per request to fetch. Defaults to 25.
        max_requests: Maximum number of requests to make. May be None to fetch all jobs. Defaults to 1.

    Returns:
        The job history.
    """
    api = get_api()
    return api.get_jobs(
        n=n, skip=skip, per_request=per_request, max_requests=max_requests
    )


def get_udfs(
    n: int | None = None,
    *,
    skip: int = 0,
    by: Literal["name", "id", "slug"] = "name",
    whose: Literal["self", "public", "community", "team"] = "self",
) -> dict:
    """
    Fetches a list of UDFs.

    Args:
        n: The total number of UDFs to fetch. Defaults to All.
        skip: The number of UDFs to skip before starting to collect the result set. Defaults to 0.
        by: The attribute by which to sort the UDFs. Can be "name", "id", or "slug". Defaults to "name".
        whose: Specifies whose UDFs to fetch. Can be "self" for the user's own UDFs or "public" for
            UDFs available publicly or "community" for all community UDFs. Defaults to "self".

    Returns:
        A list of UDFs.

    Examples:
        Fetch UDFs under the user account:
        ```py
        fused.api.get_udfs()
        ```
    """
    api = get_api()
    return api.get_udfs(by=by, whose=whose, n=n, skip=skip)


def get_apps(
    n: int | None = None,
    *,
    skip: int = 0,
    by: Literal["name", "id", "slug"] = "name",
    whose: Literal["self", "public"] = "self",
) -> dict:
    """
    Fetches a list of apps.

    Args:
        n: The total number of UDFs to fetch. Defaults to All.
        skip: The number of UDFs to skip before starting to collect the result set. Defaults to 0.
        by: The attribute by which to sort the apps. Can be "name", "id", or "slug". Defaults to "name".
        whose: Specifies whose apps to fetch. Can be "self" for the user's own apps or "public" for
            UDFs available publicly. Defaults to "self".

    Returns:
        A list of apps.

    Examples:
        Fetch apps under the user account:
        ```py
        fused.api.get_apps()
        ```
    """
    api = get_api()
    return api.get_apps(by=by, whose=whose, n=n, skip=skip)


def enable_gcs():
    """
    Save gcs credentials from AWS secret manager into a temporary local file and set its path to the env variable.
    """
    gcs_secret = secrets[OPTIONS.gcs_secret]
    if gcs_secret:
        with open(OPTIONS.gcs_filename, "w") as f:
            f.write(gcs_secret)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = OPTIONS.gcs_filename


def schedule_udf(
    udf: BaseUdf | str,
    minute: list[int] | int,
    hour: list[int] | int,
    day_of_month: list[int] | int | None = None,
    month: list[int] | int | None = None,
    day_of_week: list[int] | int | None = None,
    udf_args: dict[str, Any] | None = None,
    enabled: bool = True,
    _create_udf: bool = True,
    **kwargs,
) -> CronJob:
    """Schedule a UDF to run on a cron schedule.

    Args:
        udf: The UDF to schedule.
        minute: The minute to run the UDF on.
        hour: The hour to run the UDF on.
        day_of_month: The day of the month to run the UDF on. (Default every day)
        month: The month to run the UDF on. (Default every month)
        day_of_week: The day of the week to run the UDF on. (Default every day)
        udf_args: The arguments to pass to the UDF. (Default None)
        enabled: Whether the cron job is enabled. (Default True)
        _create_udf: Save the UDF to Fused before creating the CronJob. (Default True)
    """
    return CronJob.from_udf(
        udf,
        minute,
        hour,
        day_of_month,
        month,
        day_of_week,
        udf_args,
        enabled,
        _create_udf=_create_udf,
        **kwargs,
    )


def schedule_list():
    """List all cron jobs"""
    return CronJob.list_team()


def resolve(path: str) -> str:
    """
    Resolve a path from fd:// to the full S3 URI.

    Args:
        path: The path to resolve.

    Returns:
        S3 resolved path
    """
    api = get_api()
    return api._resolve(path=path)


def team_info() -> dict:
    """
    Fetch the team execution environment details.

    Returns:
        A dictionary with information about the execution environment.
    """
    api = get_api()
    return api._team_info()
