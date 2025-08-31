from decimal import Decimal

import pytest
from pydantic import BaseModel

from planar.app import PlanarApp
from planar.config import sqlite_config
from planar.rules import rule
from planar.testing.planar_test_client import PlanarTestClient


class ExpenseRuleInput(BaseModel):
    title: str
    amount: float
    description: str
    status: str
    category: str


class RuleOutput(BaseModel):
    reason: str
    approved: bool


class TransactionVolumeRow(BaseModel):
    period: str
    country: str
    currency: str
    completed_count: int
    rejected_count: int


class TransactionVolume(BaseModel):
    rows: list[TransactionVolumeRow]
    total_completed_count: int
    total_rejected_count: int


class PricingInput(BaseModel):
    rows: list[TransactionVolumeRow]


class TransactionPricingLine(TransactionVolumeRow):
    completed_price_per_transaction_usd: Decimal
    rejected_price_per_transaction_usd: Decimal


class PricingRuleOutput(BaseModel):
    line_items: list[TransactionPricingLine]


class PricingRuleOutputWrongType(BaseModel):
    line_items: list[TransactionPricingLine]
    some_other_field: str


@rule(description="Complex business rule")
def complex_business_rule(input: ExpenseRuleInput) -> RuleOutput:
    """
    A complex business rule that determines if the expense should be approved
    """
    # input and output must be json serializable objects for the zen / gorules lib to work
    return RuleOutput(reason="The widgets look fantastic", approved=True)


@rule(description="Calculates fees based on tiered, total transaction volume.")
def pricing_rule(
    input: PricingInput,
) -> PricingRuleOutput:
    """
    Calculates fees based on country, currency, and tiered volume.
    """
    return PricingRuleOutput(line_items=[])


@rule(
    description="Calculates fees based on tiered, total transaction volume with wrong type"
)
def pricing_rule_with_wrong_type(
    input: PricingInput,
) -> PricingRuleOutputWrongType:
    return PricingRuleOutputWrongType(line_items=[], some_other_field="test")


@pytest.fixture(name="app")
def app_fixture():
    app = PlanarApp(
        config=sqlite_config(":memory:"),
        title="Test app for agent router",
        description="Testing agent endpoints",
    )

    app.register_rule(complex_business_rule)
    app.register_rule(pricing_rule_with_wrong_type)
    app.register_rule(pricing_rule)
    return app


EXPENSE_RULE_JDM = {
    "nodes": [
        {
            "id": "7e51efb8-7463-4775-ad69-180442a34444",
            "type": "inputNode",
            "name": "Input",
            "content": {
                "schema": '{"properties": {"title": {"title": "Title", "type": "string"}, "amount": {"title": "Amount", "type": "number"}, "description": {"title": "Description", "type": "string"}, "status": {"title": "Status", "type": "string"}, "category": {"title": "Category", "type": "string"}}, "required": ["title", "amount", "description", "status", "category"], "title": "ExpenseRuleInput", "type": "object"}'
            },
            "position": {"x": 100, "y": 100},
        },
        {
            "id": "abf8c265-da42-4b81-b7bf-349d3e248294",
            "type": "decisionTableNode",
            "name": "decisionTable1",
            "content": {
                "hitPolicy": "first",
                "rules": [
                    {
                        "_id": "9fc59e78-58be-412b-9d2b-79c22bcfefe4",
                        "2a5ac809-24db-431b-a228-7bc318cd0a3f": "",
                        "25f2e0b6-c02b-43a2-a9cd-d40e5c1ca709": '"default value"',
                        "4b09e532-bb42-453b-9c00-26af89f70a03": "true",
                    }
                ],
                "inputs": [
                    {
                        "id": "2a5ac809-24db-431b-a228-7bc318cd0a3f",
                        "name": "Input",
                        "field": "",
                    }
                ],
                "outputs": [
                    {
                        "id": "25f2e0b6-c02b-43a2-a9cd-d40e5c1ca709",
                        "field": "reason",
                        "name": "reason",
                    },
                    {
                        "id": "4b09e532-bb42-453b-9c00-26af89f70a03",
                        "field": "approved",
                        "name": "approved",
                    },
                ],
                "passThrough": True,
                "passThorough": False,
                "inputField": None,
                "outputPath": None,
                "executionMode": "single",
            },
            "position": {"x": 405, "y": 120},
        },
        {
            "id": "40abc689-6e0e-40ee-bc76-df51065e6ff5",
            "type": "outputNode",
            "name": "Output",
            "content": {
                "schema": '{"properties": {"reason": {"title": "Reason", "type": "string"}, "approved": {"title": "Approved", "type": "boolean"}}, "required": ["reason", "approved"], "title": "RuleOutput", "type": "object"}'
            },
            "position": {"x": 885, "y": 130},
        },
        {
            "id": "a5385f35-5ba7-4cbf-a5b8-f87bca6fd95c",
            "type": "expressionNode",
            "name": "expression1",
            "content": {
                "expressions": [],
                "passThrough": True,
                "inputField": None,
                "outputPath": None,
                "executionMode": "single",
            },
            "position": {"x": 590, "y": 350},
        },
        {
            "id": "0689381e-0650-4ba5-b4ba-1a1800f035ca",
            "type": "decisionTableNode",
            "name": "decisionTable2",
            "content": {
                "hitPolicy": "first",
                "rules": [],
                "inputs": [
                    {
                        "id": "4caf4578-a643-4a3c-bc6e-2bdf8559e601",
                        "name": "Input",
                        "field": "",
                    }
                ],
                "outputs": [
                    {
                        "id": "4ec07a83-70ca-46ec-aee7-331c44a8da76",
                        "field": "output",
                        "name": "Output",
                    }
                ],
                "passThrough": True,
                "passThorough": None,
                "inputField": None,
                "outputPath": None,
                "executionMode": "single",
            },
            "position": {"x": 885, "y": 500},
        },
    ],
    "edges": [
        {
            "id": "cd19ba68-3f39-4b50-8014-85f01258fbe3",
            "type": "edge",
            "sourceId": "7e51efb8-7463-4775-ad69-180442a34444",
            "targetId": "abf8c265-da42-4b81-b7bf-349d3e248294",
        },
        {
            "id": "7c26024c-0f02-4393-8cf0-0f5097cd21d0",
            "type": "edge",
            "sourceId": "abf8c265-da42-4b81-b7bf-349d3e248294",
            "targetId": "40abc689-6e0e-40ee-bc76-df51065e6ff5",
        },
        {
            "id": "66d1a27e-2cf2-4b2e-862d-b65dc554c320",
            "type": "edge",
            "sourceId": "abf8c265-da42-4b81-b7bf-349d3e248294",
            "targetId": "a5385f35-5ba7-4cbf-a5b8-f87bca6fd95c",
        },
        {
            "id": "abf1329e-c27d-4655-b1a7-d410ea03b998",
            "type": "edge",
            "sourceId": "a5385f35-5ba7-4cbf-a5b8-f87bca6fd95c",
            "targetId": "40abc689-6e0e-40ee-bc76-df51065e6ff5",
        },
        {
            "id": "d56e19e6-2303-4272-b7df-49e3df75c62f",
            "type": "edge",
            "sourceId": "a5385f35-5ba7-4cbf-a5b8-f87bca6fd95c",
            "targetId": "0689381e-0650-4ba5-b4ba-1a1800f035ca",
        },
    ],
}


async def test_save_rule_endpoints(client: PlanarTestClient, app: PlanarApp):
    response = await client.get("/planar/v1/rules/complex_business_rule")

    assert response.status_code == 200

    data = response.json()

    assert len(data["configs"]) == 1

    # save the rule
    response = await client.post(
        "/planar/v1/rules/complex_business_rule", json=EXPENSE_RULE_JDM
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert len(data["configs"]) == 2


PRICING_RULE_JDM = {
    "nodes": [
        {
            "id": "6cc036d3-3350-449e-9b2c-1569b8f86ffc",
            "type": "inputNode",
            "name": "Input",
            "content": {
                "schema": '{"$defs": {"TransactionVolumeRow": {"properties": {"period": {"title": "Period", "type": "string"}, "country": {"title": "Country", "type": "string"}, "currency": {"title": "Currency", "type": "string"}, "completed_count": {"title": "Completed Count", "type": "integer"}, "rejected_count": {"title": "Rejected Count", "type": "integer"}}, "required": ["period", "country", "currency", "completed_count", "rejected_count"], "title": "TransactionVolumeRow", "type": "object"}}, "properties": {"rows": {"items": {"$ref": "#/$defs/TransactionVolumeRow"}, "title": "Rows", "type": "array"}}, "required": ["rows"], "title": "PricingInput", "type": "object"}'
            },
            "position": {"x": 100, "y": 100},
        },
        {
            "id": "3921e9d3-02e3-4a72-b74d-037c80f97eaa",
            "type": "decisionTableNode",
            "name": "decisionTable1",
            "content": {
                "hitPolicy": "first",
                "rules": [
                    {
                        "_id": "15d4429c-39bc-448d-a7f4-187eaea4493a",
                        "e5688083-30b9-449e-adaf-bf8ff69eb2ac": '"ARS"',
                        "42c29309-9aa4-4441-bd1a-b1b57d1b628e": "<= 6000",
                        "71b9d121-5b37-4b0b-b4c2-d29a868fed35": '"Argentina"',
                        "662e29e1-d0b8-4cf4-a443-3e92f2157054": "100",
                        "_description": "",
                    },
                    {
                        "_id": "9ef47884-004d-4314-a61c-38778ed7b7d7",
                        "e5688083-30b9-449e-adaf-bf8ff69eb2ac": "",
                        "42c29309-9aa4-4441-bd1a-b1b57d1b628e": "",
                        "71b9d121-5b37-4b0b-b4c2-d29a868fed35": "",
                        "662e29e1-d0b8-4cf4-a443-3e92f2157054": "1.00",
                    },
                ],
                "inputs": [
                    {
                        "id": "e5688083-30b9-449e-adaf-bf8ff69eb2ac",
                        "name": "Currency",
                        "field": "currency",
                    },
                    {
                        "id": "42c29309-9aa4-4441-bd1a-b1b57d1b628e",
                        "name": "Completed Count",
                        "field": "completed_count",
                    },
                    {
                        "id": "71b9d121-5b37-4b0b-b4c2-d29a868fed35",
                        "name": "Country",
                        "field": "country",
                    },
                ],
                "outputs": [
                    {
                        "id": "662e29e1-d0b8-4cf4-a443-3e92f2157054",
                        "field": "completed_price_per_transaction_usd",
                        "name": "Completed Price Per Transaction (USD)",
                    }
                ],
                "passThrough": True,
                "passThorough": None,
                "inputField": "rows",
                "outputPath": "line_items",
                "executionMode": "loop",
            },
            "position": {"x": 350, "y": 95},
        },
        {
            "id": "a9a82683-5dbb-4eed-8326-83dea36c1d53",
            "type": "outputNode",
            "name": "Output",
            "content": {
                "schema": '{"$defs": {"TransactionPricingLine": {"properties": {"period": {"title": "Period", "type": "string"}, "country": {"title": "Country", "type": "string"}, "currency": {"title": "Currency", "type": "string"}, "completed_count": {"title": "Completed Count", "type": "integer"}, "rejected_count": {"title": "Rejected Count", "type": "integer"}, "completed_price_per_transaction_usd": {"title": "Completed Price Per Transaction Usd", "type": "number"}, "rejected_price_per_transaction_usd": {"title": "Rejected Price Per Transaction Usd", "type": "number"}}, "required": ["period", "country", "currency", "completed_count", "rejected_count", "completed_price_per_transaction_usd", "rejected_price_per_transaction_usd"], "title": "TransactionPricingLine", "type": "object"}}, "properties": {"line_items": {"items": {"$ref": "#/$defs/TransactionPricingLine"}, "title": "Line Items", "type": "array"}}, "required": ["line_items"], "title": "PricingRuleOutput", "type": "object"}'
            },
            "position": {"x": 1195, "y": 60},
        },
        {
            "id": "b384c91d-dbc3-4043-a0f0-a3adef9ac340",
            "type": "expressionNode",
            "name": "expression1",
            "content": {
                "expressions": [
                    {
                        "id": "b0e3f514-c109-43e4-91ad-3007110d0a35",
                        "key": "rejected_price_per_transaction_usd",
                        "value": "200",
                    }
                ],
                "passThrough": True,
                "inputField": "line_items",
                "outputPath": "line_items",
                "executionMode": "loop",
            },
            "position": {"x": 670, "y": 100},
        },
        {
            "id": "b89b13b8-526f-4db2-a524-faeeca0e78d7",
            "type": "expressionNode",
            "name": "expression2",
            "content": {
                "expressions": [
                    {
                        "id": "b6a9570b-7ea1-4ebb-b5eb-b693fe14ca47",
                        "key": "line_items",
                        "value": "line_items",
                    }
                ],
                "passThrough": False,
                "inputField": None,
                "outputPath": None,
                "executionMode": "single",
            },
            "position": {"x": 950, "y": 100},
        },
    ],
    "edges": [
        {
            "id": "a9c02fbb-3ad6-4f65-a718-16c0e02d7551",
            "type": "edge",
            "sourceId": "6cc036d3-3350-449e-9b2c-1569b8f86ffc",
            "targetId": "3921e9d3-02e3-4a72-b74d-037c80f97eaa",
        },
        {
            "id": "c2959035-5f0d-4317-8ccf-2f885450b669",
            "type": "edge",
            "sourceId": "3921e9d3-02e3-4a72-b74d-037c80f97eaa",
            "targetId": "b384c91d-dbc3-4043-a0f0-a3adef9ac340",
        },
        {
            "id": "6513b9bf-7016-4776-bf84-81418caf7b74",
            "type": "edge",
            "sourceId": "b384c91d-dbc3-4043-a0f0-a3adef9ac340",
            "targetId": "b89b13b8-526f-4db2-a524-faeeca0e78d7",
        },
        {
            "id": "b75e295e-8fb4-45b6-9040-06fdd8d6723e",
            "type": "edge",
            "sourceId": "b89b13b8-526f-4db2-a524-faeeca0e78d7",
            "targetId": "a9a82683-5dbb-4eed-8326-83dea36c1d53",
        },
    ],
}


async def test_save_rule_endpoints_with_jdm(client: PlanarTestClient, app: PlanarApp):
    response = await client.get("/planar/v1/rules/pricing_rule")

    assert response.status_code == 200

    data = response.json()

    assert len(data["configs"]) == 1

    # save the rule
    response = await client.post("/planar/v1/rules/pricing_rule", json=PRICING_RULE_JDM)

    assert response.status_code == 200

    data = response.json()

    assert len(data["configs"]) == 2


async def test_save_rule_endpoints_with_jdm_wrong_type(
    client: PlanarTestClient, app: PlanarApp
):
    response = await client.get("/planar/v1/rules/pricing_rule_with_wrong_type")

    assert response.status_code == 200

    data = response.json()

    assert len(data["configs"]) == 1

    # save the rule
    response = await client.post(
        "/planar/v1/rules/pricing_rule_with_wrong_type",
        json=PRICING_RULE_JDM,
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"]["error"] == "ValidationError"
    assert response_json["detail"]["object_name"] == "pricing_rule_with_wrong_type"
    assert response_json["detail"]["object_type"] == "rule"
    assert response_json["detail"]["diagnostics"]["is_valid"] is False
    assert (
        response_json["detail"]["diagnostics"]["suggested_fix"]["jdm"]["nodes"][0][
            "content"
        ]["schema"]
        == PRICING_RULE_JDM["nodes"][0]["content"]["schema"]
    )
    # check contains some_other_field
    assert (
        "some_other_field"
        in response_json["detail"]["diagnostics"]["suggested_fix"]["jdm"]["nodes"][2][
            "content"
        ]["schema"]
    )

    assert response_json["detail"]["diagnostics"]["issues"] == [
        {
            "error_code": "MISSING_FIELD",
            "field_path": "some_other_field",
            "message": "Field 'some_other_field' is missing in current node",
            "reference_value": {
                "title": "Some Other Field",
                "type": "string",
            },
            "current_value": None,
            "for_object": "outputNode",
        }
    ]
