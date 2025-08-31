"""Configuration for Planar data module."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from planar.files.storage.config import StorageConfig


class DuckDBCatalogConfig(BaseModel):
    """Configuration for DuckDB catalog backend."""

    type: Literal["duckdb"]
    path: str  # Path to .ducklake file


class PostgresCatalogConfig(BaseModel):
    """Configuration for PostgreSQL catalog backend."""

    type: Literal["postgres"]
    host: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    db: str


class SQLiteCatalogConfig(BaseModel):
    """Configuration for SQLite catalog backend."""

    type: Literal["sqlite"]
    path: str  # Path to .sqlite file


# Discriminated union for catalog configurations
CatalogConfig = Annotated[
    DuckDBCatalogConfig | PostgresCatalogConfig | SQLiteCatalogConfig,
    Field(discriminator="type"),
]


class DataConfig(BaseModel):
    """Configuration for data features."""

    catalog: CatalogConfig
    storage: StorageConfig  # Reuse existing StorageConfig from files

    # Optional settings
    catalog_name: str = "planar_data"  # Default catalog name in Ducklake
