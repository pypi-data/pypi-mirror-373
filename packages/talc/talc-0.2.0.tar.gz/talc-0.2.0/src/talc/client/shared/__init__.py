# This is used by both the CLI and the server; do not reference modules outside of this package.

import datetime
from typing import Literal, NewType, Optional, TypeAlias, Union

from pydantic import BaseModel, ConfigDict

#
#   File Uploads
#

UploadedFileId = NewType("UploadedFileId", str)
FileUploadRequestId = NewType("FileUploadRequestId", str)
ExecutionPlanId = NewType("ExecutionPlanId", str)


class UploadInitRequest(BaseModel):
    file_name: str
    file_size_bytes: int
    file_sha256: str


class UploadInitResult_Cached(BaseModel):
    uploaded_file_id: UploadedFileId


class UploadInitResult_New(BaseModel):
    class UploadPart(BaseModel):
        part_number: int
        byte_range: tuple[int, int]
        upload_url: str

    file_upload_request_id: FileUploadRequestId
    upload_parts: list[UploadPart]


UploadInitResult: TypeAlias = Union[
    UploadInitResult_Cached,
    UploadInitResult_New,
]


class UploadFinishRequest(BaseModel):
    class UploadPart(BaseModel):
        part_number: int
        response_headers: dict[str, str]

    file_upload_request_id: FileUploadRequestId
    parts: list[UploadPart]


class UploadFinishResult(BaseModel):
    uploaded_file_id: UploadedFileId


#
#   Extraction Jobs
#

ExtractionJobId = NewType("ExtractionJobId", str)


class StartExtractionJobRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    scenario: object
    data: UploadedFileId


class StartExtractionJobResult(BaseModel):
    job_id: ExtractionJobId


class GetExtractionJobResult(BaseModel):
    job_id: ExtractionJobId
    last_heartbeat_timestamp: datetime.datetime
    start_timestamp: datetime.datetime
    end_timestamp: Optional[datetime.datetime]
    status: Literal["running", "completed", "abandoned", "failed"]
    failure_reason: Optional[str]


class GetExtractionJobOutputRequest(BaseModel):
    job_id: ExtractionJobId
    format: Literal["json"]


#
#   Execution Plans
#


class ExecutionPlanUploadRequest(BaseModel):
    plan_typescript: str


class ExecutionPlanUploadResult(BaseModel):
    plan_id: ExecutionPlanId
