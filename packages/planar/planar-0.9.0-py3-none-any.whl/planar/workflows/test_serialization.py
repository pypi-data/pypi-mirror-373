import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, List, Optional, Union

import pytest
from pydantic import BaseModel, Field

from planar.workflows.serialization import (
    deserialize_args,
    deserialize_primitive,
    deserialize_result,
    deserialize_value,
    is_pydantic_model,
    serialize_args,
    serialize_primitive,
    serialize_result,
    serialize_value,
)


class SamplePerson(BaseModel):
    name: str
    age: int
    birth_date: datetime
    balance: Decimal
    id: uuid.UUID
    active: bool
    tags: List[str]


class SampleNestedModel(BaseModel):
    person: SamplePerson
    metadata: Optional[dict] = None


@dataclass
class SampleDataClass:
    name: str
    value: int


def test_is_pydantic_model():
    assert is_pydantic_model(SamplePerson)
    assert is_pydantic_model(SampleNestedModel)
    assert not is_pydantic_model(dict)
    assert not is_pydantic_model(str)
    assert not is_pydantic_model(5)


def test_serialize_primitive():
    # Test basic primitives
    assert serialize_primitive(True) is True
    assert serialize_primitive(42) == 42
    assert serialize_primitive(3.14) == 3.14

    # Test Decimal
    decimal_value = Decimal("123.456")
    assert serialize_primitive(decimal_value) == "123.456"

    # Test UUID
    test_uuid = uuid.uuid4()
    assert serialize_primitive(test_uuid) == str(test_uuid)

    # Test datetime
    test_dt = datetime(2023, 5, 15, 12, 30, 45)
    assert serialize_primitive(test_dt) == test_dt.isoformat()

    # Test date
    test_date = date(2023, 5, 15)
    assert serialize_primitive(test_date) == test_date.isoformat()

    # Test timedelta
    test_td = timedelta(days=1, hours=2, minutes=30)
    serialized_td = serialize_primitive(test_td)
    assert isinstance(serialized_td, dict)
    assert serialized_td["days"] == 1
    assert serialized_td["seconds"] == (2 * 3600) + (30 * 60)
    assert serialized_td["microseconds"] == 0


def test_deserialize_primitive():
    # Test basic primitives
    assert deserialize_primitive(True, bool) is True
    assert deserialize_primitive(42, int) == 42
    assert deserialize_primitive(3.14, float) == 3.14

    # Test Decimal
    assert deserialize_primitive("123.456", Decimal) == Decimal("123.456")

    # Test UUID
    test_uuid = uuid.uuid4()
    assert deserialize_primitive(str(test_uuid), uuid.UUID) == test_uuid

    # Test datetime
    test_dt = datetime(2023, 5, 15, 12, 30, 45)
    assert deserialize_primitive(test_dt.isoformat(), datetime) == test_dt

    # Test date
    test_date = date(2023, 5, 15)
    assert deserialize_primitive(test_date.isoformat(), date) == test_date

    # Test timedelta as dict
    test_td = timedelta(days=1, hours=2, minutes=30)
    serialized_td = {"days": 1, "seconds": (2 * 3600) + (30 * 60), "microseconds": 0}
    assert deserialize_primitive(serialized_td, timedelta) == test_td

    # Test timedelta as seconds
    assert deserialize_primitive(3600, timedelta) == timedelta(hours=1)

    # Test invalid timedelta
    with pytest.raises(ValueError):
        deserialize_primitive("invalid", timedelta)


def test_serialize_value():
    # Test None
    assert serialize_value(None) is None

    # Test Pydantic model
    person = SamplePerson(
        name="John",
        age=30,
        birth_date=datetime(1990, 1, 1),
        balance=Decimal("1000.50"),
        id=uuid.uuid4(),
        active=True,
        tags=["developer", "python"],
    )
    serialized_person = serialize_value(person)
    assert isinstance(serialized_person, dict)
    assert serialized_person["name"] == "John"
    assert serialized_person["age"] == 30
    assert "birth_date" in serialized_person
    # Handle both string representation or Decimal object (implementation might vary)
    assert str(serialized_person["balance"]) == "1000.50"
    assert "id" in serialized_person
    assert serialized_person["active"] is True
    assert serialized_person["tags"] == ["developer", "python"]

    # Test Pydantic model type
    serialized_model_definition = serialize_value(SamplePerson)
    expected_definition = {
        "title": "SamplePerson",
        "type": "object",
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "age": {"title": "Age", "type": "integer"},
            "birth_date": {
                "title": "Birth Date",
                "type": "string",
                "format": "date-time",
            },
            "balance": {
                "title": "Balance",
                "anyOf": [{"type": "number"}, {"type": "string"}],
            },
            "id": {"format": "uuid", "title": "Id", "type": "string"},
            "active": {"title": "Active", "type": "boolean"},
            "tags": {"title": "Tags", "type": "array", "items": {"type": "string"}},
        },
        "required": ["name", "age", "birth_date", "balance", "id", "active", "tags"],
    }

    assert serialized_model_definition == expected_definition

    # Test primitives
    assert serialize_value(42) == 42
    assert serialize_value(Decimal("123.45")) == "123.45"

    # Test nested model
    nested = SampleNestedModel(person=person, metadata={"source": "test"})
    serialized_nested = serialize_value(nested)
    assert isinstance(serialized_nested, dict)
    assert "person" in serialized_nested
    assert serialized_nested["metadata"] == {"source": "test"}


def test_deserialize_value():
    # Test None
    assert deserialize_value(None) is None
    assert deserialize_value(None, str) is None

    # Test with no type hint
    assert deserialize_value(42, None) == 42

    # Test Pydantic model
    test_uuid = uuid.uuid4()
    person_data = {
        "name": "John",
        "age": 30,
        "birth_date": "1990-01-01T00:00:00",
        "balance": "1000.50",
        "id": str(test_uuid),
        "active": True,
        "tags": ["developer", "python"],
    }
    deserialized_person = deserialize_value(person_data, SamplePerson)
    assert isinstance(deserialized_person, SamplePerson)
    assert deserialized_person.name == "John"
    assert deserialized_person.age == 30
    assert deserialized_person.birth_date == datetime(1990, 1, 1)
    assert deserialized_person.balance == Decimal("1000.50")
    assert deserialized_person.id == test_uuid
    assert deserialized_person.active is True
    assert deserialized_person.tags == ["developer", "python"]

    # Test Pydantic model type
    serialized_model_definition = {
        "title": "SamplePerson",
        "type": "object",
        "properties": {
            "name": {"title": "Name", "type": "string"},
            "age": {"title": "Age", "type": "integer"},
            "birth_date": {
                "title": "Birth Date",
                "type": "string",
                "format": "date-time",
            },
            "balance": {
                "title": "Balance",
                "anyOf": [{"type": "number"}, {"type": "string"}],
            },
            "id": {"format": "uuid", "title": "Id", "type": "string"},
            "active": {"title": "Active", "type": "boolean"},
            "tags": {"title": "Tags", "type": "array", "items": {"type": "string"}},
        },
        "required": ["name", "age", "birth_date", "balance", "id", "active", "tags"],
    }
    deserialized_model_definition = deserialize_value(
        serialized_model_definition, type_hint=type[SamplePerson]
    )
    assert deserialized_model_definition == SamplePerson

    # Test Union type
    union_type = Union[int, str]
    assert deserialize_value(42, union_type) == 42
    assert deserialize_value("hello", union_type) == "hello"
    union_type_pipe = int | str
    assert deserialize_value(42, union_type_pipe) == 42
    assert deserialize_value("hello", union_type_pipe) == "hello"

    # Test primitive types
    assert deserialize_value("123.45", Decimal) == Decimal("123.45")
    assert deserialize_value(3600, timedelta) == timedelta(hours=1)

    # Test an invalid Union type
    with pytest.raises(ValueError):
        deserialize_value("not_a_number", Union[int, float])


def test_deserialize_value_uniontype():
    class FooModel(BaseModel):
        value: int

    data = {"value": 5}
    deserialized = deserialize_value(data, FooModel | None)
    assert isinstance(deserialized, FooModel)
    assert deserialized.value == 5

    deserialized = deserialize_value(data, Optional[FooModel])
    assert isinstance(deserialized, FooModel)
    assert deserialized.value == 5

    deserialized = deserialize_value(data, Union[FooModel, None])
    assert isinstance(deserialized, FooModel)
    assert deserialized.value == 5


def example_function(
    person: SamplePerson, count: int, tags: List[str] = []
) -> SampleNestedModel:
    return SampleNestedModel(
        person=person, metadata={"count": count, "tags": tags or []}
    )


def test_serialize_args():
    person = SamplePerson(
        name="Alice",
        age=25,
        birth_date=datetime(1998, 5, 10),
        balance=Decimal("500.25"),
        id=uuid.uuid4(),
        active=True,
        tags=["tester"],
    )

    args = [person]
    kwargs = {"count": 42, "tags": ["important", "test"]}

    serialized_args, serialized_kwargs = serialize_args(example_function, args, kwargs)

    # Check args
    assert isinstance(serialized_args[0], dict)
    assert serialized_args[0]["name"] == "Alice"

    # Check kwargs
    assert serialized_kwargs["count"] == 42
    assert serialized_kwargs["tags"] == ["important", "test"]


def test_deserialize_args():
    test_uuid = uuid.uuid4()
    person_data = {
        "name": "Alice",
        "age": 25,
        "birth_date": "1998-05-10T00:00:00",
        "balance": "500.25",
        "id": str(test_uuid),
        "active": True,
        "tags": ["tester"],
    }

    args = [person_data]
    kwargs = {"count": 42, "tags": ["important", "test"]}

    deserialized_args, deserialized_kwargs = deserialize_args(
        example_function, args, kwargs
    )

    # Check args
    assert isinstance(deserialized_args[0], SamplePerson)
    assert deserialized_args[0].name == "Alice"
    assert deserialized_args[0].id == test_uuid

    # Check kwargs
    assert deserialized_kwargs["count"] == 42
    assert deserialized_kwargs["tags"] == ["important", "test"]


def test_serialize_result():
    person = SamplePerson(
        name="Bob",
        age=35,
        birth_date=datetime(1988, 3, 15),
        balance=Decimal("1200.75"),
        id=uuid.uuid4(),
        active=True,
        tags=["developer"],
    )

    result = SampleNestedModel(person=person, metadata={"source": "result_test"})

    serialized_result = serialize_result(example_function, result)

    assert isinstance(serialized_result, dict)
    assert "person" in serialized_result
    assert serialized_result["person"]["name"] == "Bob"
    assert serialized_result["metadata"] == {"source": "result_test"}


def test_deserialize_result():
    test_uuid = uuid.uuid4()
    result_data = {
        "person": {
            "name": "Bob",
            "age": 35,
            "birth_date": "1988-03-15T00:00:00",
            "balance": "1200.75",
            "id": str(test_uuid),
            "active": True,
            "tags": ["developer"],
        },
        "metadata": {"source": "result_test"},
    }

    deserialized_result = deserialize_result(example_function, result_data)

    assert isinstance(deserialized_result, SampleNestedModel)
    assert isinstance(deserialized_result.person, SamplePerson)
    assert deserialized_result.person.name == "Bob"
    assert deserialized_result.person.id == test_uuid
    assert deserialized_result.metadata == {"source": "result_test"}


def test_serialize_deserialize_roundtrip():
    # Create test data
    test_uuid = uuid.uuid4()
    person = SamplePerson(
        name="Charlie",
        age=40,
        birth_date=datetime(1983, 7, 22),
        balance=Decimal("2500.10"),
        id=test_uuid,
        active=True,
        tags=["manager", "python"],
    )

    # Original function call
    args = [person]
    kwargs = {"count": 100, "tags": ["high-priority"]}

    # Serialize arguments
    serialized_args, serialized_kwargs = serialize_args(example_function, args, kwargs)

    # Deserialize arguments
    deserialized_args, deserialized_kwargs = deserialize_args(
        example_function, serialized_args, serialized_kwargs
    )

    # Call function with deserialized arguments
    result = example_function(*deserialized_args, **deserialized_kwargs)

    # Serialize result
    serialized_result = serialize_result(example_function, result)

    # Deserialize result
    deserialized_result = deserialize_result(example_function, serialized_result)

    # Verify everything is intact
    assert isinstance(deserialized_result, SampleNestedModel)
    assert deserialized_result.person.name == "Charlie"
    assert deserialized_result.person.age == 40
    assert deserialized_result.person.tags == ["manager", "python"]
    assert deserialized_result.person.birth_date == datetime(1983, 7, 22)
    assert deserialized_result.person.balance == Decimal("2500.10")
    assert deserialized_result.person.id == test_uuid
    assert deserialized_result.person.active is True
    assert deserialized_result.metadata
    assert deserialized_result.metadata["count"] == 100
    assert deserialized_result.metadata["tags"] == ["high-priority"]


# Test function with Union types for args and kwargs
class SampleEventModel(BaseModel):
    event_id: uuid.UUID
    timestamp: datetime
    description: str


class ModelWithDatetimeField(BaseModel):
    """Model to test datetime serialization"""

    timestamp: datetime = Field(...)
    name: str


class ModelWithUUID(BaseModel):
    """Model to test UUID serialization"""

    id: uuid.UUID = Field(...)
    name: str


def function_with_dicts(data: dict, count: int, metadata: dict[str, Any]) -> dict:
    return {"count": count, "metadata": metadata}


def test_serialize_args_with_dict():
    # Test with SamplePerson
    person = {"name": "David", "age": 28, "id": "1235abc"}

    args = [person]
    kwargs = {"another_dict_key": {"count": 50, "metadata": {"source": "test"}}}

    serialized_args, serialized_kwargs = serialize_args(
        function_with_dicts, args, kwargs
    )

    # Check args - should be serialized to dict
    assert isinstance(serialized_args[0], dict)
    assert serialized_args[0]["name"] == "David"
    assert serialized_args[0]["age"] == 28
    assert serialized_args[0]["id"] == "1235abc"

    # Check kwargs
    assert serialized_kwargs["another_dict_key"]["count"] == 50
    assert serialized_kwargs["another_dict_key"]["metadata"] == {"source": "test"}


def test_deserialize_args_with_dict():
    # Test with SamplePerson
    person = {"name": "David", "age": 28, "id": "1235abc"}

    args = [person]
    kwargs = {"another_dict_key": {"count": 50, "metadata": {"source": "test"}}}

    deserialized_args, deserialized_kwargs = deserialize_args(
        function_with_dicts, args, kwargs
    )

    assert deserialized_args[0] == person
    assert deserialized_kwargs["another_dict_key"] == {
        "count": 50,
        "metadata": {"source": "test"},
    }


# A function with Union type parameters for testing
def function_with_unions(
    data: Union[SamplePerson, SampleEventModel],
    count: int,
    metadata: Union[dict, str, None] = None,
) -> Union[SampleNestedModel, dict]:
    if isinstance(data, SamplePerson):
        return SampleNestedModel(
            person=data, metadata={"count": count, "extra": metadata}
        )
    else:  # SampleEventModel
        return {"event": data.model_dump(), "count": count, "metadata": metadata}


def test_serialize_args_with_unions():
    # Test with SamplePerson
    person = SamplePerson(
        name="David",
        age=28,
        birth_date=datetime(1995, 8, 12),
        balance=Decimal("750.25"),
        id=uuid.uuid4(),
        active=True,
        tags=["engineer"],
    )

    args = [person]
    kwargs = {"count": 50, "metadata": {"source": "test"}}

    serialized_args, serialized_kwargs = serialize_args(
        function_with_unions, args, kwargs
    )

    # Check args - should be serialized to dict
    assert isinstance(serialized_args[0], dict)
    assert serialized_args[0]["name"] == "David"
    assert serialized_args[0]["age"] == 28
    assert serialized_args[0]["id"] == str(person.id)

    # Check kwargs
    assert serialized_kwargs["count"] == 50
    assert serialized_kwargs["metadata"] == {"source": "test"}

    # Test with SampleEventModel
    event = SampleEventModel(
        event_id=uuid.uuid4(), timestamp=datetime.now(), description="Test event"
    )

    args = [event]
    kwargs = {"count": 10, "metadata": "event_metadata"}

    serialized_args, serialized_kwargs = serialize_args(
        function_with_unions, args, kwargs
    )

    # Check args
    assert isinstance(serialized_args[0], dict)
    assert "event_id" in serialized_args[0]
    assert "timestamp" in serialized_args[0]
    assert serialized_args[0]["description"] == "Test event"

    # Check kwargs
    assert serialized_kwargs["count"] == 10
    assert serialized_kwargs["metadata"] == "event_metadata"


def test_deserialize_args_with_unions():
    # Test with SamplePerson data
    test_uuid = uuid.uuid4()
    person_data = {
        "name": "David",
        "age": 28,
        "birth_date": "1995-08-12T00:00:00",
        "balance": "750.25",
        "id": str(test_uuid),
        "active": True,
        "tags": ["engineer"],
    }

    args = [person_data]
    kwargs = {"count": 50, "metadata": {"source": "test"}}

    deserialized_args, deserialized_kwargs = deserialize_args(
        function_with_unions, args, kwargs
    )

    # For Union types, it will try each type and use the first one that works
    # SamplePerson should be successfully deserialized
    assert isinstance(deserialized_args[0], SamplePerson)
    assert deserialized_args[0].name == "David"
    assert deserialized_args[0].age == 28
    assert deserialized_args[0].id == test_uuid

    # Check kwargs
    assert deserialized_kwargs["count"] == 50
    assert deserialized_kwargs["metadata"] == {"source": "test"}

    # Test with SampleEventModel data
    event_uuid = uuid.uuid4()
    event_time = datetime.now()
    event_data = {
        "event_id": str(event_uuid),
        "timestamp": event_time.isoformat(),
        "description": "Test event",
    }

    args = [event_data]
    kwargs = {"count": 10, "metadata": "event_metadata"}

    deserialized_args, deserialized_kwargs = deserialize_args(
        function_with_unions, args, kwargs
    )

    # It should deserialize to SampleEventModel (the first compatible type)
    assert isinstance(deserialized_args[0], SampleEventModel)
    assert deserialized_args[0].event_id == event_uuid
    assert deserialized_args[0].description == "Test event"

    # Check kwargs
    assert deserialized_kwargs["count"] == 10
    assert deserialized_kwargs["metadata"] == "event_metadata"


def test_serialize_result_with_unions():
    # Test with SampleNestedModel result
    person = SamplePerson(
        name="Eve",
        age=32,
        birth_date=datetime(1991, 3, 15),
        balance=Decimal("1500.75"),
        id=uuid.uuid4(),
        active=True,
        tags=["manager"],
    )

    result = SampleNestedModel(person=person, metadata={"source": "union_test"})

    serialized_result = serialize_result(function_with_unions, result)

    assert isinstance(serialized_result, dict)
    assert "person" in serialized_result
    assert serialized_result["person"]["name"] == "Eve"
    assert serialized_result["metadata"] == {"source": "union_test"}

    # Test with dict result
    event = SampleEventModel(
        event_id=uuid.uuid4(), timestamp=datetime.now(), description="Important event"
    )

    result = {"event": event.model_dump(), "count": 25, "metadata": "event data"}

    serialized_result = serialize_result(function_with_unions, result)

    assert isinstance(serialized_result, dict)
    assert "event" in serialized_result
    assert serialized_result["count"] == 25
    assert serialized_result["metadata"] == "event data"


def test_deserialize_result_with_unions():
    # Test with SampleNestedModel data
    test_uuid = uuid.uuid4()
    result_data = {
        "person": {
            "name": "Eve",
            "age": 32,
            "birth_date": "1991-03-15T00:00:00",
            "balance": "1500.75",
            "id": str(test_uuid),
            "active": True,
            "tags": ["manager"],
        },
        "metadata": {"source": "union_test"},
    }

    deserialized_result = deserialize_result(function_with_unions, result_data)

    # For Union types in return type, it tries each type and uses the first one that works
    assert isinstance(deserialized_result, SampleNestedModel)
    assert isinstance(deserialized_result.person, SamplePerson)
    assert deserialized_result.person.name == "Eve"
    assert deserialized_result.person.id == test_uuid
    assert deserialized_result.metadata == {"source": "union_test"}

    # Test with dict result
    event_uuid = uuid.uuid4()
    event_time = datetime.now().isoformat()
    result_data = {
        "event": {
            "event_id": str(event_uuid),
            "timestamp": event_time,
            "description": "Important event",
        },
        "count": 25,
        "metadata": "event data",
    }

    deserialized_result = deserialize_result(function_with_unions, result_data)

    # Since a dict can be parsed as-is without conversion, it should remain a dict
    assert isinstance(deserialized_result, dict)
    assert "event" in deserialized_result
    assert deserialized_result["count"] == 25
    assert deserialized_result["metadata"] == "event data"


def test_serialize_deserialize_roundtrip_with_unions():
    # Create test data - SamplePerson
    person = SamplePerson(
        name="Frank",
        age=45,
        birth_date=datetime(1978, 11, 5),
        balance=Decimal("3200.80"),
        id=uuid.uuid4(),
        active=True,
        tags=["director", "finance"],
    )

    # Original function call
    args = [person]
    kwargs = {"count": 75, "metadata": {"department": "finance"}}

    # Serialize arguments
    serialized_args, serialized_kwargs = serialize_args(
        function_with_unions, args, kwargs
    )

    # Deserialize arguments
    deserialized_args, deserialized_kwargs = deserialize_args(
        function_with_unions, serialized_args, serialized_kwargs
    )

    # Call function with deserialized arguments
    result = function_with_unions(*deserialized_args, **deserialized_kwargs)

    # Serialize result
    serialized_result = serialize_result(function_with_unions, result)

    # Deserialize result
    deserialized_result = deserialize_result(function_with_unions, serialized_result)

    # Verify everything is intact
    assert isinstance(deserialized_result, SampleNestedModel)
    assert deserialized_result.person.name == "Frank"
    assert deserialized_result.person.age == 45
    assert deserialized_result.person.tags == ["director", "finance"]
    assert deserialized_result.metadata
    assert deserialized_result.metadata["count"] == 75
    assert deserialized_result.metadata["extra"] == {"department": "finance"}

    # Create test data - SampleEventModel
    event = SampleEventModel(
        event_id=uuid.uuid4(),
        timestamp=datetime(2023, 1, 15, 14, 30),
        description="Quarterly review",
    )

    # Original function call
    args = [event]
    kwargs = {"count": 120, "metadata": "quarterly"}

    # Serialize arguments
    serialized_args, serialized_kwargs = serialize_args(
        function_with_unions, args, kwargs
    )

    # Deserialize arguments
    deserialized_args, deserialized_kwargs = deserialize_args(
        function_with_unions, serialized_args, serialized_kwargs
    )

    # Call function with deserialized arguments
    result = function_with_unions(*deserialized_args, **deserialized_kwargs)

    # Serialize result
    serialized_result = serialize_result(function_with_unions, result)

    # Deserialize result
    deserialized_result = deserialize_result(function_with_unions, serialized_result)

    # Verify everything is intact
    assert isinstance(deserialized_result, dict)
    assert "event" in deserialized_result
    assert deserialized_result["event"]["description"] == "Quarterly review"
    assert deserialized_result["count"] == 120
    assert deserialized_result["metadata"] == "quarterly"


# This class is used for testing list serialization
class ListContainer(BaseModel):
    items: List[SamplePerson]
    labels: List[str]


def test_serialize_list_of_primitives():
    # Test serializing lists of primitives
    int_list = [1, 2, 3, 4, 5]
    assert serialize_value(int_list) == int_list

    # Test with mixed primitive types
    mixed_list = [1, "string", 3.14, True]
    assert serialize_value(mixed_list) == mixed_list

    # Test with complex primitive types
    now = datetime.now()
    uuid_val = uuid.uuid4()
    decimal_val = Decimal("123.456")
    complex_list = [now, uuid_val, decimal_val]
    serialized = serialize_value(complex_list)
    assert serialized[0] == now.isoformat()
    assert serialized[1] == str(uuid_val)
    assert serialized[2] == str(decimal_val)


def test_deserialize_list_of_primitives():
    # Test deserializing lists of primitives
    serialized_ints = [1, 2, 3, 4, 5]
    assert deserialize_value(serialized_ints, List[int]) == serialized_ints

    # Test with mixed types that should be cast to a specific type
    serialized_strings = ["1", "2", "3"]
    assert deserialize_value(serialized_strings, List[int]) == [1, 2, 3]

    # Test with complex types
    uuid_val = uuid.uuid4()
    now = datetime.now()
    serialized_complex = [str(uuid_val), now.isoformat(), "123.456"]
    deserialized = deserialize_value(
        serialized_complex, List[Union[uuid.UUID, datetime, Decimal]]
    )

    # For Union types, it will use the first type that works
    # In this case, UUID should be the first successful type for str(uuid_val)
    assert deserialized[0] == uuid_val
    assert isinstance(deserialized[1], datetime)
    # The string "123.456" would be deserialized as a UUID which would fail,
    # then datetime which would fail, and finally Decimal which should succeed
    assert deserialized[2] == Decimal("123.456")


def test_serialize_list_of_models():
    # Create sample data
    persons = [
        SamplePerson(
            name="Person 1",
            age=30,
            birth_date=datetime(1993, 5, 10),
            balance=Decimal("500.00"),
            id=uuid.uuid4(),
            active=True,
            tags=["developer"],
        ),
        SamplePerson(
            name="Person 2",
            age=25,
            birth_date=datetime(1998, 8, 15),
            balance=Decimal("750.50"),
            id=uuid.uuid4(),
            active=False,
            tags=["designer", "ui"],
        ),
    ]

    # Test serializing a list of models
    serialized_persons = serialize_value(persons)
    assert isinstance(serialized_persons, list)
    assert len(serialized_persons) == 2
    assert isinstance(serialized_persons[0], dict)
    assert serialized_persons[0]["name"] == "Person 1"
    assert serialized_persons[1]["name"] == "Person 2"

    # Check that datetime fields are properly serialized
    assert isinstance(serialized_persons[0]["birth_date"], str)
    assert isinstance(serialized_persons[1]["birth_date"], str)
    # Verify they can be parsed as ISO format
    datetime.fromisoformat(serialized_persons[0]["birth_date"])
    datetime.fromisoformat(serialized_persons[1]["birth_date"])

    # Test serializing a model with a list field
    container = ListContainer(
        items=persons,
        labels=["employee", "contractor"],
    )

    serialized_container = serialize_value(container)
    assert isinstance(serialized_container, dict)
    assert isinstance(serialized_container["items"], list)
    assert len(serialized_container["items"]) == 2
    assert serialized_container["items"][0]["name"] == "Person 1"
    assert serialized_container["items"][1]["name"] == "Person 2"
    assert serialized_container["labels"] == ["employee", "contractor"]


def test_deserialize_list_of_models():
    # Create serialized data
    person1_id = uuid.uuid4()
    person2_id = uuid.uuid4()

    serialized_persons = [
        {
            "name": "Person 1",
            "age": 30,
            "birth_date": "1993-05-10T00:00:00",
            "balance": "500.00",
            "id": str(person1_id),
            "active": True,
            "tags": ["developer"],
        },
        {
            "name": "Person 2",
            "age": 25,
            "birth_date": "1998-08-15T00:00:00",
            "balance": "750.50",
            "id": str(person2_id),
            "active": False,
            "tags": ["designer", "ui"],
        },
    ]

    # Test deserializing a list of models
    deserialized_persons = deserialize_value(serialized_persons, List[SamplePerson])
    assert isinstance(deserialized_persons, list)
    assert len(deserialized_persons) == 2
    assert isinstance(deserialized_persons[0], SamplePerson)
    assert deserialized_persons[0].id == person1_id
    assert deserialized_persons[0].name == "Person 1"
    assert deserialized_persons[1].id == person2_id
    assert deserialized_persons[1].name == "Person 2"

    # Test deserializing a model with a list field
    serialized_container = {
        "items": serialized_persons,
        "labels": ["employee", "contractor"],
    }

    deserialized_container = deserialize_value(serialized_container, ListContainer)
    assert isinstance(deserialized_container, ListContainer)
    assert isinstance(deserialized_container.items, list)
    assert len(deserialized_container.items) == 2
    assert isinstance(deserialized_container.items[0], SamplePerson)
    assert deserialized_container.items[0].name == "Person 1"
    assert deserialized_container.items[1].name == "Person 2"
    assert deserialized_container.labels == ["employee", "contractor"]


# For testing list args and return values
def function_with_list_args_return(
    persons: List[SamplePerson], tags: List[str]
) -> List[ListContainer]:
    """Function that takes and returns lists for testing serialization/deserialization."""
    containers = []
    for i, tag in enumerate(tags):
        # Take a slice of persons for each container
        container_persons = persons[: i + 1]
        containers.append(
            ListContainer(
                items=container_persons,
                labels=[tag] * len(container_persons),
            )
        )
    return containers


def test_timestamp_serialization():
    """Test specifically for datetime serialization in Pydantic models"""
    # Create a model with a timestamp
    model = ModelWithDatetimeField(
        timestamp=datetime(2023, 5, 15, 12, 30, 45), name="Test Model"
    )

    # Serialize the model
    serialized = serialize_value(model)

    # Verify the timestamp is properly serialized as a string
    assert isinstance(serialized, dict)
    assert "timestamp" in serialized
    assert isinstance(serialized["timestamp"], str)

    # Verify it can be parsed back to a datetime
    dt = datetime.fromisoformat(serialized["timestamp"])
    assert dt == model.timestamp

    # Verify we can deserialize it back to the original model
    deserialized = deserialize_value(serialized, ModelWithDatetimeField)
    assert isinstance(deserialized, ModelWithDatetimeField)
    assert deserialized.timestamp == model.timestamp
    assert deserialized.name == model.name


def test_uuid_serialization():
    """Test specifically for UUID serialization in Pydantic models"""
    # Create a model with a UUID
    test_uuid = uuid.uuid4()
    model = ModelWithUUID(id=test_uuid, name="Test Model")

    # Serialize the model
    serialized = serialize_value(model)

    # Verify the UUID is properly serialized as a string
    assert isinstance(serialized, dict)
    assert "id" in serialized
    assert isinstance(serialized["id"], str)

    # Verify it can be parsed back to a UUID
    parsed_uuid = uuid.UUID(serialized["id"])
    assert parsed_uuid == test_uuid

    # Verify we can deserialize it back to the original model
    deserialized = deserialize_value(serialized, ModelWithUUID)
    assert isinstance(deserialized, ModelWithUUID)
    assert deserialized.id == test_uuid
    assert deserialized.name == model.name


def test_serialize_deserialize_list_roundtrip():
    # Create test data
    persons = [
        SamplePerson(
            name=f"Person {i}",
            age=30 + i,
            birth_date=datetime(1990, i, 15),
            balance=Decimal(f"{i}00.50"),
            id=uuid.uuid4(),
            active=i % 2 == 0,
            tags=[f"tag{i}", f"group{i}"],
        )
        for i in range(1, 4)
    ]
    tags = ["employee", "contractor"]

    # Serialize arguments
    serialized_args, serialized_kwargs = serialize_args(
        function_with_list_args_return, [persons, tags], {}
    )

    # Check serialized args
    assert isinstance(serialized_args[0], list)
    assert len(serialized_args[0]) == 3
    assert isinstance(serialized_args[0][0], dict)
    assert serialized_args[0][0]["name"] == "Person 1"
    assert serialized_args[1] == tags

    # Deserialize arguments
    deserialized_args, deserialized_kwargs = deserialize_args(
        function_with_list_args_return, serialized_args, serialized_kwargs
    )

    # Check deserialized args
    assert isinstance(deserialized_args[0], list)
    assert isinstance(deserialized_args[0][0], SamplePerson)
    assert deserialized_args[0][0].name == "Person 1"
    assert deserialized_args[1] == tags

    # Call function with deserialized arguments
    result = function_with_list_args_return(*deserialized_args, **deserialized_kwargs)

    # Serialize result
    serialized_result = serialize_result(function_with_list_args_return, result)

    # Check serialized result
    assert isinstance(serialized_result, list)
    assert len(serialized_result) == 2
    assert isinstance(serialized_result[0], dict)
    assert "items" in serialized_result[0]
    assert isinstance(serialized_result[0]["items"], list)

    # Deserialize result
    deserialized_result = deserialize_result(
        function_with_list_args_return,
        serialized_result,
        None,
        deserialized_args,
        deserialized_kwargs,
    )

    # Check deserialized result
    assert isinstance(deserialized_result, list)
    assert len(deserialized_result) == 2
    assert isinstance(deserialized_result[0], ListContainer)
    assert len(deserialized_result[0].items) == 1
    assert deserialized_result[0].items[0].name == "Person 1"
    assert deserialized_result[0].labels == ["employee"]
    assert len(deserialized_result[1].items) == 2
    assert deserialized_result[1].labels == ["contractor", "contractor"]


class GenericResultModel[T](BaseModel):
    content: T
    metadata: str


class SimpleData(BaseModel):
    value: int


def function_with_generic_return[T](data: T) -> GenericResultModel[T]:
    return GenericResultModel[T](content=data, metadata="Generic metadata")


def test_deserialize_generic_result():
    """Test deserialization of a result with a simple generic type."""
    original_data = SimpleData(value=123)
    args = [original_data]
    kwargs = {}

    # Simulate execution and serialization
    result = function_with_generic_return(*args, **kwargs)
    serialized_result = serialize_result(function_with_generic_return, result)

    # Deserialize the result, inferring the type from args
    deserialized = deserialize_result(
        function_with_generic_return, serialized_result, None, args, kwargs
    )

    assert isinstance(deserialized, GenericResultModel)
    assert isinstance(deserialized.content, SimpleData)
    assert deserialized.content.value == 123
    assert deserialized.metadata == "Generic metadata"


def function_with_generic_list_return[T](items: list[T]) -> GenericResultModel[list[T]]:
    return GenericResultModel[list[T]](content=items, metadata="List metadata")


def test_deserialize_generic_list_result():
    """Test deserialization where the generic type parameter is a List."""
    original_data = [SimpleData(value=1), SimpleData(value=2)]
    args = [original_data]
    kwargs = {}

    result = function_with_generic_list_return(*args, **kwargs)
    serialized_result = serialize_result(function_with_generic_list_return, result)

    deserialized = deserialize_result(
        function_with_generic_list_return, serialized_result, None, args, kwargs
    )

    assert isinstance(deserialized, GenericResultModel)
    assert isinstance(deserialized.content, list)
    assert len(deserialized.content) == 2
    assert isinstance(deserialized.content[0], SimpleData)
    assert deserialized.content[0].value == 1
    assert deserialized.content[1].value == 2
    assert deserialized.metadata == "List metadata"


# Test case where Generic comes before BaseModel (should still work)
class AltGenericResultModel[T](BaseModel):
    content: T
    metadata: str


def function_with_alt_generic_return[T](data: T) -> AltGenericResultModel[T]:
    return AltGenericResultModel[T](content=data, metadata="Alt Generic metadata")


def test_deserialize_alt_order_generic_result():
    """Test deserialization when Generic is inherited before BaseModel."""
    original_data = SimpleData(value=456)
    args = [original_data]
    kwargs = {}

    result = function_with_alt_generic_return(*args, **kwargs)
    serialized_result = serialize_result(function_with_alt_generic_return, result)

    deserialized = deserialize_result(
        function_with_alt_generic_return, serialized_result, None, args, kwargs
    )

    assert isinstance(deserialized, AltGenericResultModel)
    assert isinstance(deserialized.content, SimpleData)
    assert deserialized.content.value == 456
    assert deserialized.metadata == "Alt Generic metadata"


def dataclass_function(data: SampleDataClass) -> SampleDataClass:
    return SampleDataClass(name=data.name.upper(), value=data.value + 1)


def test_dataclass_serialization_roundtrip():
    item = SampleDataClass(name="foo", value=1)
    args = [item]
    kwargs = {}

    serialized_args, serialized_kwargs = serialize_args(
        dataclass_function, args, kwargs
    )
    assert isinstance(serialized_args[0], dict)

    deserialized_args, deserialized_kwargs = deserialize_args(
        dataclass_function, serialized_args, serialized_kwargs
    )
    assert isinstance(deserialized_args[0], SampleDataClass)

    result = dataclass_function(*deserialized_args, **deserialized_kwargs)

    serialized_result = serialize_result(dataclass_function, result)
    deserialized_result = deserialize_result(dataclass_function, serialized_result)

    assert isinstance(deserialized_result, SampleDataClass)
    assert deserialized_result.name == "FOO"
    assert deserialized_result.value == 2


def test_serialize_deserialize_dataclass_value():
    item = SampleDataClass(name="bar", value=5)
    serialized = serialize_value(item)
    assert serialized == {"name": "bar", "value": 5}

    deserialized = deserialize_value(serialized, SampleDataClass)
    assert isinstance(deserialized, SampleDataClass)
    assert deserialized.name == "bar"
    assert deserialized.value == 5
