from typing import Literal, TypeVar
from enum import StrEnum as _StrEnum


ApiEnv = Literal["prod", "dev", "local", "docker"]
        

class BaseUrl(_StrEnum):
    """The base URL to connect to the API."""

    PROD = "https://api.crypticorn.com"
    DEV = "https://api.crypticorn.dev"
    LOCAL = "http://localhost"
    DOCKER = "http://host.docker.internal"

    @classmethod
    def from_env(cls, env: ApiEnv) -> "BaseUrl":
        """Load the base URL from the API environment."""
        if env == "prod":
            return cls.PROD
        elif env == "dev":
            return cls.DEV
        elif env == "local":
            return cls.LOCAL
        elif env == "docker":
            return cls.DOCKER

_TErrorCodes = TypeVar("_TErrorCodes", bound=str)
"""A type variable for the error codes. It is a string type that is used to define the error codes.
e.g.: ErrorCodes = Literal['unknown_error', 'invalid_data_request', 'invalid_data_response', 'object_already_exists', 'object_not_found']"""
_ERROR_TYPE = Literal["user error", "exchange error", "server error", "no error"]
_ERROR_LEVEL = Literal["error", "info", "success", "warning"]
_EXCEPTION_TYPES = Literal["http", "websocket"]

