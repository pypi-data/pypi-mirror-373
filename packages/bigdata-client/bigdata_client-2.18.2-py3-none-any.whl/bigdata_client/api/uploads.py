import datetime
from typing import Annotated, Iterable, Literal, Optional, Protocol, Union

from pydantic import BaseModel, Field, model_validator

from bigdata_client.daterange import AbsoluteDateRange
from bigdata_client.enum_utils import StrEnum
from bigdata_client.models.sharing import SharePermission


class FileStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DELETED = "DELETED"


class FileIndexedStatus(StrEnum):
    INDEXING_FAILED = "INDEXING_FAILED"
    ANALYZE_FAILED = "ANALYZE_FAILED"
    INDEXED = "INDEXED"
    ANALYZING = "ANALYZING"


class FileResponse(BaseModel):
    """Model to represent a single upload in the ListFilesResponse"""

    id: str = Field(alias="file_id")
    name: str = Field(alias="file_name")
    status: FileStatus
    uploaded_at: datetime.datetime = Field(alias="upload_ts")
    raw_size: int
    folder_id: Optional[str] = None
    tags: Optional[list[str]] = None
    company_shared_permission: Optional[SharePermission] = None

    @model_validator(mode="before")
    @classmethod
    def set_company_shared_permission(cls, values: dict):
        if values.get("shared_with"):
            values["company_shared_permission"] = (
                SharePermission.READ
            )  # We only share with own organization
        return values

    @model_validator(mode="after")
    def set_tz(self):
        self.uploaded_at = self.uploaded_at.replace(tzinfo=datetime.timezone.utc)

        return self


class ListFilesResponse(BaseModel):
    """Model to represent the response of the list uploads endpoint"""

    results: list[FileResponse]


class ExtractorTypes(StrEnum):
    PDF_EXTRACTOR_1_0 = "PDF_EXTRACTOR_1_0"


class PostFileRequest(BaseModel):
    """Model to represent the request of the post upload endpoint"""

    filename: str
    folder_id: Optional[str] = None
    source_url: Optional[str] = None
    upload_mode: Optional[str] = None
    properties: Optional[dict] = None
    connect_to: list[Literal["smart_topics"]] = ["smart_topics"]
    extractor: Optional[ExtractorTypes] = None


class PostFileResponse(BaseModel):
    """Model to represent the response of the post upload endpoint"""

    file_id: str
    location: str = Field(alias="Location")


class GetFileStatusResponse(BaseModel):
    status: Optional[
        Annotated[Union[FileStatus, str], Field(union_mode="left_to_right")]
    ] = None
    error: Optional[str] = None


class GetFileIndexStatusResponse(BaseModel):
    status: Optional[
        Annotated[
            Union[FileIndexedStatus, FileStatus, str], Field(union_mode="left_to_right")
        ]
    ] = None
    error: Optional[str] = None


class DeleteFileResponse(BaseModel):
    message: str


class GetDownloadPresignedUrlResponse(BaseModel):
    url: str


class UploadsConnectionProtocol(Protocol):
    def list_files(
        self,
        date_range: Optional[AbsoluteDateRange],
        tags: Optional[list[str]],
        status: Optional[FileStatus],
        file_name: Optional[str],
        folder_id: Optional[str],
        page_size: int,
        shared: Optional[bool],
        offset: int,
    ) -> ListFilesResponse: ...

    def get_file(self, id: str) -> FileResponse: ...

    def post_file(self, request: PostFileRequest) -> PostFileResponse: ...

    def get_file_status(self, file_id: str) -> GetFileStatusResponse: ...

    def get_file_index_status(self, file_id: str) -> GetFileIndexStatusResponse: ...

    def delete_file(self, id: str) -> DeleteFileResponse: ...

    def get_download_presigned_url(
        self, id: str
    ) -> GetDownloadPresignedUrlResponse: ...

    def download_analytics(self, id: str) -> Iterable[bytes]: ...

    def download_annotated(self, id: str) -> Iterable[bytes]: ...

    def download_text(self, id: str) -> Iterable[bytes]: ...

    def share_file_with_company(self, file_id: str) -> FileResponse: ...

    def unshare_file_with_company(self, file_id: str) -> FileResponse: ...

    def update_file_tags(self, file_id: str, tags: list[str]) -> FileResponse: ...


class FileShareResponse(BaseModel):
    status: Literal["OK"]
    message: str
