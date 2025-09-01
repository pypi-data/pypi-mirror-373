import json
from typing import Literal, Union

from crypticorn.auth import AuthClient, Configuration, Verify200Response
from crypticorn.auth.client.exceptions import ApiException
from crypticorn_utils.types import BaseUrl
from crypticorn_utils.exceptions import (
    BaseError,
    ExceptionHandler,
)
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    SecurityScopes,
)
from typing_extensions import Annotated

_AUTH_ERROR_CODES = Literal[
    "invalid_api_key",
    "expired_api_key",
    "invalid_bearer",
    "expired_bearer",
    "invalid_basic_auth",
    "no_credentials",
    "insufficient_scopes",
    "unknown_error",
]


class _AuthError:
    INVALID_API_KEY = BaseError[_AUTH_ERROR_CODES](
        "invalid_api_key",
        "user error",
        "error",
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    INVALID_BASIC_AUTH = BaseError[_AUTH_ERROR_CODES](
        "invalid_basic_auth",
        "user error",
        "error",
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    INVALID_BEARER = BaseError[_AUTH_ERROR_CODES](
        "invalid_bearer",
        "user error",
        "error",
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    EXPIRED_API_KEY = BaseError[_AUTH_ERROR_CODES](
        "expired_api_key",
        "user error",
        "error",
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    EXPIRED_BEARER = BaseError[_AUTH_ERROR_CODES](
        "expired_bearer",
        "user error",
        "error",
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    NO_CREDENTIALS = BaseError[_AUTH_ERROR_CODES](
        "no_credentials",
        "user error",
        "error",
        status.HTTP_401_UNAUTHORIZED,
        status.WS_1008_POLICY_VIOLATION,
    )
    INSUFFICIENT_SCOPES = BaseError[_AUTH_ERROR_CODES](
        "insufficient_scopes",
        "user error",
        "error",
        status.HTTP_403_FORBIDDEN,
        status.WS_1008_POLICY_VIOLATION,
    )
    UNKNOWN_ERROR = BaseError[_AUTH_ERROR_CODES](
        "unknown_error",
        "server error",
        "error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        status.WS_1011_INTERNAL_ERROR,
    )


_handler = ExceptionHandler[_AUTH_ERROR_CODES](callback=BaseError.from_identifier)

_AUTHENTICATE_HEADER = "WWW-Authenticate"
_BEARER_AUTH_SCHEME = "Bearer"
_APIKEY_AUTH_SCHEME = "X-API-Key"
_BASIC_AUTH_SCHEME = "Basic"

# Auth Schemes
_http_bearer = HTTPBearer(
    bearerFormat="JWT",
    auto_error=False,
    description="The JWT to use for authentication.",
)

_apikey_header = APIKeyHeader(
    name=_APIKEY_AUTH_SCHEME,
    auto_error=False,
    description="The API key to use for authentication.",
)

_http_basic = HTTPBasic(
    scheme_name=_BASIC_AUTH_SCHEME,
    auto_error=False,
    description="The username and password to use for authentication.",
)


# Auth Handler
class AuthHandler:
    """
    Middleware for verifying API requests. Verifies the validity of the authentication token, scopes, etc.

    :param base_url: The base URL of the API.
    :param api_version: The version of the API.
    """

    def __init__(
        self,
        base_url: BaseUrl = BaseUrl.PROD,
    ):
        self.url = f"{base_url}/v1/auth"
        self.client = AuthClient(Configuration(host=self.url), is_sync=False)

    async def _verify_api_key(self, api_key: str) -> Verify200Response:
        """
        Verifies the API key.
        """
        self.client.config.api_key = {"APIKeyHeader": api_key}
        return await self.client.login.verify()

    async def _verify_bearer(
        self, bearer: HTTPAuthorizationCredentials
    ) -> Verify200Response:
        """
        Verifies the bearer token.
        """
        self.client.config.access_token = bearer.credentials
        return await self.client.login.verify()

    async def _verify_basic(self, basic: HTTPBasicCredentials) -> Verify200Response:
        """
        Verifies the basic authentication credentials.
        """
        return await self.client.login.verify_basic_auth(basic.username, basic.password)

    async def _validate_scopes(
        self, api_scopes: list[str], user_scopes: list[str]
    ) -> None:
        """
        Checks if the required scopes are a subset of the user scopes.
        """
        if not set(api_scopes).issubset(user_scopes):
            raise _handler.build_exception(
                "insufficient_scopes",
                message="Insufficient scopes to access this resource (required: "
                + ", ".join(api_scopes)
                + ")",
            )

    async def _extract_message(self, e: ApiException) -> str:
        """
        Tries to extract the message from the body of the exception.
        """
        try:
            load = json.loads(e.body)
        except (json.JSONDecodeError, TypeError):
            return e.body
        else:
            common_keys = ["message"]
            for key in common_keys:
                if key in load:
                    return load[key]
            return load

    async def _handle_exception(self, e: Exception) -> HTTPException:
        """
        Handles exceptions and returns a HTTPException with the appropriate status code and detail.
        """
        if isinstance(e, ApiException):
            # handle the TRPC Zod errors from auth-service
            # Unfortunately, we cannot share the error messages defined in python/crypticorn/common/errors.py with the typescript client
            message = await self._extract_message(e)
            if message == "Invalid API key":
                error = "invalid_api_key"
            elif message == "API key expired":
                error = "expired_api_key"
            elif message == "jwt expired":
                error = "expired_bearer"
            elif message == "Invalid basic authentication credentials":
                error = "invalid_basic_auth"
            else:
                message = "Invalid bearer token"
                error = "invalid_bearer"  # jwt malformed, jwt not active (https://www.npmjs.com/package/jsonwebtoken#errors--codes)
            return _handler.build_exception(error, message=message)

        elif isinstance(e, HTTPException):
            return e
        else:
            return _handler.build_exception("unknown_error", message=str(e))

    async def api_key_auth(
        self,
        api_key: Annotated[Union[str, None], Depends(_apikey_header)] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the API key and checks the scopes.
        Use this function if you only want to allow access via the API key.
        This function is used for HTTP connections.
        """
        try:
            return await self.full_auth(
                bearer=None, api_key=api_key, basic=None, sec=sec
            )
        except HTTPException as e:
            raise _handler.build_exception(
                e.detail.get("code"),
                message=e.detail.get("message"),
                headers={_AUTHENTICATE_HEADER: _APIKEY_AUTH_SCHEME},
            )

    async def bearer_auth(
        self,
        bearer: Annotated[
            Union[HTTPAuthorizationCredentials, None],
            Depends(_http_bearer),
        ] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and checks the scopes.
        Use this function if you only want to allow access via the bearer token.
        This function is used for HTTP connections.
        """
        try:
            return await self.full_auth(
                bearer=bearer, api_key=None, basic=None, sec=sec
            )
        except HTTPException as e:
            raise _handler.build_exception(
                e.detail.get("code"),
                message=e.detail.get("message"),
                headers={_AUTHENTICATE_HEADER: _BEARER_AUTH_SCHEME},
            )

    async def basic_auth(
        self,
        credentials: Annotated[Union[HTTPBasicCredentials, None], Depends(_http_basic)],
    ) -> Verify200Response:
        """
        Verifies the basic authentication credentials. This authentication method should just be used for special cases like /admin/metrics, where JWT and API key authentication are not desired or not possible.
        """
        try:
            return await self.full_auth(
                basic=credentials, bearer=None, api_key=None, sec=None
            )
        except HTTPException as e:
            raise _handler.build_exception(
                e.detail.get("code"),
                message=e.detail.get("message"),
                headers={_AUTHENTICATE_HEADER: _BASIC_AUTH_SCHEME},
            )

    async def combined_auth(
        self,
        bearer: Annotated[
            Union[HTTPAuthorizationCredentials, None], Depends(_http_bearer)
        ] = None,
        api_key: Annotated[Union[str, None], Depends(_apikey_header)] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and/or API key and checks the scopes.
        Returns early on the first successful verification, otherwise tries all available tokens.
        Use this function if you want to allow access via either the bearer token or the API key.
        This function is used for HTTP connections.
        """
        try:
            return await self.full_auth(
                basic=None, bearer=bearer, api_key=api_key, sec=sec
            )
        except HTTPException as e:
            raise _handler.build_exception(
                e.detail.get("code"),
                message=e.detail.get("message"),
                headers={
                    _AUTHENTICATE_HEADER: f"{_BEARER_AUTH_SCHEME}, {_APIKEY_AUTH_SCHEME}"
                },
            )

    async def full_auth(
        self,
        basic: Annotated[
            Union[HTTPBasicCredentials, None], Depends(_http_basic)
        ] = None,
        bearer: Annotated[
            Union[HTTPAuthorizationCredentials, None], Depends(_http_bearer)
        ] = None,
        api_key: Annotated[Union[str, None], Depends(_apikey_header)] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        IMPORTANT: combined_auth is sufficient for most use cases. This function adds basic auth to the mix, which is needed for external services like prometheus, but is not recommended for internal use.
        Verifies the bearer token, API key and basic authentication credentials and checks the scopes.
        Returns early on the first successful verification, otherwise tries all available tokens.
        Use this function if you want to allow access via either the bearer token, the API key or the basic authentication credentials.
        This function is used for HTTP connections.
        """
        tokens = [bearer, api_key, basic]
        last_error = None
        for token in tokens:
            try:
                if token is None:
                    continue
                res = None
                if isinstance(token, str):
                    res = await self._verify_api_key(token)
                elif isinstance(token, HTTPAuthorizationCredentials):
                    res = await self._verify_bearer(token)
                elif isinstance(token, HTTPBasicCredentials):
                    res = await self._verify_basic(token)
                if res is None:
                    continue
                if sec:
                    await self._validate_scopes(sec.scopes, res.scopes)
                return res

            except Exception as e:
                last_error = await self._handle_exception(e)
                continue

        if last_error:
            raise last_error
        else:
            raise _handler.build_exception(
                "no_credentials",
                message="No credentials provided. Check the WWW-Authenticate header for the available authentication methods.",
                headers={
                    _AUTHENTICATE_HEADER: f"{_BEARER_AUTH_SCHEME}, {_APIKEY_AUTH_SCHEME}, {_BASIC_AUTH_SCHEME}"
                },
            )

    async def ws_api_key_auth(
        self,
        api_key: Annotated[Union[str, None], Query()] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the API key and checks the scopes.
        Use this function if you only want to allow access via the API key.
        This function is used for WebSocket connections.
        """
        return await self.api_key_auth(api_key=api_key, sec=sec)

    async def ws_bearer_auth(
        self,
        bearer: Annotated[Union[str, None], Query()] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and checks the scopes.
        Use this function if you only want to allow access via the bearer token.
        This function is used for WebSocket connections.
        """
        credentials = (
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=bearer)
            if bearer
            else None
        )
        return await self.bearer_auth(bearer=credentials, sec=sec)

    async def ws_combined_auth(
        self,
        bearer: Annotated[Union[str, None], Query()] = None,
        api_key: Annotated[Union[str, None], Query()] = None,
        sec: SecurityScopes = SecurityScopes(),
    ) -> Verify200Response:
        """
        Verifies the bearer token and/or API key and checks the scopes.
        Use this function if you want to allow access via either the bearer token or the API key.
        This function is used for WebSocket connections.
        """
        credentials = (
            HTTPAuthorizationCredentials(scheme="Bearer", credentials=bearer)
            if bearer
            else None
        )
        return await self.combined_auth(bearer=credentials, api_key=api_key, sec=sec)
