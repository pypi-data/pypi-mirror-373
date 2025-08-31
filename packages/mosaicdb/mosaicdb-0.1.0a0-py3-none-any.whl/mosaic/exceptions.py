"""Custom exceptions for mosaic."""

class MosaicError(Exception):
    """Base exception for mosaic."""


class UnsupportedDriverError(MosaicError):
    """Raised when user requests an unsupported DB driver."""


class TableNotFoundError(MosaicError):
    """Raised when table does not exist."""


class SchemaError(MosaicError):
    """Raised when user schema is invalid or incompatible."""
