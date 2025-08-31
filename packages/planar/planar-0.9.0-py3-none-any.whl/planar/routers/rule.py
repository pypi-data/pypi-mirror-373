from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from planar.logging import get_logger
from planar.object_config.object_config import (
    ConfigValidationError,
    ConfigValidationErrorResponse,
)
from planar.object_registry import ObjectRegistry
from planar.rules import RuleSerializeable
from planar.rules.models import JDMGraph, Rule, RuleEngineConfig
from planar.rules.rule_configuration import rule_configuration
from planar.rules.runner import (
    EvaluateError,
    EvaluateResponse,
    evaluate_rule,
)
from planar.security.authorization import (
    RuleAction,
    RuleResource,
    validate_authorization_for,
)

logger = get_logger(__name__)


class EvaluateRuleRequest(BaseModel):
    input: dict
    graph: JDMGraph


def create_rule_router(object_registry: ObjectRegistry) -> APIRouter:
    router = APIRouter(tags=["Rules"])

    @router.get("/", response_model=list[RuleSerializeable])
    async def get_rules():
        validate_authorization_for(RuleResource(), RuleAction.RULE_LIST)
        rules = object_registry.get_rules()

        return [await into_rule_serializeable(rule) for rule in rules]

    @router.get("/{rule_name}", response_model=RuleSerializeable)
    async def get_rule(rule_name: str):
        validate_authorization_for(
            RuleResource(rule_name), RuleAction.RULE_VIEW_DETAILS
        )
        rules = object_registry.get_rules()
        rule = next((d for d in rules if d.name == rule_name), None)

        if not rule:
            raise HTTPException(status_code=404, detail="rule not found")

        return await into_rule_serializeable(rule)

    @router.post("/simulate", response_model=EvaluateResponse | EvaluateError)
    async def simulate_rule(request: EvaluateRuleRequest = Body(...)):
        validate_authorization_for(RuleResource(), RuleAction.RULE_SIMULATE)
        return evaluate_rule(request.graph, request.input)

    @router.post(
        "/{rule_name}",
        response_model=RuleSerializeable,
        responses={
            400: {
                "model": ConfigValidationErrorResponse,
                "description": "Configuration validation failed",
            },
            404: {"description": "Rule not found"},
        },
    )
    async def save_rule_override(rule_name: str, jdm: JDMGraph = Body(...)):
        validate_authorization_for(RuleResource(rule_name), RuleAction.RULE_UPDATE)
        rules = object_registry.get_rules()
        rule = next((d for d in rules if d.name == rule_name), None)

        if not rule:
            raise HTTPException(status_code=404, detail="rule not found")

        # Create the rule configuration
        rule_config = RuleEngineConfig(jdm=jdm)

        try:
            await rule_configuration.write_config(rule_name, rule_config)
        except ConfigValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=e.to_api_response().model_dump(mode="json", by_alias=True),
            )

        logger.info("rule override saved", rule_name=rule_name)

        return await into_rule_serializeable(rule)

    return router


async def into_rule_serializeable(rule: Rule) -> RuleSerializeable:
    config_list = await rule_configuration.read_configs_with_default(
        rule.name, rule.to_config()
    )

    return RuleSerializeable(
        input_schema=rule.input.model_json_schema(),
        output_schema=rule.output.model_json_schema(),
        name=rule.name,
        description=rule.description,
        configs=config_list,
    )
