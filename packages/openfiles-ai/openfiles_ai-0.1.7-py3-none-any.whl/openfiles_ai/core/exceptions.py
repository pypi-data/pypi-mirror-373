"""
Exceptions for OpenFiles SDK
"""

from typing import Any, Dict, Optional


class OpenFilesError(Exception):
    """Base exception class for OpenFiles SDK"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message


class APIKeyError(OpenFilesError):
    """Exception raised for API key related errors"""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message)


class NetworkError(OpenFilesError):
    """Exception raised for network related errors"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code:
            return f"{self.message} (HTTP {self.status_code})"
        return self.message


class ValidationError(OpenFilesError):
    """Exception raised for request validation errors"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field

    def __str__(self) -> str:
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class FileNotFoundError(OpenFilesError):
    """Exception raised when a requested file is not found"""

    def __init__(self, path: str):
        super().__init__(f"File not found: {path}")
        self.path = path


class FileOperationError(OpenFilesError):
    """Exception raised for file operation errors"""

    def __init__(self, operation: str, path: str, message: str):
        super().__init__(f"Failed to {operation} file '{path}': {message}")
        self.operation = operation
        self.path = path


class RateLimitError(OpenFilesError):
    """Exception raised when API rate limit is exceeded"""

    def __init__(self, retry_after: Optional[int] = None):
        message = "API rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)
        self.retry_after = retry_after


class AuthenticationError(OpenFilesError):
    """Exception raised for authentication failures"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)
