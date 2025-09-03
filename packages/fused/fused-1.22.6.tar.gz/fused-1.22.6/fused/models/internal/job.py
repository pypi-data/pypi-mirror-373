from __future__ import annotations

import warnings
from datetime import datetime, timedelta
from typing import IO, TYPE_CHECKING, Any, Union

from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr

from fused._formatter.formatter_jobs import fused_jobs_repr, fused_runresponse_repr
from fused._global_api import get_api
from fused._options import options as OPTIONS
from fused.warnings import FusedInProgressWarning

if TYPE_CHECKING:
    from fused.api import FusedAPI
    from fused.models import JobConfig, JobStepConfig


class RunResponse(BaseModel):
    job_id: StrictStr
    """The identifier of this job."""
    job_name: StrictStr

    instance_id: StrictStr | None = None
    instance_type: StrictStr | None = None
    status: StrictStr
    """The status of the instance running this job."""
    terminal_status: StrictBool

    job_status: StrictStr | None = None

    total_tasks: int
    finished_tasks: int

    def _repr_html_(self) -> str:
        return fused_runresponse_repr(self)

    @property
    def _api(self) -> FusedAPI:
        # Note that this does not import the FusedAPI class for circular import reasons
        # We assume that the API has already been instantiated before a model is created
        return get_api()

    @property
    def logs_url(self) -> str:
        """Returns a URL for getting the job's logs in the browser."""
        return f"{OPTIONS.base_web_url}/workbench/jobs/{self.job_id}"

    def get_status(self) -> RunResponse:
        """Fetch the status of this job

        Returns:
            The status of the given job.
        """
        return self._api.get_status(self)

    def get_logs(self, since_ms: int | None = None) -> list[Any]:
        """Fetch logs for this job

        Args:
            since_ms: Timestamp, in milliseconds since epoch, to get logs for. Defaults to None for all logs.

        Returns:
            Log messages for the given job.
        """
        return self._api.get_logs(self, since_ms=since_ms)

    def print_logs(self, since_ms: int | None = None, file: IO | None = None) -> None:
        """Fetch and print logs for this job

        Args:
            since_ms: Timestamp, in milliseconds since epoch, to get logs for. Defaults to None for all logs.
            file: Where to print logs to. Defaults to sys.stdout.

        Returns:
            None
        """
        logs = self.get_logs(since_ms=since_ms)
        for m in logs:
            print(m["message"].strip(), file=file)

    def get_exec_time(self) -> timedelta:
        """Determine the execution time of this job, using the logs.

        Returns:
            Time the job took. If the job is in progress, time from first to last log message is returned.
        """
        refreshed = self.get_status()
        if not refreshed.terminal_status:
            warnings.warn(
                FusedInProgressWarning(
                    f"Job is still in progress. Status: {refreshed.status}"
                )
            )

        logs = refreshed.get_logs()
        if len(logs):
            first_log = logs[0]
            last_log = logs[-1]

            first_ts = first_log["timestamp"]
            last_ts = last_log["timestamp"]

            d_ts = last_ts - first_ts
            return timedelta(milliseconds=d_ts)
        else:
            raise ValueError(
                "Job does not have logs, so execution time can't be determined"
            )

    def tail_logs(
        self,
        refresh_seconds: float = 1,
        sample_logs: bool = True,
        timeout: float | None = None,
    ) -> None:
        """Continuously print logs for this job

        Args:
            refresh_seconds: how frequently, in seconds, to check for new logs. Defaults to 1.
            sample_logs: if true, print out only a sample of logs. Defaults to True.
            timeout: if not None, how long to continue tailing logs for. Defaults to None for indefinite.
        """
        return self._api.tail_logs(
            self,
            refresh_seconds=refresh_seconds,
            sample_logs=sample_logs,
            timeout=timeout,
        )

    def wait_for_job(
        self,
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
        return self._api.wait_for_job(
            self,
            poll_interval_seconds=poll_interval_seconds,
            timeout=timeout,
        )

    def cancel(self) -> RunResponse:
        """Cancel this job

        Returns:
            A new job object.
        """
        return self._api.cancel_job(self)

    def refresh_status(self) -> RunResponse:
        """Refresh the status of this job."""
        if not self.terminal_status:
            new_status = self._api.get_status(self)
            self.job_id = new_status.job_id
            self.instance_id = new_status.instance_id
            self.instance_type = new_status.instance_type
            self.terminal_status = new_status.terminal_status
            self.status = new_status.status
            self.job_status = new_status.job_status

        return self

    def __repr__(self) -> str:
        self.refresh_status()
        return super().__repr__()

    @classmethod
    def from_job_id(cls, job: str | RunResponse) -> RunResponse:
        """Creates a RunResponse object from either a job ID or a RunResponse.

        Args:
            job: Either a job ID string, or a RunResponse.

        Returns:
            A RunResponse object.
        """
        if isinstance(job, str):
            return RunResponse(
                job_id=job,
                job_name="null",
                instance_id=None,
                instance_type=None,
                status="null",
                terminal_status=True,
            )
        return job

    def get_results(self, arg_index: int = -1) -> Any | list[Any]:
        return self._api.get_job_results(self.job_id, arg_index)


class JobResponse(BaseModel):
    id: StrictStr
    """The identifier of this job."""
    user_id: StrictStr
    creation_date: datetime
    """When this job was started."""

    job_status: StrictStr | None = None
    """The status of this job."""
    job_status_date: datetime | None = None
    """When the job_status was last updated"""

    instance_id: StrictStr | None = None
    instance_type: StrictStr | None = None
    execution_environment_id: str

    @property
    def _api(self) -> FusedAPI:
        # Note that this does not import the FusedAPI class for circular import reasons
        # We assume that the API has already been instantiated before a model is created
        return get_api()

    @property
    def logs_url(self) -> str:
        """Returns a URL for getting the job's logs in the browser."""
        return f"{OPTIONS.base_web_url}/workbench/jobs/{self.id}"

    def config(self) -> JobStepConfig:
        """Fetch the job step configuration

        Returns:
            The configuration for the job step in this job.
        """
        return self._api.get_job_config(input)._to_job_step_config()

    def steps_config(self) -> JobConfig:
        """Fetch the job configuration

        Returns:
            The configuration for all job steps in this job.
        """
        return self._api.get_job_config(input)

    def get_status(self) -> RunResponse:
        """Fetch the status of this job

        Returns:
            The status of the given job.
        """
        return self._api.get_status(self)

    def get_logs(self, since_ms: int | None = None) -> list[Any]:
        """Fetch logs for this job

        Args:
            since_ms: Timestamp, in milliseconds since epoch, to get logs for. Defaults to None for all logs.

        Returns:
            Log messages for the given job.
        """
        return self._api.get_logs(self, since_ms=since_ms)

    def print_logs(self, since_ms: int | None = None, file: IO | None = None) -> None:
        """Fetch and print logs for this job

        Args:
            since_ms: Timestamp, in milliseconds since epoch, to get logs for. Defaults to None for all logs.
            file: Where to print logs to. Defaults to sys.stdout.

        Returns:
            None
        """
        logs = self.get_logs(since_ms=since_ms)
        for m in logs:
            print(m["message"].strip(), file=file)

    def get_exec_time(self) -> timedelta:
        """Determine the execution time of this job, using the logs.

        Returns:
            Time the job took. If the job is in progress, time from first to last log message is returned.
        """
        refreshed = self.get_status()
        if not refreshed.terminal_status:
            warnings.warn(
                FusedInProgressWarning(
                    f"Job is still in progress. Status: {refreshed.status}"
                )
            )

        logs = refreshed.get_logs()
        if len(logs):
            first_log = logs[0]
            last_log = logs[-1]

            first_ts = first_log["timestamp"]
            last_ts = last_log["timestamp"]

            d_ts = last_ts - first_ts
            return timedelta(milliseconds=d_ts)
        else:
            raise ValueError(
                "Job does not have logs, so execution time can't be determined"
            )

    def tail_logs(
        self,
        refresh_seconds: float = 1,
        sample_logs: bool = True,
        timeout: float | None = None,
    ):
        """Continuously print logs for this job

        Args:
            refresh_seconds: how frequently, in seconds, to check for new logs. Defaults to 1.
            sample_logs: if true, print out only a sample of logs. Defaults to True.
            timeout: if not None, how long to continue tailing logs for. Defaults to None for indefinite.
        """
        return self._api.tail_logs(
            self,
            refresh_seconds=refresh_seconds,
            sample_logs=sample_logs,
            timeout=timeout,
        )

    def wait_for_job(
        self,
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
        return self._api.wait_for_job(
            self,
            poll_interval_seconds=poll_interval_seconds,
            timeout=timeout,
        )

    def cancel(self) -> RunResponse:
        """Cancel this job

        Returns:
            A new job object.
        """
        return self._api.cancel_job(self)


class Jobs(BaseModel):
    jobs: list[JobResponse]
    """The list of jobs."""

    # Options needed to refresh the same job list
    n: StrictInt = Field(..., repr=False)
    skip: StrictInt = Field(..., repr=False)
    per_request: StrictInt = Field(..., repr=False)
    max_requests: StrictInt | None = Field(..., repr=False)

    @property
    def _api(self) -> FusedAPI:
        return get_api()

    def refresh(self) -> Jobs:
        """Returns this object with an updated job list"""
        new_jobs = self._api.get_jobs(
            n=self.n,
            skip=self.skip,
            per_request=self.per_request,
            max_requests=self.max_requests,
        )
        self.jobs = new_jobs.jobs
        return self

    def __repr__(self) -> str:
        self.refresh()
        txt = ""
        for job in self.jobs:
            txt += f"{job.id}: {job.job_status}\n"

        return txt

    def _repr_html_(self) -> str:
        return fused_jobs_repr(self)


CoerceableToJobId = Union[str, RunResponse, JobResponse]


def _object_to_job_id(job: CoerceableToJobId) -> str:
    if isinstance(job, RunResponse):
        return job.job_id
    elif isinstance(job, JobResponse):
        return job.id
    else:
        return job
