"""PlanarDataset implementation for working with Ducklake tables."""

import asyncio
from typing import Literal, Self

import ibis
import polars as pl
import pyarrow as pa
from ibis.backends.duckdb import Backend as DuckDBBackend
from ibis.common.exceptions import TableNotFound
from pydantic import BaseModel

from planar.config import PlanarConfig
from planar.files.storage.config import LocalDirectoryConfig, S3Config
from planar.logging import get_logger
from planar.session import get_config

from .exceptions import DataError, DatasetAlreadyExistsError, DatasetNotFoundError

logger = get_logger(__name__)


class PlanarDataset(BaseModel):
    """Reference to a Ducklake table.

    This class provides a simple interface for working with datasets in Ducklake,
    handling creation, reading, writing, and deletion of tabular data.
    """

    # TODO: Add support for schema name (ie. namespace)
    name: str  # Table name in Ducklake
    # TODO: Add snapshot version: no version = latest, otherwise time travel on read operations
    # TODO: Add partition support? A Dataset representation could be a table with a partition column

    model_config = {"arbitrary_types_allowed": True}
    # TODO: Add serialization metadata to make clear this is a dataset reference
    # like EntityField.

    @classmethod
    async def create(cls, name: str, if_not_exists: bool = True) -> Self:
        """Create a dataset reference.

        Note: The actual table is created when data is first written to avoid
        DuckDB's requirement that tables have at least one column.

        Args:
            name: Name of the dataset
            if_not_exists: If True, don't raise error if dataset exists. default: True
            catalog: Catalog name in Ducklake

        Returns:
            PlanarDataset instance

        Raises:
            DatasetAlreadyExistsError: If dataset exists and if_not_exists=False
        """
        dataset = cls(name=name)

        # Check if dataset already exists
        if await dataset.exists():
            if not if_not_exists:
                raise DatasetAlreadyExistsError(f"Dataset {name} already exists")
            logger.debug("dataset already exists", dataset_name=name)
        else:
            logger.debug("dataset reference created", dataset_name=name)

        return dataset

    async def exists(self) -> bool:
        """Check if the dataset exists in Ducklake."""
        con = await self._get_connection()
        try:
            # TODO: Query for the table name directly
            tables = await asyncio.to_thread(con.list_tables)
            return self.name in tables
        except Exception as e:
            logger.warning("failed to check dataset existence", error=str(e))
            return False

    async def write(
        self,
        data: pl.DataFrame | ibis.Table | list | dict,
        mode: Literal["overwrite", "append"] = "append",
    ) -> None:
        """Write data to the dataset.

        Args:
            data: Data to write (Polars DataFrame, PyArrow Table, or Ibis expression)
            mode: Write mode - "append" or "overwrite"
        """
        con = await self._get_connection()
        overwrite = mode == "overwrite"

        try:
            if not await self.exists():
                await asyncio.to_thread(
                    con.create_table, self.name, data, overwrite=overwrite
                )
            else:
                # TODO: Explore if workflow context can be used to set metadata
                # on the snapshot version for lineage
                if isinstance(data, pl.DataFrame):
                    await asyncio.to_thread(
                        con.insert,
                        self.name,
                        ibis.memtable(data),
                        overwrite=overwrite,
                    )
                else:
                    await asyncio.to_thread(
                        con.insert, self.name, data, overwrite=overwrite
                    )

            logger.debug(
                "wrote data to dataset",
                dataset_name=self.name,
                mode=mode,
            )
        except Exception as e:
            raise DataError(f"Failed to write data: {e}") from e

    async def read(
        self,
        columns: list[str] | None = None,
        limit: int | None = None,
    ) -> ibis.Table:
        """Read data as an Ibis table expression.

        Args:
            columns: Optional list of columns to select
            limit: Optional row limit

        Returns:
            Ibis table expression that can be further filtered using Ibis methods
        """
        con = await self._get_connection()

        try:
            table = await asyncio.to_thread(con.table, self.name)

            if columns:
                table = table.select(columns)

            if limit:
                table = table.limit(limit)

            return table
        except TableNotFound as e:
            raise DatasetNotFoundError(f"Dataset {self.name} not found") from e
        except Exception as e:
            raise DataError(f"Failed to read data: {e}") from e

    async def to_polars(self) -> pl.DataFrame:
        """Read entire dataset as Polars DataFrame."""
        table = await self.read()
        return await asyncio.to_thread(table.to_polars)

    async def to_pyarrow(self) -> pa.Table:
        """Read entire dataset as PyArrow Table."""
        table = await self.read()
        return await asyncio.to_thread(table.to_pyarrow)

    async def delete(self) -> None:
        """Delete the dataset."""
        con = await self._get_connection()
        try:
            await asyncio.to_thread(con.drop_table, self.name, force=True)
            logger.info("deleted dataset", dataset_name=self.name)
        except Exception as e:
            raise DataError(f"Failed to delete dataset: {e}") from e

    async def _get_connection(self) -> DuckDBBackend:
        """Get Ibis connection to Ducklake."""
        config = get_config()

        if not config.data:
            raise DataError(
                "Data configuration not found. Please configure 'data' in your planar.yaml"
            )

        # TODO: Add cached connection pooling or memoize the connection
        return await self._create_connection(config)

    async def _create_connection(self, config: PlanarConfig) -> DuckDBBackend:
        """Create Ibis DuckDB connection with Ducklake."""
        data_config = config.data
        if not data_config:
            raise DataError("Data configuration not found")

        # Connect to DuckDB with Ducklake extension
        con = await asyncio.to_thread(ibis.duckdb.connect, extensions=["ducklake"])

        # Build Ducklake connection string based on catalog type
        catalog_config = data_config.catalog

        if catalog_config.type == "duckdb":
            metadata_path = catalog_config.path
        elif catalog_config.type == "postgres":
            # Use connection components to build postgres connection string
            pg = catalog_config
            metadata_path = f"postgres:dbname={pg.db}"
            if pg.host:
                metadata_path += f" host={pg.host}"
            if pg.port:
                metadata_path += f" port={pg.port}"
            if pg.user:
                metadata_path += f" user={pg.user}"
            if pg.password:
                metadata_path += f" password={pg.password}"
        elif catalog_config.type == "sqlite":
            metadata_path = f"sqlite:{catalog_config.path}"
        else:
            raise ValueError(f"Unsupported catalog type: {catalog_config.type}")

        # Build ATTACH statement
        attach_sql = f"ATTACH 'ducklake:{metadata_path}'"

        # Add data path from storage config
        storage = data_config.storage
        if isinstance(storage, LocalDirectoryConfig):
            data_path = storage.directory
        elif isinstance(storage, S3Config):
            data_path = f"s3://{storage.bucket_name}/"
        else:
            # Generic fallback
            data_path = getattr(storage, "path", None) or getattr(
                storage, "directory", "."
            )

        attach_sql += f" (DATA_PATH '{data_path}')"

        # Attach to Ducklake
        try:
            await asyncio.to_thread(con.raw_sql, attach_sql)
        except Exception as e:
            raise DataError(f"Failed to attach to Ducklake: {e}") from e

        # Check available catalogs (what ibis calls schemas) and use the correct one
        try:
            catalogs = await asyncio.to_thread(con.list_catalogs)
            logger.debug("available catalogs", catalogs=catalogs)

            # Find the ducklake catalog (it might have a different name pattern)
            ducklake_catalog = None
            for cat in catalogs:
                if "ducklake" in cat.lower() or cat == data_config.catalog_name:
                    ducklake_catalog = cat
                    break

            if ducklake_catalog:
                if not ducklake_catalog.replace("_", "").replace("-", "").isalnum():
                    raise DataError(f"Invalid catalog name format: {ducklake_catalog}")
                await asyncio.to_thread(con.raw_sql, f"USE {ducklake_catalog}")
                logger.debug("using catalog", catalog=ducklake_catalog)
            else:
                catalog_name = data_config.catalog_name
                if not catalog_name.replace("_", "").replace("-", "").isalnum():
                    raise DataError(f"Invalid catalog name format: {catalog_name}")
                await asyncio.to_thread(
                    con.raw_sql,
                    f"CREATE SCHEMA IF NOT EXISTS {catalog_name}",
                )
                await asyncio.to_thread(con.raw_sql, f"USE {catalog_name}")
                logger.debug(
                    "created and using catalog", catalog=data_config.catalog_name
                )

        except Exception as e:
            logger.warning("failed to set catalog, using default", error=str(e))
            # Continue without setting catalog - will use qualified names

        return con
