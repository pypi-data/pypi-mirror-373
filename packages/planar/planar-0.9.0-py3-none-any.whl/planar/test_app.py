from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, ValidationError

from examples.simple_service.models import (
    Invoice,
)
from planar import PlanarApp, sqlite_config
from planar.app import setup_auth_middleware
from planar.config import Environment, JWTConfig, SecurityConfig

load_dotenv()


router = APIRouter()


class InvoiceRequest(BaseModel):
    message: str


class InvoiceResponse(BaseModel):
    status: str
    echo: str


app = PlanarApp(
    config=sqlite_config("simple_service.db"),
    title="Sample Invoice API",
    description="API for CRUD'ing invoices",
)


def test_register_model_deduplication():
    """Test that registering the same model multiple times only adds it once to the registry."""

    # Ensure Invoice is registered (ObjectRegistry gets reset before each test)
    app.register_entity(Invoice)
    initial_model_count = len(app._object_registry.get_entities())

    # Register the Invoice model again
    app.register_entity(Invoice)

    assert len(app._object_registry.get_entities()) == initial_model_count

    # Register the same model a second time
    app.register_entity(Invoice)

    assert len(app._object_registry.get_entities()) == initial_model_count

    # Verify that the model in the registry is the Invoice model
    registered_models = app._object_registry.get_entities()
    assert any(model.__name__ == "Invoice" for model in registered_models)


class TestJWTSetup:
    def test_setup_jwt_middleware_production_requires_config(self):
        """Test that JWT setup throws ValueError in production without proper config"""
        mock_app = Mock()
        mock_app.config.environment = Environment.PROD
        mock_app.config.security = SecurityConfig()

        with pytest.raises(
            ValueError,
            match="Auth middleware is required in production. Please set the JWT config and optionally service token config.",
        ):
            setup_auth_middleware(mock_app)

    def test_setup_jwt_middleware_production_requires_client_id(self):
        """Test that JWT setup throws ValueError in production without client_id"""
        with pytest.raises(
            ValidationError,
            match="Both client_id and org_id required to enable JWT",
        ):
            JWTConfig(client_id=None, org_id="test-org")

    def test_setup_jwt_middleware_production_requires_org_id(self):
        """Test that JWT setup throws ValueError in production without org_id"""
        with pytest.raises(
            ValidationError,
            match="Both client_id and org_id required to enable JWT",
        ):
            JWTConfig(client_id="test-client-id", org_id=None)

    @patch("planar.app.logger")
    def test_setup_jwt_middleware_success_with_all_fields(self, mock_logger):
        """Test that JWT setup succeeds with all required fields"""
        mock_app = Mock()
        mock_app.config.environment = Environment.PROD
        mock_app.config.security = SecurityConfig(
            jwt=JWTConfig(
                client_id="test-client-id",
                org_id="test-org-id",
                additional_exclusion_paths=["/test/path"],
            )
        )

        setup_auth_middleware(mock_app)

        # Verify middleware was added to app.fastapi
        mock_app.fastapi.add_middleware.assert_called_once()

        # Check that info log was called
        mock_logger.info.assert_called_once_with(
            "Auth middleware enabled",
            client_id="test-client-id",
            org_id="test-org-id",
            additional_exclusion_paths=["/test/path"],
        )

    @patch("planar.app.logger")
    def test_setup_jwt_middleware_dev_environment_allows_missing_config(
        self, mock_logger
    ):
        """Test that JWT setup is skipped in dev environment without config"""
        mock_app = Mock()
        mock_app.config.environment = Environment.DEV
        mock_app.config.security = SecurityConfig()

        setup_auth_middleware(mock_app)

        # Verify warning was logged and no middleware added
        mock_logger.warning.assert_called_once_with("Auth middleware disabled")
        mock_app.fastapi.add_middleware.assert_not_called()

    @patch("planar.app.logger")
    def test_setup_jwt_middleware_dev_environment_allows_disabled_jwt(
        self, mock_logger
    ):
        """Test that JWT setup is skipped in dev environment with disabled JWT"""
        mock_app = Mock()
        mock_app.config.environment = Environment.DEV
        mock_app.config.security = SecurityConfig()

        setup_auth_middleware(mock_app)

        # Verify warning was logged and no middleware added
        mock_logger.warning.assert_called_once_with("Auth middleware disabled")
        mock_app.fastapi.add_middleware.assert_not_called()
