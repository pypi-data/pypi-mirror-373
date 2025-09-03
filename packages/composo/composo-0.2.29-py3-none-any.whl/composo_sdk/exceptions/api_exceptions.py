"""
Custom exceptions for Composo SDK
"""

from typing import Optional


class ComposoError(Exception):
    """Base exception for all Composo SDK errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class RateLimitError(ComposoError):
    """Raised when API rate limits are exceeded (429)"""

    pass


class MalformedError(ComposoError):
    """Raised when request data is malformed (422)"""

    pass


class APIError(ComposoError):
    """Raised for general API errors (500)"""

    pass


class AuthenticationError(ComposoError):
    """Raised when authentication fails (401)"""

    pass


class TimeoutError(ComposoError):
    """Raised when request times out (408)"""

    pass


class BadRequestError(ComposoError):
    """Raised when request is malformed or invalid (400)"""

    pass


def get_exception_for_status_code(
    status_code: int, message: str = "", response_body: Optional[str] = None
) -> ComposoError:
    """Factory function to create appropriate exceptions based on HTTP status codes"""

    exception_map = {
        400: BadRequestError,
        401: AuthenticationError,
        408: TimeoutError,
        422: MalformedError,
        429: RateLimitError,
        500: APIError,
    }

    exception_class = exception_map.get(status_code, ComposoError)
    return exception_class(message, status_code, response_body)
