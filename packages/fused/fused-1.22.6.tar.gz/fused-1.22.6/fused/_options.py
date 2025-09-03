import os
import tempfile
import warnings
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse

from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictStr,
    field_serializer,
    field_validator,
    model_validator,
)

from ._global_api import reset_api
from .warnings import FusedIgnoredWarning, FusedImportWarning

DEV_DEFAULT_BASE_URL = "http://localhost:8783/v1"
PROD_DEFAULT_BASE_URL = "https://www.fused.io/server/v1"
STAGING_DEFAULT_BASE_URL = "https://www-staging.fused.io/server/v1"
UNSTABLE_DEFAULT_BASE_URL = "https://unstable.fused.io/server/v1"
DEV_PR_DEFAULT_BASE_URL = "https://{}.dev.fusedlabs.io/server/v1"


OPTIONS_PATH = Path("~/.fused/settings.toml").expanduser()
"""First choice for where to find settings"""
OPTIONS_JSON_PATH = Path("~/.fused/settings.json").expanduser()
"""Second choice for where to find settings"""

StorageStr = Literal["auto", "mount", "local", "object"]


class OptionsBaseModel(BaseModel):
    def __dir__(self) -> List[str]:
        # Provide method name lookup and completion. Only provide 'public'
        # methods.
        # This enables autocompletion
        # Pydantic methods to remove in __dir__
        PYDANTIC_METHODS = {
            "Config",
            "construct",
            "copy",
            "from_orm",
            "json",
            "parse_file",
            "parse_obj",
            "schema",
            "schema_json",
            "update_forward_refs",
            "validate",
            "model_validate",
            "model_dump_json",
        }

        normal_dir = {
            name
            for name in dir(type(self))
            if (not name.startswith("_") and name not in PYDANTIC_METHODS)
        }
        pydantic_fields = set(self.model_fields.keys())
        return sorted(normal_dir | pydantic_fields)

    def _repr_html_(self) -> str:
        # Circular import because the repr needs the options
        from fused._formatter.formatter_options import fused_options_repr

        return fused_options_repr(self)


class AuthOptions(OptionsBaseModel):
    authorize_url: str = "https://dev-tjcykxcetrz6bps6.us.auth0.com/authorize"
    """The authorize URL is used for the initial login flow. This is intended to be opened in
    the user's web browser for them to sign in."""

    oauth_token_url: str = "https://dev-tjcykxcetrz6bps6.us.auth0.com/oauth/token"
    """The token url is used for programmatic access to generate access and refresh tokens."""

    logout_url: str = "https://dev-tjcykxcetrz6bps6.us.auth0.com/oidc/logout"

    # The client id, client secret, and audience identifies a specific application and API
    client_id: str = "CXiwKZQmmyo0rqXZY7pzBgfsF7AL2A9l"
    client_secret: str = (
        "FVNz012KgNmqITYnCCOM8Q1Nt81W_DO4SeCRgVsftREKTWpzZU522nia5TdSNv8h"
    )
    audience: str = "fused-python-api"

    local_redirect_url: str = "http://localhost:3000"
    """This redirect uri is passed to the authorize URL as a url parameter. This localhost
    uri is used to intercept the "code" generated from the authorization"""

    scopes: List[str] = ["openid", "email", "name", "offline_access"]
    """The offline_access scope is necessary to be able to fetch refresh tokens
    The other scopes are useful to access identifying information in the retrieved JWT"""

    credentials_path: str = "~/.fused/credentials"
    """The path where the refresh token is saved on disk. Will be user-expanded to resolve ~."""


class ShowOptions(OptionsBaseModel):
    """Options for showing debug information"""

    open_browser: Optional[StrictBool] = None
    """Whether to open a local browser window for debug information"""
    show_widget: Optional[StrictBool] = None
    """Whether to show debug information in an IPython widget"""

    enable_tqdm: StrictBool = True
    """Whether to show tqdm-based progress information"""


def cache_directory(storage: StorageStr) -> Path:
    return _get_cache_dir(storage)


def _data_directory(storage: StorageStr) -> Path:
    return _get_data_dir(storage)


def _get_data_dir(storage: StorageStr) -> Path:
    base_path = get_writable_dir(storage)
    # Keep consistency with job2 data_path where return can be /mount/tmp or /tmp
    # TODO: Maybe unify to single common dir - /mount/data and /tmp/data
    if "mount" in str(base_path):
        return base_path / "tmp"
    else:
        return base_path


def _get_cache_dir(storage: StorageStr) -> Path:
    base_path = get_writable_dir(storage)
    return base_path / "cached_data"


def get_writable_dir(storage: StorageStr) -> Path:
    mount_path = Path("/mount")
    temp_dir = Path(tempfile.gettempdir())

    if storage == "auto":
        # Cache in mounted drive if available & writable, else cache in /tmp
        if is_path_writable(mount_path):
            base_path = mount_path
        else:
            base_path = temp_dir
    elif storage == "mount":
        base_path = mount_path
    elif storage == "local":
        base_path = temp_dir
    elif storage == "object":
        base_path = Path("/")
    else:
        raise ValueError(storage)

    return base_path


def is_path_writable(p: Path) -> bool:
    return p.exists() and os.access(p, os.W_OK)


class Options(OptionsBaseModel):
    base_url: str = PROD_DEFAULT_BASE_URL
    """Fused API endpoint"""

    auth: AuthOptions = Field(default_factory=AuthOptions)
    """Options for authentication."""

    show: ShowOptions = Field(default_factory=ShowOptions)
    """Options for object reprs and how data are shown for debugging."""

    max_workers: int = 16
    """Maximum number of threads, when multithreading requests"""

    run_timeout: float = 130
    """Request timeout for UDF run requests to the Fused service"""

    request_timeout: Union[Tuple[float, float], float, None] = 5
    """Request timeout for the Fused service

    May be set to a tuple of connection timeout and read timeout"""

    request_timeout_dev: Union[Tuple[float, float], float, None] = 25
    """Alternative request timeout for the Fused service development environments

    Only used on some requests.

    May be set to a tuple of connection timeout and read timeout"""

    request_max_retries: int = 5
    """Maximum number of retries for API requests"""

    request_retry_base_delay: float = 1.0
    """Base delay before retrying a API request in seconds"""

    realtime_client_id: Optional[StrictStr] = None
    """Client ID for realtime service."""

    max_recursion_factor: int = 5
    """Maximum recursion factor for UDFs. This is used to limit the number of
    recursive calls to UDFs. If a UDF exceeds this limit, an error will be raised."""

    save_user_settings: StrictBool = True
    """Save per-user settings such as credentials and environment IDs."""

    default_udf_run_engine: Optional[StrictStr] = None
    """Default engine to run UDFs, one of: "local" or "remote"."""

    default_validate_imports: StrictBool = False
    """Default for whether to validate imports in UDFs before `run_local`,
    `run_batch`."""

    prompt_to_login: StrictBool = False
    """Automatically prompt the user to login when importing Fused."""

    no_login: StrictBool = False
    """If set, Fused will not attempt to login automatically when needed."""

    pyodide_async_requests: StrictBool = False
    """If set, Fused is being called inside Pyodide and should use pyodide
    for async HTTP requests."""

    cache_directory: Path | None = None
    """The base directory for storing cached results."""

    data_directory: Path = None
    """The base directory for storing data results. Note: if storage type is 'object', then this path is relative to
    fd_prefix."""

    temp_directory: Path = Path(tempfile.gettempdir())
    """The base directory for storing temporary files."""

    never_import: StrictBool = False
    """Never import UDF code when loading UDFs."""

    gcs_secret: str = "gcs_fused"
    """Secret name for GCS credentials."""

    gcs_filename: str = "/tmp/.gcs.fused"
    """Filename for saving temporary GCS credentials to locally or in rt2 instance"""

    gcp_project_name: Optional[StrictStr] = None
    """Project name for GCS to use for GCS operations."""

    logging: StrictBool = Field(default=False, validate_default=True)
    """Control logging for Fused"""

    verbose_udf_runs: StrictBool = True
    """Whether to print logs from UDF runs by default"""

    default_run_headers: Optional[Dict[str, str]] = {"X-Fused-Cache-Disable": "true"}
    """(Advanced) Default headers to include with UDF run requests."""

    default_dtype_out_vector: StrictStr = "parquet"
    """Default transfer type for vector (tabular) data"""

    default_dtype_out_raster: StrictStr = "tiff"
    """Default transfer type for raster data"""

    fd_prefix: Optional[str] = None
    """If set, where fd:// scheme URLs will resolve to. By default will infer this from your user account."""

    verbose_cached_functions: StrictBool = True
    """Whether to print logs from cache decorated functions by default"""

    local_engine_cache: StrictBool = True
    """Enable UDF cache with local engine"""

    default_send_status_email: StrictBool = True
    """Whether to send a status email to the user when a job is complete."""

    cache_storage: StorageStr = "auto"
    """Specify the default cache storage type"""

    @model_validator(mode="after")
    def _set_default_directories(self):
        if self.data_directory is None:
            self.data_directory = _data_directory(self.cache_storage)

        return self

    @field_validator("logging")
    @classmethod
    def _validate_logging(cls, v):
        if v:
            logger.enable("fused")
        else:
            logger.disable("fused")

        return v

    @field_serializer("cache_directory")
    def _serialize_cache_directory(self, path: Path, _info) -> str:
        return str(path)

    @field_serializer("temp_directory")
    def _serialize_temp_directory(self, path: Path, _info) -> str:
        return str(path)

    @field_validator("base_url")
    @classmethod
    def _validate_base_url(cls, v):
        reset_api()
        return v

    @field_validator("auth")
    @classmethod
    def _validate_auth(cls, v):
        from fused._auth import AUTHORIZATION

        # reset to trigger re-authentication / loading from disk to ensure setting
        # the options.auth blow has effect
        AUTHORIZATION.reset()

        return v

    @field_validator("data_directory", mode="before")
    @classmethod
    def _validate_data_directory(cls, v, values):
        if values.data["cache_storage"] != "object" and is_path_writable(Path(v)):
            return v
        else:
            return _data_directory(values.data["cache_storage"])

    @property
    def base_web_url(self):
        if self.base_url == STAGING_DEFAULT_BASE_URL:
            return "https://staging.fused.io"

        parts = urlparse(self.base_url)
        return "{scheme}://{netloc}".format(**parts._asdict())

    def _maybe_init_auth(self):
        from fused._auth import AUTHORIZATION

        AUTHORIZATION.is_configured()

    def save(self):
        """Save Fused options to `~/.fused/settings.toml`. They will be automatically
        reloaded the next time fused-py is imported.
        """
        try:
            import rtoml

            OPTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
            # None (null) will not be serialized correctly in toml, so exclude it.
            # Any option which can be None should be None by default. Some open options
            # don't do this; should be updated to not be Optional.
            rtoml.dump(
                self.model_dump(exclude_none=True, exclude_defaults=True), OPTIONS_PATH
            )
        except ImportError:
            warnings.warn(
                FusedImportWarning("rtoml is not installed so options are not saved")
            )

    def _to_toml(self) -> str:
        try:
            import rtoml

            return rtoml.dumps(
                self.model_dump(exclude_none=True, exclude_defaults=True)
            )
        except ImportError:
            warnings.warn(
                FusedImportWarning("rtoml is not installed so options are not saved")
            )

    model_config = ConfigDict(validate_assignment=True)


def _load_options():
    if OPTIONS_PATH.exists():
        try:
            import rtoml

            return Options.model_validate(rtoml.load(OPTIONS_PATH))
        except:  # noqa E722
            warnings.warn(
                FusedIgnoredWarning(
                    f"Settings file {OPTIONS_PATH} exists but could not be loaded."
                )
            )

    if OPTIONS_JSON_PATH.exists():
        try:
            import json

            with open(OPTIONS_JSON_PATH) as json_file:
                return Options.model_validate(json.load(json_file))
        except:  # noqa E722
            warnings.warn(
                FusedIgnoredWarning(
                    f"Settings file {OPTIONS_JSON_PATH} exists but could not be loaded."
                )
            )

    return Options()


options = _load_options()
"""List global configuration options.

This object contains a set of configuration options that control global behavior of the library. This object can be used to modify the options.

Examples:
    Change the `request_timeout` option from its default value to 60 seconds:
    ```py
    fused.options.request_timeout = 60
    ```
"""


def _dev_auth():
    auth = AuthOptions()
    auth.client_id = "K5XfH4xP6PQo6weGVvPYDUiLxGu7GMdb"
    auth.client_secret = (
        "sHh339I8c8bDEPXVMRHMi9rnSrwWtawBHW1588Rm9mqGTc8F5khtvpYOha6Bxk7P"
    )
    auth.audience = "fused-python-api"
    auth.oauth_token_url = "https://fused-dev.us.auth0.com/oauth/token"
    auth.authorize_url = "https://fused-dev.us.auth0.com/authorize"
    auth.credentials_path = "~/.fused/credentials-dev"
    return auth


def env(environment_name: Union[str, int]):
    """Set the environment."""
    if isinstance(environment_name, int) or environment_name.isnumeric():
        _env = DEV_PR_DEFAULT_BASE_URL.format(environment_name)
        options.auth = _dev_auth()
        setattr(options, "base_url", _env)
        return
    else:
        # reset auth options in case we are switching from a dev env
        options.auth = AuthOptions()
        # reload creds
        # Creds are normally loaded at import time, but in this code path, would be possibly re-read again at unpredictable
        # times. Therefore, we reload now instead of later if creds exist.
        options._maybe_init_auth()

    if environment_name == "dev":
        _env = DEV_DEFAULT_BASE_URL
    elif environment_name == "stg" or environment_name == "staging":
        _env = STAGING_DEFAULT_BASE_URL
    elif environment_name == "prod":
        _env = PROD_DEFAULT_BASE_URL
    elif environment_name == "unstable":
        _env = UNSTABLE_DEFAULT_BASE_URL
    else:
        raise ValueError("Available options are `dev`, `stg`, `prod`, and `unstable`.")

    # setting this will cause the global API to be reset
    setattr(options, "base_url", _env)

    # Reset realtime_client_id since it should no longer be correct for a new env.
    setattr(options, "realtime_client_id", None)
