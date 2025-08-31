import json
import logging
import logging.config
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Dict, Literal

import boto3
import yaml
from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    SecretStr,
    ValidationError,
    model_validator,
)
from sqlalchemy import URL, make_url

from planar.data.config import DataConfig
from planar.files.storage.config import LocalDirectoryConfig, StorageConfig
from planar.logging import get_logger

logger = get_logger(__name__)


class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"


class InvalidConfigurationError(Exception):
    pass


class LogLevel(str, Enum):
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LoggerConfig(BaseModel):
    level: LogLevel = LogLevel.INFO
    propagate: bool | None = False
    file: str | None = None


class SQLiteConfig(BaseModel):
    driver: Literal["sqlite", "sqlite+aiosqlite"] = "sqlite+aiosqlite"
    path: str
    strict: bool = False

    def connection_url(self) -> URL:
        driver = self.driver
        if driver == "sqlite":
            # allow "sqlite" to be used as a shortcut for "sqlite+aiosqlite"
            driver = "sqlite+aiosqlite"
        return URL.create(drivername=driver, database=self.path)


class PostgreSQLConfig(BaseModel):
    driver: Literal["postgresql", "postgresql+asyncpg"] = (
        "postgresql+asyncpg"  # Allow async PostgreSQL
    )
    host: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    db: str | None

    def connection_url(self) -> URL:
        driver = self.driver
        if driver == "postgresql":
            # allow "postgresql" to be used as a shortcut for "postgresql+asyncpg"
            # we only support asyncpg, but this lets users use "postgresql"
            driver = "postgresql+asyncpg"
        return URL.create(
            drivername=driver,
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            database=self.db,
        )


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI provider."""

    api_key: SecretStr
    base_url: str | None = None
    organization: str | None = None


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic provider."""

    api_key: SecretStr
    base_url: str | None = None


class GeminiConfig(BaseModel):
    """Configuration for Google Gemini provider."""

    api_key: SecretStr


class AIProvidersConfig(BaseModel):
    """Configuration for AI providers."""

    openai: OpenAIConfig | None = None
    anthropic: AnthropicConfig | None = None
    gemini: GeminiConfig | None = None


DatabaseConfig = Annotated[
    SQLiteConfig | PostgreSQLConfig, Field(discriminator="driver")
]


class AppConfig(BaseModel):
    db_connection: str
    max_db_conflict_retries: int | None = None


def default_storage_config() -> StorageConfig:
    return LocalDirectoryConfig(backend="localdir", directory=".files")


class CorsConfig(BaseModel):
    allow_origins: list[str] | str
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]

    @model_validator(mode="after")
    def validate_allow_origins(cls, instance):
        if instance.allow_credentials and "*" in instance.allow_origins:
            raise ValueError(
                "allow_credentials cannot be True if allow_origins includes '*'. Must explicitly specify allowed origins."
            )
        return instance


LOCAL_CORS_CONFIG = CorsConfig(
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROD_CORS_CONFIG = CorsConfig(
    allow_origins=r"^https://(?:[a-zA-Z0-9-]+\.)+coplane\.(dev|com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JWTConfig(BaseModel):
    client_id: str | None = None
    org_id: str | None = None
    additional_exclusion_paths: list[str] | None = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_client_id(cls, instance):
        if not instance.client_id or not instance.org_id:
            raise ValueError("Both client_id and org_id required to enable JWT")
        return instance


# Coplane ORG JWT config
JWT_COPLANE_CONFIG = JWTConfig(
    client_id="client_01JSJHJPKG09TMSK6NHJP0S180",
    org_id="org_01JY4QP57Y7H4EQ7HT3BGN7TNK",
)


class OtelConfig(BaseModel):
    collector_endpoint: HttpUrl
    resource_attributes: dict[str, str] | None = None


def install_otel_provider(otel_config: OtelConfig):
    try:
        from planar.logging.otel import get_otel_collector_handler  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "OpenTelemetry is not installed. Please install it to use OpenTelemetry logging."
        ) from e
    return get_otel_collector_handler(
        otel_config.collector_endpoint, otel_config.resource_attributes
    )


class AuthzConfig(BaseModel):
    enabled: bool = True
    policy_file: str | None = None


class ServiceTokenConfig(BaseModel):
    token: str | None = Field(None, min_length=1)


class SecurityConfig(BaseModel):
    cors: CorsConfig = PROD_CORS_CONFIG
    jwt: JWTConfig | None = None
    service_token: ServiceTokenConfig | None = None
    authz: AuthzConfig | None = None


class PlanarConfig(BaseModel):
    db_connections: Dict[str, DatabaseConfig | str]
    app: AppConfig
    ai_providers: AIProvidersConfig | None = None
    storage: StorageConfig | None = default_storage_config()
    sse_hub: str | bool = False
    environment: Environment = Environment.DEV
    security: SecurityConfig = SecurityConfig()
    logging: dict[str, LoggerConfig] | None = None
    use_alembic: bool | None = True
    otel: OtelConfig | None = None
    data: DataConfig | None = None

    # forbid extra keys in the config to prevent accidental misconfiguration
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_db_connection_reference(cls, instance):
        if instance.app.db_connection not in instance.db_connections:
            raise ValueError(
                f"Invalid db_connection reference: {instance.app.db_connection}"
            )
        return instance

    def connection_url(self) -> URL:
        connection = self.db_connections[self.app.db_connection]
        if isinstance(connection, str):
            # treat the connection as a URL string
            return make_url(connection)
        return connection.connection_url()

    def configure_logging(self):
        loggers_config = {
            # root logger default level should be INFO
            "": LoggerConfig(level=LogLevel.INFO),
            # force disable uvicorn's logger and let it propagate to root
            "uvicorn": LoggerConfig(level=LogLevel.NOTSET, propagate=True),
        }
        if self.logging:
            # Merge provided logging config with defaults
            loggers_config.update(self.logging)

        root_logger_config = None
        loggers = {}
        # define some standard formatters and handlers
        formatters = {
            "structured_console": {
                "()": "planar.logging.formatter.StructuredFormatter",
                "use_colors": True,
            },
            "structured_file": {
                "()": "planar.logging.formatter.StructuredFormatter",
                "use_colors": False,
            },
        }
        filters = {
            "add_attributes": {
                "()": "planar.logging.attributes.ExtraAttributesFilter",
            },
        }
        handlers = {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "structured_console",
                "stream": sys.stderr,
                "filters": ["add_attributes"],
            },
        }

        for name, cfg in loggers_config.items():
            default_handler = "console"

            if cfg.file:
                # File was specified. Create a handler for that file if it doesn't exist already
                default_handler = f"file:{cfg.file}"
                if default_handler not in handlers:
                    handlers[default_handler] = {
                        "class": "logging.FileHandler",
                        "formatter": "structured_file",
                        "filename": cfg.file,
                        "filters": ["add_attributes"],
                    }

            logging_module_cfg = {
                "level": cfg.level.value,
                "handlers": [default_handler] if not cfg.propagate else [],
                "propagate": cfg.propagate,
            }

            if name == "":
                root_logger_config = logging_module_cfg
            else:
                loggers[name] = logging_module_cfg

        logging_config = dict(
            version=1,
            disable_existing_loggers=False,
            root=root_logger_config,
            loggers=loggers,
            handlers=handlers,
            formatters=formatters,
            filters=filters,
        )
        logging.config.dictConfig(logging_config)

        if self.otel:
            handler = install_otel_provider(self.otel)
            for k, v in loggers.items():
                if not v["propagate"]:
                    # If the logger does not propagate, we need to add the otel handler
                    logger = logging.getLogger(k)
                    logger.handlers.append(handler)
            # always add otel handler to the root logger so it forwards
            # propagated logs
            logging.root.addHandler(handler)


def load_config(yaml_str: str) -> PlanarConfig:
    try:
        raw = yaml.safe_load(yaml_str) or {}
        return PlanarConfig.model_validate(raw)
    except (ValidationError, yaml.YAMLError) as e:
        raise InvalidConfigurationError(f"Configuration error: {e}") from e


def load_config_from_file(file_path: Path) -> PlanarConfig:
    """
    Load configuration from a YAML file.

    Args:
        file_path: Path to the YAML config file

    Returns:
        Parsed PlanarConfig object

    Raises:
        InvalidConfigurationError: If the config file cannot be loaded or is invalid
    """
    try:
        with open(file_path, "r") as f:
            yaml_str = f.read()
        return load_config(yaml_str)
    except FileNotFoundError:
        raise InvalidConfigurationError(f"Configuration file not found: {file_path}")
    except (ValidationError, yaml.YAMLError) as e:
        raise InvalidConfigurationError(
            f"Configuration error in {file_path}: {e}"
        ) from e


def sqlite_config(db_path: str) -> PlanarConfig:
    return PlanarConfig(
        app=AppConfig(db_connection="app"),
        db_connections={"app": SQLiteConfig(path=db_path)},
    )


def aws_postgresql_config() -> PlanarConfig:
    # Get the secret name from environment variable
    secret_name = os.environ.get("DB_SECRET_NAME")

    # Get credentials from Secrets Manager
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    credentials = json.loads(response["SecretString"])

    return PlanarConfig(
        app=AppConfig(db_connection="app"),
        db_connections={
            "app": PostgreSQLConfig(
                host=credentials["host"],
                port=credentials["port"],
                user=credentials["username"],
                password=credentials["password"],
                db=credentials["dbname"],
            )
        },
    )


def connection_string_config(connection_string: str) -> PlanarConfig:
    return PlanarConfig(
        app=AppConfig(db_connection="app"),
        db_connections={"app": connection_string},
    )


def get_environment() -> str:
    """Get the current Planar environment (dev or prod), defaulting to dev."""
    return os.environ.get("PLANAR_ENV", "dev")


def get_config_path() -> Path | None:
    """Get the path to the config file from environment variable"""
    config_path = os.environ.get("PLANAR_CONFIG")
    return Path(config_path) if config_path else None


def deep_merge_dicts(
    source: Dict[str, Any], destination: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deeply merge dictionary `source` into `destination`.

    Modifies `destination` in place.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Get node or create one
            node = destination.setdefault(key, {})
            if isinstance(node, dict):
                deep_merge_dicts(value, node)
            else:
                # If the destination node is not a dict, overwrite it
                destination[key] = value
        else:
            destination[key] = value
    return destination


def load_environment_aware_env_vars() -> None:
    """
    Load environment variables based on environment settings.

    We look for .env file in the entry point and local directory, with environment
    specific files (e.g. .env.dev, .env.prod) taking precedence.
    """
    env = get_environment()
    paths_to_check = []
    if entry_point := os.environ.get("PLANAR_ENTRY_POINT"):
        entry_point_dir = Path(entry_point).parent
        paths_to_check.append(entry_point_dir / f".env.{env}")
        paths_to_check.append(entry_point_dir / ".env")
    paths_to_check.append(Path(f".env.{env}"))
    paths_to_check.append(Path(".env"))

    for path in paths_to_check:
        if path.exists():
            load_dotenv(path)
            return


def load_environment_aware_config[ConfigClass]() -> PlanarConfig:
    """
    Load configuration based on environment settings, using environment variables
    and config files.

    Priority order:
    1. Explicit path via PLANAR_CONFIG environment variable.
    2. Environment-specific file (planar.{env}.yaml) overriding defaults.
    3. Default configuration based on environment (dev/prod).

    Returns:
        Configured PlanarConfig object

    Raises:
        InvalidConfigurationError: If configuration loading or validation fails.
    """
    load_environment_aware_env_vars()
    env = get_environment()

    if env == "dev":
        base_config = sqlite_config(db_path="planar_dev.db")
        base_config.security = SecurityConfig(cors=LOCAL_CORS_CONFIG)
        base_config.environment = Environment.DEV
    else:
        base_config = sqlite_config(db_path="planar.db")
        base_config.environment = Environment.PROD
        base_config.security = SecurityConfig(
            cors=PROD_CORS_CONFIG, jwt=JWT_COPLANE_CONFIG
        )

    # Convert base config to dict for merging
    # Use by_alias=False to work with Python field names before validation
    base_dict = base_config.model_dump(mode="python", by_alias=False)

    override_config_path = get_config_path()
    if override_config_path:
        if not override_config_path.exists():
            raise InvalidConfigurationError(
                f"Configuration file not found: {override_config_path}"
            )
    else:
        paths_to_check = []
        if os.environ.get("PLANAR_ENTRY_POINT"):
            # Extract the directory from the entry point path
            entry_point_dir = Path(os.environ["PLANAR_ENTRY_POINT"]).parent
            paths_to_check = [
                entry_point_dir / f"planar.{env}.yaml",
                entry_point_dir / "planar.yaml",
            ]
        paths_to_check.append(Path(f"planar.{env}.yaml"))
        paths_to_check.append(Path("planar.yaml"))

        override_config_path = next(
            (path for path in paths_to_check if path.exists()), None
        )
        if override_config_path is None:
            logger.warning(
                "no override config file found, using default config",
                search_paths=[str(p) for p in paths_to_check],
                env=env,
            )

    merged_dict = base_dict
    if override_config_path and override_config_path.exists():
        logger.info(
            "using override config file", override_config_path=override_config_path
        )
        try:
            # We can't use load_config_from_file here because we expect
            # the override config to not be a fully validated PlanarConfig object,
            # and we need to merge it onto the base default config.
            with open(override_config_path, "r") as f:
                override_yaml_str = f.read()

            # Expand environment variables in the YAML string
            processed_yaml_str = os.path.expandvars(override_yaml_str)
            logger.debug(
                "processed override yaml string", processed_yaml_str=processed_yaml_str
            )

            override_dict = yaml.safe_load(processed_yaml_str) or {}
            logger.debug("loaded override config", override_dict=override_dict)

            # Deep merge the override onto the base dictionary
            merged_dict = deep_merge_dicts(override_dict, base_dict)
            logger.debug("merged config dict", merged_dict=merged_dict)
        except yaml.YAMLError as e:
            raise InvalidConfigurationError(
                f"Error parsing override configuration file {override_config_path}: {e}"
            ) from e

    try:
        final_config = PlanarConfig.model_validate(merged_dict)
        return final_config
    except ValidationError as e:
        raise InvalidConfigurationError(f"Configuration validation error: {e}") from e
