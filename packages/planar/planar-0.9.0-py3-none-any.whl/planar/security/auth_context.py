"""
Authentication context management for Planar.

This module provides context variables and utilities for managing the current
authenticated principal (user) throughout the request lifecycle.
"""

import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

from pydantic import BaseModel, Field


class Principal(BaseModel):
    """Represents an authenticated principal (user) with JWT claims."""

    # Standard JWT claims
    sub: str = Field(..., description="Subject (user ID)")
    iss: str | None = Field(None, description="Issuer")
    exp: int | None = Field(None, description="Expiration timestamp")
    iat: int | None = Field(None, description="Issued at timestamp")
    sid: str | None = Field(None, description="Session ID")
    jti: str | None = Field(None, description="JWT ID")

    # WorkOS specific claims
    org_id: str | None = Field(None, description="Organization ID")
    org_name: str | None = Field(None, description="Organization name")
    user_first_name: str | None = Field(None, description="User's first name")
    user_last_name: str | None = Field(None, description="User's last name")
    user_email: str | None = Field(None, description="User's email address")
    role: str | None = Field(None, description="User's role")
    permissions: list[str] | None = Field(None, description="User's permissions")

    # Additional custom claims
    extra_claims: dict[str, Any] = Field(
        default_factory=dict, description="Additional custom claims"
    )

    @classmethod
    def from_jwt_payload(cls, payload: dict[str, Any]) -> "Principal":
        """Create a Principal from a JWT payload."""
        if "sub" not in payload:
            raise ValueError("JWT payload must contain 'sub' field")

        standard_fields = {
            "sub",
            "iss",
            "exp",
            "iat",
            "sid",
            "jti",
            "org_id",
            "org_name",
            "user_first_name",
            "user_last_name",
            "user_email",
            "role",
            "permissions",
        }

        # Extract standard fields
        principal_data = {}
        for field in standard_fields:
            if field in payload:
                principal_data[field] = payload[field]

        # All other fields go into extra_claims
        extra_claims = {k: v for k, v in payload.items() if k not in standard_fields}
        principal_data["extra_claims"] = extra_claims

        return cls(**principal_data)

    @classmethod
    def from_service_token(cls, token: str) -> "Principal":
        """Create a Principal from a service token."""
        # TO-DO Potentially lookup token in database to get org_id, org_name, user_first_name, user_last_name, user_email, role, permissions
        return cls(
            sub="service_token",
            iss="service_token",
            exp=int(time.time()) + 3600,
            iat=int(time.time()),
            sid="service_token",
            jti="service_token",
            org_id="service_token",
            org_name="service_token",
            user_first_name="service_token",
            user_last_name="service_token",
            user_email="service_token",
            role="service_token",
            permissions=["service_token"],
        )


# Context variable for the current principal
principal_var: ContextVar[Principal | None] = ContextVar("principal", default=None)


def get_current_principal() -> Principal | None:
    """
    Get the current authenticated principal from context.

    Returns:
        The current Principal or None if not authenticated.
    """
    return principal_var.get()


def require_principal() -> Principal:
    """
    Get the current authenticated principal from context.

    Returns:
        The current Principal.

    Raises:
        RuntimeError: If no principal is set in context.
    """
    principal = get_current_principal()
    if principal is None:
        raise RuntimeError("No authenticated principal in context")
    return principal


def has_role(role: str) -> bool:
    """
    Check if the current principal has the given role.
    """
    principal = get_current_principal()
    return principal is not None and principal.role == role


def set_principal(principal: Principal) -> Any:
    """
    Set the current principal in context.

    Args:
        principal: The principal to set.

    Returns:
        A token that can be used to reset the context.
    """
    return principal_var.set(principal)


def clear_principal(token: Any) -> None:
    """
    Clear the current principal from context.

    Args:
        token: The token returned from set_principal.
    """
    principal_var.reset(token)


@contextmanager
def as_principal(principal: Principal) -> Iterator[None]:
    """
    Context manager that sets the current principal in context.

    Args:
        principal: The principal to set.
    """
    token = set_principal(principal)
    try:
        yield
    finally:
        clear_principal(token)
