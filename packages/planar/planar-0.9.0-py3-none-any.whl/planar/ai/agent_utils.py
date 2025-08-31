import inspect
from typing import (
    Any,
    Callable,
    Dict,
)

from jinja2 import StrictUndefined, TemplateError
from jinja2.sandbox import SandboxedEnvironment
from pydantic import BaseModel, create_model

from planar.ai.models import (
    AgentConfig,
    ToolDefinition,
)
from planar.files.models import PlanarFile
from planar.logging import get_logger
from planar.object_config import ConfigurableObjectType, ObjectConfigurationIO
from planar.workflows import step

logger = get_logger(__name__)


class ModelSpec(BaseModel):
    """Pydantic model for AI model specifications."""

    model_id: str
    parameters: dict[str, Any] = {}


def extract_files_from_model(
    model: BaseModel | str | None,
) -> list[PlanarFile]:
    """
    Extract files from a Pydantic model. We extract any top-level or nested fields
    that are of type `PlanarFile`, or are a list of `PlanarFile`.

    Args:
        model: The Pydantic model to extract files from.

    Returns:
        A list of PlanarFile objects.
    """

    if model is None:
        return []

    if isinstance(model, PlanarFile):
        return [model]

    if isinstance(model, str):
        return []

    files: list[PlanarFile] = []
    for field_name in type(model).model_fields:
        value = getattr(model, field_name)
        match value:
            case PlanarFile() as f:
                files.append(f)
            case BaseModel():
                files.extend(extract_files_from_model(value))
            case [*items]:
                files.extend(item for item in items if isinstance(item, PlanarFile))
            case _:
                pass
    return files


# Jinja environment for safely rendering templates
_JINJA_ENV = SandboxedEnvironment(undefined=StrictUndefined)


def render_template(template: str, context: Dict[str, Any]) -> str:
    """Render a template string using a sandboxed Jinja environment."""
    try:
        return _JINJA_ENV.from_string(template).render(context)
    except TemplateError as exc:
        logger.exception("error rendering jinja template")
        raise ValueError(f"Error rendering prompt: {exc}") from exc


agent_configuration = ObjectConfigurationIO(AgentConfig, ConfigurableObjectType.AGENT)


@step(display_name="Agent Config")
async def get_agent_config(agent_name: str, agent_config: AgentConfig) -> AgentConfig:
    """
    Retrieve agent configuration overrides from the database.

    Args:
        agent_name: Name of the agent instance.

    Returns:
        AgentOverrideConfig
    """
    logger.debug("getting agent config", agent_name=agent_name)
    configs = await agent_configuration.read_configs_with_default(
        agent_name, agent_config
    )

    active_config = next((config for config in configs if config.active), None)

    if not active_config:
        logger.warning("no active configuration found for agent", agent_name=agent_name)
        raise ValueError(f"No active configuration found for agent {agent_name}")

    logger.info(
        "active configuration found for agent",
        version=active_config.version,
        agent_name=agent_name,
    )
    return active_config.data


def create_tool_definition(tool_fn: Callable) -> ToolDefinition:
    """Create a ToolDefinition from a function using a Pydantic model."""
    sig = inspect.signature(tool_fn)
    doc = inspect.getdoc(tool_fn) or ""
    name = tool_fn.__name__

    fields = {}
    for param_name, param in sig.parameters.items():
        param_type = (
            param.annotation if param.annotation != inspect.Parameter.empty else Any
        )
        default_value = (
            param.default if param.default != inspect.Parameter.empty else ...
        )
        fields[param_name] = (param_type, default_value)

    model_name = f"{name.capitalize()}Parameters"
    parameters_model = create_model(
        model_name, __config__={"extra": "forbid"}, **fields
    )

    return ToolDefinition(
        name=name,
        description=doc,
        parameters=parameters_model.model_json_schema(),
    )
