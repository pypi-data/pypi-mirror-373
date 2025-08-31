import json
from datetime import datetime, timezone
from enum import Enum
from operator import itemgetter
from pathlib import Path
from typing import Any, Dict, cast
from unittest.mock import patch
from uuid import UUID

import pytest
from pydantic import BaseModel, Field, ValidationError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.object_registry import ObjectRegistry
from planar.rules.decorator import RULE_REGISTRY, rule, serialize_for_rule_evaluation
from planar.rules.models import JDMGraph, Rule, RuleEngineConfig, create_jdm_graph
from planar.rules.rule_configuration import rule_configuration
from planar.rules.runner import EvaluateError, EvaluateResponse, evaluate_rule
from planar.workflows.decorators import workflow
from planar.workflows.execution import lock_and_execute
from planar.workflows.models import StepType, WorkflowStatus, WorkflowStep


# Test Enums
class CustomerTier(str, Enum):
    """Customer tier enumeration."""

    STANDARD = "standard"
    PREMIUM = "premium"
    VIP = "vip"


# Test data models
class PriceCalculationInput(BaseModel):
    """Input for a price calculation rule."""

    product_id: str = Field(description="Product identifier")
    base_price: float = Field(description="Base price of the product")
    quantity: int = Field(description="Quantity ordered")
    customer_tier: CustomerTier = Field(description="Customer tier")


class PriceCalculationOutput(BaseModel):
    """Output from a price calculation rule."""

    final_price: float = Field(description="Final calculated price")
    discount_applied: float = Field(description="Discount percentage applied")
    discount_reason: str = Field(description="Reason for the discount")


# Default rule implementation for testing
DEFAULT_PRICE_CALCULATION = PriceCalculationOutput(
    final_price=95.0, discount_applied=5.0, discount_reason="Standard 5% discount"
)


# Sample JDM graph for overriding the rule
PRICE_RULE_JDM_OVERRIDE = {
    "nodes": [
        {
            "id": "input-node",
            "type": "inputNode",
            "name": "Input",
            "content": {
                "schema": json.dumps(PriceCalculationInput.model_json_schema())
            },
            "position": {"x": 100, "y": 100},
        },
        {
            "id": "output-node",
            "type": "outputNode",
            "name": "Output",
            "content": {
                "schema": json.dumps(PriceCalculationOutput.model_json_schema())
            },
            "position": {"x": 700, "y": 100},
        },
        {
            "id": "function-node",
            "type": "functionNode",
            "name": "Custom Pricing Logic",
            "content": {
                "source": """
                export const handler = async (input) => {
                  let discount = 0;
                  let reason = "No discount applied";
                  
                  if (input.customer_tier === "premium") {
                    discount = 10;
                    reason = "Premium customer discount";
                  } else if (input.customer_tier === "vip") {
                    discount = 15;
                    reason = "VIP customer discount";
                  }
                  
                  if (input.quantity > 10) {
                    discount += 5;
                    reason += " + bulk order discount";
                  }
                  
                  const finalPrice = input.base_price * input.quantity * (1 - discount/100);
                  
                  return {
                    final_price: finalPrice,
                    discount_applied: discount,
                    discount_reason: reason
                  };
                };
                """
            },
            "position": {"x": 400, "y": 100},
        },
    ],
    "edges": [
        {
            "id": "edge1",
            "sourceId": "input-node",
            "targetId": "function-node",
            "type": "edge",
        },
        {
            "id": "edge2",
            "sourceId": "function-node",
            "targetId": "output-node",
            "type": "edge",
        },
    ],
}


@pytest.fixture
def price_calculation_rule():
    """Returns a rule definition for price calculation testing."""

    @rule(
        description="Calculate the final price based on product, quantity, and customer tier"
    )
    def calculate_price(input: PriceCalculationInput) -> PriceCalculationOutput:
        # In a real implementation, this would contain business logic
        # For testing, simply return the default output
        return DEFAULT_PRICE_CALCULATION

    ObjectRegistry.get_instance().register(calculate_price.__rule__)  # type: ignore

    return calculate_price


@pytest.fixture
def price_calculation_rule_with_body_variables():
    """Returns a rule definition for price calculation testing."""

    @rule(
        description="Calculate the final price based on product, quantity, and customer tier"
    )
    def calculate_price(input: PriceCalculationInput) -> PriceCalculationOutput:
        some_variable = 10
        return PriceCalculationOutput(
            final_price=input.base_price * some_variable,
            discount_applied=0,
            discount_reason="No discount applied",
        )

    return calculate_price


@pytest.fixture
def price_calculation_input():
    """Returns sample price calculation input for testing."""
    return {
        "product_id": "PROD-123",
        "base_price": 100.0,
        "quantity": 1,
        "customer_tier": "standard",
    }


async def test_rule_initialization():
    """Test that a rule function is properly initialized with the @rule decorator."""

    @rule(description="Test rule initialization")
    def test_rule(input: PriceCalculationInput) -> PriceCalculationOutput:
        return DEFAULT_PRICE_CALCULATION

    # The rule should be registered in the RULE_REGISTRY
    assert "test_rule" in RULE_REGISTRY
    registered_rule = RULE_REGISTRY["test_rule"]

    # Verify initialization
    assert registered_rule.name == "test_rule"
    assert registered_rule.description == "Test rule initialization"
    assert registered_rule.input == PriceCalculationInput
    assert registered_rule.output == PriceCalculationOutput


async def test_rule_type_validation():
    """Test that the rule decorator properly validates input and output types."""

    # Should raise ValueError when input type is not a Pydantic model
    with pytest.raises(ValueError):
        # Using Any to avoid the actual type check in pytest itself
        # The validation function in the decorator will still catch this
        @rule(description="Invalid input type")
        def invalid_input_rule(input: Any) -> PriceCalculationOutput:
            return DEFAULT_PRICE_CALCULATION

    # Should raise ValueError when output type is not a Pydantic model
    with pytest.raises(ValueError):
        # Using Any to avoid the actual type check in pytest itself
        @rule(description="Invalid output type")
        def invalid_output_rule(input: PriceCalculationInput) -> Any:
            return "Invalid"

    # Should raise ValueError when missing type annotations
    with pytest.raises(ValueError):
        # Missing type annotation for input
        @rule(description="Missing annotations")
        def missing_annotations_rule(input):
            return DEFAULT_PRICE_CALCULATION

    # Should raise ValueError when missing return type
    with pytest.raises(ValueError):
        # The decorator function should catch this
        @rule(description="Missing return type")
        def missing_return_type(input: PriceCalculationInput):
            return DEFAULT_PRICE_CALCULATION


async def test_rule_in_workflow(session: AsyncSession, price_calculation_rule):
    """Test that a rule can be used in a workflow."""

    @workflow()
    async def pricing_workflow(input_data: Dict):
        input_model = PriceCalculationInput(**input_data)
        result = await price_calculation_rule(input_model)
        return result

    # Start the workflow and run it
    input_data = {
        "product_id": "PROD-123",
        "base_price": 100.0,
        "quantity": 1,
        "customer_tier": "standard",
    }

    wf = await pricing_workflow.start(input_data)
    result = await lock_and_execute(wf)

    # Verify workflow completed successfully
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result == DEFAULT_PRICE_CALCULATION.model_dump()

    assert isinstance(result, PriceCalculationOutput)
    assert result.final_price == DEFAULT_PRICE_CALCULATION.final_price
    assert result.discount_applied == DEFAULT_PRICE_CALCULATION.discount_applied
    assert result.discount_reason == DEFAULT_PRICE_CALCULATION.discount_reason

    # Verify steps were recorded correctly
    steps = (
        await session.exec(
            select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)
        )
    ).all()
    assert len(steps) >= 1

    # Find the rule step
    rule_step = next((step for step in steps if step.step_type == StepType.RULE), None)
    assert rule_step is not None
    assert price_calculation_rule.__name__ in rule_step.function_name


async def test_rule_in_workflow_with_body_variables(
    session: AsyncSession, price_calculation_rule_with_body_variables
):
    """Test that a rule can be used in a workflow."""

    @workflow()
    async def pricing_workflow(input_data: Dict):
        input_model = PriceCalculationInput(**input_data)
        result = await price_calculation_rule_with_body_variables(input_model)
        return result

    # Start the workflow and run it
    input_data = {
        "product_id": "PROD-123",
        "base_price": 10.0,
        "quantity": 1,
        "customer_tier": "standard",
    }

    wf = await pricing_workflow.start(input_data)
    result = await lock_and_execute(wf)

    # Verify workflow completed successfully
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert (
        wf.result
        == PriceCalculationOutput(
            final_price=100.0, discount_applied=0, discount_reason="No discount applied"
        ).model_dump()
    )

    assert isinstance(result, PriceCalculationOutput)
    assert result.final_price == 100.0
    assert result.discount_applied == 0
    assert result.discount_reason == "No discount applied"


async def test_rule_override(session: AsyncSession, price_calculation_rule):
    """Test that a rule can be overridden with a JDM graph."""

    # Create and save an override
    override = RuleEngineConfig(jdm=JDMGraph.model_validate(PRICE_RULE_JDM_OVERRIDE))

    cfg = await rule_configuration.write_config(
        price_calculation_rule.__name__, override
    )
    await rule_configuration.promote_config(cfg.id)

    @workflow()
    async def pricing_workflow(input_data: Dict):
        input_model = PriceCalculationInput(**input_data)
        result = await price_calculation_rule(input_model)
        return result

    # Start the workflow with premium customer input
    premium_input = {
        "product_id": "PROD-456",
        "base_price": 100.0,
        "quantity": 5,
        "customer_tier": "premium",
    }

    wf = await pricing_workflow.start(premium_input)
    _ = await lock_and_execute(wf)

    # Verify the workflow used the override logic
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result is not None
    assert wf.result != DEFAULT_PRICE_CALCULATION.model_dump()
    assert wf.result["discount_applied"] == 10.0
    assert "Premium customer discount" in wf.result["discount_reason"]

    # Now test with VIP customer and bulk order
    vip_bulk_input = {
        "product_id": "PROD-789",
        "base_price": 100.0,
        "quantity": 15,
        "customer_tier": "vip",
    }

    wf2 = await pricing_workflow.start(vip_bulk_input)
    _ = await lock_and_execute(wf2)

    # Verify the workflow used the override logic with both discounts
    assert wf2.status == WorkflowStatus.SUCCEEDED
    assert wf2.result is not None
    assert wf2.result["discount_applied"] == 20.0  # 15% VIP + 5% bulk
    assert "VIP customer discount" in wf2.result["discount_reason"]
    assert "bulk order discount" in wf2.result["discount_reason"]


async def test_evaluate_rule_function():
    """Test the evaluate_rule function directly."""

    # Create test input data
    input_data = {
        "product_id": "PROD-123",
        "base_price": 100.0,
        "quantity": 5,
        "customer_tier": "premium",
    }

    # Test error handling
    with patch("planar.rules.runner.ZenEngine") as MockZenEngine:
        mock_decision = MockZenEngine.return_value.create_decision.return_value
        error_json = json.dumps(
            {
                "type": "RuleEvaluationError",
                "source": json.dumps({"error": "Invalid rule logic"}),
                "nodeId": "decision-table-node",
            }
        )
        mock_decision.evaluate.side_effect = RuntimeError(error_json)

        result = evaluate_rule(
            JDMGraph.model_validate(PRICE_RULE_JDM_OVERRIDE), input_data
        )

        assert isinstance(result, EvaluateError)
        assert result.success is False
        assert result.title == "RuleEvaluationError"
        assert result.message == {"error": "Invalid rule logic"}
        assert result.data["nodeId"] == "decision-table-node"


async def test_rule_override_validation(session: AsyncSession, price_calculation_rule):
    """Test validation when creating a rule override."""

    ObjectRegistry.get_instance().register(price_calculation_rule.__rule__)

    # Test with valid JDMGraph
    valid_jdm = create_jdm_graph(price_calculation_rule.__rule__)
    valid_override = RuleEngineConfig(jdm=valid_jdm)
    assert valid_override is not None
    assert isinstance(valid_override.jdm, JDMGraph)
    await rule_configuration.write_config(
        price_calculation_rule.__name__, valid_override
    )

    # Query back and verify
    configs = await rule_configuration._read_configs(price_calculation_rule.__name__)
    assert len(configs) == 1
    assert configs[0].object_name == price_calculation_rule.__name__
    assert JDMGraph.model_validate(configs[0].data.jdm) == valid_jdm

    # Test with invalid JDMGraph (missing required fields)
    with pytest.raises(ValidationError):
        # Test with incomplete dictionary
        invalid_dict = {"invalid": "structure"}
        JDMGraph.model_validate(invalid_dict)

    # Test with invalid JDMGraph type
    with pytest.raises(ValidationError):
        # Test with completely wrong type
        RuleEngineConfig(jdm="invalid_string")  # type: ignore


def test_serialize_for_rule_evaluation_dict():
    """Test serialization of dictionaries with nested datetime and UUID objects."""

    test_uuid = UUID("12345678-1234-5678-1234-567812345678")
    naive_dt = datetime(2023, 12, 25, 14, 30, 45)
    aware_dt = datetime(2023, 12, 25, 14, 30, 45, tzinfo=timezone.utc)

    test_dict = {
        "id": test_uuid,
        "created_at": naive_dt,
        "updated_at": aware_dt,
        "name": "test_item",
        "count": 42,
        "nested": {"another_id": test_uuid, "another_date": naive_dt},
    }

    serialized = serialize_for_rule_evaluation(test_dict)

    assert serialized["id"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["created_at"] == "2023-12-25T14:30:45Z"
    assert serialized["updated_at"] == "2023-12-25T14:30:45+00:00"
    assert serialized["name"] == "test_item"
    assert serialized["count"] == 42
    assert serialized["nested"]["another_id"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["nested"]["another_date"] == "2023-12-25T14:30:45Z"


def test_serialize_for_rule_evaluation():
    """Test serialization of complex nested structures."""

    test_uuid1 = UUID("12345678-1234-5678-1234-567812345678")
    test_uuid2 = UUID("87654321-4321-8765-4321-876543218765")
    naive_dt = datetime(2023, 12, 25, 14, 30, 45, 123456)
    aware_dt = datetime(2023, 12, 25, 14, 30, 45, 123456, timezone.utc)

    complex_data = {
        "metadata": {
            "id": test_uuid1,
            "created_at": naive_dt,
            "updated_at": aware_dt,
            "tags": ["tag1", "tag2", test_uuid2],
        },
        "items": [
            {
                "item_id": test_uuid1,
                "timestamp": naive_dt,
                "values": (1, 2, 3, aware_dt),
            },
            {
                "item_id": test_uuid2,
                "timestamp": aware_dt,
                "nested_list": [{"deep_uuid": test_uuid1, "deep_date": naive_dt}],
            },
        ],
        "enum_values": [CustomerTier.STANDARD],
        "simple_values": [1, "test", True, None],
    }

    serialized = serialize_for_rule_evaluation(complex_data)

    # Verify metadata
    assert serialized["metadata"]["id"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["metadata"]["created_at"] == "2023-12-25T14:30:45.123456Z"
    assert serialized["metadata"]["updated_at"] == "2023-12-25T14:30:45.123456+00:00"
    assert serialized["metadata"]["tags"][2] == "87654321-4321-8765-4321-876543218765"

    # Verify items
    assert serialized["items"][0]["item_id"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["items"][0]["timestamp"] == "2023-12-25T14:30:45.123456Z"
    assert serialized["items"][0]["values"][3] == "2023-12-25T14:30:45.123456+00:00"

    assert serialized["items"][1]["item_id"] == "87654321-4321-8765-4321-876543218765"
    assert serialized["items"][1]["timestamp"] == "2023-12-25T14:30:45.123456+00:00"
    assert (
        serialized["items"][1]["nested_list"][0]["deep_uuid"]
        == "12345678-1234-5678-1234-567812345678"
    )
    assert (
        serialized["items"][1]["nested_list"][0]["deep_date"]
        == "2023-12-25T14:30:45.123456Z"
    )

    # Verify simple values remain unchanged
    assert serialized["simple_values"] == [1, "test", True, None]


class DateTimeTestModel(BaseModel):
    """Test model with datetime fields for integration testing."""

    id: UUID = Field(description="Unique identifier")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Update timestamp")
    name: str = Field(description="Name of the item")


def test_serialize_pydantic_model_with_datetime():
    """Test serialization of Pydantic models containing datetime fields."""

    test_uuid = UUID("12345678-1234-5678-1234-567812345678")
    naive_dt = datetime(2023, 12, 25, 14, 30, 45, 123456)
    aware_dt = datetime(2023, 12, 25, 14, 30, 45, 123456, timezone.utc)

    model = DateTimeTestModel(
        id=test_uuid, created_at=naive_dt, updated_at=aware_dt, name="test_model"
    )

    # Serialize the model's dict representation
    model_dict = model.model_dump()
    serialized = serialize_for_rule_evaluation(model_dict)

    assert serialized["id"] == "12345678-1234-5678-1234-567812345678"
    assert serialized["created_at"] == "2023-12-25T14:30:45.123456Z"
    assert serialized["updated_at"] == "2023-12-25T14:30:45.123456+00:00"
    assert serialized["name"] == "test_model"


async def test_rule_with_complex_types_serialization(session: AsyncSession):
    """Integration test: Test that complex types serialization works in rule evaluation."""

    class ComplexTypesInput(BaseModel):
        event_id: UUID
        event_time: datetime
        event_name: str
        enum_value: CustomerTier

    class ComplexTypesOutput(BaseModel):
        processed_id: UUID
        processed_time: datetime
        enum_value: CustomerTier
        message: str

    @rule(description="Process datetime input")
    def process_datetime_rule(input: ComplexTypesInput) -> ComplexTypesOutput:
        # Should actually be using the rule override below.
        return ComplexTypesOutput(
            processed_id=UUID("12345678-1234-5678-1234-567812345678"),
            processed_time=datetime.now(timezone.utc),
            enum_value=CustomerTier.STANDARD,
            message="Should not be using this default rule",
        )

    ObjectRegistry.get_instance().register(process_datetime_rule.__rule__)  # type: ignore

    # Create a JDM override that uses the datetime fields
    datetime_jdm_override = {
        "nodes": [
            {
                "id": "input-node",
                "type": "inputNode",
                "name": "Input",
                "content": {
                    "schema": json.dumps(ComplexTypesInput.model_json_schema())
                },
                "position": {"x": 100, "y": 100},
            },
            {
                "id": "output-node",
                "type": "outputNode",
                "name": "Output",
                "content": {
                    "schema": json.dumps(ComplexTypesOutput.model_json_schema())
                },
                "position": {"x": 700, "y": 100},
            },
            {
                "id": "function-node",
                "type": "functionNode",
                "name": "DateTime Processing",
                "content": {
                    "source": """
                    export const handler = async (input) => {
                      return {
                        processed_id: input.event_id,
                        processed_time: input.event_time,
                        enum_value: input.enum_value,
                        message: `Override processed ${input.event_name}`
                      };
                    };
                    """
                },
                "position": {"x": 400, "y": 100},
            },
        ],
        "edges": [
            {
                "id": "edge1",
                "sourceId": "input-node",
                "targetId": "function-node",
                "type": "edge",
            },
            {
                "id": "edge2",
                "sourceId": "function-node",
                "targetId": "output-node",
                "type": "edge",
            },
        ],
    }

    # Create and save an override
    override = RuleEngineConfig(jdm=JDMGraph.model_validate(datetime_jdm_override))
    cfg = await rule_configuration.write_config(
        process_datetime_rule.__name__, override
    )
    await rule_configuration.promote_config(cfg.id)

    @workflow()
    async def datetime_workflow(input: ComplexTypesInput):
        result = await process_datetime_rule(input)
        return result

    # Test with naive datetime
    test_uuid = UUID("12345678-1234-5678-1234-567812345678")
    naive_dt = datetime(2023, 12, 25, 14, 30, 45, 123456)

    input = ComplexTypesInput(
        event_id=test_uuid,
        event_time=naive_dt,
        event_name="test_event",
        enum_value=CustomerTier.STANDARD,
    )

    wf = await datetime_workflow.start(input)
    await lock_and_execute(wf)

    # Verify the workflow completed successfully
    assert wf.status == WorkflowStatus.SUCCEEDED
    assert wf.result is not None
    assert ComplexTypesOutput.model_validate(wf.result) == ComplexTypesOutput(
        processed_id=test_uuid,
        processed_time=naive_dt.replace(tzinfo=timezone.utc),
        enum_value=CustomerTier.STANDARD,
        message="Override processed test_event",
    )


async def test_create_jdm_graph():
    """Test JDM graph generation from rule schemas."""
    rule = Rule(
        name="test_price_rule",
        description="Test price calculation rule",
        input=PriceCalculationInput,
        output=PriceCalculationOutput,
    )

    # Generate the JDM graph
    jdm_graph = create_jdm_graph(rule)

    # Verify the structure
    assert len(jdm_graph.nodes) == 3  # input, decision table, output
    assert len(jdm_graph.edges) == 2  # input->table, table->output

    # Verify node types
    node_types = {node.type for node in jdm_graph.nodes}
    assert node_types == {"inputNode", "decisionTableNode", "outputNode"}

    # Find the decision table node
    decision_table = next(
        node for node in jdm_graph.nodes if node.type == "decisionTableNode"
    )

    # Verify output columns match the output schema
    output_columns = decision_table.content.outputs
    assert len(output_columns) == 3  # final_price, discount_applied, discount_reason

    output_fields = {col.field for col in output_columns}
    assert output_fields == {"final_price", "discount_applied", "discount_reason"}

    # Verify rule values have correct default types
    rule_values = decision_table.content.rules[0]

    # Find column IDs for each field
    final_price_col = next(col for col in output_columns if col.field == "final_price")
    discount_applied_col = next(
        col for col in output_columns if col.field == "discount_applied"
    )
    discount_reason_col = next(
        col for col in output_columns if col.field == "discount_reason"
    )

    assert rule_values[final_price_col.id] == "0"  # number default
    assert rule_values[discount_applied_col.id] == "0"  # number default
    assert rule_values[discount_reason_col.id] == '"default value"'  # string default

    # Verify input and output nodes have proper schemas
    input_node = next(node for node in jdm_graph.nodes if node.type == "inputNode")
    output_node = next(node for node in jdm_graph.nodes if node.type == "outputNode")

    input_schema = json.loads(input_node.content.schema_)
    output_schema = json.loads(output_node.content.schema_)

    assert input_schema == PriceCalculationInput.model_json_schema()
    assert output_schema == PriceCalculationOutput.model_json_schema()


async def test_jdm_graph_evaluation():
    """Test evaluating a JDM graph with a simple rule."""

    # Create a rule and generate its JDM graph
    @rule(description="Test JDM evaluation")
    def simple_rule(input: PriceCalculationInput) -> PriceCalculationOutput:
        return DEFAULT_PRICE_CALCULATION

    jdm_graph = create_jdm_graph(RULE_REGISTRY[simple_rule.__name__])

    # Test input data
    test_input = {
        "product_id": "PROD-EVAL",
        "base_price": 200.0,
        "quantity": 2,
        "customer_tier": "vip",
    }

    # Evaluate the rule
    result = evaluate_rule(jdm_graph, test_input)

    # Verify the result
    assert isinstance(result, EvaluateResponse)
    assert result.success is True
    assert result.result["final_price"] == 0.0
    assert result.result["discount_applied"] == 0.0
    assert "default value" in result.result["discount_reason"]


def test_evalute_rule_with_airline_loyalty_points_calculator_rule():
    airline_loyalty_points_calculator_path = (
        Path(__file__).parent / "test_data" / "airline_loyalty_points_calculator.json"
    )
    with open(airline_loyalty_points_calculator_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "booking": {
            "fareClass": "Business",
            "routeType": "International",
            "distance": 3500,
            "isSeasonalPromotion": True,
        },
        "member": {
            "status": "Gold",
            "id": "MEM12345",
            "name": "John Smith",
            "enrollmentDate": "2020-05-15",
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "calculatedPoints": 9000,
        "seasonalPromotion": 1.5,
        "totalPoints": 9000,
    }


def test_evalute_rule_with_account_dormancy_management_rule():
    account_dormancy_management_path = (
        Path(__file__).parent / "test_data" / "account_dormancy_management.json"
    )
    with open(account_dormancy_management_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "accountId": "ACC98765432",
        "accountType": "savings",
        "customerTier": "premium",
        "lastActivityDate": "2024-11-15",
        "dormancyThreshold": 180,
        "accountBalance": 25750.45,
        "currency": "USD",
        "region": "NORTH_AMERICA",
        "contactPreference": "email",
        "customerEmail": "customer@example.com",
        "customerPhone": "+15551234567",
        "regulatoryJurisdiction": "US-NY",
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "actionPriority": "high",
        "recommendedAction": "fee_waiver",
    }


def test_evalute_rule_with_clinical_trial_eligibility_screener_rule():
    clinical_trial_eligibility_screener_path = (
        Path(__file__).parent / "test_data" / "clinical_trial_eligibility_screener.json"
    )
    with open(clinical_trial_eligibility_screener_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "patient": {
            "id": "P67890",
            "name": "John Smith",
            "age": 68,
            "diagnosis": "lung_cancer",
            "diseaseStage": "IV",
            "currentMedications": ["immunosuppressants", "albuterol", "omeprazole"],
            "priorTreatments": 3,
            "comorbidities": ["autoimmune_disease", "COPD"],
            "lastLabResults": {"wbc": 3.8, "hgb": 10.9, "plt": 150, "creatinine": 1.2},
        }
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    expected_result = {
        "decisionSummary": "Patient is not eligible for clinical trial",
        "eligibilityReasons": [
            {
                "flag": False,
                "reason": "Stage IV patients excluded from trial",
            },
            {
                "flag": True,
                "reason": "Diagnosis matches trial criteria",
            },
            {
                "flag": True,
                "reason": "Age within eligible range",
            },
            {
                "flag": False,
                "reason": "Excluded comorbidity present",
            },
            {
                "flag": False,
                "reason": "Patient taking excluded medications",
            },
            {
                "flag": False,
                "reason": "Too many prior treatments",
            },
        ],
        "failedCriteria": [
            "stage",
            "comorbidity",
            "medication",
            "priorTreatment",
        ],
        "isEligible": False,
    }

    result = cast(EvaluateResponse, result)

    def sort_reasons(reasons: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(reasons, key=itemgetter("reason"))

    assert result.success
    assert result.result["decisionSummary"] == expected_result["decisionSummary"]
    assert sort_reasons(result.result["eligibilityReasons"]) == sort_reasons(
        expected_result["eligibilityReasons"]
    )
    assert sorted(result.result["failedCriteria"]) == sorted(
        expected_result["failedCriteria"]
    )
    assert result.result["isEligible"] == expected_result["isEligible"]


def test_evalute_rule_with_customer_lifetime_value_rule():
    customer_lifetime_value_path = (
        Path(__file__).parent / "test_data" / "customer_lifetime_value.json"
    )
    with open(customer_lifetime_value_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "customer": {
            "id": "CUST-12345",
            "name": "John Doe",
            "segment": "retail",
            "acquisitionCost": 150,
            "acquisitionChannel": "paid_search",
        },
        "purchaseHistory": {
            "orderValues": [120, 89, 245, 78, 310],
            "customerDurationMonths": 18,
            "averageGrossMarginPercent": 35,
            "retentionRate": 85,
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "acquisitionCostRatio": 0.009543603664743808,
        "adjustedLTV": 15567.333333333334,
        "averageOrderValue": 168.4,
        "basicLTV": 15717.333333333334,
        "customer": {
            "acquisitionChannel": "paid_search",
            "acquisitionCost": 150,
            "id": "CUST-12345",
            "name": "John Doe",
            "segment": "retail",
        },
        "customerInsights": {
            "recommendedStrategy": "High-touch service, premium offers, exclusive events",
            "tier": "platinum",
        },
        "customerLifetimeMonths": 80,
        "grossMargin": 0.35,
        "purchaseFrequency": 3.3333333333333335,
        "purchaseHistory": {
            "averageGrossMarginPercent": 35,
            "customerDurationMonths": 18,
            "orderValues": [120, 89, 245, 78, 310],
            "retentionRate": 85,
        },
    }


def test_evaluate_rule_with_supply_chain_risk_assessment_rule():
    supply_chain_risk_assessment_path = (
        Path(__file__).parent / "test_data" / "supply_chain_risk.json"
    )
    with open(supply_chain_risk_assessment_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "supplier": {
            "name": "GlobalTech Supplies Inc.",
            "location": "medium_risk_region",
            "performanceScore": 82,
            "alternateSourcesCount": 2,
            "products": [
                {"id": "P123", "name": "Semiconductor Chip", "criticalComponent": True}
            ],
            "relationshipDurationMonths": 36,
        },
        "geopoliticalTensions": True,
        "marketVolatility": "medium",
        "supplyCategory": "electronics",
        "leadTimeData": {"averageDays": 45, "historicalVariance": 8},
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "adjustedRiskScore": 57,
        "assessment": {
            "baseRiskCategory": "medium",
            "baseRiskScore": 40,
            "recommendedAction": "Monitor supplier performance and conduct quarterly reviews",
        },
        "finalAssessment": {
            "leadTimeImpact": "minor",
            "priorityLevel": "medium",
            "riskCategory": "medium",
        },
        "geopoliticalFactor": 1.3,
        "geopoliticalTensions": True,
        "leadTimeData": {"averageDays": 45, "historicalVariance": 8},
        "marketVolatility": "medium",
        "marketVolatilityFactor": 1.1,
        "supplier": {
            "alternateSourcesCount": 2,
            "location": "medium_risk_region",
            "name": "GlobalTech Supplies Inc.",
            "performanceScore": 82,
            "products": [
                {"criticalComponent": True, "id": "P123", "name": "Semiconductor Chip"}
            ],
            "relationshipDurationMonths": 36,
        },
        "supplyCategory": "electronics",
    }


def test_evaluate_rule_with_import_duties_calculator_rule():
    import_duties_calculator_path = (
        Path(__file__).parent / "test_data" / "import_duties_calculator.json"
    )
    with open(import_duties_calculator_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "product": {
            "category": "electronics",
            "value": 1200,
            "weight": 0.8,
            "hsCode": "851712",
        },
        "origin": {"country": "CN", "hasFTA": False, "preferentialTreatment": False},
        "destination": {"country": "US"},
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "additionalFees": 0,
        "baseDuty": 180,
        "countryAdjustment": 225,
        "dutyRate": 0.1875,
        "minDuty": 225,
        "preferentialDiscount": 225,
        "totalDuty": 225,
    }


def test_evaluate_rule_with_cellular_data_rollover_system_rule():
    cellular_data_rollover_system_path = (
        Path(__file__).parent / "test_data" / "cellular_data_rollover_system.json"
    )
    with open(cellular_data_rollover_system_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "plan": {
            "type": "premium",
            "monthlyDataAllowance": 50,
            "rolloverEligible": True,
        },
        "currentBillingCycle": {
            "dataUsed": 35,
            "consecutiveRollovers": 1,
            "rolloverData": 5,
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "nextBillingCycle": {"consecutiveRollovers": 2, "status": "approved"},
        "responseMessage": "Rollover successful. You have 20 GB of rollover data available for your next billing cycle.",
    }


def test_evaluate_rule_with_online_check_in_eligibility_system_rule():
    online_check_in_eligibility_system_path = (
        Path(__file__).parent / "test_data" / "online_check_in_eligibility_system.json"
    )
    with open(online_check_in_eligibility_system_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "passenger": {
            "id": "P12345678",
            "name": "John Smith",
            "hasValidPassport": True,
            "hasValidVisa": True,
            "requiresSpecialAssistance": False,
            "frequentFlyerStatus": "gold",
        },
        "flight": {
            "flightNumber": "BA123",
            "departureTime": "2025-03-20T10:30:00Z",
            "origin": "LHR",
            "destination": "JFK",
            "requiresVisa": True,
            "hasSeatSelection": True,
            "allowsExtraBaggage": True,
            "hasSpecialMealOptions": True,
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "canAddBaggage": True,
        "canSelectSeat": True,
        "isEligible": False,
        "message": "You are eligible for online check-in.",
        "statusCode": "eligible",
    }


def test_evaluate_rule_with_warehouse_cross_docking_rule():
    warehouse_cross_docking_path = (
        Path(__file__).parent / "test_data" / "warehouse_cross_docking.json"
    )
    with open(warehouse_cross_docking_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "inboundShipmentId": "IN-12345",
        "inboundShipmentTime": "2025-03-19T10:00:00Z",
        "outboundShipmentTime": "2025-03-20T09:00:00Z",
        "matchingOutboundOrders": [
            {
                "orderId": "ORD-789",
                "customerPriority": "standard",
                "destinationZone": "East",
            },
            {
                "orderId": "ORD-790",
                "customerPriority": "premium",
                "destinationZone": "East",
            },
        ],
        "inboundShipmentItems": [
            {"sku": "ITEM-001", "quantity": 50, "category": "Electronics"},
            {"sku": "ITEM-002", "quantity": 30, "category": "Home Goods"},
        ],
        "currentStorageUsed": 7500,
        "totalStorageCapacity": 10000,
        "crossDockingBayAssignment": "Bay-E4",
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "crossDockDecision": "cross-dock",
        "crossDockingBayAssignment": "Bay-E4",
        "currentStorageUsed": 7500,
        "decisionReason": "Matching orders available within 48 hours",
        "dockingBay": "Bay-E4",
        "estimatedProcessingTime": 30,
        "hasMatchingOutboundOrders": True,
        "inboundShipmentId": "IN-12345",
        "inboundShipmentItems": [
            {"category": "Electronics", "quantity": 50, "sku": "ITEM-001"},
            {"category": "Home Goods", "quantity": 30, "sku": "ITEM-002"},
        ],
        "inboundShipmentTime": "2025-03-19T10:00:00Z",
        "matchingOutboundOrders": [
            {
                "customerPriority": "standard",
                "destinationZone": "East",
                "orderId": "ORD-789",
            },
            {
                "customerPriority": "premium",
                "destinationZone": "East",
                "orderId": "ORD-790",
            },
        ],
        "outboundShipmentTime": "2025-03-20T09:00:00Z",
        "priority": "normal",
        "timeDifferenceHours": 23,
        "totalStorageCapacity": 10000,
        "warehouseCapacityPercentage": 75,
    }


def test_evaluate_rule_with_booking_fraud_detection_rule():
    booking_fraud_detection_path = (
        Path(__file__).parent / "test_data" / "booking_fraud_detection.json"
    )
    with open(booking_fraud_detection_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "booking": {
            "payment_method": "prepaid_card",
            "amount": 2500,
            "ip_country": "US",
        },
        "account": {"country": "US", "bookings_last_24h": 6},
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "flags": {"manual_review": True, "requires_verification": True},
    }


def test_evaluate_rule_with_applicant_risk_assessment_rule():
    applicant_risk_assessment_path = (
        Path(__file__).parent / "test_data" / "applicant_risk_assessment.json"
    )
    with open(applicant_risk_assessment_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "applicant": {
            "creditScore": 710,
            "latePayments": 1,
            "creditHistoryMonths": 48,
            "employmentMonths": 36,
            "incomeVerification": "complete",
            "bankAccountStanding": "good",
            "debtToIncomeRatio": 0.35,
            "outstandingLoans": 2,
        }
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result == {
        "applicant": {
            "bankAccountStanding": "good",
            "creditHistoryMonths": 48,
            "creditScore": 710,
            "debtToIncomeRatio": 0.35,
            "employmentMonths": 36,
            "incomeVerification": "complete",
            "latePayments": 1,
            "outstandingLoans": 2,
        },
        "approvalStatus": "manual-review",
        "interestRateModifier": 0,
        "negativeFactors": [],
        "negativeFactorsCount": 0,
        "riskCategory": "medium",
        "scores": {"creditHistory": 20, "debtToIncome": 15, "incomeStability": 20},
        "totalRiskScore": 55,
    }


def test_evaluate_rule_with_insurance_prior_authorization_rule():
    insurance_prior_authorization_path = (
        Path(__file__).parent / "test_data" / "insurance_prior_authorization.json"
    )
    with open(insurance_prior_authorization_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "patientInfo": {"insuranceType": "Commercial"},
        "diagnosisCodes": ["M54.5", "M51.26"],
        "serviceType": "Imaging",
        "serviceDetails": {
            "code": "70551",
            "cost": 1200,
            "isEmergency": False,
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success
    assert cast(EvaluateResponse, result).result["requiresAuthorization"]
    assert (
        cast(EvaluateResponse, result).result["reason"]
        == "Advanced imaging requires prior authorization"
    )


def test_evaluate_rule_with_portfolio_risk_monitor_rule():
    portfolio_risk_monitor_path = (
        Path(__file__).parent / "test_data" / "portfolio_risk_monitor.json"
    )
    with open(portfolio_risk_monitor_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "customer": {
            "id": "cust-78945",
            "name": "John Smith",
            "riskTolerance": "moderate",
            "investmentHorizon": "long-term",
            "preferences": {
                "allowAutomaticAdjustments": True,
                "alertThreshold": "moderate",
                "communicationPreference": "email",
            },
        },
        "portfolio": {
            "id": "port-12345",
            "name": "Retirement Portfolio",
            "totalValue": 750000,
            "creationDate": "2019-05-12",
            "lastRebalance": 95,
            "volatility": 22.5,
            "highRiskPercentage": 35,
            "currentAllocation": {"equity": 65, "bonds": 25, "cash": 10},
            "targetAllocation": {"equity": 60, "bonds": 35, "cash": 5},
            "holdings": [
                {
                    "symbol": "VTI",
                    "category": "equity",
                    "percentage": 30,
                    "value": 225000,
                },
                {
                    "symbol": "VXUS",
                    "category": "equity",
                    "percentage": 20,
                    "value": 150000,
                },
                {
                    "symbol": "VGT",
                    "category": "equity",
                    "percentage": 15,
                    "value": 112500,
                },
                {
                    "symbol": "BND",
                    "category": "bonds",
                    "percentage": 25,
                    "value": 187500,
                },
                {
                    "symbol": "CASH",
                    "category": "cash",
                    "percentage": 10,
                    "value": 75000,
                },
            ],
        },
        "market": {
            "volatilityIndex": 28.5,
            "trendPercentage": -12.5,
            "interestRate": 3.75,
            "sectorPerformance": {
                "technology": -15.2,
                "healthcare": -5.1,
                "financials": -18.4,
                "consumerStaples": -3.2,
                "utilities": 1.5,
            },
            "economicIndicators": {
                "gdpGrowth": 0.8,
                "inflation": 4.2,
                "unemploymentRate": 4.1,
            },
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success

    assert cast(EvaluateResponse, result).result["action"] == "rebalance"
    assert cast(EvaluateResponse, result).result["outcome"] == {
        "riskScore": 0.53,
        "status": "rebalance_suggested",
        "timestamp": cast(EvaluateResponse, result).result["outcome"]["timestamp"],
    }

    assert cast(EvaluateResponse, result).result["rebalanceDetails"] == {
        "currentAllocation": {"bonds": 25, "cash": 10, "equity": 65},
        "customerId": "cust-78945",
        "date": cast(EvaluateResponse, result).result["rebalanceDetails"]["date"],
        "driftPercentage": "5.0",
        "message": "Rebalancing recommended: Portfolio has drifted 5.0% from target allocation.",
        "portfolioId": "port-12345",
        "riskCategory": "high",
        "riskScore": 0.53,
        "suggestedChanges": {"bonds": 10, "cash": -5, "equity": -5},
        "targetAllocation": {"bonds": 35, "cash": 5, "equity": 60},
    }


def test_evaluate_rule_with_order_consolidation_system_rule():
    order_consolidation_system_path = (
        Path(__file__).parent / "test_data" / "order_consolidation_system.json"
    )
    with open(order_consolidation_system_path, "r", encoding="utf-8") as f:
        jdm_dict = json.load(f)

    input_data = {
        "orders": [
            {
                "orderId": "ORD-12345",
                "customerName": "John Smith",
                "deliveryAddress": {
                    "street": "123 Main St",
                    "city": "Springfield",
                    "state": "IL",
                    "zipCode": "62704",
                    "coordinates": {"latitude": 39.7817, "longitude": -89.6501},
                },
                "requestedDeliveryDate": "2025-03-25T14:00:00Z",
                "orderWeight": 12.5,
                "orderItems": 3,
            },
            {
                "orderId": "ORD-12346",
                "customerName": "Jane Doe",
                "deliveryAddress": {
                    "street": "456 Oak Ave",
                    "city": "Springfield",
                    "state": "IL",
                    "zipCode": "62702",
                    "coordinates": {"latitude": 39.8021, "longitude": -89.6443},
                },
                "requestedDeliveryDate": "2025-03-25T16:00:00Z",
                "orderWeight": 8.2,
                "orderItems": 2,
            },
        ],
        "distanceKm": 35,
        "deliveryWindowDifferenceHours": 24,
        "availableCarrierCapacity": 4,
        "orderWeight1": 12.5,
        "orderWeight2": 8.2,
        "carrierDetails": {
            "carrierId": "CAR-789",
            "maxCapacity": 500,
            "currentLoad": 320,
        },
    }

    result = evaluate_rule(JDMGraph.model_validate(jdm_dict), input_data)

    assert result.success

    assert cast(EvaluateResponse, result).result["canConsolidate"]
    assert cast(EvaluateResponse, result).result["schedulingPriority"] == "high"
    assert cast(EvaluateResponse, result).result["availableCarrierCapacity"] == 4
    assert cast(EvaluateResponse, result).result["carrierDetails"] == {
        "carrierId": "CAR-789",
        "currentLoad": 320,
        "maxCapacity": 500,
    }
    assert (
        cast(EvaluateResponse, result).result["consolidationAction"]
        == "immediate_consolidation"
    )
    assert cast(EvaluateResponse, result).result["consolidationPriority"] == "high"
    assert cast(EvaluateResponse, result).result["consolidationWeight"] == 20.7
    assert cast(EvaluateResponse, result).result["costSavingEstimate"] == 23.75
    assert cast(EvaluateResponse, result).result["costSavingsReport"] == {
        "fuelSavings": 5.25,
        "laborSavings": 23.75,
        "totalSavings": 29,
    }

    assert cast(EvaluateResponse, result).result["deliverySchedule"] == {
        "estimatedDeliveryTime": None,
        "notificationRequired": False,
        "type": "consolidated",
    }
    assert cast(EvaluateResponse, result).result["deliveryWindowDifferenceHours"] == 24
    assert cast(EvaluateResponse, result).result["distanceKm"] == 35
    assert cast(EvaluateResponse, result).result["expectedFuelSavings"] == 5.25
    assert (
        cast(EvaluateResponse, result).result["explanation"]
        == "Orders are nearby, delivery window compatible, and carrier has capacity"
    )
    assert cast(EvaluateResponse, result).result["orderWeight1"] == 12.5
    assert cast(EvaluateResponse, result).result["orderWeight2"] == 8.2
    assert cast(EvaluateResponse, result).result["orders"] == [
        {
            "customerName": "John Smith",
            "deliveryAddress": {
                "city": "Springfield",
                "coordinates": {"latitude": 39.7817, "longitude": -89.6501},
                "state": "IL",
                "street": "123 Main St",
                "zipCode": "62704",
            },
            "orderId": "ORD-12345",
            "orderItems": 3,
            "orderWeight": 12.5,
            "requestedDeliveryDate": "2025-03-25T14:00:00Z",
        },
        {
            "customerName": "Jane Doe",
            "deliveryAddress": {
                "city": "Springfield",
                "coordinates": {"latitude": 39.8021, "longitude": -89.6443},
                "state": "IL",
                "street": "456 Oak Ave",
                "zipCode": "62702",
            },
            "orderId": "ORD-12346",
            "orderItems": 2,
            "orderWeight": 8.2,
            "requestedDeliveryDate": "2025-03-25T16:00:00Z",
        },
    ]
