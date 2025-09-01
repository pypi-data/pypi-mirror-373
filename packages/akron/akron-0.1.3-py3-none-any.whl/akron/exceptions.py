"""Custom exceptions for akron."""

class AkronError(Exception):
    """Base exception for Akron."""


class UnsupportedDriverError(AkronError):
    """Raised when user requests an unsupported DB driver."""


class TableNotFoundError(AkronError):
    """Raised when table does not exist."""


class SchemaError(AkronError):
    """Raised when user schema is invalid or incompatible."""
