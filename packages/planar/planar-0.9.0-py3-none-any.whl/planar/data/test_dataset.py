"""Tests for PlanarDataset."""

import polars as pl
import pyarrow as pa
import pytest
from ibis import literal

from planar import PlanarApp
from planar.data import PlanarDataset
from planar.data.config import DataConfig, SQLiteCatalogConfig
from planar.data.exceptions import (
    DataError,
    DatasetAlreadyExistsError,
    DatasetNotFoundError,
)
from planar.files.storage.config import LocalDirectoryConfig
from planar.workflows import step


@pytest.fixture
def data_config(tmp_path):
    """Create a test data configuration."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)

    catalog_path = data_dir / "test.sqlite"
    storage_path = data_dir / "ducklake_files"
    storage_path.mkdir(exist_ok=True)

    return DataConfig(
        catalog=SQLiteCatalogConfig(type="sqlite", path=str(catalog_path)),
        storage=LocalDirectoryConfig(backend="localdir", directory=str(storage_path)),
    )


@pytest.fixture(name="app")
def app_fixture(data_config):
    """Create a PlanarApp with data configuration."""
    app = PlanarApp()
    # Add data config to the app's config
    app.config.data = data_config
    return app


@pytest.mark.asyncio
async def test_dataset_create(client):
    """Test creating a dataset reference."""
    dataset = await PlanarDataset.create("test_table")
    assert dataset.name == "test_table"

    # Dataset reference exists but table isn't created until first write
    assert not await dataset.exists()

    # Write some data to actually create the table
    df = pl.DataFrame({"id": [1], "name": ["test"]})
    await dataset.write(df, mode="overwrite")

    # Now it should exist
    assert await dataset.exists()

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_create_if_not_exists(client):
    """Test creating a dataset with if_not_exists behavior."""
    # Create dataset and write data to make it exist
    dataset1 = await PlanarDataset.create("test_table")
    df = pl.DataFrame({"id": [1], "name": ["test"]})
    await dataset1.write(df, mode="overwrite")

    # Create again with if_not_exists=True (default) - should not raise
    dataset2 = await PlanarDataset.create("test_table", if_not_exists=True)
    assert dataset2.name == dataset1.name

    # Create again with if_not_exists=False - should raise
    with pytest.raises(DatasetAlreadyExistsError):
        await PlanarDataset.create("test_table", if_not_exists=False)

    # Cleanup
    await dataset1.delete()


@pytest.mark.asyncio
async def test_dataset_write_and_read_polars(client):
    """Test writing and reading data with Polars."""
    dataset = await PlanarDataset.create("test_polars")

    # Create test data
    df = pl.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "amount": [100.5, 200.0, 150.75],
        }
    )

    # Write data
    await dataset.write(df, mode="overwrite")

    # Read data back
    result = await dataset.to_polars()

    # Verify
    assert result.shape == df.shape
    assert set(result.columns) == set(df.columns)
    assert result["id"].to_list() == [1, 2, 3]
    assert result["name"].to_list() == ["Alice", "Bob", "Charlie"]

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_write_and_read_pyarrow(client):
    """Test writing and reading data with PyArrow."""
    dataset = await PlanarDataset.create("test_pyarrow")

    # Create test data
    table = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "amount": [100.5, 200.0, 150.75],
        }
    )

    # Write data
    await dataset.write(table, mode="overwrite")

    # Read data back
    result = await dataset.to_pyarrow()

    # Verify
    assert result.num_rows == table.num_rows
    assert result.column_names == table.column_names

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_append_mode(client):
    """Test appending data to a dataset."""
    dataset = await PlanarDataset.create("test_append")

    # Write initial data
    df1 = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
    await dataset.write(df1, mode="overwrite")

    # Append more data
    df2 = pl.DataFrame({"id": [3, 4], "value": ["c", "d"]})
    await dataset.write(df2, mode="append")

    result = await dataset.to_polars()

    # Verify
    assert len(result) == 4
    assert set(result["id"].to_list()) == {1, 2, 3, 4}
    assert set(result["value"].to_list()) == {"a", "b", "c", "d"}

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_overwrite_replaces_existing(client):
    """Overwrite should replace existing rows completely."""
    dataset = await PlanarDataset.create("test_overwrite")

    df1 = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
    await dataset.write(df1, mode="overwrite")
    result1 = await dataset.to_polars()
    assert result1.shape == (2, 2)

    df2 = pl.DataFrame({"id": [3], "value": ["c"]})
    await dataset.write(df2, mode="overwrite")
    result2 = await dataset.to_polars()
    assert result2.shape == (1, 2)
    assert result2["id"].to_list() == [3]
    assert result2["value"].to_list() == ["c"]

    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_read_with_filter(client):
    """Test reading data with Ibis filtering."""
    dataset = await PlanarDataset.create("test_filter")

    # Write test data
    df = pl.DataFrame({"id": range(1, 11), "value": range(10, 101, 10)})
    await dataset.write(df, mode="overwrite")

    table = await dataset.read()
    filtered_table = table.filter(table.value > literal(50))
    filtered_df = filtered_table.to_polars()

    assert len(filtered_df) == 5
    assert all(v > 50 for v in filtered_df["value"].to_list())

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_read_with_columns_and_limit(client):
    """Test reading specific columns with limit."""
    dataset = await PlanarDataset.create("test_select")

    # Write test data
    df = pl.DataFrame(
        {
            "id": range(1, 11),
            "name": [f"user_{i}" for i in range(1, 11)],
            "value": range(10, 101, 10),
        }
    )
    await dataset.write(df, mode="overwrite")

    # Read specific columns with limit
    table = await dataset.read(columns=["id", "name"], limit=5)
    result_df = table.to_polars()

    # Verify
    assert len(result_df) == 5
    assert set(result_df.columns) == {"id", "name"}
    assert "value" not in result_df.columns

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_not_found(client):
    """Test reading from non-existent dataset."""
    dataset = PlanarDataset(name="nonexistent")

    # Check exists returns False
    assert not await dataset.exists()

    # Try to read - should raise
    with pytest.raises(DatasetNotFoundError):
        await dataset.read()


@pytest.mark.asyncio
async def test_dataset_delete(client):
    """Test deleting a dataset."""
    dataset = await PlanarDataset.create("test_delete")

    # Write some data
    df = pl.DataFrame({"id": [1, 2, 3]})
    await dataset.write(df)

    # Verify it exists
    assert await dataset.exists()

    # Delete it
    await dataset.delete()

    # Verify it's gone
    assert not await dataset.exists()


@pytest.mark.asyncio
async def test_dataset_write_list_of_dicts(client):
    """Write list-of-dicts input and read back with Polars."""
    dataset = await PlanarDataset.create("test_list_of_dicts")

    rows = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    await dataset.write(rows, mode="overwrite")

    result = await dataset.to_polars()
    assert set(result.columns) == {"id", "name"}
    assert sorted(result["id"].to_list()) == [1, 2]

    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_write_dict_of_lists(client):
    """Write dict-of-lists input and read back with Polars."""
    dataset = await PlanarDataset.create("test_dict_of_lists")

    data = {"id": [1, 2], "name": ["a", "b"]}
    await dataset.write(data, mode="overwrite")

    result = await dataset.to_polars()
    assert result.shape == (2, 2)
    assert set(result["name"].to_list()) == {"a", "b"}

    await dataset.delete()


@pytest.mark.asyncio
async def test_dataset_workflow_serialization(client):
    """Test that PlanarDataset can be used as workflow input/output."""

    @step()
    async def create_data() -> PlanarDataset:
        """Create a dataset with sample data."""
        dataset = await PlanarDataset.create("workflow_data")

        df = pl.DataFrame(
            {"product": ["A", "B", "C", "D"], "sales": [100, 200, 150, 300]}
        )
        await dataset.write(df, mode="overwrite")

        return dataset

    @step()
    async def analyze_data(dataset: PlanarDataset) -> float:
        """Analyze the dataset and return total sales."""
        df = await dataset.to_polars()
        return float(df["sales"].sum())

    # Test basic workflow functionality without API
    dataset = await create_data()
    total = await analyze_data(dataset)

    # Verify results
    assert total == 750.0  # Sum of [100, 200, 150, 300]

    # Cleanup
    await dataset.delete()


@pytest.mark.asyncio
async def test_no_data_config_error(client):
    """Test error when data config is not set."""
    # Remove data config
    client.app.config.data = None

    dataset = PlanarDataset(name="test")

    with pytest.raises(DataError, match="Data configuration not found"):
        await dataset._get_connection()


@pytest.mark.asyncio
async def test_write_with_invalid_input_raises(client):
    """Unknown input types to write() should raise a DataError."""

    class Foo:
        pass

    dataset = await PlanarDataset.create("test_invalid_input")

    with pytest.raises(DataError):
        await dataset.write(Foo(), mode="overwrite")  # type: ignore

    await dataset.delete()
