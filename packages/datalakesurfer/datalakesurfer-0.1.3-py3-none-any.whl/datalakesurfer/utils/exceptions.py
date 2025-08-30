from typing import Any, Dict, Optional


class DataLakeSurferError(Exception):
    """
    Base class for all custom exceptions in DataLakeSurfer.

    Attributes:
        message: Human readable message (required).
        cause: Optional original exception.
        details: Optional structured details.
        code: Optional machine code to classify errors.
    """
    def __init__(
        self,
        message: str,
        *,
        cause: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.details = details or {}
        self.code = code

    def __str__(self) -> str:
        return self.message if not self.cause else f"{self.message} (cause: {self.cause})"

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable dict suitable for returning to callers/APIs."""
        payload: Dict[str, Any] = {"status": "error", "message": self.message}
        if self.code:
            payload["code"] = self.code
        if self.details:
            payload["details"] = self.details
        if self.cause:
            # keep cause as string to avoid serializing nested exceptions
            payload["cause"] = str(self.cause)
        return payload


# Specific exception types (use these to be explicit about failures)
class FormatDetectionError(DataLakeSurferError):
    """Raised when format detection fails unexpectedly."""


class SchemaRetrievalError(DataLakeSurferError):
    """Raised when retrieving schema fails."""


class PartitionDetectionError(DataLakeSurferError):
    """Raised when partition detection fails."""


class CredentialError(DataLakeSurferError):
    """Raised for credential/authorization issues."""


class FileSystemError(DataLakeSurferError):
    """Raised when filesystem operations fail (fsspec / adlfs / pyarrow)."""


class UnsupportedFormatError(DataLakeSurferError):
    """Raised when a format is unsupported by the library."""


class NotFoundError(DataLakeSurferError):
    """Raised when a resource (path / container) is not found."""


class ExternalDependencyError(DataLakeSurferError):
    """Raised when an external library or service returns an unexpected error."""


class ConfigurationError(DataLakeSurferError):
    """Raised for invalid configuration/state inside the library."""

def to_error_response(exc: Exception) -> Dict[str, Any]:
    """
    Convert an exception into a standardized error dict.
    - If it's a DataLakeSurferError, use its `to_dict()`.
    - Otherwise return a minimal error `{"status":"error","message": str(exc)}`.

    Use this inside top-level except handlers or where you need to maintain the
    library's existing return-style (dicts with status/message).
    """
    if isinstance(exc, DataLakeSurferError):
        return exc.to_dict()
    return {"status": "error", "message": str(exc)}
