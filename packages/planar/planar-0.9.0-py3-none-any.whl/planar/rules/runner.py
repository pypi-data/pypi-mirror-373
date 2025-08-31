import json
from typing import Any, Literal, TypeVar, cast

from pydantic import BaseModel
from zen import ZenDecisionContent, ZenEngine

from planar.logging import get_logger
from planar.rules.models import JDMGraph

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class EvaluateResponse(BaseModel):
    success: Literal[True]
    performance: str
    result: dict
    trace: dict | None


class EvaluateError(BaseModel):
    success: Literal[False]
    title: str
    message: dict
    data: dict


def evaluate_rule(
    jdm: JDMGraph, input: dict[str, Any]
) -> EvaluateResponse | EvaluateError:
    logger.debug(
        "evaluating rule",
        input_keys=list(input.keys()),
        node_count=len(jdm.nodes),
    )
    engine = ZenEngine()
    zen_decision = engine.create_decision(cast(ZenDecisionContent, jdm.model_dump()))
    try:
        result = zen_decision.evaluate(input, {"trace": True})
        logger.info("rule evaluation successful")
        return EvaluateResponse.model_validate(
            {
                "success": True,
                "performance": result["performance"],
                "result": result["result"],
                "trace": result.get("trace", None),
            }
        )
    except RuntimeError as e:
        logger.exception("rule evaluation failed")
        error_data = json.loads(str(e))
        message = json.loads(error_data["source"])

        return EvaluateError.model_validate(
            {
                "success": False,
                "title": error_data["type"],
                "message": message,
                "data": {
                    "nodeId": error_data["nodeId"],
                },
            }
        )
