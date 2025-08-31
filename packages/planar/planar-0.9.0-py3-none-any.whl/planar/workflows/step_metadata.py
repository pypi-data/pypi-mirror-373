"""
Utility functions for gathering rich metadata for workflow steps.

This module provides helper functions for getting step-specific
metadata for the various step types in Planar workflows.
"""

from typing import Annotated, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import select

from planar.ai.models import ToolCall
from planar.ai.utils import AgentSerializeable, get_agent_serializable
from planar.human import HumanTask, get_human_tasks
from planar.logging import get_logger
from planar.object_registry import ObjectRegistry
from planar.rules.models import (
    RuleSerializeable,
)
from planar.rules.rule_configuration import rule_configuration
from planar.session import get_session
from planar.workflows.models import StepType, WorkflowStep

logger = get_logger(__name__)


class HumanTaskMetadata(BaseModel):
    """Metadata wrapper for human task steps."""

    step_type: Literal[StepType.HUMAN_IN_THE_LOOP] = StepType.HUMAN_IN_THE_LOOP
    human_task: HumanTask


class AgentMetadata(BaseModel):
    """Metadata wrapper for agent steps."""

    step_type: Literal[StepType.AGENT] = StepType.AGENT
    agent: AgentSerializeable


class RuleMetadata(BaseModel):
    """Metadata wrapper for rule steps."""

    step_type: Literal[StepType.RULE] = StepType.RULE
    rule: RuleSerializeable


class ToolCallMetadata(BaseModel):
    """Metadata wrapper for tool call steps."""

    step_type: Literal[StepType.TOOL_CALL] = StepType.TOOL_CALL
    tool_call: ToolCall


StepMetadata = Annotated[
    Union[
        HumanTaskMetadata,
        AgentMetadata,
        RuleMetadata,
        ToolCallMetadata,
    ],
    Field(discriminator="step_type"),
]


def extract_simple_name(fully_qualified_name: str) -> str:
    """
    Extract the last part of a fully qualified name.

    For example: 'module.directory.fn_name' becomes 'fn_name'.
    If there are no periods in the string, returns the original string.

    Args:
        fully_qualified_name: A possibly fully qualified name with dot separators

    Returns:
        The last part of the name
    """
    return (
        fully_qualified_name.split(".")[-1]
        if "." in fully_qualified_name
        else fully_qualified_name
    )


async def get_human_step_metadata(
    workflow_id: UUID, step_id: int
) -> Optional[HumanTaskMetadata]:
    """
    Get metadata for a human-in-the-loop step.

    Args:
        workflow_id: The ID of the workflow
        step_id: The ID of the step

    Returns:
        A HumanTaskMetadata object, or None if no task is found
    """
    # Get human tasks for this workflow
    tasks = await get_human_tasks(workflow_id=workflow_id)

    # Tasks are ordered by creation time, newest first
    # For now, we'll assume the most recent task is associated with this step
    # In the future, we may want to add a step_id field to HumanTask for direct correlation
    if not tasks:
        logger.debug("no human tasks found", workflow_id=workflow_id, step_id=step_id)
        return None

    task = tasks[0]
    logger.debug(
        "found human task",
        task_id=task.id,
        workflow_id=workflow_id,
        step_id=step_id,
    )
    return HumanTaskMetadata(human_task=task)


async def get_agent_step_metadata(
    workflow_id: UUID, step_id: int, registry: ObjectRegistry
) -> Optional[AgentMetadata]:
    """
    Get metadata for an agent step.

    Args:
        workflow_id: The ID of the workflow
        step_id: The ID of the step
        registry: ObjectRegistry instance for looking up agents

    Returns:
        An AgentMetadata object, or None if no metadata is found
    """
    session = get_session()

    logger.debug(
        "getting agent step metadata", workflow_id=workflow_id, step_id=step_id
    )
    async with session.begin_read():
        step = (
            await session.exec(
                select(WorkflowStep).where(
                    (WorkflowStep.workflow_id == workflow_id)
                    & (WorkflowStep.step_id == step_id)
                )
            )
        ).first()

    if not step or not step.display_name:
        logger.debug(
            "agent step or display_name not found",
            workflow_id=workflow_id,
            step_id=step_id,
        )
        return None

    agent_name = step.display_name
    logger.debug("agent name from step display_name", agent_name=agent_name)

    agent_serializable = await get_agent_serializable(
        agent_name=agent_name, registry=registry
    )

    if not agent_serializable:
        logger.debug("agent serializable not found", agent_name=agent_name)
        return None

    logger.info("agent metadata retrieved", agent_name=agent_name)
    return AgentMetadata(agent=agent_serializable)


async def get_rule_step_metadata(
    workflow_id: UUID, step_id: int, registry: ObjectRegistry
) -> Optional[RuleMetadata]:
    """
    Get metadata for a rule step.

    Args:
        workflow_id: The ID of the workflow
        step_id: The ID of the step

    Returns:
        A RuleMetadata object, or None if no metadata is found
    """
    session = get_session()

    logger.debug("getting rule step metadata", workflow_id=workflow_id, step_id=step_id)
    async with session.begin_read():
        step = (
            await session.exec(
                select(WorkflowStep).where(
                    (WorkflowStep.workflow_id == workflow_id)
                    & (WorkflowStep.step_id == step_id)
                )
            )
        ).first()

    if not step:
        logger.debug("rule step not found", workflow_id=workflow_id, step_id=step_id)
        return None

    rule_name = extract_simple_name(step.function_name)
    logger.debug("rule name extracted", rule_name=rule_name)

    rule = next((r for r in registry.get_rules() if r.name == rule_name), None)

    if not rule:
        logger.debug("rule not found in registry", rule_name=rule_name)
        return None

    configs = await rule_configuration.read_configs_with_default(
        rule_name, rule.to_config()
    )
    logger.debug(
        "retrieved configs for rule",
        count=len(configs),
        rule_name=rule_name,
    )

    rule_serializable = RuleSerializeable(
        input_schema=rule.input.model_json_schema(),
        output_schema=rule.output.model_json_schema(),
        name=rule_name,
        description=step.display_name or rule_name,
        configs=configs,
    )
    logger.info("rule metadata retrieved", rule_name=rule_name)
    return RuleMetadata(rule=rule_serializable)


async def get_tool_call_step_metadata(
    workflow_id: UUID, step_id: int
) -> Optional[ToolCallMetadata]:
    """
    Get metadata for a tool call step.

    Args:
        workflow_id: The ID of the workflow
        step_id: The ID of the step

    Returns:
        A ToolCallMetadata object, or None if no metadata is found
    """
    session = get_session()

    logger.debug(
        "getting tool call step metadata", workflow_id=workflow_id, step_id=step_id
    )
    async with session.begin_read():
        step = (
            await session.exec(
                select(WorkflowStep).where(
                    (WorkflowStep.workflow_id == workflow_id)
                    & (WorkflowStep.step_id == step_id)
                )
            )
        ).first()

        if not step:
            logger.debug(
                "tool call step not found", workflow_id=workflow_id, step_id=step_id
            )
            return None
        tool_name = extract_simple_name(step.function_name)
        logger.debug("tool name extracted", tool_name=tool_name)

        # Get the parent step if available
        parent_step = None
        if step.parent_step_id:
            logger.debug(
                "fetching parent step for tool call step",
                parent_step_id=step.parent_step_id,
                step_id=step_id,
            )
            parent_step = (
                await session.exec(
                    select(WorkflowStep).where(
                        (WorkflowStep.workflow_id == workflow_id)
                        & (WorkflowStep.step_id == step.parent_step_id)
                    )
                )
            ).first()
            logger.debug("parent step found", found=parent_step is not None)

    tool_call_id = None
    if parent_step and parent_step.result and isinstance(parent_step.result, dict):
        if "tool_calls" in parent_step.result:
            for tc in parent_step.result["tool_calls"]:
                if tc.get("name") == tool_name:
                    tool_call_id = tc.get("id")
                    logger.debug(
                        "found tool_call_id for tool in parent step result",
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                    )
                    break

    if not tool_call_id:
        logger.debug("could not determine tool_call_id for tool", tool_name=tool_name)

    tool_call_obj = ToolCall(
        id=tool_call_id, name=tool_name, arguments=step.kwargs or {}
    )
    logger.info("tool call metadata retrieved", tool_name=tool_name)
    return ToolCallMetadata(tool_call=tool_call_obj)


async def get_steps_metadata(
    steps: List[WorkflowStep], registry: ObjectRegistry
) -> Dict[int, StepMetadata]:
    """
    Get metadata for multiple steps efficiently.

    Args:
        steps: A list of workflow steps
        registry: Optional ObjectRegistry instance for looking up agents

    Returns:
        A dictionary mapping step_id to strongly-typed StepMetadata objects
    """
    result = {}

    human_steps = [s for s in steps if s.step_type == StepType.HUMAN_IN_THE_LOOP]
    agent_steps = [s for s in steps if s.step_type == StepType.AGENT]
    rule_steps = [s for s in steps if s.step_type == StepType.RULE]
    tool_call_steps = [s for s in steps if s.step_type == StepType.TOOL_CALL]

    if human_steps:
        for step in human_steps:
            metadata = await get_human_step_metadata(step.workflow_id, step.step_id)
            if metadata:
                result[step.step_id] = metadata

    if agent_steps:
        for step in agent_steps:
            metadata = await get_agent_step_metadata(
                step.workflow_id, step.step_id, registry
            )
            if metadata:
                result[step.step_id] = metadata

    if rule_steps:
        for step in rule_steps:
            metadata = await get_rule_step_metadata(
                step.workflow_id, step.step_id, registry
            )
            if metadata:
                result[step.step_id] = metadata

    if tool_call_steps:
        for step in tool_call_steps:
            metadata = await get_tool_call_step_metadata(step.workflow_id, step.step_id)
            if metadata:
                result[step.step_id] = metadata

    return result
