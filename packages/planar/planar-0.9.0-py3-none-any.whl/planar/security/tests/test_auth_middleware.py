from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from planar.security.auth_middleware import AuthMiddleware


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def auth_middleware(app):
    return AuthMiddleware(
        app=app,
        client_id="test-client-id",
        org_id="test-org-id",
        additional_exclusion_paths=["/test/exclude"],
        service_token="plt_test-service-token",
    )


class TestAuthMiddleware:
    def test_org_id_validation_none(self, auth_middleware):
        """Test that org_id validation fails when token has None org_id"""
        with (
            patch.object(auth_middleware, "get_signing_key_from_jwt"),
            patch("jwt.decode") as mock_decode,
        ):
            mock_decode.return_value = {"org_id": None}

            with pytest.raises(HTTPException) as exc_info:
                auth_middleware.validate_jwt_token("fake-token")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid organization"

    def test_org_id_validation_empty_string(self, auth_middleware):
        """Test that org_id validation fails when token has empty string org_id"""
        with (
            patch.object(auth_middleware, "get_signing_key_from_jwt"),
            patch("jwt.decode") as mock_decode,
        ):
            mock_decode.return_value = {"org_id": ""}

            with pytest.raises(HTTPException) as exc_info:
                auth_middleware.validate_jwt_token("fake-token")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid organization"

    def test_org_id_validation_mismatch(self, auth_middleware):
        """Test that org_id validation fails when token org_id doesn't match"""
        with (
            patch.object(auth_middleware, "get_signing_key_from_jwt"),
            patch("jwt.decode") as mock_decode,
        ):
            mock_decode.return_value = {"org_id": "different-org-id"}

            with pytest.raises(HTTPException) as exc_info:
                auth_middleware.validate_jwt_token("fake-token")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid organization"

    def test_org_id_validation_success(self, auth_middleware):
        """Test that org_id validation succeeds when token org_id matches"""
        with (
            patch.object(auth_middleware, "get_signing_key_from_jwt"),
            patch("jwt.decode") as mock_decode,
        ):
            expected_payload = {"org_id": "test-org-id", "user_id": "test-user"}
            mock_decode.return_value = expected_payload

            result = auth_middleware.validate_jwt_token("fake-token")

            assert result == expected_payload

    @pytest.mark.asyncio
    async def test_service_token_validation_success(self, auth_middleware):
        """Test that service token validation succeeds when token matches"""
        mock_request = Mock()
        mock_request.url.path = "/planar/v1/something"
        mock_request.headers = {"Authorization": "Bearer plt_test-service-token"}
        mock_call_next = Mock()
        mock_call_next.return_value = JSONResponse(
            status_code=200, content={"message": "success"}
        )

        async def mock_call_next_func(request):
            return mock_call_next(request)

        result = await auth_middleware.dispatch(mock_request, mock_call_next_func)
        mock_call_next.assert_called_once_with(mock_request)
        assert result is not None
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_service_token_validation_failure(self, auth_middleware):
        """Test that service token validation succeeds when token matches"""
        mock_request = Mock()
        mock_request.url.path = "/planar/v1/something"
        mock_request.headers = {"Authorization": "Bearer plt_wrong-token"}
        mock_call_next = Mock()
        mock_call_next.return_value = JSONResponse(
            status_code=200, content={"message": "success"}
        )

        async def mock_call_next_func(request):
            return mock_call_next(request)

        result = await auth_middleware.dispatch(mock_request, mock_call_next_func)
        mock_call_next.assert_not_called()
        assert result is not None
        assert result.status_code == 401

    @pytest.mark.asyncio
    async def test_exclusion_paths_includes_health_and_additional(self, app):
        """Test that exclusion paths include health endpoint and additional paths"""
        middleware = AuthMiddleware(
            app=app,
            client_id="test-client-id",
            org_id="test-org-id",
            additional_exclusion_paths=["/custom/path", "/another/path"],
        )

        mock_request = Mock()
        mock_call_next = Mock()

        async def mock_call_next_func(request):
            return mock_call_next(request)

        expected_paths = ["/planar/v1/health", "/custom/path", "/another/path"]
        for path in expected_paths:
            mock_request.url.path = path
            mock_call_next.reset_mock()

            await middleware.dispatch(mock_request, mock_call_next_func)  # type: ignore

            mock_call_next.assert_called_once_with(mock_request)

        # Test that non-excluded paths are not excluded
        mock_request.url.path = "/not-excluded"
        mock_call_next.reset_mock()
        result = await middleware.dispatch(mock_request, mock_call_next_func)
        assert result is not None
        assert result.status_code == 401
        mock_call_next.assert_not_called()

    def test_required_org_id_parameter(self, app):
        """Test that org_id parameter is required (not optional)"""
        # This test ensures org_id cannot be None based on type hints
        # The actual enforcement is at the type level, so we just verify
        # the constructor works with a valid org_id
        middleware = AuthMiddleware(
            app=app, client_id="test-client-id", org_id="required-org-id"
        )

        assert middleware.org_id == "required-org-id"
