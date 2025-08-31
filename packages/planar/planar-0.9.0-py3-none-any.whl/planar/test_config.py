import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from planar.config import (
    JWT_COPLANE_CONFIG,
    LOCAL_CORS_CONFIG,
    PROD_CORS_CONFIG,
    InvalidConfigurationError,
    PostgreSQLConfig,
    SecurityConfig,
    SQLiteConfig,
    load_config,
    load_environment_aware_config,
)

VALID_CONFIG = """
db_connections:
  sqlite_test:
    driver: sqlite
    path: /tmp/test.db

  pg_test1:
    driver: postgresql
    db: mydb
    user: user

  pg_test2:
    driver: postgresql+asyncpg
    host: db.example.com
    port: 6432
    user: readonly
    password: secret
    db: analytics

app:
  db_connection: pg_test2
"""


def test_valid_full_config():
    config = load_config(VALID_CONFIG)

    assert config.app.db_connection == "pg_test2"
    assert len(config.db_connections) == 3

    # Test SQLite config
    sqlite = config.db_connections["sqlite_test"]
    assert isinstance(sqlite, SQLiteConfig)
    assert str(sqlite.connection_url()) == "sqlite+aiosqlite:////tmp/test.db"

    # Test minimal PostgreSQL config
    pg1 = config.db_connections["pg_test1"]
    assert isinstance(pg1, PostgreSQLConfig)
    assert str(pg1.connection_url()) == "postgresql+asyncpg://user@/mydb"

    # Test full PostgreSQL config
    pg2 = config.db_connections["pg_test2"]
    assert isinstance(pg2, PostgreSQLConfig)
    assert pg2.port == 6432
    assert str(pg2.connection_url()) == (
        "postgresql+asyncpg://readonly:***@db.example.com:6432/analytics"
    )

    # Test selected connection
    assert config.connection_url() == pg2.connection_url()


def test_missing_required_fields():
    config_yaml = """
    db_connections:
      invalid:
        driver: sqlite
        # missing path
    app:
      db_connection: invalid
    """

    with pytest.raises(InvalidConfigurationError) as excinfo:
        load_config(config_yaml)

    assert "path" in str(excinfo.value)


def test_invalid_driver():
    config_yaml = """
    db_connections:
      invalid:
        driver: mysql
        database: test
    app:
      db_connection: invalid
    """

    with pytest.raises(InvalidConfigurationError) as excinfo:
        load_config(config_yaml)

    assert "driver" in str(excinfo.value)


def test_invalid_port_type():
    config_yaml = """
    db_connections:
      invalid:
        driver: postgresql
        port: 'not-an-int'
        db: test
    app:
      db_connection: invalid
    """

    with pytest.raises(InvalidConfigurationError) as excinfo:
        load_config(config_yaml)

    assert "port" in str(excinfo.value)


def test_missing_db_connection_reference():
    config_yaml = """
    db_connections:
      exists:
        driver: sqlite
        path: test.db
    app:
      db_connection: missing
    """

    with pytest.raises(InvalidConfigurationError) as excinfo:
        load_config(config_yaml)

    assert "missing" in str(excinfo.value)


def test_empty_config():
    with pytest.raises(InvalidConfigurationError):
        load_config("")


def test_invalid_yaml_syntax():
    invalid_yaml = """
    db_connections
      invalid: yaml
    """

    with pytest.raises(InvalidConfigurationError) as excinfo:
        load_config(invalid_yaml)

    assert "mapping values are not allowed here" in str(excinfo.value)


def test_postgresql_minimal_config():
    config_yaml = """
    db_connections:
      minimal_pg:
        driver: postgresql
        db: essential
    app:
      db_connection: minimal_pg
    """

    config = load_config(config_yaml)
    pg = config.db_connections["minimal_pg"]
    assert isinstance(pg, PostgreSQLConfig)
    assert pg.host is None
    assert pg.port is None
    assert pg.user is None
    assert pg.password is None
    assert str(pg.connection_url()) == "postgresql+asyncpg:///essential"


def test_connection_priorities():
    config_yaml = """
    db_connections:
      pg_env:
        driver: postgresql+asyncpg
        host: localhost
        db: testdb
    app:
      db_connection: pg_env
    """

    config = load_config(config_yaml)
    conn_str = str(config.connection_url())
    assert "asyncpg" in conn_str
    assert "localhost" in conn_str
    assert "testdb" in conn_str


def test_config_with_extra_fields():
    config_yaml = """
    db_connections:
      with_extras:
        driver: sqlite
        path: data.db
        unknown_field: should_be_ignored
    app:
      db_connection: with_extras
      extra_setting: 123
    """

    config = load_config(config_yaml)
    # Should parse without errors and ignore extra fields
    assert config.app.db_connection == "with_extras"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file for testing."""
    config_file = temp_dir / "test_config.yaml"
    yield str(config_file)


@pytest.fixture
def override_config_content():
    """Sample override config content for testing."""
    return """
db_connections:
  custom_db:
    driver: postgresql
    host: custom.example.com
    port: 5433
    user: custom_user
    password: custom_pass
    db: custom_db

app:
  db_connection: custom_db

security:
    cors:
        allow_origins: ["https://custom.example.com"]
        allow_credentials: true
        allow_methods: ["GET", "POST"]
        allow_headers: ["Authorization"]
"""


def test_load_environment_aware_config_dev_default():
    """Test loading default dev configuration."""
    with patch.dict(os.environ, {"PLANAR_ENV": "dev", "PLANAR_CONFIG": ""}, clear=True):
        config = load_environment_aware_config()

        assert config.environment == "dev"
        assert config.security.cors == LOCAL_CORS_CONFIG
        assert config.security.jwt is None
        assert config.app.db_connection == "app"
        assert isinstance(config.db_connections["app"], SQLiteConfig)
        assert config.db_connections["app"].path == "planar_dev.db"


def test_load_environment_aware_config_prod_default():
    """Test loading default prod configuration."""
    with patch.dict(
        os.environ, {"PLANAR_ENV": "prod", "PLANAR_CONFIG": ""}, clear=False
    ):
        config = load_environment_aware_config()

        assert config.environment == "prod"
        assert config.security == SecurityConfig(
            cors=PROD_CORS_CONFIG, jwt=JWT_COPLANE_CONFIG
        )
        assert config.app.db_connection == "app"
        assert isinstance(config.db_connections["app"], SQLiteConfig)
        assert config.db_connections["app"].path == "planar.db"


def test_load_environment_aware_config_with_explicit_config_path(
    temp_config_file, override_config_content
):
    """Test loading config with explicit PLANAR_CONFIG path."""
    # Write override config to temp file
    with open(temp_config_file, "w") as f:
        f.write(override_config_content)

    with patch.dict(
        os.environ,
        {"PLANAR_CONFIG": temp_config_file, "PLANAR_ENV": "dev"},
        clear=False,
    ):
        config = load_environment_aware_config()

        # Should use override config
        assert config.app.db_connection == "custom_db"
        assert isinstance(config.db_connections["custom_db"], PostgreSQLConfig)
        assert config.db_connections["custom_db"].host == "custom.example.com"
        assert config.db_connections["custom_db"].port == 5433


def test_load_environment_aware_config_with_env_var_expansion(temp_config_file):
    """Test environment variable expansion in config files."""
    config_with_env_vars = """
db_connections:
  env_db:
    driver: postgresql
    host: ${DB_HOST}
    port: ${DB_PORT}
    user: ${DB_USER}
    password: ${DB_PASSWORD}
    db: ${DB_NAME}

app:
  db_connection: env_db
"""

    with open(temp_config_file, "w") as f:
        f.write(config_with_env_vars)

    env_vars = {
        "PLANAR_CONFIG": temp_config_file,
        "PLANAR_ENV": "dev",
        "DB_HOST": "env.example.com",
        "DB_PORT": "5434",
        "DB_USER": "env_user",
        "DB_PASSWORD": "env_pass",
        "DB_NAME": "env_db",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        config = load_environment_aware_config()

        db_config = config.db_connections["env_db"]
        assert isinstance(db_config, PostgreSQLConfig)
        assert db_config.host == "env.example.com"
        assert db_config.port == 5434
        assert db_config.user == "env_user"
        assert db_config.password == "env_pass"
        assert db_config.db == "env_db"


def test_load_environment_aware_config_missing_explicit_file():
    """Test error when explicit config file doesn't exist."""
    non_existent_path = "/path/that/does/not/exist.yaml"

    with patch.dict(os.environ, {"PLANAR_CONFIG": non_existent_path}, clear=False):
        with pytest.raises(InvalidConfigurationError) as excinfo:
            load_environment_aware_config()

        assert "Configuration file not found" in str(excinfo.value)
        assert non_existent_path in str(excinfo.value)


def test_load_environment_aware_config_invalid_yaml(temp_config_file):
    """Test error handling for invalid YAML in override config."""
    invalid_yaml = """
db_connections:
  invalid
    driver: sqlite
"""

    with open(temp_config_file, "w") as f:
        f.write(invalid_yaml)

    with patch.dict(os.environ, {"PLANAR_CONFIG": temp_config_file}, clear=False):
        with pytest.raises(InvalidConfigurationError) as excinfo:
            load_environment_aware_config()

        assert "Error parsing override configuration file" in str(excinfo.value)


def test_load_environment_aware_config_partial_override(temp_config_file):
    """Test that partial override configs merge correctly with defaults."""
    partial_override = """
security:
  cors:
    allow_origins: ["https://custom.example.com"]
"""

    with open(temp_config_file, "w") as f:
        f.write(partial_override)

    with patch.dict(
        os.environ,
        {"PLANAR_CONFIG": temp_config_file, "PLANAR_ENV": "dev"},
        clear=False,
    ):
        config = load_environment_aware_config()

        # Should override specific fields
        assert config.security.cors.allow_origins == ["https://custom.example.com"]

        # Should keep defaults for non-overridden fields
        assert config.app.db_connection == "app"  # default
        assert config.security.cors.allow_credentials  # from LOCAL_CORS_CONFIG
        assert config.environment == "dev"
        assert isinstance(config.db_connections["app"], SQLiteConfig)


def test_load_environment_aware_config_with_entry_point_path(
    temp_dir, override_config_content
):
    """Test config file discovery using PLANAR_ENTRY_POINT."""
    entry_point_path = temp_dir / "app.py"
    config_path = temp_dir / "planar.dev.yaml"

    # Create the config file in the entry point directory
    with open(config_path, "w") as f:
        f.write(override_config_content)

    env_vars = {"PLANAR_ENTRY_POINT": str(entry_point_path), "PLANAR_ENV": "dev"}

    # Clear PLANAR_CONFIG to test entry point discovery
    with patch.dict(os.environ, env_vars, clear=False):
        if "PLANAR_CONFIG" in os.environ:
            del os.environ["PLANAR_CONFIG"]

        config = load_environment_aware_config()

        # Should find and use the config file from entry point directory
        assert config.app.db_connection == "custom_db"


def test_load_environment_aware_config_with_env_dev_file(temp_dir):
    """Test loading environment variables from .env.dev file."""
    entry_point_path = temp_dir / "app.py"
    env_dev_path = temp_dir / ".env.dev"

    # Create .env.dev file with test variables
    env_content = """
DB_HOST=dev.example.com
DB_PORT=5433
DB_USER=dev_user
DB_PASSWORD=dev_secret
"""
    with open(env_dev_path, "w") as f:
        f.write(env_content)

    # Create a config file that uses these env vars
    config_content = """
db_connections:
  app:
    driver: postgresql
    host: ${DB_HOST}
    port: ${DB_PORT}
    user: ${DB_USER}
    password: ${DB_PASSWORD}
    db: test_db
"""
    config_path = temp_dir / "planar.dev.yaml"
    with open(config_path, "w") as f:
        f.write(config_content)

    env_vars = {
        "PLANAR_ENTRY_POINT": str(entry_point_path),
        "PLANAR_ENV": "dev",
        "PLANAR_CONFIG": str(config_path),
    }

    with patch.dict(os.environ, env_vars, clear=False):
        config = load_environment_aware_config()

        # Verify that env vars from .env.dev were loaded and used
        db_config = config.db_connections["app"]
        assert isinstance(db_config, PostgreSQLConfig)
        assert db_config.host == "dev.example.com"
        assert db_config.port == 5433
        assert db_config.user == "dev_user"
        assert db_config.password == "dev_secret"


def test_load_environment_aware_config_with_generic_env_file(temp_dir):
    """Test loading environment variables from generic .env file."""
    entry_point_path = temp_dir / "app.py"
    env_path = temp_dir / ".env"

    # Create .env file with test variables
    env_content = """
DB_HOST=generic.example.com
DB_PORT=5432
DB_USER=generic_user
DB_PASSWORD=generic_secret
"""
    with open(env_path, "w") as f:
        f.write(env_content)

    # Create a config file that uses these env vars
    config_content = """
db_connections:
  app:
    driver: postgresql
    host: ${DB_HOST}
    port: ${DB_PORT}
    user: ${DB_USER}
    password: ${DB_PASSWORD}
    db: test_db
"""
    config_path = temp_dir / "planar.yaml"
    with open(config_path, "w") as f:
        f.write(config_content)

    env_vars = {
        "PLANAR_ENTRY_POINT": str(entry_point_path),
        "PLANAR_ENV": "prod",  # Using prod to test generic .env fallback
        "PLANAR_CONFIG": str(config_path),
    }

    with patch.dict(os.environ, env_vars, clear=False):
        config = load_environment_aware_config()

        # Verify that env vars from .env were loaded and used
        db_config = config.db_connections["app"]
        assert isinstance(db_config, PostgreSQLConfig)
        assert db_config.host == "generic.example.com"
        assert db_config.port == 5432
        assert db_config.user == "generic_user"
        assert db_config.password == "generic_secret"
