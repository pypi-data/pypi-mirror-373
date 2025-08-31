import json
from typing import Any

from planar.object_config import ConfigurableObjectType, ObjectConfigurationIO
from planar.object_config.models import (
    ConfigDiagnosticIssue,
    ConfigDiagnostics,
    DiffErrorCode,
)
from planar.object_registry import ObjectRegistry
from planar.rules.models import JDMGraph, JDMNode, RuleEngineConfig, create_jdm_graph


def node_diff(
    reference: JDMNode | dict,
    current: JDMNode | dict,
    for_object: str,
    path: str = "",
) -> list[ConfigDiagnosticIssue]:
    """
    Recursively compare two dictionaries and return a list of diagnostics.

    Args:
        reference: The reference dictionary to compare against
        current: The current dictionary being validated
        path: The current field path (used for nested objects)

    Returns:
        List of DiffDiagnostic objects describing the differences found
    """
    diagnostics = []

    reference_dict = (
        reference.model_dump() if isinstance(reference, JDMNode) else reference
    )
    current_dict = current.model_dump() if isinstance(current, JDMNode) else current

    # First pass: Check reference against current
    for key, ref_value in reference_dict.items():
        current_path = f"{path}.{key}" if path else key

        if key not in current_dict:
            # Missing field in current
            diagnostics.append(
                ConfigDiagnosticIssue.model_validate(
                    {
                        "error_code": DiffErrorCode.MISSING_FIELD,
                        "field_path": current_path,
                        "message": f"Field '{current_path}' is missing in current node",
                        "reference_value": ref_value,
                        "current_value": None,
                        "for_object": for_object,
                    }
                )
            )
        else:
            current_value = current_dict[key]

            # Both are dictionaries - recurse
            if (isinstance(ref_value, dict) and isinstance(current_value, dict)) or (
                isinstance(ref_value, JDMNode) and isinstance(current_value, JDMNode)
            ):
                nested_diagnostics = node_diff(
                    ref_value,
                    current_value,
                    for_object,
                    current_path,
                )
                diagnostics.extend(nested_diagnostics)

            # Values are different (and not both dicts)
            elif ref_value != current_value:
                diagnostics.append(
                    ConfigDiagnosticIssue.model_validate(
                        {
                            "error_code": DiffErrorCode.VALUE_MISMATCH,
                            "field_path": current_path,
                            "message": f"Value mismatch at '{current_path}': expected {ref_value}, got {current_value}",
                            "reference_value": ref_value,
                            "current_value": current_value,
                            "for_object": for_object,
                        }
                    )
                )

    # Second pass: Check current for extra fields not in reference
    for key, current_value in current_dict.items():
        current_path = f"{path}.{key}" if path else key

        if key not in reference_dict:
            diagnostics.append(
                ConfigDiagnosticIssue.model_validate(
                    {
                        "error_code": DiffErrorCode.EXTRA_FIELD,
                        "field_path": current_path,
                        "message": f"Extra field '{current_path}' found in current node",
                        "reference_value": None,
                        "current_value": current_value,
                        "for_object": for_object,
                    }
                )
            )

    return diagnostics


def get_input_and_output_node_schemas(
    jdm: JDMGraph,
) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes = jdm.nodes

    input_node = next((node for node in nodes if node.type == "inputNode"), None)
    output_node = next((node for node in nodes if node.type == "outputNode"), None)

    # if a jdm graph was uploaded from a 3rd party site such as https://editor.gorules.io/?template=shipping-fees
    # then the schema will just be "", and json.loads will raise an error trying to parse an empty string
    input_schema = (
        json.loads(input_node.content.schema_)
        if input_node and input_node.content.schema_
        else {}
    )
    output_schema = (
        json.loads(output_node.content.schema_)
        if output_node and output_node.content.schema_
        else {}
    )

    return input_schema, output_schema


def validate_config(
    name: str,
    config: RuleEngineConfig,
) -> ConfigDiagnostics:
    """
    Validate a configuration against a default configuration using JDM nodes comparison.

    Args:
        config: The configuration to validate
        default: The default/reference configuration

    Returns:
        True if configuration is valid, False otherwise
    """

    rules = ObjectRegistry.get_instance().get_rules()
    rule = next((rule for rule in rules if rule.name == name), None)

    if rule is None:
        raise ValueError(f"Rule with name {name} not found")

    rule_input_schema = rule.input.model_json_schema()
    rule_output_schema = rule.output.model_json_schema()

    config_input_node_schema, config_output_node_schema = (
        get_input_and_output_node_schemas(config.jdm)
    )

    input_node_diagnostics = node_diff(
        rule_input_schema.get("properties", {}),
        config_input_node_schema.get("properties", {}),
        "inputNode",
    )
    output_node_diagnostics = node_diff(
        rule_output_schema.get("properties", {}),
        config_output_node_schema.get("properties", {}),
        "outputNode",
    )

    if len(input_node_diagnostics) > 0 or len(output_node_diagnostics) > 0:
        return ConfigDiagnostics.model_validate(
            {
                "is_valid": False,
                "suggested_fix": RuleEngineConfig(jdm=create_jdm_graph(rule)),
                "issues": input_node_diagnostics + output_node_diagnostics,
            }
        )

    return ConfigDiagnostics.model_validate(
        {
            "is_valid": True,
            "issues": [],
        }
    )


rule_configuration = ObjectConfigurationIO(
    RuleEngineConfig,
    ConfigurableObjectType.RULE,
    validate_config=validate_config,
)
