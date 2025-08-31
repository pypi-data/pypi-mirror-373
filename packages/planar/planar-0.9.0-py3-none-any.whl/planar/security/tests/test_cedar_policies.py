import pytest

from planar.security.auth_context import Principal
from planar.security.authorization import (
    AgentAction,
    CedarEntity,
    PolicyService,
    RuleAction,
    WorkflowAction,
)


@pytest.fixture
def policy_service():
    return PolicyService()


def test_workflow_permissions(policy_service: PolicyService):
    # Create a test principal (user)
    user_principal = Principal(
        sub="user123"  # type: ignore
    )

    # Create test resources
    workflow_resource = CedarEntity.from_workflow("com.example.workflow.ProcessData")

    # Test Workflow Actions
    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        WorkflowAction.WORKFLOW_LIST,
        workflow_resource,
    ), "User should be able to list workflows"

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        WorkflowAction.WORKFLOW_VIEW_DETAILS,
        workflow_resource,
    ), "User should be able to view workflow details"

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        WorkflowAction.WORKFLOW_RUN,
        workflow_resource,
    ), "User should be able to run workflow"

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        WorkflowAction.WORKFLOW_CANCEL,
        workflow_resource,
    ), "User should be able to cancel workflow"


def test_agent_permissions(policy_service: PolicyService):
    user_principal = Principal(
        sub="user123"  # type: ignore
    )

    agent_resource = CedarEntity.from_agent("OcrAgent")

    # Test Agent Actions
    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        AgentAction.AGENT_LIST,
        agent_resource,
    ), "User should be able to list agents"

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        AgentAction.AGENT_VIEW_DETAILS,
        agent_resource,
    ), "User should be able to view agent details"

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        AgentAction.AGENT_RUN,
        agent_resource,
    ), "User should be able to run agent"

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        AgentAction.AGENT_UPDATE,
        agent_resource,
    ), "User should be able to configure agent"


def test_denied_permission(policy_service: PolicyService):
    # Create a test principal (user)
    user_principal = Principal(
        sub="user123"  # type: ignore
    )

    # Create test resource
    workflow_resource = CedarEntity.from_workflow("com.example.workflow.ProcessData")

    # Test that a non-existent action is denied
    assert not policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        "Workflow::Delete",  # This action is not defined in our policies
        workflow_resource,
    ), "User should not be able to delete workflows"


def test_deny_edits_to_rules_for_member_role(policy_service: PolicyService):
    member_jwt_data = {
        "org_name": "CoPlane",
        "user_first_name": "Donald",
        "user_last_name": "Knuth",
        "user_email": "don@coplane.com",
        "iss": "https://auth-api.coplane.com",
        "sub": "user_02JYMGMYETXMAVB0GKT868T8V7",
        "sid": "session_01JZ6NJVC1MSR86VZNR54BF9D4",
        "jti": "01JZ8EHD793F6RTY8FC4A3H4E9",
        "org_id": "org_01JY4QP57Y7H4EQ7HT3BGN7TNK",
        "role": "member",
        "permissions": [],
        "feature_flags": [],
        "exp": 1751556901,
        "iat": 1751556601,
    }

    user_principal = Principal.from_jwt_payload(member_jwt_data)

    rule_resource = CedarEntity.from_rule("complex_business_rule")

    assert not policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        RuleAction.RULE_UPDATE,
        rule_resource,
    )


def test_allow_edits_to_rules_for_admin_role(policy_service: PolicyService):
    member_jwt_data = {
        "org_name": "CoPlane",
        "user_first_name": "Donald",
        "user_last_name": "Knuth",
        "user_email": "don@coplane.com",
        "iss": "https://auth-api.coplane.com",
        "sub": "user_02JYMGMYETXMAVB0GKT868T8V7",
        "sid": "session_01JZ6NJVC1MSR86VZNR54BF9D4",
        "jti": "01JZ8EHD793F6RTY8FC4A3H4E9",
        "org_id": "org_01JY4QP57Y7H4EQ7HT3BGN7TNK",
        "role": "admin",
        "permissions": [],
        "feature_flags": [],
        "exp": 1751556901,
        "iat": 1751556601,
    }

    user_principal = Principal.from_jwt_payload(member_jwt_data)

    rule_resource = CedarEntity.from_rule("complex_business_rule")

    assert policy_service.is_allowed(
        CedarEntity.from_principal(user_principal),
        RuleAction.RULE_UPDATE,
        rule_resource,
    )
