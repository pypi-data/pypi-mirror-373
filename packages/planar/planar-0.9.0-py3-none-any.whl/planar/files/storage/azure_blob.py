import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import AsyncGenerator, override
from urllib.parse import urlparse

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient

from planar.logging import get_logger

from .base import Storage

logger = get_logger(__name__)


class AzureAuthMethod(Enum):
    CONNECTION_STRING = "connection_string"
    ACCOUNT_KEY = "account_key"
    AZURE_AD = "azure_ad"


class AzureBlobStorage(Storage):
    """Stores files and mime types in Azure Blob Storage using the async SDK."""

    def __init__(
        self,
        container_name: str,
        connection_string: str | None = None,
        account_url: str | None = None,
        use_azure_ad: bool = False,
        account_key: str | None = None,
        sas_ttl: int = 3600,
    ):
        """
        Initializes AzureBlobStorage.

        Args:
            container_name: The name of the Azure Storage container.
            connection_string: Full connection string (includes all credentials).
            account_url: Storage account URL (e.g., 'https://<account>.blob.core.windows.net').
            use_azure_ad: Whether to use DefaultAzureCredential for Azure AD auth.
            account_key: Storage account key (used with account_url).
            sas_ttl: Time in seconds for which SAS URLs are valid.
        """
        # Import Azure dependencies when the class is instantiated
        try:
            from azure.storage.blob.aio import BlobServiceClient
        except ImportError as e:
            raise ImportError(
                "Azure storage dependencies are not installed. "
                "Install with: pip install planar[azure]"
            ) from e

        self.container_name = container_name
        self.sas_ttl = sas_ttl
        self.client: "BlobServiceClient"

        self.auth_method: AzureAuthMethod
        self._account_name: str | None = None
        self._account_key: str | None = None

        from azure.storage.blob._shared.policies_async import ExponentialRetry

        client_kwargs = {
            "connection_timeout": 10,
            "read_timeout": 40,
            "retry_policy": ExponentialRetry(
                retry_total=2,
            ),
        }

        # Initialize BlobServiceClient based on auth method
        if connection_string:
            self.client = BlobServiceClient.from_connection_string(
                connection_string,
                **client_kwargs,
            )
            self.auth_method = AzureAuthMethod.CONNECTION_STRING
            # Extract account name and key from the connection string for SAS signing
            self._account_name = self._extract_account_name_from_connection_string(
                connection_string
            )
            self._account_key = self._extract_account_key_from_connection_string(
                connection_string
            )

        elif use_azure_ad:
            if not account_url:
                raise ValueError(
                    "account_url is required when using Azure AD authentication"
                )
            from azure.identity.aio import DefaultAzureCredential

            credential = DefaultAzureCredential()
            self.client = BlobServiceClient(
                account_url=account_url, credential=credential, **client_kwargs
            )
            self.auth_method = AzureAuthMethod.AZURE_AD
            self._account_key = None
            self._account_name = self._extract_account_name_from_account_url(
                account_url
            )

        elif account_key:
            if not account_url:
                raise ValueError(
                    "account_url is required when using account key authentication"
                )
            self.client = BlobServiceClient(
                account_url=account_url, credential=account_key, **client_kwargs
            )
            self.auth_method = AzureAuthMethod.ACCOUNT_KEY
            self._account_key = account_key
            # Extract account name from URL for SAS generation
            self._account_name = self._extract_account_name_from_account_url(
                account_url
            )

        else:
            raise ValueError(
                "Must provide either connection_string, use_azure_ad=True, or account_key"
            )

    async def __aenter__(self):
        """Enter async context manager for proper cleanup in tests."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager and cleanup resources."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    @override
    async def close(self):
        """Explicitly close the client. Only needed if not using as context manager."""
        await self.client.close()

    async def put(
        self, stream: AsyncGenerator[bytes, None], mime_type: str | None = None
    ) -> str:
        """
        Stores a stream and optional mime type to Azure Blob Storage.

        The storage reference returned is a unique UUID.
        The mime_type is stored as the blob's ContentType.
        """
        ref = str(uuid.uuid4())

        content_settings = None
        if mime_type:
            from azure.storage.blob import ContentSettings

            content_settings = ContentSettings(content_type=mime_type)

        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(ref)

            await blob_client.upload_blob(
                stream,
                content_settings=content_settings,
                overwrite=True,
            )
            return ref

        except Exception as e:
            logger.exception(
                "failed azure blob upload",
                ref=ref,
                container_name=self.container_name,
            )
            raise IOError(f"Failed to upload to Azure blob {ref}. Error: {e}") from e

    async def get(self, ref: str) -> tuple[AsyncGenerator[bytes, None], str | None]:
        """
        Retrieves a stream and its mime type from Azure Blob Storage.
        """
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(ref)

            # Get blob properties for content type
            properties = await blob_client.get_blob_properties()
            mime_type = (
                properties.content_settings.content_type
                if properties.content_settings
                else None
            )

            async def _stream_wrapper():
                download_stream = await blob_client.download_blob()
                async for chunk in download_stream.chunks():
                    yield chunk

            return _stream_wrapper(), mime_type
        except ResourceNotFoundError as e:
            logger.warning(
                "azure blob not found",
                ref=ref,
                container_name=self.container_name,
                error=e,
            )
            raise FileNotFoundError(f"Azure blob not found: {ref}") from e
        except Exception as e:
            logger.exception(
                "failed azure blob download",
                ref=ref,
                container_name=self.container_name,
            )
            raise IOError(
                f"Failed to download from Azure blob {ref}. Error: {e}"
            ) from e

    async def delete(self, ref: str) -> None:
        """
        Deletes a blob from Azure Storage.
        Does not raise an error if the blob does not exist.
        """
        try:
            container_client = self.client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(ref)

            await blob_client.delete_blob(delete_snapshots="include")

        except ResourceNotFoundError:
            logger.debug(
                "azure blob not found, not raising error",
                ref=ref,
                container_name=self.container_name,
            )
        except Exception as e:
            logger.exception(
                "failed azure blob delete",
                ref=ref,
                container_name=self.container_name,
            )
            raise IOError(f"Failed to delete Azure blob {ref}. Error: {e}") from e

    async def external_url(self, ref: str) -> str | None:
        """
        Returns a SAS URL to access the Azure blob if we have the capability.

        Supports SAS generation for:
        - Account Key (Account SAS signed with account key)
        - Connection String (Account SAS signed with extracted account key)
        - Azure AD (User Delegation SAS signed with a User Delegation Key)
        """

        if not self._account_name:
            logger.debug(
                "cannot generate sas url without account name",
                ref=ref,
                has_account_name=bool(self._account_name),
            )
            return None

        expiry_time = datetime.now(UTC) + timedelta(seconds=self.sas_ttl)

        if self.auth_method.name in ("ACCOUNT_KEY", "CONNECTION_STRING"):
            if not self._account_key:
                logger.debug(
                    "cannot generate account-key SAS without account key",
                    ref=ref,
                    has_account_key=bool(self._account_key),
                )
                return None

            sas_token = generate_blob_sas(
                account_name=self._account_name,
                container_name=self.container_name,
                blob_name=ref,
                account_key=self._account_key,
                permission=BlobSasPermissions(read=True),
                expiry=expiry_time,
            )

        elif self.auth_method.name == "AZURE_AD":
            # Generate a User Delegation SAS signed with a user delegation key
            start_time = datetime.utcnow()
            user_delegation_key = await self.client.get_user_delegation_key(
                key_start_time=start_time, key_expiry_time=expiry_time
            )
            sas_token = generate_blob_sas(
                account_name=self._account_name,
                container_name=self.container_name,
                blob_name=ref,
                user_delegation_key=user_delegation_key,
                permission=BlobSasPermissions(read=True),
                expiry=expiry_time,
            )
        else:
            return None

        blob_url = f"{self.client.url}{self.container_name}/{ref}"
        return f"{blob_url}?{sas_token}"

    @staticmethod
    def _extract_account_name_from_connection_string(
        connection_string: str,
    ) -> str | None:
        try:
            # Split on ';' and build a dict of key/value pairs
            parts = dict(
                part.split("=", 1)
                for part in connection_string.split(";")
                if "=" in part
            )
            account_name = parts.get("AccountName")
            return account_name
        except Exception:
            return None

    @staticmethod
    def _extract_account_key_from_connection_string(
        connection_string: str,
    ) -> str | None:
        try:
            parts = dict(
                part.split("=", 1)
                for part in connection_string.split(";")
                if "=" in part
            )
            return parts.get("AccountKey")
        except Exception:
            return None

    @staticmethod
    def _extract_account_name_from_account_url(account_url: str) -> str | None:
        try:
            parsed = urlparse(account_url)
            host = parsed.hostname or ""
            # Standard Azure: https://{account}.blob.core.windows.net
            if "." in host and not host.startswith("127.") and host != "localhost":
                return host.split(".")[0]
            # Azurite style: http://127.0.0.1:10000/{account}
            path = parsed.path.strip("/")
            if path:
                return path.split("/")[0]
            return None
        except Exception:
            return None
