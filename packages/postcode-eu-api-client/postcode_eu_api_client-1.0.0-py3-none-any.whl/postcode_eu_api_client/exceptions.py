"""Exception classes for the Postcode.eu API client."""


class PostcodeEuException(Exception):
    """Base exception for all Postcode.eu API client exceptions."""
    pass


class AuthenticationException(PostcodeEuException):
    """Authentication failed with the API."""
    pass


class BadRequestException(PostcodeEuException):
    """Bad request sent to the API."""
    pass


class CurlException(PostcodeEuException):
    """HTTP request error (equivalent to cURL error in PHP)."""
    pass


class CurlNotLoadedException(PostcodeEuException):
    """HTTP library not available (equivalent to cURL not loaded in PHP)."""
    pass


class ForbiddenException(PostcodeEuException):
    """Access forbidden by the API."""
    pass


class InvalidJsonResponseException(PostcodeEuException):
    """Invalid JSON response received from the API."""
    pass


class InvalidPostcodeException(PostcodeEuException):
    """Invalid postcode format provided."""
    pass


class InvalidSessionValueException(PostcodeEuException):
    """Invalid session value provided."""
    pass


class NotFoundException(PostcodeEuException):
    """Resource not found."""
    pass


class ServerUnavailableException(PostcodeEuException):
    """API server is unavailable."""
    pass


class TooManyRequestsException(PostcodeEuException):
    """Too many requests sent to the API."""
    pass


class UnexpectedException(PostcodeEuException):
    """Unexpected response from the API."""
    pass
