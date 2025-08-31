import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, TypedDict, cast

from cedarpy import (
    AuthzResult,
    Decision,
    format_policies,
    is_authorized,
)
from fastapi import HTTPException
from pydantic import BaseModel

from planar.logging import get_logger
from planar.security.auth_context import Principal, get_current_principal

logger = get_logger(__name__)

# Context variable for the current authorization service
policy_service_var: ContextVar["PolicyService | None"] = ContextVar(
    "policy_service", default=None
)


def get_policy_service() -> "PolicyService | None":
    """
    Get the current authorization service from context.

    Returns:
        The current PolicyService or None if not set.
    """
    return policy_service_var.get()


def set_policy_service(policy_service: "PolicyService | None") -> Any:
    """
    Set the current authorization service in context.

    Args:
        policy_service: The authorization service to set.

    Returns:
        A token that can be used to reset the context.
    """
    return policy_service_var.set(policy_service)


@asynccontextmanager
async def policy_service_context(policy_service: "PolicyService | None"):
    """Context manager for setting up and tearing down authorization service context"""
    token = set_policy_service(policy_service)
    try:
        yield policy_service
    finally:
        policy_service_var.reset(token)


class WorkflowAction(str, Enum):
    """Actions that can be performed on a workflow."""

    WORKFLOW_LIST = "Workflow::List"
    WORKFLOW_VIEW_DETAILS = "Workflow::ViewDetails"
    WORKFLOW_RUN = "Workflow::Run"
    WORKFLOW_CANCEL = "Workflow::Cancel"


class AgentAction(str, Enum):
    """Actions that can be performed on an agent."""

    AGENT_LIST = "Agent::List"
    AGENT_VIEW_DETAILS = "Agent::ViewDetails"
    AGENT_RUN = "Agent::Run"
    AGENT_UPDATE = "Agent::Update"
    AGENT_SIMULATE = "Agent::Simulate"


class RuleAction(str, Enum):
    """Actions that can be performed on rules."""

    RULE_LIST = "Rule::List"
    RULE_VIEW_DETAILS = "Rule::ViewDetails"
    RULE_UPDATE = "Rule::Update"
    RULE_SIMULATE = "Rule::Simulate"


class ResourceType(str, Enum):
    PRINCIPAL = "Principal"
    WORKFLOW = "Workflow"
    ENTITY = "Entity"
    AGENT = "Agent"
    Rule = "Rule"


class EntityIdentifier(TypedDict):
    type: str
    id: str


class EntityUid(TypedDict):
    __entity: EntityIdentifier


class EntityDict(TypedDict):
    uid: EntityUid
    attrs: dict
    parents: list[EntityIdentifier]


@dataclass(frozen=True, slots=True)
class AgentResource:
    """`id=None` means “any agent” (wild-card)."""

    id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowResource:
    """`name=None` means “any workflow”."""

    function_name: str | None = None


@dataclass(frozen=True, slots=True)
class RuleResource:
    rule_name: str | None = None


ResourceDescriptor = AgentResource | WorkflowResource | RuleResource


class CedarEntity(BaseModel):
    resource_type: ResourceType
    resource_key: str
    resource_attributes: dict[str, Any] = {}

    def to_dict(self) -> EntityDict:
        role = self.resource_attributes.get("role", None)
        parents = []
        if role is not None:
            parents.append({"type": "Role", "id": role})

        return {
            "uid": {
                "__entity": {
                    "type": self.resource_type.value,
                    "id": str(self.resource_attributes[self.resource_key]),
                }
            },
            "attrs": {
                k: v for k, v in self.resource_attributes.items() if v is not None
            },
            "parents": parents,
        }

    @property
    def id(self) -> str:
        """
        Returns the identifier value for this CedarEntity, based on its resource_key.

        Sometimes, such as when authorizing on a list of resources, there is no id present
        for a given resource_key. In this case, we return the string "None".
        """
        return str(self.resource_attributes.get(self.resource_key))

    @staticmethod
    def from_principal(principal: Principal) -> "CedarEntity":
        """Create a CedarEntity instance from principal data.

        Args:
            principal: Principal instance

        Returns:
            CedarEntity: A new CedarEntity instance
        """
        return CedarEntity(
            resource_type=ResourceType.PRINCIPAL,
            resource_key="sub",
            resource_attributes=principal.model_dump(),
        )

    @staticmethod
    def from_workflow(function_name: str | None) -> "CedarEntity":
        """Create a CedarEntity instance from workflow data."""
        return CedarEntity(
            resource_type=ResourceType.WORKFLOW,
            resource_key="function_name",
            resource_attributes={"function_name": function_name},
        )

    @staticmethod
    def from_agent(agent_id: str | None) -> "CedarEntity":
        """Create a CedarEntity instance from agent data."""
        return CedarEntity(
            resource_type=ResourceType.AGENT,
            resource_key="agent_id",
            resource_attributes={"agent_id": agent_id},
        )

    @staticmethod
    def from_rule(rule_name: str | None) -> "CedarEntity":
        """Create a CedarEntity instance from rule data"""
        return CedarEntity(
            resource_type=ResourceType.Rule,
            resource_key="rule_name",
            resource_attributes={"rule_name": rule_name},
        )


class PolicyService:
    """Service for managing and evaluating Authorization policies."""

    def __init__(self, policy_file_path: str | None = None) -> None:
        """Initialize the Cedar policy service.

        Args:
            policy_file_path: Path to the Cedar policy file. If not provided,
                            will look for 'policies.cedar' in the current directory.
        """
        self.policy_file_path = (
            policy_file_path or "planar/security/default_policies.cedar"
        )
        self.policies = self._load_policies()

    def _load_policies(self) -> str:
        """Load Cedar policies from the specified file."""
        try:
            policy = Path(self.policy_file_path).read_text()
            formatted_policy = format_policies(policy)
            return formatted_policy
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found: {self.policy_file_path}")

    def _get_relevant_role_entities(
        self, principal_entity: EntityDict
    ) -> list[EntityDict]:
        member_role_entity_id: EntityIdentifier = {
            "type": "Role",
            "id": "member",
        }

        member_role_entity: EntityDict = {
            "uid": {
                "__entity": member_role_entity_id,
            },
            "attrs": {},
            "parents": [],
        }

        admin_role_entity_id: EntityIdentifier = {
            "type": "Role",
            "id": "admin",
        }

        admin_role_entity: EntityDict = {
            "uid": {"__entity": admin_role_entity_id},
            "attrs": {},
            "parents": [member_role_entity_id],
        }

        for parent in principal_entity["parents"]:
            if parent["type"] == "Role" and parent["id"] == "admin":
                return [admin_role_entity, member_role_entity]
            elif parent["type"] == "Role" and parent["id"] == "member":
                return [member_role_entity]

        return []

    def is_allowed(
        self,
        principal: CedarEntity,
        action: str | WorkflowAction | AgentAction | RuleAction,
        resource: CedarEntity,
    ) -> bool:
        """Check if the principal is permitted to perform the action on the resource.

        Args:
            principal: Dictionary containing principal data with all required fields
            action: The action to perform (e.g., "Workflow::Run")
            resource_type: Type of the resource (e.g., "Workflow", "DomainModel")
            resource_data: Dictionary containing resource data with all required fields

        Returns:
            bool: True if the action is permitted, False otherwise
        """
        # Create principal and resource entities
        principal_entity = principal.to_dict()
        resource_entity = resource.to_dict()

        if (
            isinstance(action, WorkflowAction)
            or isinstance(action, AgentAction)
            or isinstance(action, RuleAction)
        ):
            action = f'Action::"{action.value}"'
        else:
            action = f'Action::"{action}"'

        # Create request with principal and resource entities
        request = {
            "principal": f'Principal::"{principal.id}"',
            "action": f"{action}",
            "resource": f'{resource.resource_type.value}::"{resource.id}"',
        }

        # Add entities for this request
        entities = [
            principal_entity,
            resource_entity,
            *self._get_relevant_role_entities(principal_entity),
        ]

        # Log the authorization request
        auth_request_uuid = str(uuid.uuid4())

        logger.info(
            "authorization request",
            uuid=auth_request_uuid,
            principal=principal.id,
            action=action,
            resource=resource.id,
        )

        authz_result = is_authorized(request, self.policies, cast(list[dict], entities))

        match authz_result:
            case AuthzResult(decision=Decision.Allow):
                logger.info("authorization decision: allow", uuid=auth_request_uuid)
                return True
            case _:
                logger.warning(
                    "authorization decision: deny",
                    uuid=auth_request_uuid,
                    reasons=authz_result.diagnostics.reasons,
                    errors=authz_result.diagnostics.errors,
                )
                return False

    def reload_policies(self) -> None:
        """Reload policies from the policy file."""
        self.policies = self._load_policies()


def validate_authorization_for(
    resource_descriptor: ResourceDescriptor,
    action: WorkflowAction | AgentAction | RuleAction,
):
    authz_service = get_policy_service()

    if not authz_service:
        logger.warning("No authorization service configured, skipping authorization")
        return

    entity: CedarEntity | None = None

    match action:
        case WorkflowAction() if isinstance(resource_descriptor, WorkflowResource):
            entity = CedarEntity.from_workflow(resource_descriptor.function_name)
        case AgentAction() if isinstance(resource_descriptor, AgentResource):
            entity = CedarEntity.from_agent(resource_descriptor.id)
        case RuleAction() if isinstance(resource_descriptor, RuleResource):
            entity = CedarEntity.from_rule(resource_descriptor.rule_name)
        case _:
            raise ValueError(
                f"Invalid resource descriptor {type(resource_descriptor).__name__} for action {action}"
            )

    # Get current principal and check authorization on current resource
    principal: Principal | None = get_current_principal()
    if not principal:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not authz_service.is_allowed(
        CedarEntity.from_principal(principal),
        action,
        entity,
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to perform this action"
        )
