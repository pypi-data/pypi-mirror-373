from datetime import datetime, timedelta

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.workflows.decorators import step, workflow
from planar.workflows.execution import execute
from planar.workflows.models import Workflow, WorkflowStatus
from planar.workflows.step_core import Suspend, suspend


class ModelData(BaseModel):
    name: str
    value: int
    created_at: datetime


async def test_suspend_with_pydantic_return_value(session: AsyncSession):
    """Test that a step returning a pydantic model properly deserializes after suspension."""

    @step()
    async def data_step() -> ModelData:
        """Step that returns a pydantic model."""
        return ModelData(name="test-data", value=42, created_at=datetime.now())

    @workflow()
    async def suspend_workflow():
        # First get the pydantic model from the step
        data = await data_step()

        await suspend(interval=timedelta(seconds=0.1))

        # After resume, verify we can still access the pydantic model's properties
        # This verifies the model was properly deserialized on re-execution
        return ModelData(name=data.name, value=data.value, created_at=data.created_at)

    # Start the workflow
    wf = await suspend_workflow.start()

    # First execution should suspend
    result = await execute(wf)
    assert result is not None
    assert isinstance(result, Suspend)

    # Resume workflow after suspend
    result = await execute(wf)
    assert result is not None
    assert isinstance(result, ModelData)
    # Check that the result contains our expected data with proper types
    assert result.name == "test-data"
    assert result.value == 42
    assert isinstance(result.created_at, datetime)

    # Verify workflow completed successfully
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.SUCCEEDED


async def test_suspend_with_generic_model_deserialization(session: AsyncSession):
    """Test deserialization of a generic model (like Agent's CompletionResponse) after workflow suspension."""

    class ToolCall(BaseModel):
        """Simplified version of a tool call."""

        name: str
        arguments: dict[str, str]

    # Define a model similar to what an Agent might return
    class GenericResponse[DataT](BaseModel):
        """Similar structure to CompletionResponse used by Agent."""

        content: DataT | None = None
        tool_calls: list[ToolCall] | None = None

    class ResultData(BaseModel):
        """Example result data model."""

        title: str
        score: int
        timestamp: datetime

    @step()
    async def generic_data_step[DataT](payload: DataT) -> GenericResponse[DataT]:
        """Step that returns a generic response with a pydantic model."""
        return GenericResponse[DataT](
            content=payload,
            tool_calls=[ToolCall(name="test_tool", arguments={"param": "value"})],
        )

    @workflow()
    async def generic_suspend_workflow():
        # Get the generic response from the step
        result_data = ResultData(
            title="Test Generic Response",
            score=95,
            timestamp=datetime(2021, 1, 1, 12, 0, 0),
        )
        response = await generic_data_step(result_data)

        # Suspend the workflow
        await suspend(interval=timedelta(seconds=0.1))

        # After resuming, verify we can still access properties of the generic response
        # This confirms proper deserialization of the generic model
        return response

    # Start the workflow
    wf = await generic_suspend_workflow.start()

    # First execution should suspend
    result = await execute(wf)
    assert result is not None
    assert isinstance(result, Suspend)

    # Resume workflow after suspend
    final_result = await execute(wf)
    assert final_result is not None
    # Check against the origin type first
    assert isinstance(final_result, GenericResponse)
    assert final_result.content is not None
    assert isinstance(final_result.content, ResultData)
    assert final_result.content.title == "Test Generic Response"
    assert final_result.content.score == 95
    assert isinstance(final_result.content.timestamp, datetime)
    assert final_result.tool_calls is not None
    assert len(final_result.tool_calls) == 1
    assert final_result.tool_calls[0].name == "test_tool"

    # Verify workflow completed successfully
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.SUCCEEDED


async def test_suspend_with_generic_list_deserialization(session: AsyncSession):
    """Test deserialization of a generic model containing a list after suspension."""

    # Define a model similar to what an Agent might return
    class GenericListResponse[DataT](BaseModel):
        """Generic response containing a list."""

        items: list[DataT] | None = None
        description: str = ""

    @step()
    async def generic_list_step[DataT](
        payload: list[DataT],
    ) -> GenericListResponse[DataT]:
        """Step that returns a generic response with a list."""
        return GenericListResponse[DataT](items=payload, description="List of items")

    @workflow()
    async def generic_list_suspend_workflow():
        # Example list data
        str_list = ["apple", "banana", "cherry"]
        response = await generic_list_step(str_list)

        # Suspend the workflow
        await suspend(interval=timedelta(seconds=0.1))

        # After resuming, verify we can still access properties
        return response

    # Start the workflow
    wf = await generic_list_suspend_workflow.start()

    # First execution should suspend
    result = await execute(wf)
    assert result is not None
    assert isinstance(result, Suspend)

    # Resume workflow after suspend
    final_result = await execute(wf)
    assert final_result is not None
    assert isinstance(final_result, GenericListResponse)
    assert final_result.items is not None
    assert isinstance(final_result.items, list)
    assert final_result.items == ["apple", "banana", "cherry"]
    assert final_result.description == "List of items"

    # Verify workflow completed successfully
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == WorkflowStatus.SUCCEEDED


async def test_suspend_with_dict_deserialization(session: AsyncSession):
    """Test deserialization of a dict after suspension."""

    dict_payload = {
        "a": 1,
        "b": "string",
        "c": {"d": "nested", "e": [1, 2, 3]},
        "f": [{"g": "nested_list"}],
        # "h": datetime(2021, 1, 1, 12, 0, 0), # Not supported in dict
        # "i": uuid.uuid4(), # Not supported in dict
        "j": True,
        "k": False,
        "l": None,
        # "m": Decimal(100), # Not supported in dict
        "n": [1, 2, 3],
        "o": 1.1,
    }

    @step()
    async def dict_step(
        payload: dict,
    ) -> dict:
        """Step that returns a generic response with a list."""
        return payload

    @workflow()
    async def dict_suspend_workflow(dict_payload: dict):
        response = await dict_step(dict_payload)

        # Suspend the workflow
        await suspend(interval=timedelta(seconds=0.1))

        # After resuming, verify we can still access properties
        return response

    wf = await dict_suspend_workflow.start(dict_payload)

    result = await execute(wf)
    assert result is not None
    assert isinstance(result, Suspend)

    final_result = await execute(wf)
    assert final_result is not None
    assert final_result == dict_payload
