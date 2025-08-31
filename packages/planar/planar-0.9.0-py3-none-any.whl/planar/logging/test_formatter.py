import json
import logging
import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel

from planar.logging.formatter import StructuredFormatter, dictionary_print, json_print


class SampleModel(BaseModel):
    name: str
    value: int


class TestJsonPrint:
    def test_json_print_simple_values(self):
        """Test json_print with simple values"""
        assert json_print("test") == '"test"'
        assert json_print(42) == "42"
        assert json_print(True) == "true"
        assert json_print(None) == "null"

    def test_json_print_dict(self):
        """Test json_print with dictionary"""
        data = {"key": "value", "number": 42}
        result = json_print(data)
        assert json.loads(result) == data

    def test_json_print_list_without_colors(self):
        """Test json_print with list without colors - should produce valid JSON"""
        data = ["item1", "item2", {"nested": "value"}]
        result = json_print(data, use_colors=False)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

    def test_json_print_list_with_colors(self):
        """Test json_print with list with colors - should produce valid JSON with ANSI codes"""
        data = ["item1", "item2", {"nested": "value"}]
        result = json_print(data, use_colors=True)
        # Should contain ANSI escape codes but when stripped should be valid JSON
        # Remove ANSI codes to check JSON validity
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_result = ansi_escape.sub("", result)
        parsed = json.loads(clean_result)
        assert parsed == data
        # Should contain color codes
        assert "\x1b[" in result

    def test_json_print_nested_structures(self):
        """Test json_print with deeply nested structures"""
        data = {
            "messages": [
                {"content": "hello", "role": "user"},
                {"content": "world", "role": "assistant"},
            ],
            "tools": [
                {"name": "tool1", "params": {"key": "value"}},
                {"name": "tool2", "params": {"num": 42}},
            ],
        }
        result = json_print(data, use_colors=False)
        parsed = json.loads(result)
        assert parsed == data

    def test_json_print_pydantic_model(self):
        """Test json_print with Pydantic models"""
        model = SampleModel(name="test", value=42)
        result = json_print(model, use_colors=False)
        parsed = json.loads(result)
        assert parsed == {"name": "test", "value": 42}

    def test_json_print_custom_objects(self):
        """Test json_print with custom objects that need string conversion"""

        class CustomObject:
            def __str__(self):
                return "custom_object"

        data = {"obj": CustomObject()}
        result = json_print(data, use_colors=False)
        parsed = json.loads(result)
        assert parsed == {"obj": "custom_object"}

    def test_json_print_no_ansi_in_escaped_strings(self):
        """Test that ANSI codes don't get escaped in JSON strings"""
        data = ["message1", "message2", {"key": "value"}]
        result = json_print(data, use_colors=False)
        # Should not contain escaped ANSI codes like \u001b
        assert "\\u001b" not in result
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

    def test_json_print_complex_types(self):
        """Test json_print with datetime, uuid, and decimal types"""
        test_datetime = datetime(2023, 12, 25, 10, 30, 45)
        test_uuid = uuid4()
        test_decimal = Decimal("123.45")

        # Test complex data structure with these types
        data = {
            "timestamp": test_datetime,
            "id": test_uuid,
            "amount": test_decimal,
            "nested": {
                "dates": [test_datetime, datetime(2024, 1, 1)],
                "ids": [test_uuid, uuid4()],
                "values": [test_decimal, Decimal("67.89")],
            },
        }

        # Test without colors
        result = json_print(data, use_colors=False)

        # Should be valid JSON
        parsed = json.loads(result)

        # All complex types should be converted to strings
        assert isinstance(parsed["timestamp"], str)
        assert isinstance(parsed["id"], str)
        assert isinstance(parsed["amount"], str)
        assert isinstance(parsed["nested"]["dates"][0], str)
        assert isinstance(parsed["nested"]["ids"][0], str)
        assert isinstance(parsed["nested"]["values"][0], str)

        # Verify string representations contain expected content
        assert "2023-12-25" in parsed["timestamp"]
        assert str(test_uuid) == parsed["id"]
        assert "123.45" in parsed["amount"]

        # Test with colors - should also work and produce valid JSON when stripped
        result_colored = json_print(data, use_colors=True)
        assert "\x1b[" in result_colored  # Should contain ANSI codes

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_result = ansi_escape.sub("", result_colored)
        parsed_colored = json.loads(clean_result)
        assert parsed_colored == parsed  # Should be same as non-colored version

    def test_json_print_with_base_model(self):
        """Test json_print with BaseModel using complex data"""

        class TestModel(BaseModel):
            name: str
            date: datetime
            uuid_val: UUID
            decimal_val: Decimal

        model = TestModel(
            name="test",
            date=datetime(2023, 12, 25, 10, 30, 45),
            uuid_val=uuid4(),
            decimal_val=Decimal("123.45"),
        )
        result = json_print(model, use_colors=False)
        parsed = json.loads(result)
        assert parsed == {
            "name": "test",
            "date": "2023-12-25T10:30:45",
            "uuid_val": str(model.uuid_val),
            "decimal_val": "123.45",
        }


class TestDictionaryPrint:
    def test_dictionary_print_simple(self):
        """Test dictionary_print with simple values"""
        data = {"key": "value", "number": 42}
        result = dictionary_print(data, use_colors=False)
        assert 'key="value"' in result
        assert "number=42" in result

    def test_dictionary_print_with_lists(self):
        """Test dictionary_print with lists"""
        data = {"items": ["a", "b", "c"], "count": 3}
        result = dictionary_print(data, use_colors=False)
        assert 'items=["a","b","c"]' in result or 'items=["a", "b", "c"]' in result
        assert "count=3" in result

    def test_dictionary_print_with_colors(self):
        """Test dictionary_print with colors enabled"""
        data = {"key": "value"}
        result = dictionary_print(data, use_colors=True)
        # Should contain ANSI codes
        assert "\x1b[" in result
        # Should still contain the key-value pair
        assert "key=" in result


class TestStructuredFormatter:
    def test_structured_formatter_with_extra_attrs(self):
        """Test StructuredFormatter with extra attributes"""
        formatter = StructuredFormatter(use_colors=False)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Add extra attributes (simulating what PlanarLogger does)
        record.__dict__.update(
            {
                "$workflow_id": "test-workflow",
                "$step_id": 42,
                "$messages": ["msg1", "msg2"],
            }
        )

        result = formatter.format(record)
        assert "workflow_id=" in result
        assert "step_id=42" in result
        assert "messages=" in result
        # Should not contain escaped ANSI codes
        assert "\\u001b" not in result

    def test_structured_formatter_with_colors(self):
        """Test StructuredFormatter with colors enabled"""
        formatter = StructuredFormatter(use_colors=True)

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        # Should contain ANSI color codes
        assert "\x1b[" in result

    def test_structured_formatter_complex_data(self):
        """Test StructuredFormatter with complex nested data like the original issue"""
        formatter = StructuredFormatter(use_colors=True)

        record = logging.LogRecord(
            name="planar.ai.test_agent",
            level=logging.INFO,
            pathname="test_agent.py",
            lineno=188,
            msg="patched_complete",
            args=(),
            exc_info=None,
        )

        # Simulate the complex data from the original issue
        record.__dict__.update(
            {
                "$messages": [
                    {"content": "Use tools to solve the problem"},
                    {"content": "Problem: complex problem", "files": []},
                    {
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "name": "tool1",
                                "arguments": {"param": "test_param"},
                            }
                        ],
                    },
                    {"content": "Tool 1 result: test_param", "tool_call_id": "call_1"},
                ],
                "$tools": [
                    {
                        "name": "tool1",
                        "description": "Test tool 1",
                        "parameters": {
                            "type": "object",
                            "properties": {"param": {"type": "string"}},
                        },
                    },
                    {
                        "name": "tool2",
                        "description": "Test tool 2",
                        "parameters": {
                            "type": "object",
                            "properties": {"num": {"type": "integer"}},
                        },
                    },
                ],
                "$workflow_id": "test-workflow-id",
                "$step_id": 4,
            }
        )

        result = formatter.format(record)

        # Should contain the message
        assert "patched_complete" in result
        assert "planar.ai.test_agent" in result

        # Should contain the extra attributes
        assert "messages=" in result
        assert "tools=" in result
        assert "workflow_id=" in result
        assert "step_id=" in result

        # Most importantly: should NOT contain escaped ANSI codes
        assert "\\u001b" not in result

        # Should contain actual ANSI codes (for colors)
        assert "\x1b[" in result

        # Verify the fix - the data should be properly formatted JSON with colors
        # Extract the JSON parts and verify they're valid when ANSI codes are stripped
        import re

        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_result = ansi_escape.sub("", result)

        # The messages should be valid JSON when extracted
        assert '"content": "Use tools to solve the problem"' in clean_result
        assert '"content": "Problem: complex problem"' in clean_result
