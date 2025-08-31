"""
Used to track what objects have been registered with a PlanarAppinstance

Note that in planar/workflows/execution.py, we also have a registry of workflows
called _WORKFLOW_FUNCTION_REGISTRY. However, that registry is internal to the implementation
of workflows. Do not use that registry.
"""

from __future__ import annotations

from typing import Type

from planar.ai.agent import Agent
from planar.modeling.orm.planar_base_entity import PlanarBaseEntity
from planar.registry_items import RegisteredWorkflow
from planar.rules.models import Rule
from planar.workflows.decorators import WorkflowWrapper


# singleton
class ObjectRegistry:
    _instance: ObjectRegistry | None = None

    _rules: dict[str, Rule]
    _workflows: dict[str, RegisteredWorkflow]
    _entities: dict[str, Type[PlanarBaseEntity]]
    _agents: dict[str, Agent]

    def __new__(cls) -> ObjectRegistry:
        if cls._instance is None:
            cls._instance = super(ObjectRegistry, cls).__new__(cls)

            cls._instance._rules = {}
            cls._instance._workflows = {}
            cls._instance._entities = {}
            cls._instance._agents = {}

        return cls._instance

    @staticmethod
    def get_instance() -> ObjectRegistry:
        if ObjectRegistry._instance is None:
            return ObjectRegistry()

        return ObjectRegistry._instance

    def register(
        self, obj: Type[PlanarBaseEntity] | "WorkflowWrapper" | "Agent" | "Rule"
    ) -> None:
        """
        Register a PlanarBaseEntity or WorkflowWrapper object.
        Adding the same object more than once is a no-op.

        Note that when registering a WorkflowWrapper, its rules are also registered as there is no
        explicit registration of rules API. It's implicit the moment a rule function (@rule) is invoked
        from within a workflow.
        """

        if isinstance(obj, type) and issubclass(obj, PlanarBaseEntity):
            self._entities[obj.__name__] = obj
        elif isinstance(obj, WorkflowWrapper):
            self._workflows[obj.function_name] = RegisteredWorkflow.from_workflow(obj)
        elif isinstance(obj, Agent):
            self._agents[obj.name] = obj
        elif isinstance(obj, Rule):
            self._rules[obj.name] = obj

    def get_entities(self) -> list[Type[PlanarBaseEntity]]:
        """
        Get all registered PlanarBaseEntity objects.
        """
        return list(self._entities.values())

    def get_workflows(self) -> list[RegisteredWorkflow]:
        """
        Get all registered WorkflowWrapper objects.
        """
        return list(self._workflows.values())

    def get_rules(self) -> list[Rule]:
        """
        Get all registered rule objects.
        """
        return list(self._rules.values())

    def get_agents(self) -> list[Agent]:
        """
        Get all registered Agent objects.
        """
        return list(self._agents.values())

    def reset(self) -> None:
        """
        Reset the registry by clearing all registered objects.
        This is useful for testing to ensure clean state between tests.
        """
        self._rules = {}
        self._workflows = {}
        self._entities = {}
        self._agents = {}
