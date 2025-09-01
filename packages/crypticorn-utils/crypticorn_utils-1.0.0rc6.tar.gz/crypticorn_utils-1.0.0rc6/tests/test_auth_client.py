import pytest
from crypticorn_utils.auth import AuthHandler
from crypticorn_utils.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBasicCredentials
from tests.envs import (
    ADMIN_SCOPES,
    EXPIRED_API_KEY,
    EXPIRED_JWT,
    INTERNAL_SCOPES,
    ONE_SCOPE_API_KEY,
    ONE_SCOPE_API_KEY_SCOPE,
    PURCHASEABLE_SCOPES,
    VALID_ADMIN_JWT,
    VALID_JWT,
    VALID_PREDICTION_JWT,
)

# Debug
UPDATE_SCOPES = "you probably need to bring the scopes in both the api client and the auth service in sync"

# Each function is tested without credentials, with invalid credentials, and with valid credentials.
# The test is successful if the correct HTTPException is raised.


# COMBINED AUTH
@pytest.mark.asyncio
async def test_combined_auth_without_credentials(auth_handler: AuthHandler):
    """Without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.combined_auth(bearer=None, api_key=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


# BEARER AUTH TESTS
@pytest.mark.asyncio
async def test_bearer_auth_without_credentials(auth_handler: AuthHandler):
    """Bearer auth without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.bearer_auth(bearer=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_bearer_auth_with_invalid_token(auth_handler: AuthHandler):
    """Bearer auth with invalid token"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.bearer_auth(
            bearer=HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
        )
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "invalid_bearer"


@pytest.mark.asyncio
async def test_bearer_auth_with_valid_token(auth_handler: AuthHandler):
    """Bearer auth with valid token"""
    res = await auth_handler.bearer_auth(
        bearer=HTTPAuthorizationCredentials(scheme="Bearer", credentials=VALID_JWT)
    )
    assert not res.admin
    assert all([key not in res.scopes for key in PURCHASEABLE_SCOPES])


# API KEY AUTH TESTS
@pytest.mark.asyncio
async def test_api_key_auth_without_credentials(auth_handler: AuthHandler):
    """API key auth without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.api_key_auth(api_key=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_api_key_auth_with_invalid_key(auth_handler: AuthHandler):
    """API key auth with invalid key"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.api_key_auth(api_key="invalid")
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "invalid_api_key"


@pytest.mark.asyncio
async def test_api_key_auth_with_valid_key(auth_handler: AuthHandler):
    """API key auth with valid key"""
    res = await auth_handler.api_key_auth(api_key=ONE_SCOPE_API_KEY)
    assert ONE_SCOPE_API_KEY_SCOPE in res.scopes
    assert len(res.scopes) == 1


# BASIC AUTH TESTS
@pytest.mark.asyncio
async def test_basic_auth_without_credentials(auth_handler: AuthHandler):
    """Basic auth without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.basic_auth(credentials=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_basic_auth_with_invalid_credentials(auth_handler: AuthHandler):
    """Basic auth with invalid credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.basic_auth(
            credentials=HTTPBasicCredentials(username="invalid", password="invalid")
        )
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "invalid_basic_auth"


# FULL AUTH TESTS
@pytest.mark.asyncio
async def test_full_auth_without_credentials(auth_handler: AuthHandler):
    """Full auth without any credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.full_auth(bearer=None, api_key=None, basic=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_full_auth_with_valid_bearer(auth_handler: AuthHandler):
    """Full auth with valid bearer token"""
    res = await auth_handler.full_auth(
        bearer=HTTPAuthorizationCredentials(scheme="Bearer", credentials=VALID_JWT),
        api_key=None,
        basic=None,
    )
    assert not res.admin
    assert all([key not in res.scopes for key in PURCHASEABLE_SCOPES])


@pytest.mark.asyncio
async def test_full_auth_with_valid_api_key(auth_handler: AuthHandler):
    """Full auth with valid API key"""
    res = await auth_handler.full_auth(
        bearer=None,
        api_key=ONE_SCOPE_API_KEY,
        basic=None,
    )
    assert ONE_SCOPE_API_KEY_SCOPE in res.scopes
    assert len(res.scopes) == 1


# COMBINED AUTH BEARER TESTS
@pytest.mark.asyncio
async def test_combined_auth_with_invalid_bearer_token(auth_handler: AuthHandler):
    """With invalid bearer token"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.combined_auth(
            bearer=HTTPAuthorizationCredentials(scheme="Bearer", credentials="123"),
            api_key=None,
        )
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "invalid_bearer"


@pytest.mark.asyncio
async def test_combined_auth_with_expired_bearer_token(auth_handler: AuthHandler):
    """With expired bearer token"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.combined_auth(
            bearer=HTTPAuthorizationCredentials(
                scheme="Bearer", credentials=EXPIRED_JWT
            ),
            api_key=None,
        )
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "expired_bearer"


@pytest.mark.asyncio
async def test_combined_auth_with_valid_bearer_token(auth_handler: AuthHandler):
    """With valid bearer token"""
    res = await auth_handler.combined_auth(
        bearer=HTTPAuthorizationCredentials(scheme="Bearer", credentials=VALID_JWT),
        api_key=None,
    )
    assert all(
        [key not in res.scopes for key in PURCHASEABLE_SCOPES]
    ), "non admin should not have access to purchaseable scopes"
    assert all(
        [key not in res.scopes for key in ADMIN_SCOPES]
    ), "non admin should not have access to any of the admin keys"
    assert all(
        [key not in res.scopes for key in INTERNAL_SCOPES]
    ), "non admin should not have access to any of the internal keys"
    assert not res.admin, "non admin should not be admin"


@pytest.mark.asyncio
async def test_combined_auth_with_valid_prediction_bearer_token(
    auth_handler: AuthHandler,
):
    """With valid bearer token"""
    res = await auth_handler.combined_auth(
        bearer=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=VALID_PREDICTION_JWT
        ),
        api_key=None,
    )
    assert all(
        [key in res.scopes for key in ["read:predictions"]]
    ), "non admin which purchased predictions should have access to purchaseable scopes"
    assert all(
        [key not in res.scopes for key in ADMIN_SCOPES]
    ), "non admin should not have access to any of the admin keys"
    assert all(
        [key not in res.scopes for key in INTERNAL_SCOPES]
    ), "non admin should not have access to any of the internal keys"
    assert not res.admin, "non admin should not be admin"


@pytest.mark.asyncio
async def test_combined_auth_with_valid_admin_bearer_token(auth_handler: AuthHandler):
    """With valid admin bearer token"""
    res = await auth_handler.combined_auth(
        bearer=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=VALID_ADMIN_JWT
        ),
        api_key=None,
    )
    assert all(
        [key in res.scopes for key in PURCHASEABLE_SCOPES]
    ), "admin should have access to purchaseable scopes"
    assert all(
        [key in res.scopes for key in ADMIN_SCOPES]
    ), "admin should have access to any of the admin keys"
    assert all(
        [key not in res.scopes for key in INTERNAL_SCOPES]
    ), "admin should not have access to any of the internal keys"
    assert res.admin, "admin should be true"


# COMBINED AUTH API KEY TESTS
@pytest.mark.asyncio
async def test_combined_auth_with_invalid_api_key(auth_handler: AuthHandler):
    """With invalid api key"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.combined_auth(bearer=None, api_key="123")
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "invalid_api_key"


@pytest.mark.asyncio
async def test_combined_auth_with_one_scope_valid_api_key(auth_handler: AuthHandler):
    """With one scope valid api key"""
    res = await auth_handler.combined_auth(bearer=None, api_key=ONE_SCOPE_API_KEY)
    assert ONE_SCOPE_API_KEY_SCOPE in res.scopes, UPDATE_SCOPES
    assert len(res.scopes) == 1, "should only have one scope"


@pytest.mark.asyncio
async def test_combined_auth_with_expired_api_key(auth_handler: AuthHandler):
    """With expired api key"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.combined_auth(bearer=None, api_key=EXPIRED_API_KEY)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "expired_api_key"


# WEBSOCKET AUTH TESTS
@pytest.mark.asyncio
async def test_ws_combined_auth_without_credentials(auth_handler: AuthHandler):
    """WS combined auth without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.ws_combined_auth(bearer=None, api_key=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_ws_combined_auth_with_valid_bearer(auth_handler: AuthHandler):
    """WS combined auth with valid bearer token"""
    res = await auth_handler.ws_combined_auth(bearer=VALID_JWT, api_key=None)
    assert not res.admin
    assert all([key not in res.scopes for key in PURCHASEABLE_SCOPES])


@pytest.mark.asyncio
async def test_ws_combined_auth_with_valid_api_key(auth_handler: AuthHandler):
    """WS combined auth with valid API key"""
    res = await auth_handler.ws_combined_auth(bearer=None, api_key=ONE_SCOPE_API_KEY)
    assert ONE_SCOPE_API_KEY_SCOPE in res.scopes
    assert len(res.scopes) == 1


@pytest.mark.asyncio
async def test_ws_bearer_auth_without_credentials(auth_handler: AuthHandler):
    """WS bearer auth without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.ws_bearer_auth(bearer=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_ws_bearer_auth_with_valid_token(auth_handler: AuthHandler):
    """WS bearer auth with valid token"""
    res = await auth_handler.ws_bearer_auth(bearer=VALID_JWT)
    assert not res.admin
    assert all([key not in res.scopes for key in PURCHASEABLE_SCOPES])


@pytest.mark.asyncio
async def test_ws_api_key_auth_without_credentials(auth_handler: AuthHandler):
    """WS API key auth without credentials"""
    with pytest.raises(HTTPException) as e:
        await auth_handler.ws_api_key_auth(api_key=None)
    assert e.value.status_code == 401
    assert e.value.detail.get("code") == "no_credentials"


@pytest.mark.asyncio
async def test_ws_api_key_auth_with_valid_key(auth_handler: AuthHandler):
    """WS API key auth with valid key"""
    res = await auth_handler.ws_api_key_auth(api_key=ONE_SCOPE_API_KEY)
    assert ONE_SCOPE_API_KEY_SCOPE in res.scopes
    assert len(res.scopes) == 1


# SCOPE VALIDATION TESTS
@pytest.mark.asyncio
async def test_combined_auth_scope_validation_with_insufficient_scopes(
    auth_handler: AuthHandler,
):
    """Test scope validation with insufficient scopes"""
    from fastapi.security import SecurityScopes

    with pytest.raises(HTTPException) as e:
        # Try to access with a token that has read:trade:bots scope but require admin scope
        await auth_handler.combined_auth(
            bearer=None,
            api_key=ONE_SCOPE_API_KEY,
            sec=SecurityScopes(scopes=["read:admin"]),
        )
    assert e.value.status_code == 403
    assert e.value.detail.get("code") == "insufficient_scopes"


@pytest.mark.asyncio
async def test_combined_auth_scope_validation_with_sufficient_scopes(
    auth_handler: AuthHandler,
):
    """Test scope validation with sufficient scopes"""
    from fastapi.security import SecurityScopes

    # This should pass since we're requiring a scope that the API key has
    res = await auth_handler.combined_auth(
        bearer=None,
        api_key=ONE_SCOPE_API_KEY,
        sec=SecurityScopes(scopes=[ONE_SCOPE_API_KEY_SCOPE]),
    )
    assert ONE_SCOPE_API_KEY_SCOPE in res.scopes
