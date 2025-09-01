from typing import Literal
from unittest.mock import Mock

import pytest
from crypticorn_utils.exceptions import (
    BaseError,
    ExceptionHandler,
    _ExceptionDetail,
)
from fastapi import FastAPI, HTTPException, Request, WebSocketException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Define error codes as a Literal type for testing
TestErrorCodes = Literal["unknown_error", "test_error", "not_found"]


# Test fixtures and mock classes
class MockApiError:
    """Mock API error for testing"""

    UNKNOWN_ERROR = BaseError[TestErrorCodes](
        identifier="unknown_error",
        type="server error",
        level="error",
        http_code=500,
        websocket_code=1011,
    )
    TEST_ERROR = BaseError[TestErrorCodes](
        identifier="test_error",
        type="user error",
        level="warning",
        http_code=400,
        websocket_code=1007,
    )
    NOT_FOUND = BaseError[TestErrorCodes](
        identifier="not_found",
        type="user error",
        level="error",
        http_code=404,
        websocket_code=1008,
    )


handler = ExceptionHandler[TestErrorCodes](callback=BaseError.from_identifier)


@pytest.fixture
def mock_request():
    """Create a mock FastAPI request"""
    request = Mock(spec=Request)
    request.url = Mock()
    request.url.path = "/test"
    return request

class TestExceptionDetail:
    """Test cases for ExceptionDetail model"""

    def test_exception_detail_creation(self):
        """Test creating an ExceptionDetail instance"""
        detail = _ExceptionDetail[TestErrorCodes](
            code="test_error",
            type="user error",
            level="warning",
            status_code=400,
        )

        assert detail.code == "test_error"
        assert detail.type == "user error"
        assert detail.level == "warning"
        assert detail.status_code == 400
        assert detail.message is None
        assert detail.details is None

    def test_exception_detail_with_optional_fields(self):
        """Test creating ExceptionDetail with all fields"""
        detail = _ExceptionDetail[TestErrorCodes](
            message="Test error message",
            code="test_error",
            type="user error",
            level="error",
            status_code=400,
            details={"extra": "info"},
        )

        assert detail.message == "Test error message"
        assert detail.code == "test_error"
        assert detail.type == "user error"
        assert detail.level == "error"
        assert detail.status_code == 400
        assert detail.details == {"extra": "info"}

    def test_exception_detail_model_dump(self):
        """Test ExceptionDetail model serialization"""
        detail = _ExceptionDetail[TestErrorCodes](
            message="Test message",
            code="test_error",
            type="server error",
            level="error",
            status_code=500,
        )

        dumped = detail.model_dump(mode="json")
        expected = {
            "message": "Test message",
            "code": "test_error",
            "type": "server error",
            "level": "error",
            "status_code": 500,
            "details": None,
        }

        assert dumped == expected

    def test_exception_detail_validation_error(self):
        """Test ExceptionDetail validation with invalid data"""
        with pytest.raises(ValidationError):
            _ExceptionDetail[TestErrorCodes](
                code="test_error",
                type="invalid_type",  # Invalid type
                level="error",
                status_code=400,
            )


class TestBaseError:
    """Test cases for BaseError class"""

    def test_base_error_properties(self):
        """Test BaseError property access"""
        error = MockApiError.TEST_ERROR

        assert error.identifier == "test_error"
        assert error.type == "user error"
        assert error.level == "warning"
        assert error.http_code == 400
        assert error.websocket_code == 1007

    def test_base_error_from_identifier(self):
        """Test BaseError.from_identifier method"""
        error = BaseError.from_identifier("test_error")
        assert error == MockApiError.TEST_ERROR

        error = BaseError.from_identifier("unknown_error")
        assert error == MockApiError.UNKNOWN_ERROR

    def test_base_error_from_identifier_not_found(self):
        """Test BaseError.from_identifier with non-existent identifier"""
        with pytest.raises(
            ValueError, match="Unknown error identifier: non_existent_error"
        ):
            BaseError.from_identifier("non_existent_error")

    def test_all_mock_api_errors(self):
        """Test all mock API error definitions"""
        # Test UNKNOWN_ERROR
        error = MockApiError.UNKNOWN_ERROR
        assert error.identifier == "unknown_error"
        assert error.type == "server error"
        assert error.level == "error"
        assert error.http_code == 500
        assert error.websocket_code == 1011

        # Test NOT_FOUND
        error = MockApiError.NOT_FOUND
        assert error.identifier == "not_found"
        assert error.type == "user error"
        assert error.level == "error"
        assert error.http_code == 404
        assert error.websocket_code == 1008


class TestExceptionHandler:
    """Test cases for ExceptionHandler class"""

    def test_exception_handler_initialization(self):
        """Test ExceptionHandler initialization"""
        assert handler.callback == BaseError.from_identifier

    def test_build_http_exception(self):
        """Test building HTTP exception"""
        exception = handler.build_exception("test_error")

        assert isinstance(exception, HTTPException)
        assert exception.status_code == 400
        assert exception.detail["code"] == "test_error"
        assert exception.detail["type"] == "user error"
        assert exception.detail["level"] == "warning"
        assert exception.detail["status_code"] == 400

    def test_build_websocket_exception(self):
        """Test building WebSocket exception"""
        exception = handler.build_exception("test_error", type="websocket")

        assert isinstance(exception, WebSocketException)
        assert exception.code == 400
        assert exception.reason["code"] == "test_error"
        assert exception.reason["type"] == "user error"
        assert exception.reason["level"] == "warning"

    def test_build_exception_with_message(self):
        """Test building exception with custom message"""
        exception = handler.build_exception("test_error", message="Custom message")

        assert isinstance(exception, HTTPException)
        assert exception.detail["message"] == "Custom message"
        assert exception.detail["code"] == "test_error"

    def test_build_exception_with_headers(self):
        """Test building HTTP exception with headers"""
        headers = {"X-Custom-Header": "value"}
        exception = handler.build_exception("test_error", headers=headers)

        assert isinstance(exception, HTTPException)
        assert exception.headers == headers

    def test_build_exception_with_details(self):
        """Test building exception with additional details"""
        details = {"field": "value", "extra": "info"}
        exception = handler.build_exception("test_error", details=details)

        assert isinstance(exception, HTTPException)
        assert exception.detail["details"] == details

    def test_build_exception_all_parameters(self):
        """Test building exception with all parameters"""
        headers = {"X-Custom": "header"}
        details = {"extra": "details"}

        exception = handler.build_exception(
            "test_error", message="Custom message", headers=headers, details=details
        )

        assert isinstance(exception, HTTPException)
        assert exception.detail["message"] == "Custom message"
        assert exception.detail["code"] == "test_error"
        assert exception.detail["details"] == details
        assert exception.headers == headers
        assert exception.status_code == 400


class TestExceptionHandlerMethods:
    """Test cases for ExceptionHandler exception handling methods"""

    @pytest.mark.asyncio
    async def test_general_handler(self):
        """Test general exception handler"""
        test_exception = Exception("Test error")

        response = await handler._general_handler(mock_request, test_exception)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

        # Check response content
        content = response.body.decode()
        assert "Test error" in content
        assert "unknown_error" in content
        assert "server error" in content

    @pytest.mark.asyncio
    async def test_request_validation_handler(self):
        """Test request validation error handler"""
        # Create a mock RequestValidationError
        validation_error = RequestValidationError(errors=[])

        response = await handler._request_validation_handler(
            mock_request, validation_error
        )

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        # Check response content
        content = response.body.decode()
        assert "invalid_data_request" in content
        assert "user error" in content

    @pytest.mark.asyncio
    async def test_response_validation_handler(self):
        """Test response validation error handler"""
        # Create a mock ResponseValidationError
        validation_error = ResponseValidationError(errors=[])

        response = await handler._response_validation_handler(
            mock_request, validation_error
        )

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        # Check response content
        content = response.body.decode()
        assert "invalid_data_response" in content
        assert "user error" in content

    @pytest.mark.asyncio
    async def test_http_handler(self):
        """Test HTTP exception handler"""
        http_exception = HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": "Resource not found"},
            headers={"X-Custom": "header"},
        )

        response = await handler._http_handler(mock_request, http_exception)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        assert response.headers["X-Custom"] == "header"

        # Check response content matches original detail
        content = response.body.decode()
        assert "not_found" in content
        assert "Resource not found" in content

    def test_register_exception_handlers(self):
        """Test registering exception handlers with FastAPI app"""
        app = FastAPI()

        # Mock the add_exception_handler method
        app.add_exception_handler = Mock()

        handler.register_exception_handlers(app)

        # Verify all exception handlers were registered
        assert app.add_exception_handler.call_count == 4

        # Check that the right exception types were registered
        calls = app.add_exception_handler.call_args_list
        exception_types = [call[0][0] for call in calls]

        assert Exception in exception_types
        assert HTTPException in exception_types
        assert RequestValidationError in exception_types
        assert ResponseValidationError in exception_types


class TestIntegrationScenarios:
    """Integration test scenarios"""

    def test_complete_error_flow(self):
        """Test complete error handling flow"""
        # Build exception
        exception = handler.build_exception(
            "not_found", message="User not found", details={"user_id": 123}
        )

        # Verify exception properties
        assert isinstance(exception, HTTPException)
        assert exception.status_code == 404
        assert exception.detail["code"] == "not_found"
        assert exception.detail["message"] == "User not found"
        assert exception.detail["type"] == "user error"
        assert exception.detail["level"] == "error"
        assert exception.detail["details"]["user_id"] == 123

    def test_websocket_error_flow(self):
        """Test WebSocket error handling flow"""
        exception = handler.build_exception(
            "unknown_error", message="Internal server error", type="websocket"
        )

        # Verify WebSocket exception properties
        assert isinstance(exception, WebSocketException)
        assert exception.code == 500
        assert exception.reason["code"] == "unknown_error"
        assert exception.reason["message"] == "Internal server error"
        assert exception.reason["type"] == "server error"
        assert exception.reason["level"] == "error"

    def test_error_callback_integration(self):
        """Test integration between ExceptionHandler and BaseError"""

        def callback(identifier: TestErrorCodes) -> BaseError[TestErrorCodes]:
            return BaseError.from_identifier(identifier)

        test_handler = ExceptionHandler[TestErrorCodes](callback=callback)

        # Test with each mock error
        test_errors = [
            MockApiError.UNKNOWN_ERROR,
            MockApiError.TEST_ERROR,
            MockApiError.NOT_FOUND,
        ]
        for mock_error in test_errors:
            exception = test_handler.build_exception(mock_error.identifier)

            assert isinstance(exception, HTTPException)
            assert exception.status_code == mock_error.http_code
            assert exception.detail["code"] == mock_error.identifier
            assert exception.detail["type"] == mock_error.type
            assert exception.detail["level"] == mock_error.level
