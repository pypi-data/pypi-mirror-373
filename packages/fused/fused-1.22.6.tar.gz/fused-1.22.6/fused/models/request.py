from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator
from pydantic_core import PydanticCustomError

from .urls import DatasetUrl

# Note that instance types above 4xlarge are undocumented publicly
WHITELISTED_INSTANCE_TYPES_values = [
    "m5.large",
    "m5.xlarge",
    "m5.2xlarge",
    "m5.4xlarge",
    "m5.8xlarge",
    "m5.12xlarge",
    "m5.16xlarge",
    "r5.large",
    "r5.xlarge",
    "r5.2xlarge",
    "r5.4xlarge",
    "r5.8xlarge",
    "r5.12xlarge",
    "r5.16xlarge",
    "t3.small",
    "t3.medium",
    "t3.large",
    "t3.xlarge",
    "t3.2xlarge",
    "c2-standard-4",
    "c2-standard-8",
    "c2-standard-16",
    "c2-standard-30",
    "c2-standard-60",
    "agent",
]
# replace the below duplicated list with the unpacking once we drop Python 3.10 support
# WHITELISTED_INSTANCE_TYPES = Literal[*WHITELISTED_INSTANCE_TYPES_values]
WHITELISTED_INSTANCE_TYPES = Literal[
    "m5.large",
    "m5.xlarge",
    "m5.2xlarge",
    "m5.4xlarge",
    "m5.8xlarge",
    "m5.12xlarge",
    "m5.16xlarge",
    "r5.large",
    "r5.xlarge",
    "r5.2xlarge",
    "r5.4xlarge",
    "r5.8xlarge",
    "r5.12xlarge",
    "r5.16xlarge",
    "t3.small",
    "t3.medium",
    "t3.large",
    "t3.xlarge",
    "t3.2xlarge",
    "c2-standard-4",
    "c2-standard-8",
    "c2-standard-16",
    "c2-standard-30",
    "c2-standard-60",
    "agent",
]


class GetTableBboxRequest(BaseModel):
    path: str
    bbox_minx: float
    bbox_miny: float
    bbox_maxx: float
    bbox_maxy: float

    n_rows: Optional[int] = None
    clip: bool = True
    columns: Optional[List[str]] = None
    buffer: Optional[float] = None
    model_config = ConfigDict(populate_by_name=True)


class StartJobRequest(BaseModel):
    region: Optional[StrictStr] = None
    instance_type: Optional[WHITELISTED_INSTANCE_TYPES] = None
    disk_size_gb: Optional[StrictInt] = None
    additional_env: Optional[List[StrictStr]] = Field(default_factory=list)
    backend: Optional[StrictStr] = None


class ListJobsRequest(BaseModel):
    skip: Optional[StrictInt] = None
    limit: Optional[StrictInt] = None


class JobIncrementProgressRequest(BaseModel):
    amount: StrictInt


class UdfType(str, Enum):
    auto = "auto"
    vector_tile = "vector_tile"
    vector_single = "vector_single"
    vector_single_none = "vector_single_none"
    raster = "raster"
    raster_single = "raster_single"
    app = "app"


class SaveUdfRequest(BaseModel):
    slug: Optional[str] = None
    udf_body: str
    udf_type: UdfType
    allow_public_read: Optional[bool] = None
    allow_public_list: Optional[bool] = None


class ListUdfsRequest(BaseModel):
    skip: Optional[StrictInt] = None
    limit: Optional[StrictInt] = None
    udf_type: Optional[str] = None


class GetPathRequest(BaseModel):
    path: DatasetUrl


class GetEfsFileRequest(BaseModel):
    file_name: str


class SignPathRequest(BaseModel):
    path: DatasetUrl


class ListPathRequest(BaseModel):
    path: DatasetUrl

    # TODO: Maybe add full support of /mount besides file:///mount, instead of an error
    @field_validator("path", mode="before")
    @classmethod
    def validate_path_format(cls, value: Any) -> Any:
        if isinstance(value, str) and value.startswith("/mount"):
            raise PydanticCustomError(
                "invalid_path_format",
                'Path "{path}" needs a URL scheme. For /mount paths, use "file://{path}" instead.',
                {"path": value},
            )
        return value


class DeletePathRequest(BaseModel):
    path: DatasetUrl
    max_deletion_depth: Union[Optional[int], Literal["unlimited"]]


class ResolvePathRequest(BaseModel):
    path: DatasetUrl


class UploadRequest(BaseModel):
    path: DatasetUrl


class UploadTempRequest(BaseModel):
    extension: Optional[str] = None


class SignUploadRequest(BaseModel):
    content_length: int
    path: DatasetUrl


class SignUploadTempRequest(BaseModel):
    content_length: int
    extension: Optional[str] = None


class ListUdfAccessTokensRequest(BaseModel):
    skip: Optional[StrictInt] = None
    limit: Optional[StrictInt] = None


class CreateUdfAccessTokenRequest(BaseModel):
    udf_email: Optional[str] = None
    udf_slug: Optional[str] = None
    udf_id: Optional[str] = None
    client_id: Optional[str] = None
    public_read: Optional[bool] = None
    access_scope: Optional[str] = None
    cache: bool = True
    metadata_json: Dict[str, Any] = {}
    enabled: bool = True


class UpdateUdfAccessTokenRequest(BaseModel):
    client_id: Optional[str] = None
    cache: Optional[bool] = None
    public_read: Optional[bool] = None
    access_scope: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class UpdateSecretRequest(BaseModel):
    value: str
