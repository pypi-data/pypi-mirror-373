"""Custom exceptions for SlipperPy."""

from typing import Any, Dict, List, Optional


class SlipperError(Exception):
    """Base exception for all SlipperPy errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NetworkError(SlipperError):
    """Raised when a network-related error occurs."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class GraphQLError(SlipperError):
    """Raised when GraphQL returns errors."""

    def __init__(
        self,
        message: str,
        locations: Optional[List[Dict[str, int]]] = None,
        path: Optional[List[str]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.locations = locations or []
        self.path = path or []
        self.extensions = extensions or {}


class AuthenticationError(SlipperError):
    """Raised when authentication fails."""

    pass


class ValidationError(SlipperError):
    """Raised when input validation fails."""

    pass


class TimeoutError(SlipperError):
    """Raised when a request times out."""

    pass
