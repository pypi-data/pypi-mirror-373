import logging
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Optional,
    TypeAlias,
    Union,
    cast,
)
from crypticorn_utils.types import _TErrorCodes, _ERROR_TYPE, _ERROR_LEVEL, _EXCEPTION_TYPES
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import HTTPException as FastAPIHTTPException
from fastapi import Request, WebSocketException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

_logger = logging.getLogger("crypticorn")

def get_exception_response(error_codes: TypeAlias) -> dict[str, dict[str, Any]]:
    """The default schema if an error is returned.
    ```python
    ErrorCodes = Literal['unknown_error', 'invalid_data_request']
    app = FastAPI(responses={**get_exception_response(ErrorCodes)})
    ```
    """
    # Note: this constructs a very ugly OpenAPI schema name for the ExceptionDetail model due to the generic type.
    # something like this: ExceptionDetailLiteralUnknownErrorInvalidDataRequestInvalidDataResponseObjectAlreadyExistsObjectNotFound...
    # Since the error codes may be extended by the server implementation, the schema name will even change.
    # Clients are advised not to use this class directly. Instead get the properties from the raw response.
    # >>> try:
    # >>>     response = requests.get(url)
    # >>>     response.json()['default']['model']
    # >>> except Exception as e:
    # >>>     # This will contain the ExceptionDetail model with the error codes as JSON
    # >>>     # instead of validating it against the schema, we can just print the error code like this:
    # >>>     print(e.get('code'))

    # This issue is tracked in Pydantic:
    # - https://docs.pydantic.dev/1.10/usage/schema/#schema-customization
    # - https://github.com/pydantic/pydantic/issues/6304
    # - https://github.com/pydantic/pydantic/issues/7376

    return {
        "default": {
            "model": _ExceptionDetail[error_codes],
            "description": "Error response",
        }
    }


class _ExceptionDetail(BaseModel, Generic[_TErrorCodes]):
    """Exception details returned to the client."""

    message: Optional[str] = Field(None, description="An additional error message")
    code: _TErrorCodes = Field(..., description="The unique error code")
    type: _ERROR_TYPE = Field(..., description="The type of error")
    level: _ERROR_LEVEL = Field(..., description="The level of the error")
    status_code: int = Field(..., description="The HTTP status code")
    details: Any = Field(None, description="Additional details about the error")

    class Config:
        title = "ExceptionDetail"


@dataclass(frozen=True)
class BaseError(Generic[_TErrorCodes]):
    """Base API error class defining the error details.

    ```python
    class Errors:
        UNKNOWN_ERROR = BaseError[ErrorCodes](
            identifier='unknown_error',
            type="server error",
            level="error",
            http_code=500,
            websocket_code=1011,
        )
    ```
    """

    identifier: _TErrorCodes
    type: _ERROR_TYPE
    level: _ERROR_LEVEL
    http_code: int
    websocket_code: int

    # Class variable to store all instances
    _instances: ClassVar[dict[str, "BaseError"]] = {}

    def __post_init__(self):
        # Register this instance
        self._instances[str(self.identifier)] = self

    @classmethod
    def from_identifier(cls, identifier: _TErrorCodes) -> "BaseError[_TErrorCodes]":
        """Get an error instance by its identifier."""
        if str(identifier) not in cls._instances:
            raise ValueError(f"Unknown error identifier: {identifier}")
        return cls._instances[str(identifier)]

    @classmethod
    def get_all_instances(cls) -> dict[str, "BaseError[_TErrorCodes]"]:
        """Get all registered error instances."""
        return cls._instances.copy()


class ExceptionHandler(Generic[_TErrorCodes]):
    """This class is used to handle errors and exceptions. It is used to build exceptions and raise them.

    - Register the exception handlers to the FastAPI app.
    - Configure the instance with a callback to get the error object from the error identifier.
    - Build exceptions from error codes defined in the client code.

    Example for the client code implementation:

    ```python
    from crypticorn_utils import ExceptionHandler, BaseError
    from typing import Literal

    # Define error codes as a Literal type
    ErrorCodes = Literal[
        'unknown_error',
        'invalid_data_request',
        'invalid_data_response',
        'object_already_exists',
        'object_not_found'
    ]

    # Define errors as instances of BaseError
    class Errors:
        UNKNOWN_ERROR = BaseError[ErrorCodes](
            identifier='unknown_error',
            type="server error",
            level="error",
            http_code=500,
            websocket_code=1011,
        )
        INVALID_DATA_REQUEST = BaseError[ErrorCodes](
            identifier='invalid_data_request',
            type="user error",
            level="error",
            http_code=422,
            websocket_code=1007,
        )
        INVALID_DATA_RESPONSE = BaseError[ErrorCodes](
            identifier='invalid_data_response',
            type="server error",
            level="error",
            http_code=422,
            websocket_code=1007,
        )
        OBJECT_ALREADY_EXISTS = BaseError[ErrorCodes](
            identifier='object_already_exists',
            type="user error",
            level="error",
            http_code=409,
            websocket_code=1008,
        )
        OBJECT_NOT_FOUND = BaseError[ErrorCodes](
            identifier='object_not_found',
            type="user error",
            level="error",
            http_code=404,
            websocket_code=1008,
        )

    handler = ExceptionHandler[ErrorCodes](callback=BaseError.from_identifier)
    handler.register_exception_handlers(app)

    @app.get("/")
    def get_root():
        raise handler.build_exception('object_not_found')
    ```
    """

    def __init__(
        self,
        callback: Callable[[_TErrorCodes], BaseError[_TErrorCodes]],
    ):
        """
        :param callback: The callback to use to get the error object from the error identifier.
        """
        self.callback = callback

    def _http_exception(
        self,
        content: _ExceptionDetail[_TErrorCodes],
        headers: Optional[dict[str, str]] = None,
    ) -> HTTPException:
        return HTTPException(
            detail=content.model_dump(mode="json"),
            headers=headers,
            status_code=content.status_code,
        )

    def _websocket_exception(
        self, content: _ExceptionDetail[_TErrorCodes]
    ) -> WebSocketException:
        return WebSocketException(
            reason=content.model_dump(mode="json"),
            code=content.status_code,
        )

    def build_exception(
        self,
        code: _TErrorCodes,
        *,
        message: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        details: Any = None,
        type: _EXCEPTION_TYPES = "http",
    ) -> Union[HTTPException, WebSocketException]:
        """Build an exception, without raising it.
        :param code: The error code to raise.
        :param message: The message to include in the error.
        :param headers: The headers to include in the error.
        :param details: The details to include in the error.
        :param type: The type of exception to raise. Defaults to HTTP.

        :return: The exception to raise, either an HTTPException or a WebSocketException.

        ```python
        @app.get("/")
        def get_root():
            raise handler.build_exception('object_not_found')
        ```
        """
        error = self.callback(code)
        content = _ExceptionDetail[_TErrorCodes](
            message=message,
            code=error.identifier,
            type=error.type,
            level=error.level,
            status_code=error.http_code,
            details=details,
        )
        if type == "http":
            return self._http_exception(content, headers)
        elif type == "websocket":
            return self._websocket_exception(content)

    async def _general_handler(self, request: Request, exc: Exception) -> JSONResponse:
        """Default exception handler for all exceptions."""
        body = _ExceptionDetail[_TErrorCodes](
            message=str(exc),
            code=cast(_TErrorCodes, "unknown_error"),
            type="server error",
            level="error",
            status_code=500,
        )
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"General error: {str(exc)}")
        return res

    async def _request_validation_handler(
        self, request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Exception handler for all request validation errors."""
        body = _ExceptionDetail[_TErrorCodes](
            message=str(exc),
            code=cast(_TErrorCodes, "invalid_data_request"),
            type="user error",
            level="error",
            status_code=400,
        )
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Request validation error: {str(exc)}")
        return res

    async def _response_validation_handler(
        self, request: Request, exc: ResponseValidationError
    ) -> JSONResponse:
        """Exception handler for all response validation errors."""
        body = _ExceptionDetail[_TErrorCodes](
            message=str(exc),
            code=cast(_TErrorCodes, "invalid_data_response"),
            type="user error",
            level="error",
            status_code=400,
        )
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Response validation error: {str(exc)}")
        return res

    async def _http_handler(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Exception handler for HTTPExceptions. It unwraps the HTTPException and returns the detail in a flat JSON response."""
        res = JSONResponse(
            status_code=exc.status_code, content=exc.detail, headers=exc.headers
        )
        _logger.error(f"HTTP error: {str(exc)}")
        return res

    def register_exception_handlers(self, app: FastAPI) -> None:
        """Utility to register serveral exception handlers in one go. Catches Exception, HTTPException and Data Validation errors, logs them and responds with a unified json body.

        ```python
        handler.register_exception_handlers(app)
        ```
        """
        app.add_exception_handler(Exception, self._general_handler)
        app.add_exception_handler(FastAPIHTTPException, self._http_handler)
        app.add_exception_handler(
            RequestValidationError, self._request_validation_handler
        )
        app.add_exception_handler(
            ResponseValidationError, self._response_validation_handler
        )
