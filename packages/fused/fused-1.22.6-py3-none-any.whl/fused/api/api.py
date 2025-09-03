from __future__ import annotations

import io
import os
import shutil
import time
import uuid
import warnings
from functools import lru_cache
from io import SEEK_END, SEEK_SET
from pathlib import Path
from tempfile import TemporaryFile
from threading import RLock
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Iterable,
    Literal,
    Sequence,
    TypeVar,
    overload,
)
from urllib.parse import urlparse

import fused
import fused.models.request as request_models
from fused._auth import AUTHORIZATION
from fused._global_api import set_api, set_api_class
from fused._optional_deps import HAS_PANDAS, PD_DATAFRAME
from fused._options import (
    DEV_DEFAULT_BASE_URL,
    PROD_DEFAULT_BASE_URL,
    STAGING_DEFAULT_BASE_URL,
    UNSTABLE_DEFAULT_BASE_URL,
)
from fused._options import options as OPTIONS
from fused._request import raise_for_status, session_with_retries
from fused._str_utils import detect_passing_local_file_as_str, is_uuid
from fused.core._impl._context_impl import context_in_batch, context_in_realtime
from fused.core._realtime_ops import _process_response
from fused.models.api import (
    JobConfig,
    JobStepConfig,
    ListDetails,
    UdfAccessToken,
    UdfAccessTokenList,
)
from fused.models.api._cronjob import CronJob, CronJobSequence
from fused.models.internal import Jobs, RunResponse
from fused.models.internal.job import CoerceableToJobId, _object_to_job_id
from fused.models.request import WHITELISTED_INSTANCE_TYPES, UdfType
from fused.models.udf import AnyBaseUdf, load_udf_from_response_data
from fused.models.udf._udf_registry import UdfRegistry
from fused.models.udf.base_udf import METADATA_FUSED_EXPLORER_TAB
from fused.warnings import (
    FusedIgnoredWarning,
    FusedNonProductionWarning,
    FusedOnPremWarning,
    FusedWarning,
)

if TYPE_CHECKING:
    import geopandas as gpd


_list_realtime_instances_lock = RLock()


def _detect_upload_length(data: bytes | BinaryIO) -> int:
    if hasattr(data, "tell") and hasattr(data, "seek"):
        # Looks like an IO, try to get size that way
        data.seek(0, SEEK_END)
        length = data.tell()
        # Reset to beginning
        data.seek(0, SEEK_SET)
        return length

    return len(data)


T = TypeVar("T")
FUSED_MOUNT_PATH = "file:///mount"


def resolve_udf_server_url(
    client_id: str | None = None,
    *,
    base_url: str | None = None,
    shared: bool = False,
) -> str:
    realtime_path = "realtime-shared" if shared else "realtime"
    if client_id and client_id.endswith("-staging"):
        return f"{base_url or STAGING_DEFAULT_BASE_URL}/{realtime_path}/{client_id}"

    if client_id is None:
        api = FusedAPI()
        client_id = api._automatic_realtime_client_id()

        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

    return f"{base_url or OPTIONS.base_url}/{realtime_path}/{client_id}"


class FusedAPI:
    """API for running jobs in the Fused service."""

    base_url: str

    def __init__(
        self,
        *,
        base_url: str | None = None,
        set_global_api: bool = True,
        credentials_needed: bool = True,
    ):
        """Create a FusedAPI instance.

        Keyword Args:
            base_url: The Fused instance to send requests to. Defaults to `https://www.fused.io/server/v1`.
            set_global_api: Set this as the global API object. Defaults to True.
            credentials_needed: If True, automatically attempt to log in. Defaults to True.
        """
        if credentials_needed and not OPTIONS.no_login:
            AUTHORIZATION.initialize()
        base_url = base_url or OPTIONS.base_url

        self.base_url = base_url
        self._check_is_prod()

        if set_global_api:
            set_api(self)

    def _check_is_prod(self):
        if context_in_realtime() or context_in_batch():
            # when we are in a management environment, never shown warnings
            return

        if self.base_url in [
            UNSTABLE_DEFAULT_BASE_URL,
            STAGING_DEFAULT_BASE_URL,
            DEV_DEFAULT_BASE_URL,
        ]:
            warnings.warn(
                FusedNonProductionWarning(
                    "FusedAPI is connected to a development environment"
                )
            )
        elif self.base_url != PROD_DEFAULT_BASE_URL:
            warnings.warn(
                FusedOnPremWarning("FusedAPI is connected to an on-prem environment")
            )

    def start_job(
        self,
        config: JobConfig | JobStepConfig,
        *,
        instance_type: WHITELISTED_INSTANCE_TYPES | None = None,
        region: str | None = None,
        disk_size_gb: int | None = None,
        additional_env: Sequence[str] | None = ("FUSED_CREDENTIAL_PROVIDER=ec2",),
        image_name: str | None = None,
        send_status_email: bool | None = None,
    ) -> RunResponse:
        """Execute an operation

        Args:
            config: the configuration object to run in the job.

        Keyword Args:
            instance_type: The AWS EC2 instance type to use for the job. Acceptable strings are "m5.large", "m5.xlarge", "m5.2xlarge", "m5.4xlarge", "r5.large", "r5.xlarge", "r5.2xlarge", "r5.4xlarge". Defaults to None.
            region: The AWS region in which to run. Defaults to None.
            disk_size_gb: The disk size to specify for the job. Defaults to None.
            additional_env: Any additional environment variables to be passed into the job, each in the form KEY=value. Defaults to None.
            image_name: Custom image name to run. Defaults to None for default image.
            send_status_email: Whether to send a status email to the user when the job is complete.
        """
        url = f"{self.base_url}/run"

        if isinstance(config, JobStepConfig):
            config = JobConfig(steps=[config])

        if send_status_email is None:
            send_status_email = OPTIONS.default_send_status_email

        body = {"config": config.model_dump(), "send_status_email": send_status_email}
        if additional_env:
            body["additional_env"] = additional_env
        if image_name:
            body["image_name"] = image_name

        params = request_models.StartJobRequest(
            region=region,
            instance_type=instance_type,
            disk_size_gb=disk_size_gb,
        )

        self._check_is_prod()
        with session_with_retries() as session:
            r = session.post(
                url=url,
                params=params.model_dump(),
                json=body,
                headers=self._generate_headers(),
                timeout=OPTIONS.run_timeout,
            )
        raise_for_status(r)
        return RunResponse.model_validate_json(r.content)

    @staticmethod
    def _is_type_app(udf: AnyBaseUdf) -> bool:
        """
        Checks whether the given UDF (User Defined Function) is of type 'app'.

        Args:
            udf (AnyBaseUdf): The UDF object whose type is to be checked.

        Returns:
            bool: True if the UDF type is 'app', False otherwise.
        """
        return (
            udf.metadata.get("fused:udfType") == UdfType.app if udf.metadata else False
        )

    def save_udf(
        self,
        udf: AnyBaseUdf,
        slug: str | None = None,
        id: str | None = None,
        allow_public_read: bool = False,
        allow_public_list: bool = False,
    ) -> UdfRegistry:
        url = f"{self.base_url}/udf/by-id/{id}" if id else f"{self.base_url}/udf/new"
        updated_udf = udf._with_udf_entrypoint()
        body = request_models.SaveUdfRequest(
            slug=slug,
            udf_body=updated_udf.model_dump_json(),
            udf_type=request_models.UdfType.auto
            if not self._is_type_app(udf)
            else request_models.UdfType.app,
            allow_public_read=allow_public_read,
            allow_public_list=allow_public_list,
        )

        self._check_is_prod()
        with session_with_retries() as session:
            r = session.post(
                url=url,
                json=body.model_dump(),
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        # TODO: body
        return r.json()

    def delete_saved_udf(self, id: str):
        url = f"{self.base_url}/udf/by-id/{id}"

        self._check_is_prod()
        with session_with_retries() as session:
            r = session.delete(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        # TODO: body
        return r.json()

    def delete_cache(self, id: str, client_id: str | None = None):
        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        client_base_url = resolve_udf_server_url(
            client_id=client_id, base_url=self.base_url, shared=True
        )

        url = f"{client_base_url}/udf-cache/by-id/{id}/delete"

        self._check_is_prod()
        with session_with_retries() as session:
            r = session.delete(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)

    def _get_udf(
        self,
        email_or_handle_or_id: str,
        slug: str | None = None,
    ):
        if slug is None:  # first arg is id
            if is_uuid(email_or_handle_or_id):
                return self._get_udf_by_id(email_or_handle_or_id)

            slug = email_or_handle_or_id
            email = self._whoami()["email"]
            return self._get_udf_by_email(email, slug)
        else:
            if "@" in email_or_handle_or_id:
                return self._get_udf_by_email(email_or_handle_or_id, slug)
            elif "team" == email_or_handle_or_id:
                return self._get_udf_by_team(slug)
            else:
                return self._get_udf_by_handle(email_or_handle_or_id, slug)

    async def _get_udf_async(
        self,
        email_or_handle_or_id: str,
        slug: str | None = None,
    ):
        """Async version of _get_udf that uses aiohttp to avoid blocking the event loop"""
        if slug is None:  # first arg is id
            if is_uuid(email_or_handle_or_id):
                return await self._get_udf_by_id_async(email_or_handle_or_id)

            slug = email_or_handle_or_id
            whoami_result = await self._whoami_async()
            email = whoami_result["email"]
            return await self._get_udf_by_email_async(email, slug)
        else:
            if "@" in email_or_handle_or_id:
                return await self._get_udf_by_email_async(email_or_handle_or_id, slug)
            elif "team" == email_or_handle_or_id:
                return await self._get_udf_by_team_async(slug)
            else:
                return await self._get_udf_by_handle_async(email_or_handle_or_id, slug)

    async def _get_udf_by_team_async(self, slug):
        """Async version of _get_udf_by_team"""
        from fused.core._realtime_ops import _get_shared_session

        url = f"{self.base_url}/udf/exec-env/self/by-slug/{slug}"
        session = await _get_shared_session()
        async with session.get(
            url=url,
            headers=self._generate_headers(),
            timeout=OPTIONS.request_timeout,
        ) as r:
            r.raise_for_status()
            return await r.json()

    async def _get_udf_by_email_async(self, email, slug):
        """Async version of _get_udf_by_email"""
        from fused.core._realtime_ops import _get_shared_session

        url = f"{self.base_url}/udf/by-user-email/{email}/by-slug/{slug}"
        session = await _get_shared_session()
        async with session.get(
            url=url,
            headers=self._generate_headers(),
            timeout=OPTIONS.request_timeout,
        ) as r:
            r.raise_for_status()
            return await r.json()

    async def _get_udf_by_handle_async(self, handle, slug):
        """Async version of _get_udf_by_handle"""
        from fused.core._realtime_ops import _get_shared_session

        url = f"{self.base_url}/udf/by-user-handle/{handle}/by-slug/{slug}"
        session = await _get_shared_session()
        async with session.get(
            url=url,
            headers=self._generate_headers(),
            timeout=OPTIONS.request_timeout,
        ) as r:
            r.raise_for_status()
            return await r.json()

    async def _get_udf_by_id_async(self, id: str):
        """Async version of _get_udf_by_id"""
        from fused.core._realtime_ops import _get_shared_session

        url = f"{self.base_url}/udf/by-id/{id}"
        session = await _get_shared_session()
        async with session.get(
            url=url,
            headers=self._generate_headers(),
            timeout=OPTIONS.request_timeout,
        ) as r:
            r.raise_for_status()
            return await r.json()

    def _get_udf_by_team(self, slug):
        url = f"{self.base_url}/udf/exec-env/self/by-slug/{slug}"
        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_udf_by_email(self, email, slug):
        url = f"{self.base_url}/udf/by-user-email/{email}/by-slug/{slug}"
        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_udf_by_handle(self, handle, slug):
        url = f"{self.base_url}/udf/by-user-handle/{handle}/by-slug/{slug}"
        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_udf_by_id(self, id: str):
        url = f"{self.base_url}/udf/by-id/{id}"
        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_udf_by_token(self, token: str):
        url = f"{self.base_url}/udf/shared/by-token/{token}"
        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_public_udf(
        self,
        id: str,
    ):
        url = f"{self.base_url}/udf/public/by-slug/{id}"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_code_by_url(self, url: str):
        req_url = f"{self.base_url}/code-proxy/by-url"

        with session_with_retries() as session:
            r = session.get(
                url=req_url,
                params={
                    "url": url,
                },
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _get_udf_objects(
        self,
        *,
        n: int | None = None,
        skip: int = 0,
        object_type: Literal["app", "udf"] = "udf",
        by: Literal["name", "id", "slug"] = "name",
        whose: Literal["self", "public", "community", "team"] = "self",
    ) -> UdfRegistry:
        """
        If n is a positive integer, fetch up to n UDFs; if n is None or <= 0, fetch all
        udf's until the API returns an empty list.

        Returns a UdfRegistry containing all deserialized UDFs.
        """

        if whose == "self":
            base_url = f"{self.base_url}/udf/self"
        elif whose in ("public", "community"):
            base_url = f"{self.base_url}/udf/public"
        elif whose == "team":
            base_url = f"{self.base_url}/udf/exec-env/self"
        else:
            raise ValueError(
                'Invalid value for `whose`, should be one of: "self", "public", "community", "team"'
            )

        collected: dict[str, AnyBaseUdf] = {}

        page_size = 300
        fetch_all = (n is None) or (isinstance(n, int) and n <= 0)
        remaining_to_fetch = n if (isinstance(n, int) and n > 0) else None

        while True:
            if remaining_to_fetch is None:
                this_limit = page_size
            else:
                this_limit = min(remaining_to_fetch, page_size)

            params = request_models.ListUdfsRequest(
                skip=skip, limit=this_limit, udf_type=object_type
            )

            with session_with_retries() as session:
                r = session.get(
                    url=base_url,
                    params=params.model_dump(),
                    headers=self._generate_headers(),
                    timeout=OPTIONS.request_timeout,
                )
            raise_for_status(r)

            udfs = r.json()

            if not udfs:
                break

            # Deserialize each returned UDF, filter if needed, and insert into our dictionary
            for udf in udfs:
                if "udf_body" not in udf or not udf["udf_body"]:
                    continue

                try:
                    deserialized_udf = load_udf_from_response_data(udf)
                    udf_id_key = (
                        deserialized_udf.name
                        if by == "name"
                        else (
                            udf["id"]
                            if by == "id"
                            else (udf["slug"] if by == "slug" else None)
                        )
                    )

                    # Filter out “public” vs “community”
                    filtered_public_udf = (
                        whose == "public"
                        and deserialized_udf._get_metadata_safe(
                            METADATA_FUSED_EXPLORER_TAB
                        )
                        == "community"
                    ) or (
                        whose == "community"
                        and deserialized_udf._get_metadata_safe(
                            METADATA_FUSED_EXPLORER_TAB
                        )
                        != "community"
                    )

                    if udf_id_key is not None and not filtered_public_udf:
                        collected[udf_id_key] = deserialized_udf

                except Exception as e:
                    warnings.warn(
                        FusedWarning(
                            f"UDF {udf['slug']} ({udf['id']}) could not be deserialized: {e}"
                        ),
                    )

            fetched_count = len(udfs)
            skip += fetched_count

            if not fetch_all:
                remaining_to_fetch -= fetched_count
                if remaining_to_fetch <= 0:
                    break

        return UdfRegistry(collected)

    def get_apps(
        self,
        *,
        n: int | None = None,
        skip: int = 0,
        by: Literal["name", "id", "slug"] = "name",
        whose: Literal["self", "public", "community", "team"] = "self",
    ):
        return self._get_udf_objects(
            object_type="app", by=by, whose=whose, n=n, skip=skip
        )

    def get_udfs(
        self,
        *,
        n: int | None = None,
        skip: int = 0,
        by: Literal["name", "id", "slug"] = "name",
        whose: Literal["self", "public", "community", "team"] = "self",
    ):
        return self._get_udf_objects(
            object_type="udf", by=by, whose=whose, n=n, skip=skip
        )

    def get_udf_access_tokens(
        self,
        n: int | None = None,
        *,
        skip: int = 0,
        per_request: int = 25,
        max_requests: int | None = 1,
        _whose: Literal["self", "all"] = "self",
    ) -> UdfAccessTokenList:
        request_count = 0
        has_content = True
        tokens = []

        assert per_request >= 0

        while has_content:
            url = f"{self.base_url}/udf-access-token/{_whose}"

            params = request_models.ListUdfAccessTokensRequest(
                skip=skip,
                limit=per_request,
            )
            skip += per_request

            with session_with_retries() as session:
                r = session.get(
                    url=url,
                    params=params.model_dump(),
                    headers=self._generate_headers(),
                    timeout=OPTIONS.request_timeout,
                )
            raise_for_status(r)
            tokens_this_request = r.json()
            if tokens_this_request:
                tokens.extend(tokens_this_request)
            else:
                has_content = False

            request_count += 1
            if n is not None and (
                len(tokens) >= n
                or (max_requests is not None and request_count == max_requests)
            ):
                break

        tokens_deserialized = UdfAccessTokenList()
        for token in tokens:
            token_deserialized = UdfAccessToken.model_validate(token)
            tokens_deserialized.append(token_deserialized)

        return tokens_deserialized

    def get_udf_access_token(
        self,
        token: str | UdfAccessToken,
    ) -> UdfAccessToken:
        if isinstance(token, UdfAccessToken):
            token = token.token
        url = f"{self.base_url}/udf-access-token/by-token/{token}"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                # May be a public token
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        token_obj = UdfAccessToken.model_validate_json(r.content)
        return token_obj

    def delete_udf_access_token(
        self,
        token: str | UdfAccessToken,
    ) -> UdfAccessToken:
        if isinstance(token, UdfAccessToken):
            token = token.token
        url = f"{self.base_url}/udf-access-token/by-token/{token}"

        with session_with_retries() as session:
            r = session.delete(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        token_obj = UdfAccessToken.model_validate_json(r.content)
        return token_obj

    def update_udf_access_token(
        self,
        token: str | UdfAccessToken,
        *,
        client_id: str | None = None,
        public_read: bool | None = None,
        access_scope: str | None = None,
        cache: bool | None = None,
        metadata_json: dict[str, Any] | None = None,
        enabled: bool | None = None,
    ) -> UdfAccessToken:
        if isinstance(token, UdfAccessToken):
            token = token.token
        url = f"{self.base_url}/udf-access-token/by-token/{token}"

        body = request_models.UpdateUdfAccessTokenRequest(
            client_id=client_id,
            cache=cache,
            public_read=public_read,
            access_scope=access_scope,
            metadata_json=metadata_json,
            enabled=enabled,
        ).model_dump()  # type: ignore

        with session_with_retries() as session:
            r = session.post(
                url=url,
                json=body,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        token_obj = UdfAccessToken.model_validate_json(r.content)
        return token_obj

    def create_udf_access_token(
        self,
        udf_email_or_name_or_id: str | None = None,
        /,
        udf_name: str | None = None,
        *,
        udf_email: str | None = None,
        udf_id: str | None = None,
        client_id: str | Ellipsis | None = ...,
        public_read: bool | None = None,
        access_scope: str | None = None,
        cache: bool = True,
        metadata_json: dict[str, Any] | None = None,
        enabled: bool = True,
    ) -> UdfAccessToken:
        """
        Create a token for running a UDF. The token allows anyone who has it to run
        the UDF, with the parameters they choose. The UDF will run under your environment.

        The token does not allow running any other UDF on your account.

        Args:
            udf_email_or_name_or_id: A UDF ID, email address (for use with udf_name), or UDF name.
            udf_name: The name of the UDF to create the token for.

        Keyword Args:
            udf_email: The email of the user owning the UDF, or, if udf_name is None, the name of the UDF.
            udf_id: The backend ID of the UDF to create the token for.
            client_id: If specified, overrides which realtime environment to run the UDF under.
            cache: If True, UDF tiles will be cached.
            metadata_json: Additional metadata to serve as part of the tiles metadata.json.
            enable: If True, the token can be used.
        """
        if udf_id is not None:
            if (
                udf_name is not None
                or udf_email is not None
                or udf_email_or_name_or_id is not None
            ):
                warnings.warn(
                    FusedIgnoredWarning(
                        "All other ways of specifying the UDF are ignored in favor of udf_id."
                    ),
                )
                udf_name = None
                udf_email = None
        elif udf_name is not None:
            if udf_email_or_name_or_id is not None:
                if udf_email is not None:
                    warnings.warn(
                        FusedIgnoredWarning(
                            "All other ways of specifying the UDF are ignored in favor of the first argument and udf_name."
                        ),
                    )
                udf_email = udf_email_or_name_or_id
        elif udf_email_or_name_or_id is not None:
            if udf_name is not None:
                udf_email = udf_email_or_name_or_id
            else:
                # Need to figure out what exactly the first argument is and how it specifies a UDF
                is_valid_uuid = True
                try:
                    uuid.UUID(udf_email_or_name_or_id)
                except ValueError:
                    is_valid_uuid = False
                if is_valid_uuid:
                    udf_id = udf_email_or_name_or_id
                elif "/" in udf_email_or_name_or_id:
                    udf_email, udf_name = udf_email_or_name_or_id.split("/", maxsplit=1)
                else:
                    udf_name = udf_email_or_name_or_id
                    udf_email = self._whoami()["email"]
        else:
            raise ValueError("No UDF specified to create an access token for.")

        if client_id is Ellipsis:
            client_id = self._automatic_realtime_client_id()

        if client_id is Ellipsis:
            raise ValueError("Failed to detect realtime client ID")

        url = f"{self.base_url}/udf-access-token/new"

        metadata_json = metadata_json or {}

        body = request_models.CreateUdfAccessTokenRequest(
            udf_email=udf_email,
            udf_slug=udf_name,
            udf_id=udf_id,
            client_id=client_id,
            cache=cache,
            public_read=public_read,
            access_scope=access_scope,
            metadata_json=metadata_json,
            enabled=enabled,
        ).model_dump()  # type: ignore

        with session_with_retries() as session:
            r = session.post(
                url=url,
                json=body,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        token_obj = UdfAccessToken.model_validate_json(r.content)
        return token_obj

    def get_secret_value(
        self,
        key: str,
        client_id: str | None = None,
    ) -> str:
        """Retrieve a secret value from the Fused service."""
        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        url = f"{resolve_udf_server_url(client_id=client_id, base_url=self.base_url)}/api/v1/secrets/{key}"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def set_secret_value(
        self,
        key: str,
        value: str,
        client_id: str | None = None,
    ) -> str:
        """Set a secret value on the Fused service."""
        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        body = request_models.UpdateSecretRequest(value=value).model_dump()
        url = f"{resolve_udf_server_url(client_id=client_id, base_url=self.base_url)}/api/v1/secrets/{key}"

        with session_with_retries() as session:
            r = session.put(
                url=url,
                json=body,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def delete_secret_value(
        self,
        key: str,
        client_id: str | None = None,
    ) -> str:
        """Delete a secret value on the Fused service."""
        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        url = f"{resolve_udf_server_url(client_id=client_id, base_url=self.base_url)}/api/v1/secrets/{key}"

        with session_with_retries() as session:
            r = session.delete(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def list_secrets(
        self,
        client_id: str | None = None,
    ) -> Iterable[str]:
        """List available secret values on the Fused service.

        This may also be used to retrieve all secrets."""
        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        url = f"{resolve_udf_server_url(client_id=client_id, base_url=self.base_url)}/api/v1/secrets"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json().keys()

    def get_jobs(
        self,
        n: int = 5,
        *,
        skip: int = 0,
        per_request: int = 25,
        max_requests: int | None = 1,
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
        request_count = 0
        has_content = True
        jobs = []
        original_skip = skip

        assert per_request >= 0

        while has_content:
            url = f"{self.base_url}/job/self"

            params = request_models.ListJobsRequest(
                skip=skip,
                limit=per_request,
            )
            skip += per_request

            with session_with_retries() as session:
                r = session.get(
                    url=url,
                    params=params.model_dump(),
                    headers=self._generate_headers(),
                    timeout=OPTIONS.request_timeout,
                )
            raise_for_status(r)
            jobs_this_request = r.json()
            if jobs_this_request:
                jobs.extend(jobs_this_request)
            else:
                has_content = False

            request_count += 1
            if len(jobs) >= n or (
                max_requests is not None and request_count == max_requests
            ):
                break

        return Jobs(
            jobs=jobs[:n],
            n=n,
            skip=original_skip,
            per_request=per_request,
            max_requests=max_requests,
        )

    def get_job_config(self, job: CoerceableToJobId) -> JobConfig:
        job_id = _object_to_job_id(job)
        url = f"{self.base_url}/job/by-id/{job_id}/config"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
                allow_redirects=False,
            )
        raise_for_status(r)

        redirect_location = r.headers["location"]

        with session_with_retries() as session:
            r2 = session.get(
                url=redirect_location,
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r2)

        return JobConfig.model_validate_json(r2.content)

    def get_status(self, job: CoerceableToJobId) -> RunResponse:
        """Fetch the status of a running job

        Args:
            job: the identifier of a job or a `RunResponse` object.

        Returns:
            The status of the given job.
        """
        job_id = _object_to_job_id(job)
        url = f"{self.base_url}/run/by-id/{job_id}"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return RunResponse.model_validate_json(r.content)

    def get_logs(
        self,
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
        job_id = _object_to_job_id(job)
        url = f"{self.base_url}/logs/{job_id}"
        params = {}
        if since_ms is not None:
            params["since_ms"] = since_ms

        with session_with_retries() as session:
            r = session.get(
                url=url,
                params=params,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def tail_logs(
        self,
        job: CoerceableToJobId,
        refresh_seconds: float = 1,
        sample_logs: bool = False,
        timeout: float | None = None,
    ):
        """Continuously print logs for a job

        Args:
            job: the identifier of a job or a `RunResponse` object.
            refresh_seconds: how frequently, in seconds, to check for new logs. Defaults to 1.
            sample_logs: if true, print out only a sample of logs. Defaults to False.
            timeout: if not None, how long to continue tailing logs for. Defaults to None for indefinite.
        """
        # TODO: Move this to the RunResponse object
        start_time = time.time()
        job = self.get_status(job)
        print(f"Logs for: {job.job_id}")

        def _tail_get_logs(job: RunResponse, since_ms: int | None = None) -> list[Any]:
            return self.get_logs(job, since_ms=since_ms)

        r = _tail_get_logs(job)

        # Job no longer executing, print and return early
        if job.status not in ["running", "pending"]:
            print(f"Job is not running ({job.status})")
            for message in r:
                print(message["message"].rstrip())
            return

        if len(r) == 0:
            print("Configuring packages and waiting for logs...")
            while len(r) == 0:
                time.sleep(refresh_seconds)
                r = _tail_get_logs(job)
                if timeout is not None and time.time() - start_time > timeout:
                    raise TimeoutError("Timed out waiting for logs")

        last_message: str | None = None
        last_since_ms: int | None = None
        while True:
            # If any results -- there may be none because we are filtering them with since_ms
            if len(r):
                current_message: str = r[-1]["message"]
                if last_message != current_message:
                    # If the most recent log line has changed, print it out
                    last_message = current_message
                    last_since_ms = r[-1]["timestamp"]

                    if sample_logs:
                        print(current_message.rstrip())
                    else:
                        for message in r:
                            print(message["message"].rstrip())

            if "ERROR" in current_message or self.get_status(job).status != "running":
                # Try to detect exit scenarios: an error has occured and the job will stop,
                # or the job is no longer in a running state.
                return

            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError("Timed out")

            time.sleep(refresh_seconds)
            r = _tail_get_logs(job, since_ms=last_since_ms)

    def wait_for_job(
        self,
        job: CoerceableToJobId,
        poll_interval_seconds: float = 5,
        timeout: float | None = None,
    ) -> RunResponse:
        """Block the Python kernel until the given job has finished

        Args:
            job: the identifier of a job or a `RunResponse` object.
            poll_interval_seconds: How often (in seconds) to poll for status updates. Defaults to 5.
            timeout: The length of time in seconds to wait for the job. Defaults to None.

        Raises:
            TimeoutError: if waiting for the job timed out.

        Returns:
            The status of the given job.
        """
        # TODO: Move this to the RunResponse object
        start_time = time.time()
        status = self.get_status(job)
        while not status.terminal_status:
            time.sleep(poll_interval_seconds)
            status = self.get_status(job)
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for job")
        return status

    def cancel_job(self, job: CoerceableToJobId) -> RunResponse:
        """Cancel an existing job

        Args:
            job: the identifier of a job or a `RunResponse` object.

        Returns:
            A new job object.
        """
        job_id = _object_to_job_id(job)
        url = f"{self.base_url}/run/by-id/{job_id}/cancel"

        self._check_is_prod()
        with session_with_retries() as session:
            r = session.post(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return RunResponse.model_validate_json(r.content)

    def get_job_results(
        self, job: CoerceableToJobId, arg_index: int = -1
    ) -> Any | list[Any]:
        """Get the deserialized batch results of a job

        Args:
            job: the identifier of a job or a `RunResponse` object.
            arg_index: number representing the desired partition result of a batch job

        Returns:
            A single deserialized vector or raster, or a list of them
        """
        files = self._list_job_results(job)
        sorted_files = sorted(files, key=lambda o: int(o["name"].split(".")[0]))
        if arg_index > -1:
            file_obj = sorted_files[arg_index]
            return self._process_job_result_obj(file_obj)

        return [self._process_job_result_obj(fo) for fo in sorted_files]

    def _update_job_progress(self, job: CoerceableToJobId, progress_amount: int):
        job_id = _object_to_job_id(job)
        url = f"{self.base_url}/run/by-id/{job_id}/increment-progress"
        data = request_models.JobIncrementProgressRequest(
            amount=progress_amount
        ).model_dump()
        with session_with_retries() as session:
            r = session.post(
                url=url,
                json=data,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _list_job_results(self, job: CoerceableToJobId) -> list[dict]:
        job_id = _object_to_job_id(job)
        results_url = f"{self.base_url}/run/by-id/{job_id}/results"
        with session_with_retries() as session:
            r = session.get(
                url=results_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _process_job_result_obj(self, file_obj: dict) -> Any:
        # Url is signed, so we do not need to add auth headers. Otherwise it would error
        # mentioning multiple auth mechanisms are not allowed
        with session_with_retries() as session:
            r = session.get(
                url=file_obj["url"],
                timeout=OPTIONS.request_timeout,
            )

        # TODO: Time taken is misleading as we're just fetching result urls, set to 0
        return _process_response(r, step_config=None, time_taken_seconds=0.0)

    def _whoami(self) -> Any:
        """
        Returns information on the currently logged in user
        """
        url = f"{self.base_url}/user/self"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    async def _whoami_async(self) -> Any:
        """
        Async version of _whoami that returns information on the currently logged in user
        """
        from fused.core._realtime_ops import _get_shared_session

        url = f"{self.base_url}/user/self"
        session = await _get_shared_session()
        async with session.get(
            url=url,
            headers=self._generate_headers(),
            timeout=OPTIONS.request_timeout,
        ) as response:
            response.raise_for_status()
            return await response.json()

    def _list_realtime_instances(self, *, whose: str = "self") -> list[Any]:
        """
        Returns information about available realtime instances
        """
        url = f"{self.base_url}/realtime-instance"
        if whose == "self":
            url += "/available"
        else:
            assert whose == "public", "whose must be 'public' or 'self'"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _automatic_realtime_client_id(self) -> str | None:
        if (client_id := OPTIONS.realtime_client_id) is not None:
            return client_id

        # in case of multiple threads trying to get the default ID, lock
        # to ensure we only fetch it once (doing it in parallel does not
        # make it faster and can actually slow down the endpoint)
        with _list_realtime_instances_lock:
            client_id = OPTIONS.realtime_client_id
            if client_id is None:
                instances = self._list_realtime_instances()
                if len(instances):
                    instances = sorted(
                        instances,
                        key=lambda instance: instance.get("preference_rank", 0),
                        reverse=True,
                    )
                    client_id = instances[0]["client_id"]
                if OPTIONS.save_user_settings and client_id:
                    OPTIONS.realtime_client_id = client_id

        return client_id

    def _list_efs(self, path: str, details: bool, client_id: str | None):
        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        path = path.removeprefix(FUSED_MOUNT_PATH)

        # Having a slash at the beginning causes incorrect paths when reconstructing
        # the item url we get from the API
        if path.startswith("/"):
            path = path[1:]

        list_request_url = f"{self.base_url}/efs/{client_id}/list"
        payload = {"item": path}
        # Fetch all pages
        params = {"limit": -1}

        with session_with_retries() as session:
            r = session.post(
                url=list_request_url,
                json=payload,
                params=params,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        result = r.json()
        items = result["items"]
        for item in items:
            item["url"] = f"{FUSED_MOUNT_PATH}/{item['url']}"
        if details:
            return [ListDetails.model_validate(item) for item in items]
        return [item["url"] for item in items]

    def _delete_efs(self, path: str, client_id: str | None):
        """
        Delete EFS directory

        Args:
            path (str): EFS path
            client_id (str): EFS client id
        """
        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        path = path.removeprefix(FUSED_MOUNT_PATH)
        # Get file name
        file_name = path.rsplit("/", 1)[-1]

        # Get file path
        try:
            file_path = path.rsplit("/", 1)[-2]
        except IndexError:
            file_path = None

        if file_name := self._check_efs_is_file(file_name, file_path, client_id):
            delete_request_url = f"{self.base_url}/efs/{client_id}/delete-file"
            payload = {"item": f"/{file_path}/{file_name}" if file_path else file_name}
        else:
            delete_request_url = f"{self.base_url}/efs/{client_id}/delete-dir"
            payload = {"item": path}

        with session_with_retries() as session:
            r = session.delete(
                url=delete_request_url,
                json=payload,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        result = r.json()
        return result

    def _get_efs(self, path: str, client_id: str | None):
        """
        Get EFS file
        """
        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        path = path.removeprefix(FUSED_MOUNT_PATH)
        params = request_models.GetEfsFileRequest(file_name=path).model_dump()
        get_request_url = f"{self.base_url}/efs/{client_id}/download"
        with session_with_retries() as session:
            r = session.get(
                url=get_request_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
                params=params,
            )
        raise_for_status(r)
        result = r.content
        return result

    def _upload_efs(
        self,
        path: str,
        file: bytes | BinaryIO,
        client_id: str | None,
        timeout: float | None = None,
    ):
        if client_id is None:
            raise ValueError("Failed to detect realtime client ID")

        path = path.removeprefix(FUSED_MOUNT_PATH)
        directory = os.path.dirname(path) or "/"
        filename = os.path.basename(path)

        # Ensure BytesIO file object and attach filename
        if isinstance(file, (bytes, bytearray)):
            file_obj = io.BytesIO(file)
        else:
            file_obj = file

        try:
            file_obj.name = filename
        except Exception:
            # Some streams may not allow setting name; ignore in that case
            pass

        data = {"dir": directory}
        files = {"file": file_obj}
        upload_url = f"{self.base_url}/efs/{client_id}/upload"
        with session_with_retries() as session:
            r = session.post(
                url=upload_url,
                data=data,
                files=files,
                headers=self._generate_headers(),
                timeout=timeout if timeout is not None else OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _check_efs_is_file(self, file_name: str, file_path: str | None, client_id: str):
        efs_objects_list = self._list_efs(
            f"{FUSED_MOUNT_PATH}/{file_path}" if file_path else "/",
            details=True,
            client_id=client_id,
        )
        for efs_object in efs_objects_list:
            efs_object_dict = dict(efs_object)
            if (
                efs_object_dict.get("file_name") == file_name
                and efs_object_dict.get("is_directory") is False
            ):
                return efs_object_dict.get("file_name")
        return False

    @staticmethod
    def _validate_file_path_schema(path: str):
        """
        Validate the file path schema and if mount create absolute path under mount

        Args:
            path: File path to be validated
        """
        original_path = path
        parsed_url = urlparse(path)
        scheme = parsed_url.scheme

        if not scheme and path.startswith("/mount"):
            path = f"file://{original_path}"  # Prepend file:// if absolute local path under /mount
            scheme = "file"  # Update scheme for the check

        supported_schemes = {"s3", "gs", "fd", "file"}

        if scheme not in supported_schemes:
            choice_str = ", ".join(f"{s!r}" for s in supported_schemes)
            raise ValueError(
                f"Path '{original_path}' is invalid. It must start with one of {choice_str}, "
                f"or be an absolute local path under /mount (e.g., /mount/path/to/file)."
            )
        return path

    @overload
    def list(self, path: str, *, details: Literal[True]) -> list[ListDetails]: ...

    @overload
    def list(self, path: str, *, details: Literal[False] = False) -> list[str]: ...

    def list(self, path: str, *, details: bool = False, client_id: str | None = None):
        path = self._validate_file_path_schema(path)
        if client_id is None and AUTHORIZATION.is_configured():
            client_id = self._automatic_realtime_client_id()

        if path.startswith(FUSED_MOUNT_PATH):
            return self._list_efs(path, details, client_id)

        list_request_url = f"{self.base_url}/files/list{'-details' if details else ''}"
        # ListPathRequest
        params = {"path": path}
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.get(
                url=list_request_url,
                params=params,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        result = r.json()
        if details:
            result = [ListDetails.model_validate(detail) for detail in result]
        return result

    def delete(
        self,
        path: str,
        max_deletion_depth: int | Literal["unlimited"] = 3,
        *,
        client_id: str | None = None,
    ) -> bool:
        path = self._validate_file_path_schema(path)

        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if path.startswith(FUSED_MOUNT_PATH):
            return self._delete_efs(path, client_id)

        delete_request_url = f"{self.base_url}/files/delete"
        params = request_models.DeletePathRequest(
            path=path,
            max_deletion_depth=max_deletion_depth,
        ).model_dump()
        # Pass path directly to avoid double-encoding from Pydantic model
        params["path"] = path
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.delete(
                url=delete_request_url,
                params=params,
                json="{}",
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _resolve(self, path: str) -> str:
        resolve_request_url = f"{self.base_url}/files/resolve"

        # ResolvePathRequest
        params = {"path": path}

        with session_with_retries() as session:
            r = session.post(
                url=resolve_request_url,
                params=params,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def get(self, path: str, *, client_id: str | None = None) -> bytes:
        path = self._validate_file_path_schema(path)

        if client_id is None and AUTHORIZATION.is_configured():
            client_id = self._automatic_realtime_client_id()

        if path.startswith(FUSED_MOUNT_PATH):
            return self._get_efs(path, client_id)

        get_request_url = f"{self.base_url}/files/get"
        # GetPathRequest
        params = {"path": path}
        if client_id:
            params["client_id"] = client_id
        with session_with_retries() as session:
            r = session.get(
                url=get_request_url,
                params=params,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
                allow_redirects=True,
            )
        raise_for_status(r)
        return r.content

    def download(
        self,
        path: str,
        local_path: str | Path,
        *,
        client_id: str | None = None,
    ) -> None:
        if client_id is None and AUTHORIZATION.is_configured():
            client_id = self._automatic_realtime_client_id()

        if path.startswith("/mount"):
            path = (
                f"file://{path}"  # Prepend file:// if absolute local path under /mount
            )

        if path.startswith(FUSED_MOUNT_PATH):
            path = path.removeprefix(FUSED_MOUNT_PATH)
            params = request_models.GetEfsFileRequest(file_name=path).model_dump()
            get_request_url = f"{self.base_url}/efs/{client_id}/download"
        else:
            get_request_url = f"{self.base_url}/files/get"
            params = request_models.GetPathRequest(path=path).model_dump()
            if client_id:
                params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.get(
                url=get_request_url,
                params=params,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
                allow_redirects=True,
                stream=True,
            )
        raise_for_status(r)
        with open(local_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    def sign_url(self, path: str, *, client_id: str | None = None) -> str:
        sign_request_url = f"{self.base_url}/files/sign"

        # SignPathRequest - pass path directly to avoid double-encoding from Pydantic model
        params = {"path": path}
        if client_id is None and AUTHORIZATION.is_configured():
            client_id = self._automatic_realtime_client_id()
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.get(
                url=sign_request_url,
                params=params,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def sign_url_prefix(
        self, path: str, *, client_id: str | None = None
    ) -> dict[str, str]:
        sign_prefix_request_url = f"{self.base_url}/files/sign_prefix"

        # SignPathRequest - pass path directly to avoid double-encoding from Pydantic model
        params = {"path": path}
        if client_id is None and AUTHORIZATION.is_configured():
            client_id = self._automatic_realtime_client_id()
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.get(
                url=sign_prefix_request_url,
                params=params,
                headers=self._generate_headers(credentials_needed=False),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def upload(
        self,
        path: str,
        data: bytes | BinaryIO,
        client_id: str | None = None,
        timeout: float | None = None,
    ) -> None:
        """Upload a binary blob to a cloud location"""
        path = self._validate_file_path_schema(path)
        if client_id is None:
            client_id = self._automatic_realtime_client_id()

        if path.startswith(FUSED_MOUNT_PATH):
            return self._upload_efs(path, data, client_id=client_id, timeout=timeout)

        return self._upload_signed(
            path=path, data=data, client_id=client_id, timeout=timeout
        )

    def _upload_tmp(self, extension: str, data: bytes | BinaryIO) -> str:
        """Upload a binary blob to a temporary cloud location, and return the new URL"""
        return self._upload_tmp_signed(extension=extension, data=data)

    def _upload_signed(
        self,
        path: str,
        data: bytes | BinaryIO,
        *,
        client_id: str | None = None,
        timeout: float | None = None,
    ) -> None:
        """Upload a binary blob to a cloud location"""
        upload_url = f"{self.base_url}/files/sign-upload"
        # UploadRequest - pass path directly to avoid double-encoding from Pydantic model
        params = {"path": path, "content_length": _detect_upload_length(data)}
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.get(
                url=upload_url,
                params=params,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        signed_post = r.json()

        with session_with_retries() as session:
            r2 = session.post(
                url=signed_post["url"],
                data=signed_post["fields"],
                files={"file": data},
                timeout=timeout if timeout is not None else OPTIONS.request_timeout,
            )
        raise_for_status(r2)

    def _upload_tmp_signed(
        self,
        extension: str,
        data: bytes | BinaryIO,
        *,
        client_id: str | None = None,
    ) -> str:
        """Upload a binary blob to a temporary cloud location, and return the new URL"""
        upload_temp_url = f"{self.base_url}/files/sign-upload-temp"

        params = request_models.SignUploadTempRequest(
            extension=extension, content_length=_detect_upload_length(data)
        ).model_dump()
        if client_id is None:
            client_id = self._automatic_realtime_client_id()
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.get(
                url=upload_temp_url,
                params=params,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        sign_details = r.json()

        signed_post = sign_details["signed_post"]
        with session_with_retries() as session:
            r2 = session.post(
                url=signed_post["url"],
                data=signed_post["fields"],
                files={"file": data},
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r2)

        return sign_details["storage_url"]

    def _upload_direct(
        self,
        path: str,
        data: bytes | BinaryIO,
        *,
        client_id: str | None = None,
    ) -> None:
        """Upload a binary blob to a cloud location"""
        upload_url = f"{self.base_url}/files/upload"

        params = request_models.UploadRequest(path=path).model_dump()
        if client_id is None:
            client_id = self._automatic_realtime_client_id()
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.put(
                url=upload_url,
                params=params,
                headers=self._generate_headers(
                    {"Content-Type": "application/octet-stream"}
                ),
                data=data,
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)

    def _upload_tmp_direct(
        self,
        extension: str,
        data: bytes | BinaryIO,
        *,
        client_id: str | None = None,
    ) -> str:
        """Upload a binary blob to a temporary cloud location, and return the new URL"""
        upload_temp_url = f"{self.base_url}/files/upload-temp"

        params = request_models.UploadTempRequest(extension=extension).model_dump()
        if client_id is None:
            client_id = self._automatic_realtime_client_id()
        if client_id:
            params["client_id"] = client_id

        with session_with_retries() as session:
            r = session.post(
                url=upload_temp_url,
                params=params,
                headers=self._generate_headers(
                    {"Content-Type": "application/octet-stream"}
                ),
                data=data,
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _upload_local_input(
        self, input: str | Path | list[str | Path] | gpd.GeoDataFrame
    ) -> str | list[str]:
        """Upload local input (in-memory DataFrame or path to local file(s)).

        If uploaded, return a URL to it. Otherwise return input unchanged.
        """
        # in-memory (Geo)DataFrame
        if HAS_PANDAS and isinstance(input, PD_DATAFRAME):
            with TemporaryFile(dir=OPTIONS.temp_directory) as tmp:
                input.to_parquet(tmp)
                tmp.seek(0, SEEK_SET)
                input = self._upload_tmp(extension="parquet", data=tmp)
                return input

        # local file path(s)
        def _upload_path(input_path: Path) -> str:
            with open(input_path, "rb") as f:
                extension = input_path.name.rsplit(".", 1)[-1]
                uploaded_input = self._upload_tmp(extension=extension, data=f)
            return uploaded_input

        if isinstance(input, (str, Path)):
            input = detect_passing_local_file_as_str(input)
            if isinstance(input, Path):
                return _upload_path(input)
            else:
                # not a local file path, return as is
                return input
        elif isinstance(input, list):
            uploaded_inputs = []
            for input_path in input:
                input_path = detect_passing_local_file_as_str(input_path)
                if isinstance(input_path, Path):
                    uploaded_inputs.append(_upload_path(input_path))
                else:
                    uploaded_inputs.append(input_path)
            return uploaded_inputs
        else:
            raise TypeError(f"Unsupported input type: {type(input)}")

    def list_cronjobs(self) -> list[CronJob]:
        """List all cronjobs"""
        cronjobs_url = f"{self.base_url}/cronjob/get-self"
        with session_with_retries() as session:
            r = session.get(
                cronjobs_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return CronJobSequence.model_validate(r.json())

    def create_cronjob(self, cronjob: CronJob) -> CronJob:
        """Create a cronjob"""
        cronjobs_url = f"{self.base_url}/cronjob/create"
        with session_with_retries() as session:
            r = session.post(
                cronjobs_url,
                json=cronjob.model_dump(by_alias=True),
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return CronJob.model_validate(r.json())

    def update_cronjob(self, cronjob: CronJob) -> CronJob:
        """Update a cronjob"""
        cronjobs_url = f"{self.base_url}/cronjob/by-id/{cronjob.id}"
        with session_with_retries() as session:
            r = session.post(
                cronjobs_url,
                json=cronjob.model_dump(by_alias=True),
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return CronJob.model_validate(r.json())

    def delete_cronjob(self, cronjob_id: str) -> CronJob:
        """Delete a cronjob"""
        cronjobs_url = f"{self.base_url}/cronjob/by-id/{cronjob_id}"
        with session_with_retries() as session:
            r = session.delete(
                cronjobs_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return CronJob.model_validate(r.json())

    def get_cronjob(self, cronjob_id: str) -> CronJob:
        """Get a cronjob"""
        cronjobs_url = f"{self.base_url}/cronjob/by-id/{cronjob_id}"
        with session_with_retries() as session:
            r = session.get(
                cronjobs_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return CronJob.model_validate(r.json())

    def get_cronjobs_for_udf(self, udf_id: str) -> CronJobSequence:
        """Get cronjob(s) for this given UDF ID"""
        cronjobs_url = f"{self.base_url}/cronjob/by-udf-id/{udf_id}"
        with session_with_retries() as session:
            r = session.get(
                cronjobs_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return CronJobSequence.model_validate(r.json())

    def run_cronjob(self, cronjob_id: str):
        """Run a cronjob"""
        cronjobs_url = f"{self.base_url}/cronjob/user-run/by-id/{cronjob_id}"
        with session_with_retries() as session:
            r = session.post(
                cronjobs_url,
                json={},
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        result = r.json()
        return {
            "run": RunResponse.model_validate(result["run"]),
            "cronjob": CronJob.model_validate(result["cronjob"]),
        }

    def _health(self) -> bool:
        """Check the health of the API backend"""
        with session_with_retries() as session:
            r = session.get(f"{self.base_url}/health", timeout=OPTIONS.request_timeout)
        raise_for_status(r)
        return True

    def auth_token(self) -> str:
        """
        Returns the current user's Fused environment (team) auth token
        """
        url = f"{self.base_url}/execution-env/token"

        with session_with_retries() as session:
            r = session.get(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _generate_headers(
        self,
        headers: dict[str, str] | None = None,
        *,
        credentials_needed: bool = True,
    ) -> dict[str, str]:
        if headers is None:
            headers = {}

        common_headers = {
            "Fused-Py-Version": fused.__version__,
            **OPTIONS.default_run_headers,
            **headers,
        }

        if AUTHORIZATION.is_configured() or credentials_needed:
            common_headers["Authorization"] = (
                f"{AUTHORIZATION.credentials.auth_scheme} {AUTHORIZATION.credentials.access_token}"
            )

        return common_headers

    @lru_cache
    def dependency_whitelist(self) -> str:
        sign_request_url = f"{self.base_url}/internal/dependency-whitelist"
        with session_with_retries() as session:
            r = session.get(
                url=sign_request_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _team_info(self):
        execution_environment_url = f"{self.base_url}/execution-env/self"
        with session_with_retries() as session:
            r = session.get(
                url=execution_environment_url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
            )
        raise_for_status(r)
        return r.json()

    def _run_lite(self, function_name, params):
        url = f"{self.base_url}/fused_lite/invoke/{function_name}"
        with session_with_retries() as session:
            r = session.post(
                url=url,
                headers=self._generate_headers(),
                timeout=OPTIONS.request_timeout,
                json=params,
            )
        raise_for_status(r)
        return r.json()


set_api_class(FusedAPI)
