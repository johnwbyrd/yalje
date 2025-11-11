"""Custom exception classes for yalje."""


class YaljeError(Exception):
    """Base exception for all yalje errors."""

    pass


class AuthenticationError(YaljeError):
    """Raised when authentication fails."""

    pass


class SessionExpiredError(AuthenticationError):
    """Raised when session cookies have expired."""

    pass


class APIError(YaljeError):
    """Raised when API requests fail."""

    pass


class ParsingError(YaljeError):
    """Raised when parsing responses fails."""

    pass


class ExportError(YaljeError):
    """Raised when export operations fail."""

    pass


class ConfigurationError(YaljeError):
    """Raised when configuration is invalid."""

    pass


class ValidationError(YaljeError):
    """Raised when data validation fails."""

    pass
