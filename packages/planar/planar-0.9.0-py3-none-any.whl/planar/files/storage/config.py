from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from .local_directory import LocalDirectoryStorage
from .s3 import S3Storage

if TYPE_CHECKING:
    from .azure_blob import AzureBlobStorage


class LocalDirectoryConfig(BaseModel):
    backend: Literal["localdir"]
    directory: str


class S3Config(BaseModel):
    backend: Literal["s3"]
    bucket_name: str
    region: str
    access_key: str | None = None
    secret_key: str | None = None
    endpoint_url: str | None = None
    presigned_url_ttl: int = 3600


class AzureBlobConfig(BaseModel):
    backend: Literal["azure_blob"]
    container_name: str

    # Authentication options (mutually exclusive)
    connection_string: str | None = None  # Full connection string
    account_url: str | None = None  # Storage account URL
    use_azure_ad: bool | None = None  # Use DefaultAzureCredential
    account_key: str | None = None  # Storage account key

    # Common settings
    sas_ttl: int = 3600  # SAS URL expiry time in seconds

    @model_validator(mode="after")
    def validate_auth_config(self):
        """Ensure exactly one valid authentication configuration."""

        # Check if connection_string is provided
        if self.connection_string:
            # Connection string is self-contained
            if self.account_url or self.use_azure_ad or self.account_key:
                raise ValueError(
                    "When using connection_string, don't provide account_url, use_azure_ad, or account_key"
                )
            return self

        # If no connection string, must have account_url
        if not self.account_url:
            raise ValueError("Either connection_string or account_url must be provided")

        # With account_url, must have exactly one credential type
        credential_methods = [
            self.use_azure_ad is True,
            self.account_key is not None,
        ]

        if sum(credential_methods) != 1:
            raise ValueError(
                "When using account_url, exactly one credential method must be specified: "
                "use_azure_ad=true or account_key"
            )

        return self


StorageConfig = Annotated[
    LocalDirectoryConfig | S3Config | AzureBlobConfig,
    Field(discriminator="backend"),
]


def create_from_config(
    config: StorageConfig,
) -> LocalDirectoryStorage | S3Storage | AzureBlobStorage:
    """Creates a storage instance from the given configuration."""
    if config.backend == "localdir":
        return LocalDirectoryStorage(config.directory)
    elif config.backend == "s3":
        return S3Storage(
            bucket_name=config.bucket_name,
            region=config.region,
            access_key_id=config.access_key,
            secret_access_key=config.secret_key,
            endpoint_url=config.endpoint_url,
            presigned_url_ttl=config.presigned_url_ttl,
        )
    elif config.backend == "azure_blob":
        from .azure_blob import AzureBlobStorage

        return AzureBlobStorage(
            container_name=config.container_name,
            connection_string=config.connection_string,
            account_url=config.account_url,
            use_azure_ad=config.use_azure_ad or False,
            account_key=config.account_key,
            sas_ttl=config.sas_ttl,
        )
    else:
        raise ValueError(f"Unsupported backend: {config.backend}")
