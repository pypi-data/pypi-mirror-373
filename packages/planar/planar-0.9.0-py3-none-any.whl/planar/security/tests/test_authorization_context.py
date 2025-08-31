from planar.security.auth_context import Principal
from planar.security.authorization import (
    CedarEntity,
    PolicyService,
    ResourceType,
    WorkflowAction,
    get_policy_service,
    policy_service_context,
    set_policy_service,
)


def test_policy_service_context_variable():
    """Test that the authorization service context variable works correctly."""
    # Initially, no authz service should be set
    assert get_policy_service() is None

    # Create a mock policy service
    policy_service = PolicyService()

    # Set the policy service in context
    set_policy_service(policy_service)
    assert get_policy_service() is policy_service

    # Reset the context
    set_policy_service(None)
    assert get_policy_service() is None

    # Test the context manager
    async def test_context_manager():
        async with policy_service_context(policy_service):
            assert get_policy_service() is policy_service
        # After exiting the context, it should be None again
        assert get_policy_service() is None

    # Run the async test
    import asyncio

    asyncio.run(test_context_manager())


def test_policy_service_with_principal():
    """Test that the policy service works with principal resources."""
    policy_service = PolicyService()

    # Create a mock principal with only required fields
    principal = Principal(sub="test-user")  # type: ignore

    # Create resources
    principal_resource = CedarEntity.from_principal(principal)
    workflow_resource = CedarEntity.from_workflow("test_workflow")

    # Test that the service can be used
    assert principal_resource.resource_type == ResourceType.PRINCIPAL
    assert workflow_resource.resource_type == ResourceType.WORKFLOW
    assert principal_resource.resource_attributes["sub"] == "test-user"
    assert workflow_resource.resource_attributes["function_name"] == "test_workflow"

    assert (
        policy_service.is_allowed(
            principal_resource, WorkflowAction.WORKFLOW_RUN, workflow_resource
        )
        is True
    )

    assert (
        policy_service.is_allowed(
            principal_resource, WorkflowAction.WORKFLOW_RUN, workflow_resource
        )
        is True
    )

    assert (
        policy_service.is_allowed(
            principal_resource, "Workflow::Fail", workflow_resource
        )
        is False
    )
