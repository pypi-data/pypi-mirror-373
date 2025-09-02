import json
import time
from dataclasses import field
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional, Union

import requests
from pydantic import BaseModel, Field

from bigdata_client.api.uploads import (
    FileIndexedStatus,
    FileStatus,
    UploadsConnectionProtocol,
)
from bigdata_client.connection import get_chunks_from_presigned_url
from bigdata_client.exceptions import BigdataClientIncompatibleStateError
from bigdata_client.models.sharing import SharePermission

CHUNK_SIZE = 32 * 1024
TIMEOUT_WAITING_FOR_COMPLETION = 40 * 60  # 40 minutes


class File(BaseModel):
    """
    Representation of a file.
    """

    _uploads_api: UploadsConnectionProtocol
    id: str
    name: Optional[str] = None
    status: Optional[Union[FileStatus, str]] = None
    uploaded_at: Optional[datetime] = None
    raw_size: Optional[int] = None
    folder_id: Optional[str] = None
    tags: list[str] = field(default_factory=lambda: [])
    company_shared_permission: Optional[SharePermission] = None
    _indexing_status: Optional[
        Annotated[
            Union[FileIndexedStatus, FileStatus, str], Field(union_mode="left_to_right")
        ]
    ] = None

    def __init__(self, **data):
        super().__init__(**data)
        if "_uploads_api" in data:
            self._uploads_api = data["_uploads_api"]

    def delete(self):
        """
        Deletes the file from the server.
        The file must be fully processed before deleting.
        """
        try:
            self._uploads_api.delete_file(self.id)
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.TOO_EARLY:
                raise BigdataClientIncompatibleStateError(
                    "File is being processed and cannot be deleted yet."
                )
            raise

    def reload_status(self):
        """Updates the status of the file."""
        status_response = self._uploads_api.get_file_status(self.id)
        if status_response.error:
            raise ValueError(status_response.error)
        self.status = status_response.status

    def wait_for_analysis_completed(
        self, timeout: int = TIMEOUT_WAITING_FOR_COMPLETION
    ):
        """Waits for the file to be completed."""
        completed_status = [FileStatus.COMPLETED, FileStatus.DELETED, FileStatus.FAILED]
        time_elapsed = 0
        delta = 1
        while self.status not in completed_status:
            time.sleep(delta)
            time_elapsed += delta
            self.reload_status()
            if time_elapsed >= timeout:
                raise TimeoutError(
                    "Timeout waiting for file to be uploaded and processed"
                )

    def wait_for_completion(self, timeout: int = TIMEOUT_WAITING_FOR_COMPLETION):
        completed_status = [
            FileStatus.DELETED,
            FileStatus.FAILED,
            FileStatus.COMPLETED,
            FileIndexedStatus.INDEXED,
            FileIndexedStatus.INDEXING_FAILED,
            FileIndexedStatus.ANALYZE_FAILED,
        ]
        time_elapsed = 0
        delta = 1
        while self._indexing_status not in completed_status:
            time.sleep(delta)
            time_elapsed += delta
            self.reset_indexing_status()
            if time_elapsed >= timeout:
                raise TimeoutError(
                    "Timeout waiting for file to be uploaded, processed and indexed"
                )

    def reset_indexing_status(self) -> Union[FileIndexedStatus, FileStatus]:
        """Reset the indexing status of the file"""
        self._indexing_status = self._uploads_api.get_file_index_status(self.id).status

        return self._indexing_status

    def download_original(self, filename: str):
        """Downloads the original content of the file."""
        # GET /file/<id> returns the URL to S3, not the content
        # Other types of files can be downloaded directly
        response = self._uploads_api.get_download_presigned_url(self.id)
        content = get_chunks_from_presigned_url(response.url)
        with open(filename, "wb") as f:
            for chunk in content:
                f.write(chunk)

    def download_analytics(self, filename: str):
        """Downloads the analytics in the file."""
        content = self._uploads_api.download_analytics(self.id)
        with open(filename, "wb") as f:
            for chunk in content:
                f.write(chunk)

    def get_analytics_dict(self):
        """Retrieves the analytics in the file, as a dictionary."""
        content_chunks = self._uploads_api.download_analytics(self.id)
        content = b"".join(content_chunks)
        return json.loads(content)

    def download_annotated(self, filename: str):
        """Downloads the annotated version of the file."""
        content = self._uploads_api.download_annotated(self.id)
        with open(filename, "wb") as f:
            for chunk in content:
                f.write(chunk)

    def get_annotated_dict(self):
        """Retrieves the annotated version of the file, as a dictionary."""
        content_chunks = self._uploads_api.download_annotated(self.id)
        content = b"".join(content_chunks)
        return json.loads(content)

    def share_with_company(self):
        """
        Shares a file with the whole company.
        """
        try:
            response = self._uploads_api.share_file_with_company(file_id=self.id)
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.TOO_EARLY:
                raise BigdataClientIncompatibleStateError(
                    "File is being processed and cannot be shared yet."
                )
            raise
        self.company_shared_permission = SharePermission.READ
        return response.model_dump()

    def unshare_with_company(self):
        """
        Stops sharing a file with the whole company.
        """
        try:
            response = self._uploads_api.unshare_file_with_company(file_id=self.id)
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.TOO_EARLY:
                raise BigdataClientIncompatibleStateError(
                    "File is being processed and cannot be unshared yet."
                )
            raise
        self.company_shared_permission = None
        return response.model_dump()

    def add_tags(self, value: list[str]) -> dict:
        """Add tags to a file.

        Args:
            value (list[str]): Tags to be added.

        Returns:
            dict: File information.

        Raises:
            ValueError: If 'value' parameter is not a list.
            ValueError: If 'value' parameter is empty.
        """
        self._validate_tags_value(value)
        file_response = self._uploads_api.get_file(id=self.id)
        updated_tags = set(file_response.tags or [])
        updated_tags.update(value)

        try:
            response = self._uploads_api.update_file_tags(
                file_id=self.id, tags=sorted(updated_tags)
            )
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.TOO_EARLY:
                raise BigdataClientIncompatibleStateError(
                    "File is being processed and its tags cannot be modified yet."
                )
            raise
        self.tags = response.tags or []
        return response.model_dump()

    def remove_tags(self, value: list[str]) -> dict:
        """Remove tags to a file.

        Args:
            value (list[str]): Tags to be removed.

        Returns:
            dict: File information.

        Raises:
            ValueError: If 'value' parameter is not a list.
            ValueError: If 'value' parameter is empty.
        """
        self._validate_tags_value(value)
        file_response = self._uploads_api.get_file(id=self.id)
        updated_tags = set(file_response.tags or [])
        updated_tags.difference_update(value)

        try:
            response = self._uploads_api.update_file_tags(
                file_id=self.id, tags=sorted(updated_tags)
            )
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.TOO_EARLY:
                raise BigdataClientIncompatibleStateError(
                    "File is being processed and its tags cannot be modified yet."
                )
            raise
        self.tags = response.tags or []
        return response.model_dump()

    def set_tags(self, value: list[str]) -> dict:
        """Remove tags to a file.

        Args:
            value (list[str]): Tags to be removed.

        Returns:
            dict: File information.

        Raises:
            ValueError: If 'value' parameter is not a list.
            ValueError: If 'value' parameter is empty.
        """
        self._validate_tags_value(value)
        try:
            response = self._uploads_api.update_file_tags(
                file_id=self.id, tags=sorted(set(value))
            )
        except requests.HTTPError as e:
            if e.response.status_code == HTTPStatus.TOO_EARLY:
                raise BigdataClientIncompatibleStateError(
                    "File is being processed and its tags cannot be modified yet."
                )
            raise
        self.tags = response.tags or []
        return response.model_dump()

    def _validate_tags_value(self, value: list[str]):
        if not isinstance(value, list):
            raise ValueError("'value' must be a list.")
        if not value:
            raise ValueError("'value' cannot be empty.")
        filtered_tag_list = [tag for tag in value if tag]
        if not filtered_tag_list:
            raise ValueError("'value' cannot be composed of empty values.")

    def _download_text(self, filename: str):
        """
        Downloads the text extraction of the file.
        Marked as private to not cause confusion to the user
        """
        content = self._uploads_api.download_text(self.id)
        with open(filename, "wb") as f:
            for chunk in content:
                f.write(chunk)

    def __str__(self):
        """Returns a string representation of the file with the ls -l format."""
        file_id = self.id or "FILE NOT UPLOADED               "
        size = (
            padded(human_readable_size(self.raw_size), 4) if self.raw_size else " N/A"
        )

        date = (
            human_readable_date(self.uploaded_at) if self.uploaded_at else "        N/A"
        )

        name = self.name if self.name else "N/A"
        return f"{file_id} {size} {date} {name}"


def human_readable_size(num_bytes: int) -> str:
    """
    Returns a human readable string of the given size in bytes.

    It displays the size in the highest unit possible

    >>> human_readable_size(1)
    '1'
    >>> human_readable_size(32)
    '32'
    >>> human_readable_size(512 * 1024)
    '512K'
    >>> human_readable_size(3 * 1024 * 1024)
    '3M'
    >>> human_readable_size(1024 * 1024 * 1024)
    '1G'

    It only shows the decimal part for units between 1 and 9.9, and only if they are not 0:

    >>> human_readable_size(1.1 * 1024)
    '1.1K'
    >>> human_readable_size(2.1 * 1024)
    '2.1K'
    >>> human_readable_size(9.9 * 1024)
    '9.9K'
    >>> human_readable_size(10.01 * 1024)
    '10K'
    >>> human_readable_size(52.5 * 1024)
    '52K'
    >>> human_readable_size(0.9 * 1024 * 1024)
    '921K'

    Finally, it rounds the number to the nearest integer

    >>> human_readable_size(1000)
    '1K'
    >>> human_readable_size(1023)
    '1K'
    >>> human_readable_size(1024 * 1024 - 1)
    '1M'
    """
    size = float(num_bytes)
    for unit in ["", "K", "M", "G", "T", "P", "E"]:
        # 1000 instead of 1024 to get things like 1M instead of 1001K
        if size < 1000:
            ssize = f"{size:.1f}" if size < 10 else f"{int(size)}"
            # Remove leading zeros
            if ssize[-2:] == ".0":
                ssize = ssize[:-2]
            return f"{ssize}{unit}"
        size /= 1024
    return f"{int(size)}Z"


def human_readable_date(date: datetime) -> str:
    """Returns a human readable date of the given date."""
    month = date.strftime("%b")
    day = date.strftime("%d")
    if day[0] == "0":
        day = f" {day[1:]}"
    year = date.strftime("%Y")
    return f"{month} {day} {year}"


def padded(value: str, length: int) -> str:
    """Returns a string with the given value padded to the right."""
    return f"{value:>{length}}"


class UploadQuotaFiles(BaseModel):
    available: int
    error: int
    total: int


class UploadQuotaUsage(BaseModel):
    max_units_allowed: int
    storage_bytes_used: int
    units_remaining: int
    units_used: int


class UploadQuotaSubscriptionUsage(BaseModel):
    current_month: UploadQuotaUsage
    subscription: UploadQuotaUsage


class UploadQuota(BaseModel):
    files: UploadQuotaFiles
    quota: UploadQuotaSubscriptionUsage
