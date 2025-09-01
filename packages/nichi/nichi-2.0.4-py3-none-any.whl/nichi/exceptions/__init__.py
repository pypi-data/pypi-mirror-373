"""Custom exceptions for the Video File Organizer application."""

from typing import Optional


class VideoOrganizerError(Exception):
    """Base exception for the Video File Organizer application."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.cause = cause


class FileProcessingError(VideoOrganizerError):
    """Raised when there's an error processing files."""

    def __init__(self, message: str, filepath: Optional[str] = None):
        super().__init__(message)
        self.filepath = filepath


class TranslationError(VideoOrganizerError):
    """Raised when there's an error during translation."""

    def __init__(self, message: str, language_code: Optional[str] = None):
        super().__init__(message)
        self.language_code = language_code


class ConfigurationError(VideoOrganizerError):
    """Raised when there's a configuration error."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
