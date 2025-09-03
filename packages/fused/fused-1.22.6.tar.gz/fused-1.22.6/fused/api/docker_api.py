from __future__ import annotations

import json
import shlex
import subprocess
from base64 import b64encode
from functools import lru_cache
from io import SEEK_SET, BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Sequence
from uuid import uuid4

from pydantic import BaseModel

from fused._global_api import set_api
from fused._optional_deps import HAS_PANDAS, PD_DATAFRAME
from fused._options import DEV_DEFAULT_BASE_URL, STAGING_DEFAULT_BASE_URL
from fused._options import options as OPTIONS
from fused.api.api import FusedAPI
from fused.models.api import JobConfig, JobStepConfig

if TYPE_CHECKING:
    import pandas as pd

# TODO: Consider making this us-west-2, depending on where the user is logged in
# DEFAULT_REPOSITORY = "926411091187.dkr.ecr.us-east-1.amazonaws.com/fused-job2"
DEFAULT_REPOSITORY = "926411091187.dkr.ecr.us-west-2.amazonaws.com/fused-job2"
DEFAULT_TAG = "latest"

MAX_ERROR_MESSAGE_SIZE = 10000
JOB_MOUNT_PATH = "/job/job.json"
JOB_INPUT_MOUNT_PATH = "/job/input"
DEFAULT_JOB_INPUT_HOST = "/tmp"


class DockerRunnable(BaseModel):
    command: str

    def run_and_get_bytes(self) -> bytes:
        """
        Run the command and return the bytes written to stdout.

        Raises an exception if the return code is not 0.
        """
        # TODO: Disable shell here
        # Check is false because we check it ourselves next
        p = subprocess.run(self.command, shell=True, capture_output=True, check=False)
        if p.returncode:
            error_message = p.stderr.decode("utf-8")
            if len(error_message) > MAX_ERROR_MESSAGE_SIZE:
                error_message = (
                    error_message[:MAX_ERROR_MESSAGE_SIZE] + "... (truncated)"
                )
            if len(error_message) == 0:
                error_message = "No message on stderr"
            raise ValueError(f"Failed ({p.returncode}): {error_message}")
        return p.stdout

    def run_and_get_output(self) -> str:
        """
        Run the command and return the utf-8 string written to stdout.

        Raises an exception if the return code is not 0.
        """
        return self.run_and_get_bytes().decode("utf-8")

    def run_and_tail_output(self) -> None:
        """
        Run the command and print output to stdout.

        Raises an exception if the return code is not 0.
        """
        # TODO: Disable shell here
        subprocess.run(self.command, shell=True, check=True)


class FusedDockerAPI(FusedAPI):
    """API for running jobs in the Fused Docker container."""

    repository: str
    tag: str
    mount_aws_credentials: bool
    mount_data_directory: str | None
    mount_job_input_directory: str | None
    additional_docker_args: Sequence[str]
    docker_command_wrapper: Callable[[str], str] | None
    _auth_token: str | None
    is_staging: bool
    is_gcp: bool
    is_aws: bool

    def __init__(
        self,
        *,
        repository: str = DEFAULT_REPOSITORY,
        tag: str = DEFAULT_TAG,
        mount_aws_credentials: bool = False,
        mount_data_directory: str | None = None,
        mount_job_input_directory: str | None = DEFAULT_JOB_INPUT_HOST,
        additional_docker_args: Sequence[str] = (),
        docker_command_wrapper: Callable[[str], str] | None = None,
        auth_token: str | None = None,
        auto_auth_token: bool = True,
        set_global_api: bool = True,
        is_staging: bool | None = None,
        is_gcp: bool = False,
        is_aws: bool = False,
        pass_config_as_file: bool = True,
        base_url: str | None = None,
        credentials_needed: bool = True,
    ):
        """Create a FusedDockerAPI instance.

        Keyword Args:
            repository: Repository name for jobs to start.
            tag: Tag name for jobs to start. Defaults to `'latest'`.
            mount_aws_credentials: Whether to add an additional volume for AWS credentials in the job. Defaults to False.
            mount_data_directory: If not None, path on the host to mount as the /data directory in the container. Defaults to None.
            mount_job_input_directory: If not None, path on the host to mount as the /job/input/ directory in the container. Defaults to None.
            additional_docker_args: Additional arguments to pass to Docker. Defaults to empty.
            docker_command_wrapper: Command to wrap the Docker execution in, e.g. `'echo {} 1>&2; exit 1'`. Defaults to None for no wrapping.
            auth_token: Auth token to pass to the Docker command. Defaults to automatically detect when auto_auth_token is True.
            auto_auth_token: Obtain the auth token from the (previous) global Fused API. Defaults to True.
            set_global_api: Set this as the global API object. Defaults to True.
            is_staging: Set this if connecting to the Fused staging environment. Defaults to None to automatically detect.
            is_gcp: Set this if running in GCP. Defaults to False.
            is_aws: Set this if running in AWS. Defaults to False.
            pass_config_as_file: If True, job configurations are first written to a temporary file and then passed to Docker. Defaults to True.
        """
        super().__init__(
            base_url=base_url,
            credentials_needed=credentials_needed,
            set_global_api=False,
        )
        self.repository = repository
        self.tag = tag
        self.mount_aws_credentials = mount_aws_credentials
        self.mount_data_directory = mount_data_directory
        self.mount_job_input_directory = mount_job_input_directory
        self.additional_docker_args = additional_docker_args
        self.docker_command_wrapper = docker_command_wrapper
        self.is_gcp = is_gcp
        self.is_aws = is_aws
        self.pass_config_as_file = pass_config_as_file
        if auth_token or not auto_auth_token:
            self._auth_token = auth_token
        else:
            self._auth_token = FusedAPI(set_global_api=False).auth_token()

        if is_staging is not None:
            self.is_staging = is_staging
        else:
            # Autodetect whether staging flag should be set based on base_url.
            self.is_staging = OPTIONS.base_url in (
                STAGING_DEFAULT_BASE_URL,
                DEV_DEFAULT_BASE_URL,
            )

        if set_global_api:
            set_api(self)

    def start_job(
        self,
        config: JobConfig | JobStepConfig,
        *,
        additional_env: Sequence[str] | None = ("FUSED_CREDENTIAL_PROVIDER=ec2",),
        **kwargs,
    ) -> DockerRunnable:
        """Execute an operation

        Args:
            config: the configuration object to run in the job.

        Keyword Args:
            additional_env: Any additional environment variables to be passed into the job, each in the form KEY=value. Defaults to None.
        """
        assert kwargs.get("region") is None, (
            "region may not be specified with FusedDockerAPI"
        )
        assert kwargs.get("instance_type") is None, (
            "instance_type may not be specified with FusedDockerAPI"
        )
        assert kwargs.get("disk_size_gb") is None, (
            "disk_size_gb may not be specified with FusedDockerAPI"
        )
        assert kwargs.get("image_name") is None, (
            "image_name may not be specified with FusedDockerAPI"
        )

        if isinstance(config, JobStepConfig):
            config = JobConfig(steps=[config])

        if self.pass_config_as_file:
            config_path = self._make_config_path(config.model_dump_json())
            args = ["--config-from-file", JOB_MOUNT_PATH]
        else:
            config_path = None
            args = ["--config", config.model_dump_json()]

        # TODO: This should return a RunResponse
        return self._make_run_command(
            "run-config", args, env=additional_env, config_path=config_path
        )

    def _make_run_command(
        self,
        command: str,
        args: Sequence[str],
        env: Sequence[str] | None = None,
        config_path: str | None = None,
    ) -> DockerRunnable:
        docker_args_part: list[str] = [*self.additional_docker_args]
        if env:
            for e in env:
                docker_args_part.append("-e")
                docker_args_part.append(shlex.quote(e))
        # TODO: Send in the base_url
        if self._auth_token:
            docker_args_part.append("-e")
            docker_args_part.append(f"FUSED_AUTH_TOKEN={self._auth_token}")
        if self.is_staging:
            docker_args_part.append("-e")
            docker_args_part.append("__FUSED_STAGING_LICENSE_CHECK=1")
        if self.mount_aws_credentials:
            docker_args_part.append("-v")
            docker_args_part.append(
                '"$HOME/.aws/credentials:/root/.aws/credentials:ro"'
            )
        if self.mount_data_directory is not None:
            docker_args_part.append("--mount")
            docker_args_part.append(
                f"type=bind,src={self.mount_data_directory},target=/data"
            )
            docker_args_part.append("-e")
            docker_args_part.append("FUSED_DATA_DIRECTORY=/data")
        if config_path is not None:
            docker_args_part.append("--mount")
            docker_args_part.append(
                f"type=bind,src={config_path},target={JOB_MOUNT_PATH}"
            )
        if self.mount_job_input_directory is not None:
            docker_args_part.append("--mount")
            docker_args_part.append(
                f"type=bind,src={self.mount_job_input_directory},target={JOB_INPUT_MOUNT_PATH}"
            )
        if self.is_gcp:
            docker_args_part.append("-e")
            docker_args_part.append("FUSED_GCP=1")
        if self.is_aws:
            docker_args_part.append("-e")
            docker_args_part.append("FUSED_AWS=1")

        args_part = [shlex.quote(a) for a in args]

        docker_image_name = f"{self.repository}:{self.tag}"

        job_command = shlex.quote(command)
        docker_command = f"docker run {' '.join(docker_args_part)} --rm {docker_image_name} {job_command} {' '.join(args_part)}"
        if self.docker_command_wrapper is not None:
            docker_command = self.docker_command_wrapper(docker_command)

        return DockerRunnable(command=docker_command)

    def _make_config_path(self, config_json: str) -> str:
        temp_file_name = f"/tmp/job_{uuid4()}.json"

        # TODO: Confirm temp_file_name doesn't already exist

        # We don't directly create the file in order to support running over SSH
        create_command = f"cat | base64 --decode > {temp_file_name}"
        if self.docker_command_wrapper is not None:
            create_command = self.docker_command_wrapper(create_command)

        b64data = b64encode(config_json.encode("utf-8"))

        # Don't capture output so that if the command errors, the output gets
        # sent back to the user
        subprocess.run(
            create_command,
            shell=True,
            check=True,
            input=b64data,
        )
        return temp_file_name

    def _replace_df_input(
        self, input: str | list[str] | pd.DataFrame
    ) -> str | list[str]:
        replacement_bytes: bytes | None = None
        extension: str | None = None
        if HAS_PANDAS and isinstance(input, PD_DATAFRAME):
            with BytesIO() as tmp:
                input.to_parquet(tmp)
                tmp.seek(0, SEEK_SET)
                replacement_bytes = tmp.getvalue()
                extension = "parquet"
        elif isinstance(input, Path):
            with open(input, "rb") as f:
                replacement_bytes = f.read()
                extension = input.name.split(".", 1)[-1]

        if replacement_bytes is not None:
            assert self.mount_job_input_directory, (
                "mount_job_input_directory must be set to pass DataFrame input"
            )
            temp_file_name = f"df_{uuid4()}.{extension}"
            host_file_name = f"{Path(self.mount_job_input_directory) / temp_file_name}"
            container_file_name = f"file://{JOB_INPUT_MOUNT_PATH}/{temp_file_name}"

            # TODO: Confirm temp_file_name doesn't already exist

            # We don't directly create the file in order to support running over SSH
            # We use "base64 --decode" because Parquet as a binary file could interact with the shell in bad ways
            create_command = f"cat | base64 --decode > {host_file_name}"
            if self.docker_command_wrapper is not None:
                create_command = self.docker_command_wrapper(create_command)

            b64data = b64encode(replacement_bytes)

            # Don't capture output so that if the command errors, the output gets
            # sent back to the user
            subprocess.run(
                create_command,
                shell=True,
                check=True,
                input=b64data,
            )
            return container_file_name
        else:
            return input

    def _health(self) -> bool:
        """Check the health of the API backend"""
        runnable = self._make_run_command("version", [])
        runnable.run_and_get_output()
        return True

    @lru_cache
    def dependency_whitelist(self) -> dict[str, str]:
        runnable = self._make_run_command("dependency-whitelist", [])
        content = runnable.run_and_get_bytes()
        return json.loads(content)


def ssh_command_wrapper(conn_string: str) -> Callable[[str], str]:
    """Creates a command wrapper that connects via SSH and sudo runs the command."""
    return (
        lambda command: f'ssh {conn_string} -t "sudo sh -c "{shlex.quote(shlex.quote(command))}""'
    )


def gcloud_command_wrapper(
    conn_string: str, *, zone: str | None = None, project: str | None = None
) -> Callable[[str], str]:
    """Creates a command wrapper that connects via gcloud and runs the command."""
    zone_arg = f"--zone {zone}" if zone else ""
    project_arg = f"--project {project}" if project else ""
    return (
        lambda command: f"gcloud compute ssh {zone_arg} {project_arg} {conn_string} --command {shlex.quote(command)}"
    )
