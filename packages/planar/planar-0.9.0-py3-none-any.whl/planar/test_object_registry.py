from planar.registry_items import create_pydantic_model_for_workflow
from planar.workflows.decorators import workflow


@workflow()
async def sample_workflow(foo: int, bar: str = "baz"):
    pass


def test_create_pydantic_model_for_workflow_strips_module_name():
    model_cls = create_pydantic_model_for_workflow(sample_workflow)
    assert model_cls.__name__ == "SampleWorkflowStartRequest"
    assert "foo" in model_cls.model_fields
    assert "bar" in model_cls.model_fields
