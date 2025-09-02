"""
OpenFiles Core Client - Direct API access

Provides type-safe access to the OpenFiles API with automatic
authentication, error handling, and response validation.
"""

from typing import Any, Optional, Union

import httpx

from ..utils.logger import get_logger
from ..utils.path import resolve_path
from .exceptions import (
    APIKeyError,
    AuthenticationError,
    FileNotFoundError,
    FileOperationError,
    NetworkError,
    RateLimitError,
    ValidationError,
)
from .generated.models import (
    AppendFileRequest,
    ContentType,
    EditFileRequest,
    FileContentResponse,
    FileListResponse,
    FileMetadata,
    FileMetadataResponse,
    FileVersionsResponse,
    OverwriteFileRequest,
    WriteFileRequest,
)

logger = get_logger(__name__)


class OpenFilesClient:
    """Direct API client for OpenFiles platform"""

    DEFAULT_BASE_URL = "https://api.openfiles.ai/functions/v1/api"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        base_path: Optional[str] = None,
    ):
        """
        Initialize OpenFiles client

        Args:
            api_key: OpenFiles API key (must start with 'oa_')
            base_url: API base URL (defaults to production)
            timeout: Request timeout in seconds
            base_path: Base path prefix for all operations

        Raises:
            APIKeyError: If API key format is invalid
        """
        if not api_key:
            raise APIKeyError("API key is required")
        
        if not api_key.startswith('oa_') or len(api_key) < 35:
            raise APIKeyError("Invalid API key format. API key must start with 'oa_' and be at least 35 characters long")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.base_path = base_path

        # Setup HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "openfiles-python-sdk/0.1.0",
            },
            timeout=self.timeout,
        )

        logger.debug(f"OpenFiles client initialized with base_url={self.base_url}")

    def with_base_path(self, base_path: str) -> "OpenFilesClient":
        """
        Create a new OpenFilesClient instance with a base path prefix
        All file operations will automatically prefix paths with the base path
        
        Args:
            base_path: The base path to prefix to all operations
            
        Returns:
            New OpenFilesClient instance with the specified base path
            
        Example:
            >>> client = OpenFilesClient(api_key="oa_...", base_url="...")
            >>> reports_client = client.with_base_path("reports")
            >>> await reports_client.write_file("sales.csv", data)  # Creates "reports/sales.csv"
        """
        # Combine base paths
        enhanced_base_path = base_path
        if self.base_path:
            enhanced_base_path = f"{self.base_path}/{base_path}".replace("//", "/").rstrip("/")
        
        return OpenFilesClient(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            base_path=enhanced_base_path
        )

    async def write_file(
        self,
        path: str,
        content: str,
        content_type: Union[str, ContentType] = ContentType.text_plain,
        is_base64: bool = False,
        base_path: Optional[str] = None,
    ) -> FileMetadata:
        """
        Write a new file or create new version

        Args:
            path: File path (S3-style, no leading slash)
            content: File content
            content_type: MIME type of the content
            is_base64: Whether content is base64 encoded
            base_path: Base path prefix for this operation

        Returns:
            File metadata for the created/updated file

        Raises:
            ValidationError: If request validation fails
            FileOperationError: If file operation fails
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        # Convert content_type to ContentType enum if it's a string
        if isinstance(content_type, str):
            try:
                content_type = ContentType(content_type)
            except ValueError:
                content_type = ContentType.text_plain

        request = WriteFileRequest(
            path=resolved_path, content=content, contentType=content_type, isBase64=is_base64
        )

        try:
            response = await self._client.post(
                "/files", json=request.model_dump(by_alias=True, mode="json")
            )
            await self._handle_response_errors(response, "write_file", resolved_path)

            response_data = response.json()
            return FileMetadata(**response_data["data"])

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during write_file: {str(e)}") from e

    async def read_file(
        self, path: str, version: Optional[int] = None, base_path: Optional[str] = None
    ) -> FileContentResponse:
        """
        Read file content

        Args:
            path: File path (S3-style, no leading slash)
            version: Specific version to read (optional)
            base_path: Base path prefix for this operation

        Returns:
            File content response with metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        params = {}
        if version is not None:
            params["version"] = str(version)

        try:
            response = await self._client.get(f"/files/{resolved_path}", params=params)
            await self._handle_response_errors(response, "read_file", resolved_path)

            response_data = response.json()
            return FileContentResponse(**response_data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during read_file: {str(e)}") from e

    async def edit_file(
        self, path: str, old_string: str, new_string: str, base_path: Optional[str] = None
    ) -> FileMetadata:
        """
        Edit file with find and replace

        Args:
            path: File path (S3-style, no leading slash)
            old_string: Exact string to find and replace
            new_string: Replacement string
            base_path: Base path prefix for this operation

        Returns:
            Updated file metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            FileOperationError: If edit operation fails
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        request = EditFileRequest(oldString=old_string, newString=new_string)

        try:
            response = await self._client.put(
                f"/files/edit/{resolved_path}", json=request.model_dump(by_alias=True, mode="json")
            )
            await self._handle_response_errors(response, "edit_file", resolved_path)

            response_data = response.json()
            return FileMetadata(**response_data["data"])

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during edit_file: {str(e)}") from e

    async def list_files(
        self, directory: str = "", recursive: bool = False, limit: int = 10, offset: int = 0, base_path: Optional[str] = None
    ) -> FileListResponse:
        """
        List files in directory

        Args:
            directory: Directory path to list files from
            recursive: If True, lists all files across all directories. If False (default), only lists files in the specified directory
            limit: Maximum number of files to return
            offset: Number of files to skip
            base_path: Base path prefix for this operation

        Returns:
            File list response with metadata

        Raises:
            NetworkError: If network request fails
        """
        resolved_dir = resolve_path(directory, base_path or self.base_path)
        if not resolved_dir:
            resolved_dir = ""

        params = {"directory": resolved_dir, "limit": str(limit), "offset": str(offset)}
        if recursive:
            params["recursive"] = "true"

        try:
            response = await self._client.get("/files", params=params)
            await self._handle_response_errors(response, "list_files", resolved_dir)

            response_data = response.json()
            return FileListResponse(**response_data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during list_files: {str(e)}") from e

    async def append_file(
        self, path: str, content: str, base_path: Optional[str] = None
    ) -> FileMetadata:
        """
        Append content to existing file

        Args:
            path: File path (S3-style, no leading slash)
            content: Content to append
            base_path: Base path prefix for this operation

        Returns:
            Updated file metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        request = AppendFileRequest(content=content)

        try:
            response = await self._client.put(
                f"/files/append/{resolved_path}",
                json=request.model_dump(by_alias=True, mode="json"),
            )
            await self._handle_response_errors(response, "append_file", resolved_path)

            response_data = response.json()
            return FileMetadata(**response_data["data"])

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during append_file: {str(e)}") from e

    async def overwrite_file(
        self, path: str, content: str, is_base64: bool = False, base_path: Optional[str] = None
    ) -> FileMetadata:
        """
        Overwrite entire file content

        Args:
            path: File path (S3-style, no leading slash)
            content: New content to replace existing content
            is_base64: Whether content is base64 encoded
            base_path: Base path prefix for this operation

        Returns:
            Updated file metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        request = OverwriteFileRequest(content=content, isBase64=is_base64)

        try:
            response = await self._client.put(
                f"/files/overwrite/{resolved_path}",
                json=request.model_dump(by_alias=True, mode="json"),
            )
            await self._handle_response_errors(response, "overwrite_file", resolved_path)

            response_data = response.json()
            return FileMetadata(**response_data["data"])

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during overwrite_file: {str(e)}") from e

    async def get_metadata(
        self, path: str, version: Optional[int] = None, base_path: Optional[str] = None
    ) -> FileMetadataResponse:
        """
        Get file metadata without content

        Args:
            path: File path (S3-style, no leading slash)
            version: Specific version to get metadata for
            base_path: Base path prefix for this operation

        Returns:
            File metadata response

        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        params = {"metadata": "true"}
        if version is not None:
            params["version"] = str(version)

        try:
            response = await self._client.get(f"/files/{resolved_path}", params=params)
            await self._handle_response_errors(response, "get_metadata", resolved_path)

            response_data = response.json()
            return FileMetadataResponse(**response_data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during get_metadata: {str(e)}") from e

    async def get_versions(
        self, path: str, limit: int = 10, offset: int = 0, base_path: Optional[str] = None
    ) -> FileVersionsResponse:
        """
        Get file version history

        Args:
            path: File path (S3-style, no leading slash)
            limit: Maximum number of versions to return
            offset: Number of versions to skip
            base_path: Base path prefix for this operation

        Returns:
            File versions response

        Raises:
            FileNotFoundError: If file doesn't exist
            NetworkError: If network request fails
        """
        resolved_path = resolve_path(path, base_path or self.base_path)

        params = {"versions": "true", "limit": str(limit), "offset": str(offset)}

        try:
            response = await self._client.get(f"/files/{resolved_path}", params=params)
            await self._handle_response_errors(response, "get_versions", resolved_path)

            response_data = response.json()
            return FileVersionsResponse(**response_data)

        except httpx.RequestError as e:
            raise NetworkError(f"Network error during get_versions: {str(e)}") from e

    async def _handle_response_errors(
        self, response: httpx.Response, operation: str, path: str
    ) -> None:
        """Handle HTTP response errors and raise appropriate exceptions"""
        if response.status_code == 200:
            return

        if response.status_code == 401:
            raise AuthenticationError("Authentication failed - check your API key")
        elif response.status_code == 404:
            raise FileNotFoundError(path)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            raise RateLimitError(retry_seconds)
        elif 400 <= response.status_code < 500:
            try:
                error_data = response.json()
                if "error" in error_data:
                    error_message = error_data["error"].get("message", "Unknown error")
                else:
                    error_message = f"Client error: {response.status_code}"
                raise ValidationError(error_message)
            except Exception:
                raise ValidationError(f"Client error: {response.status_code}") from None
        elif response.status_code >= 500:
            raise FileOperationError(operation, path, f"Server error: {response.status_code}")
        else:
            raise NetworkError(f"Unexpected response: {response.status_code}", response.status_code)

    async def close(self) -> None:
        """Close the HTTP client"""
        await self._client.aclose()

    async def __aenter__(self) -> "OpenFilesClient":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit"""
        await self.close()
