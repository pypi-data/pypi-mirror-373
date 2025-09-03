import json
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union
from uuid import uuid4

import aiohttp
from pydantic import BaseModel, ConfigDict, Field

from vector_bridge import AsyncVectorBridgeClient, VectorBridgeClient
from vector_bridge.schema.ai_knowledge import BaseAIKnowledge
from vector_bridge.schema.helpers.enums import (FileAccessType,
                                                FileCheckStatus,
                                                FileSystemError,
                                                FileSystemType, SortOrder)

# CREATES ---


class AIKnowledgeFileSystemItemCreate(BaseAIKnowledge):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    name: str = Field(default=None)
    parent_id: Optional[str] = Field(default=None)
    source_documents_ids: Optional[List[str]] = Field(default_factory=list)
    type: FileSystemType = Field(default=FileSystemType.FILE)
    file_size_bytes: int = Field(default=0)
    starred: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)
    private: bool = Field(default=False)
    users_with_read_access: List[str] = Field(default_factory=list)
    users_with_write_access: List[str] = Field(default_factory=list)
    groups_with_read_access: List[str] = Field(default_factory=list)
    groups_with_write_access: List[str] = Field(default_factory=list)
    created_by: str
    cloud_stored: bool = Field(default=False)
    vectorized: bool = Field(default=True)


class AIKnowledgeFileSystemItemUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    starred: Optional[bool] = None
    tags: Optional[List[str]] = None
    timestamp: Optional[datetime] = None  # datetime.now(timezone.utc)
    archived: Optional[bool] = None

    def to_dict(self):
        _dict = self.model_dump()
        if _dict["timestamp"]:
            _dict["timestamp"] = _dict["timestamp"].isoformat()

        return _dict


# OUTPUTS ---


class AIKnowledgeFileSystemItemChunk(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    item_id: str = Field(default_factory=lambda: str(uuid4()))
    index: int
    content: str

    @property
    def uuid(self):
        return self.item_id


class AIKnowledgeFileSystemItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    item_id: str
    name: str
    chunks: List[AIKnowledgeFileSystemItemChunk] = Field(default_factory=list)
    parent: Optional["AIKnowledgeFileSystemItem"] = Field(default=None)
    source_documents: List["AIKnowledgeFileSystemItem"] = Field(default_factory=list)
    derived_documents: List["AIKnowledgeFileSystemItem"] = Field(default_factory=list)
    parent_id: Optional[str]
    parent_ids_hierarchy: List[str]
    type: FileSystemType
    file_size_bytes: int
    starred: bool
    tags: List[str]
    private: bool
    users_with_read_access: List[str]
    users_with_write_access: List[str]
    groups_with_read_access: List[str]
    groups_with_write_access: List[str]
    unique_identifier: str
    timestamp: str
    created_by: str
    cloud_stored: bool
    vectorized: bool = Field(default=True)
    archived: bool = Field(default=False)

    @property
    def uuid(self):
        return self.item_id

    def delete(self, client: VectorBridgeClient) -> None:
        """Delete this file or folder."""
        client.admin.files.delete_file_or_folder(item_id=self.item_id)

    async def a_delete(self, client: AsyncVectorBridgeClient) -> None:
        """Asynchronously delete this file or folder."""
        await client.admin.files.delete_file_or_folder(item_id=self.item_id)

    def update(
        self,
        client: VectorBridgeClient,
        updated_properties: AIKnowledgeFileSystemItemUpdate,
    ) -> "AIKnowledgeFileSystemItem":
        """Update this file or folder with new properties."""
        return client.admin.files.update_file_or_folder(item_id=self.item_id, updated_properties=updated_properties)

    async def a_update(
        self,
        client: AsyncVectorBridgeClient,
        updated_properties: AIKnowledgeFileSystemItemUpdate,
    ) -> "AIKnowledgeFileSystemItem":
        """Asynchronously update this file or folder with new properties."""
        return await client.admin.files.update_file_or_folder(
            item_id=self.item_id, updated_properties=updated_properties
        )

    def rename(self, client: VectorBridgeClient, new_name: str) -> "AIKnowledgeFileSystemItem":
        """Rename this file or folder."""
        return client.admin.files.rename_file_or_folder(item_id=self.item_id, new_name=new_name)

    async def a_rename(self, client: AsyncVectorBridgeClient, new_name: str) -> "AIKnowledgeFileSystemItem":
        """Asynchronously rename this file or folder."""
        return await client.admin.files.rename_file_or_folder(item_id=self.item_id, new_name=new_name)

    def refresh(self, client: VectorBridgeClient) -> "AIKnowledgeFileSystemItem":
        """Refresh this file or folder's data from the server."""
        updated_item = client.admin.files.get_file_or_folder(item_id=self.item_id)
        return updated_item if updated_item else self

    async def a_refresh(self, client: AsyncVectorBridgeClient) -> "AIKnowledgeFileSystemItem":
        """Asynchronously refresh this file or folder's data from the server."""
        updated_item = await client.admin.files.get_file_or_folder(item_id=self.item_id)
        return updated_item if updated_item else self

    def get_download_link(self, client: VectorBridgeClient, expiration_seconds: int = 60) -> str:
        """Get a download link for this file (only works for files, not folders)."""
        return client.admin.files.get_download_link_for_document(
            item_id=self.item_id, expiration_seconds=expiration_seconds
        )

    async def a_get_download_link(self, client: AsyncVectorBridgeClient, expiration_seconds: int = 60) -> str:
        """Asynchronously get a download link for this file (only works for files, not folders)."""
        return await client.admin.files.get_download_link_for_document(
            item_id=self.item_id, expiration_seconds=expiration_seconds
        )

    def get_path(self, client: VectorBridgeClient) -> List["AIKnowledgeFileSystemItem"]:
        """Get the full path to this file or folder as a list of items."""
        return client.admin.files.get_file_or_folder_path(item_id=self.item_id)

    async def a_get_path(self, client: AsyncVectorBridgeClient) -> List["AIKnowledgeFileSystemItem"]:
        """Asynchronously get the full path to this file or folder as a list of items."""
        return await client.admin.files.get_file_or_folder_path(item_id=self.item_id)

    def grant_user_access(
        self,
        client: VectorBridgeClient,
        user_id: str,
        has_access: bool,
        access_type: FileAccessType = None,
    ) -> Union[None, "AIKnowledgeFileSystemItem"]:
        """Grant or revoke user access to this file or folder."""
        # Import here to avoid circular imports
        from vector_bridge.schema.helpers.enums import FileAccessType

        if access_type is None:
            access_type = FileAccessType.READ

        return client.admin.files.grant_or_revoke_user_access(
            item_id=self.item_id,
            user_id=user_id,
            has_access=has_access,
            access_type=access_type,
        )

    async def a_grant_user_access(
        self,
        client: AsyncVectorBridgeClient,
        user_id: str,
        has_access: bool,
        access_type: FileAccessType = None,
    ) -> Union[None, "AIKnowledgeFileSystemItem"]:
        """Asynchronously grant or revoke user access to this file or folder."""
        # Import here to avoid circular imports
        from vector_bridge.schema.helpers.enums import FileAccessType

        if access_type is None:
            access_type = FileAccessType.READ

        return await client.admin.files.grant_or_revoke_user_access(
            item_id=self.item_id,
            user_id=user_id,
            has_access=has_access,
            access_type=access_type,
        )

    def grant_security_group_access(
        self,
        client: VectorBridgeClient,
        group_id: str,
        has_access: bool,
        access_type: FileAccessType = None,
    ) -> Union[None, "AIKnowledgeFileSystemItem"]:
        """Grant or revoke security group access to this file or folder."""
        # Import here to avoid circular imports
        from vector_bridge.schema.helpers.enums import FileAccessType

        if access_type is None:
            access_type = FileAccessType.READ

        return client.admin.files.grant_or_revoke_security_group_access(
            item_id=self.item_id,
            group_id=group_id,
            has_access=has_access,
            access_type=access_type,
        )

    async def a_grant_security_group_access(
        self,
        client: AsyncVectorBridgeClient,
        group_id: str,
        has_access: bool,
        access_type: FileAccessType = None,
    ) -> Union[None, "AIKnowledgeFileSystemItem"]:
        """Asynchronously grant or revoke security group access to this file or folder."""
        # Import here to avoid circular imports
        if access_type is None:
            access_type = FileAccessType.READ

        return await client.admin.files.grant_or_revoke_security_group_access(
            item_id=self.item_id,
            group_id=group_id,
            has_access=has_access,
            access_type=access_type,
        )


AIKnowledgeFileSystemItem.model_rebuild()


class AIKnowledgeFileSystemItemsList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[AIKnowledgeFileSystemItem]
    limit: Union[int, None] = Field(default=None)
    offset: Union[int, None] = Field(default=None)
    has_more: bool = Field(default=False)


class AIKnowledgeFileSystemFilters(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    file_name_like: str = Field(default=None)
    file_name_equal: str = Field(default=None)
    item_id: str = Field(default=None)
    parent_id: str = Field(default=None)
    parent_id_is_null: bool = Field(default=None)
    parent_ids_hierarchy_contains_any: List[str] = Field(default=None)
    source_documents_ids_contains_any: List[str] = Field(default=None)
    source_documents_ids_contains_all: List[str] = Field(default=None)
    type: FileSystemType = Field(default=None)
    is_starred: bool = Field(default=None)
    tags_contains_any: List[str] = Field(default=None)
    tags_contains_all: List[str] = Field(default=None)
    is_private: bool = Field(default=None)
    users_with_read_access_contains_any: List[str] = Field(default=None)
    users_with_read_access_contains_all: List[str] = Field(default=None)
    users_with_write_access_contains_any: List[str] = Field(default=None)
    users_with_write_access_contains_all: List[str] = Field(default=None)
    groups_with_read_access_contains_any: List[str] = Field(default=None)
    groups_with_read_access_contains_all: List[str] = Field(default=None)
    groups_with_write_access_contains_any: List[str] = Field(default=None)
    groups_with_write_access_contains_all: List[str] = Field(default=None)
    unique_identifier: str = Field(default="")
    file_size_bytes_min: int = Field(default=None)
    file_size_bytes_max: int = Field(default=None)
    timestamp_after: str = Field(default="")
    timestamp_before: str = Field(default="")
    is_cloud_stored: bool = Field(default=None)
    is_vectorized: bool = Field(default=None)
    is_archived: bool = Field(default=None)
    limit: int = Field(default=100)
    offset: int = Field(default=None)
    sort_by: str = Field(default="timestamp")
    sort_order: SortOrder = Field(default=SortOrder.DESCENDING)

    def to_non_empty_dict(self):
        _dict = self.model_dump()
        return {k: v for k, v in _dict.items() if v is not None and v != ""}

    def to_serializable_non_empty_dict(self):
        _dict = self.model_dump()
        if self.sort_order:
            _dict["sort_order"] = self.sort_order.value
        if self.type:
            _dict["type"] = self.type.value
        return {k: v for k, v in _dict.items() if v is not None and v != ""}


class FileSystemItemArchivedCount(BaseModel):
    files: int
    archived_files: int


class FileSystemItemCount(BaseModel):
    files: int
    folders: int


class FileSystemItemAggregatedCount(BaseModel):
    items: Dict[str, FileSystemItemCount]


class StreamingResponse:
    """
    Handles streaming response from file upload with real-time progress tracking and final result.

    This class provides:
    - progress_updates: an iterator yielding progress values as they arrive in real-time
    - checks: list of checks performed during processing
    - issues: list of issues found during processing
    - item: the final complete AIKnowledgeFileSystemItem (waits for completion if needed)
    """

    def __init__(self, response):
        self._response = response
        self._progress_updates = []
        self._checks_buffer = ""
        self._file_buffer = ""
        self._result = None
        self._fully_consumed = False
        self._raw_file_data = None
        self._lines_iterator = None
        self._in_section = None  # Tracks current section: 'checks', 'progress', or 'file'

    @property
    def progress_updates(self) -> Iterator[float]:
        """
        Iterator over progress values that streams in real-time.

        Yields:
            Progress values (0.0 to 1.0) as they arrive from the API.
        """
        # Initialize the lines iterator if needed
        if self._lines_iterator is None:
            self._lines_iterator = self._response.iter_lines()

        # Process the stream line by line, yielding progress updates as they arrive
        try:
            while not self._fully_consumed:
                progress = self._process_next_line()
                if progress is not None:
                    self._progress_updates.append(progress)
                    yield progress
        except StopIteration:
            self._fully_consumed = True

    @property
    def checks(self) -> List[str]:
        """Get the list of checks performed during processing."""
        self._ensure_fully_consumed()
        return self._parse_checks()

    @property
    def issues(self) -> List[str]:
        """Get the list of issues found during processing."""
        self._ensure_fully_consumed()
        return self._parse_issues()

    @property
    def item(self) -> Any:
        """
        Get the final AIKnowledgeFileSystemItem, waiting for completion if necessary.

        Returns:
            The final AIKnowledgeFileSystemItem object
        """
        self._ensure_fully_consumed()
        return self._result

    @property
    def raw_file_data(self) -> Optional[Dict[str, Any]]:
        """Get the raw file data as a dictionary."""
        self._ensure_fully_consumed()
        return self._raw_file_data

    def _ensure_fully_consumed(self):
        """Ensure the stream is fully consumed."""
        if not self._fully_consumed:
            # Consume all remaining lines
            for _ in self.progress_updates:
                pass

    def _process_next_line(self):
        """
        Process the next line from the response stream.

        Returns:
            Float progress value if a progress update was found, None otherwise
        """
        if self._fully_consumed:
            return None

        try:
            line = next(self._lines_iterator)
            if not line:
                return None

            decoded_line = line.decode("utf-8").strip()

            # Handle section markers
            if decoded_line == "<checks>":
                self._in_section = "checks"
                self._checks_buffer = ""
                return None
            elif decoded_line == "</checks>":
                self._in_section = None
                return None
            elif decoded_line == "<progress>":
                self._in_section = "progress"
                return None
            elif decoded_line == "</progress>":
                self._in_section = None
                return None
            elif decoded_line == "<file>":
                self._in_section = "file"
                self._file_buffer = ""
                return None
            elif decoded_line == "</file>":
                self._in_section = None
                self._parse_file(self._file_buffer)
                self._fully_consumed = True
                return None

            # Process content based on current section
            if self._in_section == "checks":
                self._checks_buffer += decoded_line + "\n"
                return None
            elif self._in_section == "progress":
                try:
                    # Try to parse the line as a progress value
                    progress = float(decoded_line)
                    return progress
                except ValueError:
                    return None
            elif self._in_section == "file":
                self._file_buffer += decoded_line + "\n"
                return None

        except StopIteration:
            self._fully_consumed = True
            raise

        return None

    def _parse_checks(self):
        """Parse checks from buffer."""
        checks = []
        for line in self._checks_buffer.strip().split("\n"):
            line = line.strip()
            if line.startswith("checking:"):
                checks.append(line[9:].strip())
        return checks

    def _parse_issues(self):
        """Parse issues from buffer."""
        issues = []
        for line in self._checks_buffer.strip().split("\n"):
            line = line.strip()
            if line.startswith(">> Error:"):
                issues.append(line[9:].strip())
        return issues

    def _parse_file(self, buffer: str):
        """Parse final file data from buffer."""
        try:
            self._raw_file_data = json.loads(buffer.strip())
            # Convert to AIKnowledgeFileSystemItem if the class is available
            try:
                self._result = AIKnowledgeFileSystemItem.model_validate(self._raw_file_data)
            except (NameError, AttributeError):
                # If AIKnowledgeFileSystemItem is not available, just return the raw data
                self._result = self._raw_file_data
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse file JSON: {buffer}")


class AsyncStreamingResponse:
    """
    Handles async streaming response from file upload with real-time progress tracking and final result.

    This class provides:
    - progress_updates: an async iterator yielding progress values as they arrive in real-time
    - checks: list of checks performed during processing
    - issues: list of issues found during processing
    - item: the final complete AIKnowledgeFileSystemItem (waits for completion if needed)
    """

    def __init__(self, response: aiohttp.ClientResponse):
        self._response = response
        self._progress_updates = []
        self._checks_buffer = ""
        self._file_buffer = ""
        self._result = None
        self._fully_consumed = False
        self._raw_file_data = None
        self._lines_iterator = None
        self._in_section = None  # Tracks current section: 'checks', 'progress', or 'file'

    @property
    async def progress_updates(self) -> AsyncIterator[float]:
        """
        Async iterator over progress values that streams in real-time.

        Yields:
            Progress values (0.0 to 1.0) as they arrive from the API.
        """
        # Initialize the lines iterator if needed
        if self._lines_iterator is None:
            self._lines_iterator = self._response.content

        # Process the stream line by line, yielding progress updates as they arrive
        try:
            async for line in self._lines_iterator:
                if self._fully_consumed:
                    break

                progress = await self._process_line(line)
                if progress is not None:
                    self._progress_updates.append(progress)
                    yield progress
        except Exception:
            self._fully_consumed = True
            raise

    async def get_progress_updates(self) -> AsyncIterator[float]:
        """
        Alternative method name for accessing progress updates.

        Yields:
            Progress values (0.0 to 1.0) as they arrive from the API.
        """
        async for progress in self.progress_updates:
            yield progress

    @property
    async def checks(self) -> List[FileCheckStatus]:
        """Get the list of checks performed during processing."""
        await self._ensure_fully_consumed()
        return self._parse_checks()

    @property
    async def issues(self) -> List[FileSystemError]:
        """Get the list of issues found during processing."""
        await self._ensure_fully_consumed()
        return self._parse_issues()

    @property
    async def item(self) -> Any:
        """
        Get the final AIKnowledgeFileSystemItem, waiting for completion if necessary.

        Returns:
            The final AIKnowledgeFileSystemItem object
        """
        await self._ensure_fully_consumed()
        return self._result

    @property
    async def raw_file_data(self) -> Optional[Dict[str, Any]]:
        """Get the raw file data as a dictionary."""
        await self._ensure_fully_consumed()
        return self._raw_file_data

    async def _ensure_fully_consumed(self):
        """Ensure the stream is fully consumed."""
        if not self._fully_consumed:
            # Consume all remaining lines
            async for _ in self.progress_updates:
                pass

    async def _process_line(self, line: bytes) -> Optional[float]:
        """
        Process a line from the response stream.

        Args:
            line: Raw bytes line from the stream

        Returns:
            Float progress value if a progress update was found, None otherwise
        """
        if self._fully_consumed:
            return None

        try:
            if not line:
                return None

            decoded_line = line.decode("utf-8").strip()

            # Handle section markers
            if decoded_line == "<checks>":
                self._in_section = "checks"
                self._checks_buffer = ""
                return None
            elif decoded_line == "</checks>":
                self._in_section = None
                return None
            elif decoded_line == "<progress>":
                self._in_section = "progress"
                return None
            elif decoded_line == "</progress>":
                self._in_section = None
                return None
            elif decoded_line == "<file>":
                self._in_section = "file"
                self._file_buffer = ""
                return None
            elif decoded_line == "</file>":
                self._in_section = None
                await self._parse_file(self._file_buffer)
                self._fully_consumed = True
                return None

            # Process content based on current section
            if self._in_section == "checks":
                self._checks_buffer += decoded_line + "\n"
                return None
            elif self._in_section == "progress":
                try:
                    # Try to parse the line as a progress value
                    progress = float(decoded_line)
                    return progress
                except ValueError:
                    return None
            elif self._in_section == "file":
                self._file_buffer += decoded_line + "\n"
                return None

        except UnicodeDecodeError:
            # Skip lines that can't be decoded
            return None

        return None

    def _parse_checks(self) -> List[FileCheckStatus]:
        """Parse checks from buffer."""
        checks = []
        for line in self._checks_buffer.strip().split("\n"):
            line = line.strip()
            if line.startswith("checking:"):
                checks.append(FileCheckStatus(line[9:].strip()))
        return checks

    def _parse_issues(self) -> List[FileSystemError]:
        """Parse issues from buffer."""
        issues = []
        for line in self._checks_buffer.strip().split("\n"):
            line = line.strip()
            if line.startswith(">> Error:"):
                issues.append(FileSystemError(line[9:].strip()))
        return issues

    async def _parse_file(self, buffer: str):
        """Parse final file data from buffer."""
        try:
            self._raw_file_data = json.loads(buffer.strip())
            # Convert to AIKnowledgeFileSystemItem if the class is available
            try:
                self._result = AIKnowledgeFileSystemItem.model_validate(self._raw_file_data)
            except (NameError, AttributeError):
                # If AIKnowledgeFileSystemItem is not available, just return the raw data
                self._result = self._raw_file_data
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse file JSON: {buffer}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if not self._response.closed:
            self._response.close()

    # Convenience methods for easier usage
    async def get_checks(self) -> List[str]:
        """Get the list of checks performed during processing."""
        return await self.checks

    async def get_issues(self) -> List[str]:
        """Get the list of issues found during processing."""
        return await self.issues

    async def get_item(self) -> Any:
        """Get the final AIKnowledgeFileSystemItem."""
        return await self.item

    async def get_raw_file_data(self) -> Optional[Dict[str, Any]]:
        """Get the raw file data as a dictionary."""
        return await self.raw_file_data
