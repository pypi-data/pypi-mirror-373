import pytest

from planar.security.auth_context import (
    Principal,
    clear_principal,
    get_current_principal,
    has_role,
    require_principal,
    set_principal,
)


def test_principal_from_jwt_payload():
    # Test with minimal required fields
    payload = {"sub": "user123"}
    principal = Principal.from_jwt_payload(payload)
    assert principal.sub == "user123"
    assert principal.extra_claims == {}

    # Test with all standard fields
    payload = {
        "sub": "user123",
        "iss": "https://auth-api.coplane.com",
        "exp": 1234567890,
        "iat": 1234567890,
        "sid": "session123",
        "jti": "jwt123",
        "org_id": "org123",
        "org_name": "Test Org",
        "user_first_name": "John",
        "user_last_name": "Doe",
        "user_email": "john@example.com",
        "role": "admin",
        "permissions": ["read", "write"],
    }
    principal = Principal.from_jwt_payload(payload)
    assert principal.sub == "user123"
    assert principal.iss == "https://auth-api.coplane.com"
    assert principal.exp == 1234567890
    assert principal.iat == 1234567890
    assert principal.sid == "session123"
    assert principal.jti == "jwt123"
    assert principal.org_id == "org123"
    assert principal.org_name == "Test Org"
    assert principal.user_first_name == "John"
    assert principal.user_last_name == "Doe"
    assert principal.user_email == "john@example.com"
    assert principal.role == "admin"
    assert principal.permissions == ["read", "write"]
    assert principal.extra_claims == {}

    # Test with extra claims
    payload = {
        "sub": "user123",
        "custom_field": "custom_value",
        "another_field": 123,
    }
    principal = Principal.from_jwt_payload(payload)
    assert principal.sub == "user123"
    assert principal.extra_claims == {
        "custom_field": "custom_value",
        "another_field": 123,
    }

    # Test with missing required field
    with pytest.raises(ValueError, match="JWT payload must contain 'sub' field"):
        Principal.from_jwt_payload({})


def test_get_current_principal():
    # Test when no principal is set
    assert get_current_principal() is None

    # Test when principal is set
    principal = Principal(
        sub="user123",
        iss=None,
        exp=None,
        iat=None,
        sid=None,
        jti=None,
        org_id=None,
        org_name=None,
        user_first_name=None,
        user_last_name=None,
        user_email=None,
        role=None,
        permissions=None,
    )
    token = set_principal(principal)
    try:
        assert get_current_principal() == principal
    finally:
        clear_principal(token)

    # Verify principal is cleared
    assert get_current_principal() is None


def test_has_role():
    # Test when no principal is set
    assert not has_role("admin")

    # Test when principal has matching role
    principal = Principal(
        sub="user123",
        role="admin",
        iss=None,
        exp=None,
        iat=None,
        sid=None,
        jti=None,
        org_id=None,
        org_name=None,
        user_first_name=None,
        user_last_name=None,
        user_email=None,
        permissions=None,
    )
    token = set_principal(principal)
    try:
        assert has_role("admin")
        assert not has_role("user")
    finally:
        clear_principal(token)

    # Test when principal has no role
    principal = Principal(
        sub="user123",
        iss=None,
        exp=None,
        iat=None,
        sid=None,
        jti=None,
        org_id=None,
        org_name=None,
        user_first_name=None,
        user_last_name=None,
        user_email=None,
        role=None,
        permissions=None,
    )
    token = set_principal(principal)
    try:
        assert not has_role("admin")
    finally:
        clear_principal(token)


def test_require_principal():
    # Test when no principal is set
    with pytest.raises(RuntimeError, match="No authenticated principal in context"):
        require_principal()

    # Test when principal is set
    principal = Principal(
        sub="user123",
        iss=None,
        exp=None,
        iat=None,
        sid=None,
        jti=None,
        org_id=None,
        org_name=None,
        user_first_name=None,
        user_last_name=None,
        user_email=None,
        role=None,
        permissions=None,
    )
    token = set_principal(principal)
    try:
        assert require_principal() == principal
    finally:
        clear_principal(token)

    # Verify principal is cleared
    with pytest.raises(RuntimeError, match="No authenticated principal in context"):
        require_principal()
