from http import HTTPStatus

import pytest

from planar import PlanarApp, sqlite_config
from planar.config import AuthzConfig, SecurityConfig
from planar.security.auth_context import Principal, clear_principal, set_principal
from planar.testing.planar_test_client import PlanarTestClient
from planar.workflows import workflow


# ------ TEST SETUP ------
@workflow()
async def simple_test_workflow(test_id: str) -> str:
    """
    Simpleorkflow that returns the test id
    """
    return test_id


@pytest.fixture(name="app_with_no_authz")
def create_app_no_authz():
    config = sqlite_config("test_authz_router.db")

    return PlanarApp(
        config=config,
        title="Test Authorization in Router",
        description="API for testing workflow routers",
    ).register_workflow(simple_test_workflow)


@pytest.fixture(name="app_with_default_authz")
def create_app_with_authz():
    config = sqlite_config("test_authz_router.db")
    config.security = SecurityConfig(authz=AuthzConfig(enabled=True, policy_file=None))

    return PlanarApp(
        config=config,
        title="Test Authorization in Router",
        description="API for testing workflow routers",
    ).register_workflow(simple_test_workflow)


@pytest.fixture
def restrictive_policy_file(tmp_path):
    """Create a restrictive policy file for testing."""
    policy_content = """
    // Only allow Workflow::List actions when role is admin
    permit (
        principal,
        action == Action::"Workflow::List",
        resource
    ) when {
        principal.role == "admin"
    };

    """
    policy_file = tmp_path / "restrictive_policies.cedar"
    policy_file.write_text(policy_content)
    return str(policy_file)


@pytest.fixture(name="app_with_restricted_authz")
def create_app_with_restricted_authz(tmp_path, restrictive_policy_file):
    db_path = tmp_path / "test_authz_router.db"
    config = sqlite_config(str(db_path))
    config.security = SecurityConfig(
        authz=AuthzConfig(enabled=True, policy_file=restrictive_policy_file)
    )

    return PlanarApp(
        config=config,
        title="Test Authorization in Router",
        description="API for testing workflow routers",
    ).register_workflow(simple_test_workflow)


# ------ TESTS ------


def assert_workflow_list(response):
    # Verify the response status code
    assert response.status_code == 200

    # Parse the response data
    data = response.json()

    # Verify that two workflows are returned
    assert data["total"] == 1
    assert len(data["items"]) == 1

    assert data["offset"] == 0
    assert data["limit"] == 10

    # Verify the expense workflow details
    simple_test_workflow = next(
        item for item in data["items"] if item["name"] == "simple_test_workflow"
    )
    assert simple_test_workflow["fully_qualified_name"] == "simple_test_workflow"

    # # Verify that the workflows have input and output schemas
    assert "input_schema" in simple_test_workflow
    assert "output_schema" in simple_test_workflow


async def test_list_workflows_no_authz(app_with_no_authz):
    """
    Test that the workflow management router correctly lists registered workflows.
    """

    async with app_with_no_authz._lifespan(app_with_no_authz.fastapi):
        client = PlanarTestClient(app_with_no_authz)
        # Call the workflow management endpoint to list workflows
        response = await client.get("/planar/v1/workflows/")
        assert_workflow_list(response)


async def test_list_workflows_with_default_authz(app_with_default_authz):
    """
    Test that the workflow management router correctly lists registered workflows when authorization is enabled but no policy file is provided.
    """

    async with app_with_default_authz._lifespan(app_with_default_authz.fastapi):
        client = PlanarTestClient(app_with_default_authz)
        principal = Principal(sub="test_user")  # type: ignore
        token = set_principal(principal)

        # Call the workflow management endpoint to list workflows
        response = await client.get("/planar/v1/workflows/")
        assert_workflow_list(response)

        clear_principal(token)


async def test_list_workflows_with_restricted_authz(app_with_restricted_authz):
    """
    Test that the workflow management router correctly lists registered workflows when authorization is enabled and a policy file is provided.
    """

    async with app_with_restricted_authz._lifespan(app_with_restricted_authz.fastapi):
        client = PlanarTestClient(app_with_restricted_authz)
        principal = Principal(sub="test_user", role="admin")  # type: ignore
        token = set_principal(principal)

        # Call the workflow management endpoint to list workflows
        response = await client.get("/planar/v1/workflows/")
        assert_workflow_list(response)

        clear_principal(token)


async def test_list_workflows_with_restricted_authz_and_wrong_role(
    app_with_restricted_authz,
):
    """
    Test that the workflow management router correctly forbids access to workflows list.
    """

    async with app_with_restricted_authz._lifespan(app_with_restricted_authz.fastapi):
        client = PlanarTestClient(app_with_restricted_authz)
        principal = Principal(sub="test_user", role="test_role")  # type: ignore
        token = set_principal(principal)

        # Call the workflow management endpoint to list workflows
        response = await client.get("/planar/v1/workflows/")
        assert response.status_code == HTTPStatus.FORBIDDEN

        clear_principal(token)
