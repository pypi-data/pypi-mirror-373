"""Exception classes for novus-pytils package."""


# Base exception classes
class FileHandlerError(Exception):
    """Base exception for file handler operations."""
    pass


class UnsupportedFormatError(FileHandlerError):
    """Exception raised when attempting to work with unsupported file formats."""
    pass


class ConversionError(FileHandlerError):
    """Exception raised when file conversion fails."""
    pass


class ValidationError(FileHandlerError):
    """Exception raised when file validation fails."""
    pass


class SecurityError(FileHandlerError):
    """Exception raised when security checks fail."""
    pass


class WAVError(Exception):
    """Base exception for WAV parsing errors."""
    pass


class InvalidWAVFormatError(WAVError):
    """Raised when WAV file format is invalid or unsupported."""
    pass


class CorruptedFileError(WAVError):
    """Raised when WAV file appears to be corrupted."""
    pass