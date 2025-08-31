from __future__ import annotations

import json
from typing import Annotated, Literal, Type
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from planar.modeling.field_helpers import JsonSchema
from planar.object_config.object_config import (
    ObjectConfigurationBase,
)


class JDMBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Position(JDMBaseModel):
    """Represents the x,y coordinates of a node in the graph"""

    x: int | float
    y: int | float


class InputOutputNodeContent(JDMBaseModel):
    """Content structure for input or output nodes containing JSON schema"""

    schema_: str = Field(
        alias="schema"
    )  # JSON string representation of the input schema


class RuleTableInput(JDMBaseModel):
    """Represents an input column in a decision table"""

    id: str
    field: str | None = None  # The field name from the input schema
    name: str


class RuleTableOutput(JDMBaseModel):
    """Represents an output column in a decision table"""

    id: str
    field: str  # The field name from the output schema
    name: str


class DecisionTableNodeContent(JDMBaseModel):
    """Content structure for decision table nodes"""

    hitPolicy: Literal["first"] | Literal["collect"]  # Policy for rule evaluation
    rules: list[dict[str, str]]  # List of rule rows
    inputs: list[RuleTableInput]  # Input column definitions
    outputs: list[RuleTableOutput]  # Output column definitions

    passThrough: bool | None = None  # Whether to pass through input data
    passThorough: bool | None = (
        None  # Note: typo preserved from original implementation, see https://github.com/gorules/jdm-editor/issues/186
    )

    inputField: str | None = None  # Field mapping for input (currently unused)
    outputPath: str | None = None  # Path mapping for output (currently unused)
    executionMode: Literal["single", "loop"] | None  # Execution mode for the table


class InputNode(JDMBaseModel):
    """Represents an input node in the JDM graph"""

    id: str
    type: Literal["inputNode"]
    name: str
    content: InputOutputNodeContent
    position: Position


class DecisionTableNode(JDMBaseModel):
    """Represents a decision table node in the JDM graph"""

    id: str
    type: Literal["decisionTableNode"]
    name: str
    content: DecisionTableNodeContent
    position: Position


class OutputNode(JDMBaseModel):
    """Represents an output node in the JDM graph"""

    id: str
    type: Literal["outputNode"]
    name: str
    content: InputOutputNodeContent
    position: Position


class FunctionNodeContent(JDMBaseModel):
    """Content structure for a function node containing JavaScript source code."""

    source: str


class FunctionNode(JDMBaseModel):
    """Represents a JavaScript function node in the JDM graph."""

    id: str
    type: Literal["functionNode"]
    name: str
    content: FunctionNodeContent
    position: Position


# The gorules site sometimes uses this legacy node in their (presumably outdated) examples.
# so safe to ignore since our go rules editor frontend won't generate this node.
#
# class LegacyFunctionNode(JDMBaseModel):
#     """Represents a legacy JavaScript function node in the JDM graph.
#     The GoRules examples (such as https://editor.gorules.io/?template=shipping-fees use a legacy fn node)
#     """
#     id: str
#     type: Literal["functionNode"]
#     name: str
#     content: str
#     position: Position


class SwitchStatement(JDMBaseModel):
    """Represents a statement in a switch node."""

    id: str
    condition: str
    isDefault: bool


class SwitchNodeContent(JDMBaseModel):
    """Content structure for a switch node."""

    hitPolicy: Literal["collect", "first"]
    statements: list[SwitchStatement]


class SwitchNode(JDMBaseModel):
    """Represents a switch node in the JDM graph."""

    id: str
    type: Literal["switchNode"]
    name: str
    content: SwitchNodeContent
    position: Position


class Expression(JDMBaseModel):
    """Represents a single expression in an expression node."""

    id: str
    key: str
    value: str


class ExpressionNodeContent(JDMBaseModel):
    """Content structure for an expression node."""

    expressions: list[Expression]
    passThrough: bool | None = None  # Whether to pass through input data
    inputField: str | None = None  # Field mapping for input (currently unused)
    outputPath: str | None = None  # Path mapping for output (currently unused)
    executionMode: Literal["single", "loop"] | None = (
        None  # Execution mode for the node
    )


class ExpressionNode(JDMBaseModel):
    """Represents an expression node in the JDM graph."""

    id: str
    type: Literal["expressionNode"]
    name: str
    content: ExpressionNodeContent
    position: Position


JDMNode = (
    InputNode
    | DecisionTableNode
    | OutputNode
    | FunctionNode
    # | LegacyFunctionNode
    | SwitchNode
    | ExpressionNode
)

JDMNodeWithType = Annotated[JDMNode, Field(discriminator="type")]


class JDMEdge(JDMBaseModel):
    """Represents an edge connecting nodes in the JDM graph"""

    id: str
    type: Literal["edge"]
    sourceId: str  # ID of the source node
    targetId: str  # ID of the target node
    sourceHandle: str | None = None


class JDMGraph(JDMBaseModel):
    """
    Complete JDM (JSON Decision Model) graph structure.
    This represents a GoRules decision flow with input, processing, and output nodes.
    """

    contentType: Literal["application/vnd.gorules.decision"] | None = None
    nodes: list[JDMNodeWithType]  # All nodes in the graph
    edges: list[JDMEdge]  # All edges connecting the nodes


def create_jdm_graph(rule: Rule) -> JDMGraph:
    """
    Create a JDM (JSON Decision Model) graph based on input and output JSON schemas.

    Args:
        rule: A Rule object containing input and output Pydantic models

    Returns:
        A dictionary representing the JDM graph with nodes and edges
    """
    # Get JSON schemas from the Pydantic models
    input_json_schema = rule.input.model_json_schema()
    output_json_schema = rule.output.model_json_schema()

    # Generate UUIDs for nodes and edges
    input_node_id = str(uuid4())
    output_node_id = str(uuid4())
    rule_table_node_id = str(uuid4())
    input_to_table_edge_id = str(uuid4())
    table_to_output_edge_id = str(uuid4())

    # Create output columns for rule table based on output schema properties
    output_columns = []
    output_properties = output_json_schema.get("properties", {})

    for field_name, field_info in output_properties.items():
        column = {
            "id": str(uuid4()),
            "field": field_name,
            "name": field_name,
        }
        output_columns.append(column)

    # Create a rule with default values for each output field
    rule_values = {}
    input_column_id = str(uuid4())
    rule_values[input_column_id] = ""

    # Add values for each output column based on field type
    for column in output_columns:
        field_name = column["field"]
        field_type = output_properties.get(field_name, {}).get("type")

        if field_type == "string":
            rule_values[column["id"]] = '"default value"'
        elif field_type == "boolean":
            rule_values[column["id"]] = "true"
        elif field_type == "number":
            rule_values[column["id"]] = "0"
        elif field_type == "integer":
            rule_values[column["id"]] = "0"
        else:
            rule_values[column["id"]] = '""'

    # Create the JDM graph structure using Pydantic models
    return JDMGraph(
        nodes=[
            InputNode(
                id=input_node_id,
                type="inputNode",
                name="Input",
                content=InputOutputNodeContent(schema=json.dumps(input_json_schema)),
                position=Position(x=100, y=100),
            ),
            DecisionTableNode(
                id=rule_table_node_id,
                type="decisionTableNode",
                name="decisionTable1",
                content=DecisionTableNodeContent(
                    hitPolicy="first",
                    rules=[{"_id": str(uuid4()), **rule_values}],
                    inputs=[
                        RuleTableInput(
                            id=input_column_id,
                            name="Input",
                            field=next(
                                iter(input_json_schema.get("properties", {})), ""
                            ),
                        )
                    ],
                    outputs=[RuleTableOutput(**col) for col in output_columns],
                    passThrough=True,
                    inputField=None,
                    outputPath=None,
                    executionMode="single",
                    passThorough=False,  # Note: keeping the typo from original JS code
                ),
                position=Position(x=400, y=100),
            ),
            OutputNode(
                id=output_node_id,
                type="outputNode",
                name="Output",
                content=InputOutputNodeContent(schema=json.dumps(output_json_schema)),
                position=Position(x=700, y=100),
            ),
        ],
        edges=[
            JDMEdge(
                id=input_to_table_edge_id,
                type="edge",
                sourceId=input_node_id,
                targetId=rule_table_node_id,
            ),
            JDMEdge(
                id=table_to_output_edge_id,
                type="edge",
                sourceId=rule_table_node_id,
                targetId=output_node_id,
            ),
        ],
    )


class RuleBase(BaseModel):
    name: str
    description: str


class Rule(RuleBase):
    input: Type[BaseModel]
    output: Type[BaseModel]

    def to_config(self) -> RuleEngineConfig:
        jdm_graph = create_jdm_graph(self)
        return RuleEngineConfig(jdm=jdm_graph)


class RuleEngineConfig(BaseModel):
    jdm: JDMGraph = Field()


class RuleSerializeable(RuleBase):
    input_schema: JsonSchema
    output_schema: JsonSchema
    configs: list[ObjectConfigurationBase[RuleEngineConfig]]
