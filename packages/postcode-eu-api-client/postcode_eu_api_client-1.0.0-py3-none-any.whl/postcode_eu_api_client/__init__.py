"""Postcode.eu API client for Python."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version('postcode-eu-api-client')
except importlib.metadata.PackageNotFoundError:
    # Fallback for development installs or when package isn't installed
    __version__ = 'unknown'

from .client import Client
from .exceptions import (
    PostcodeEuException,
    AuthenticationException,
    BadRequestException,
    CurlException,
    CurlNotLoadedException,
    ForbiddenException,
    InvalidJsonResponseException,
    InvalidPostcodeException,
    InvalidSessionValueException,
    NotFoundException,
    ServerUnavailableException,
    TooManyRequestsException,
    UnexpectedException,
)

__all__ = [
    'Client',
    'PostcodeEuException',
    'AuthenticationException',
    'BadRequestException',
    'CurlException',
    'CurlNotLoadedException',
    'ForbiddenException',
    'InvalidJsonResponseException',
    'InvalidPostcodeException',
    'InvalidSessionValueException',
    'NotFoundException',
    'ServerUnavailableException',
    'TooManyRequestsException',
    'UnexpectedException',
]
