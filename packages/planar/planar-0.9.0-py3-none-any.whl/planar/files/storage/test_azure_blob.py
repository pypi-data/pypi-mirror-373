from __future__ import annotations

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import pytest

try:
    from azure.core.exceptions import ResourceExistsError
    from azure.storage.blob._shared.policies_async import ExponentialRetry
    from azure.storage.blob.aio import BlobServiceClient

    from planar.files.storage.azure_blob import AzureBlobStorage

    azure_available = True
    import_error = None
except ImportError as e:
    import_error = e
    azure_available = False

# Avoid evaluating runtime annotations when Azure SDK isn't installed
if TYPE_CHECKING or azure_available:
    # Only imported for type checking; not at runtime
    from azure.core.exceptions import ResourceExistsError
    from azure.storage.blob._shared.policies_async import ExponentialRetry
    from azure.storage.blob.aio import BlobServiceClient

    from planar.files.storage.azure_blob import AzureBlobStorage  # pragma: no cover
else:
    AzureBlobStorage = Any  # type: ignore

from planar.logging import get_logger

pytestmark = [
    pytest.mark.skipif(
        not azure_available,
        reason=f"Azure blob not available: {import_error or 'unknown error'}",
    ),
    pytest.mark.azure_blob,
]


logger = get_logger(__name__)

# --- Configuration for Azurite (Azure Storage Emulator) ---

AZURITE_ACCOUNT_NAME = "devstoreaccount1"
AZURITE_ACCOUNT_KEY = "Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=="
AZURITE_ENDPOINT = "http://127.0.0.1:10000"
AZURITE_CONNECTION_STRING = (
    f"DefaultEndpointsProtocol=http;AccountName={AZURITE_ACCOUNT_NAME};"
    f"AccountKey={AZURITE_ACCOUNT_KEY};BlobEndpoint={AZURITE_ENDPOINT}/{AZURITE_ACCOUNT_NAME};"
)

# Generate a unique container name for each test run session
SESSION_CONTAINER_NAME = f"planar-test-{uuid.uuid4()}"


@pytest.fixture()
def azure_client():
    """Provides an Azure BlobServiceClient for direct interaction (e.g., container creation)."""
    client = BlobServiceClient.from_connection_string(
        AZURITE_CONNECTION_STRING,
        connection_timeout=5,
        read_timeout=5,
        retry_policy=ExponentialRetry(
            retry_total=1,
        ),
    )
    return client


@pytest.fixture(autouse=True)
async def ensure_azure_container(azure_client):
    """
    Ensures the Azure container exists before tests run.
    This runs automatically due to autouse=True.
    """
    logger.warning(
        "attempting to create container",
        container_name=SESSION_CONTAINER_NAME,
        storage_type="azurite",
    )

    try:
        # Add timeout to container creation to fail fast if Azurite isn't running
        async with azure_client:
            container_client = azure_client.get_container_client(SESSION_CONTAINER_NAME)
            await container_client.create_container(timeout=1)
        logger.info("container created", container_name=SESSION_CONTAINER_NAME)
    except ResourceExistsError:
        logger.info("container already exists", container_name=SESSION_CONTAINER_NAME)
    except asyncio.TimeoutError:
        pytest.fail(
            f"Timeout creating Azure container {SESSION_CONTAINER_NAME}. "
            "Is Azurite running? Start with: docker run -p 127.0.0.1:10000:10000 -d mcr.microsoft.com/azure-storage/azurite azurite-blob"
        )
    except Exception as e:
        pytest.fail(
            f"Failed to create Azure container {SESSION_CONTAINER_NAME}: {e}. "
            "Is Azurite running? Start with: docker run -p 127.0.0.1:10000:10000 -d mcr.microsoft.com/azure-storage/azurite azurite-blob"
        )

    yield  # Tests run here


@pytest.fixture
async def azure_storage_connection_string():
    """Provides an AzureBlobStorage instance using connection string auth."""
    storage_instance = AzureBlobStorage(
        container_name=SESSION_CONTAINER_NAME,
        connection_string=AZURITE_CONNECTION_STRING,
    )
    async with storage_instance as storage:
        yield storage


@pytest.fixture
async def azure_storage_account_key():
    """Provides an AzureBlobStorage instance using account key auth."""
    account_url = f"{AZURITE_ENDPOINT}/{AZURITE_ACCOUNT_NAME}"
    storage_instance = AzureBlobStorage(
        container_name=SESSION_CONTAINER_NAME,
        account_url=account_url,
        account_key=AZURITE_ACCOUNT_KEY,
    )
    async with storage_instance as storage:
        yield storage


@asynccontextmanager
async def cleanup_azure_blob(storage: AzureBlobStorage, ref: str):
    """Context manager to ensure an Azure blob is deleted after use."""
    try:
        yield
    finally:
        try:
            logger.debug("cleaning up blob", blob_ref=ref)
            await storage.delete(ref)
        except FileNotFoundError:
            logger.debug("blob already deleted", blob_ref=ref)
        except Exception as e:
            logger.warning("blob cleanup failed", blob_ref=ref, error=str(e))


# --- Test Cases ---
async def test_put_get_bytes_connection_string(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test storing and retrieving raw bytes using connection string auth."""
    storage = azure_storage_connection_string
    test_data = b"some binary data \x00\xff for azure blob"
    mime_type = "application/octet-stream"
    ref = None

    try:
        ref = await storage.put_bytes(test_data, mime_type=mime_type)
        assert isinstance(ref, str)

        # Validate ref is a UUID
        try:
            uuid.UUID(ref)
        except ValueError:
            pytest.fail(f"Returned ref '{ref}' is not a valid UUID string")

        async with cleanup_azure_blob(storage, ref):
            retrieved_data, retrieved_mime = await storage.get_bytes(ref)

            assert retrieved_data == test_data
            assert retrieved_mime == mime_type

            # Check external URL (should be a SAS URL)
            url = await storage.external_url(ref)
            assert url is not None
            assert SESSION_CONTAINER_NAME in url
            assert ref in url
            assert "sig=" in url  # SAS signature

    except Exception as e:
        if ref:
            await cleanup_azure_blob(storage, ref).__aexit__(None, None, None)
        raise e


async def test_put_get_bytes_account_key(
    azure_storage_account_key: AzureBlobStorage,
):
    """Test storing and retrieving raw bytes using account key auth."""
    storage = azure_storage_account_key
    test_data = b"azure blob test data with account key"
    mime_type = "text/plain"
    ref = None

    try:
        ref = await storage.put_bytes(test_data, mime_type=mime_type)

        async with cleanup_azure_blob(storage, ref):
            retrieved_data, retrieved_mime = await storage.get_bytes(ref)

            assert retrieved_data == test_data
            assert retrieved_mime == mime_type

            # Check external URL
            url = await storage.external_url(ref)
            assert url is not None
            assert ref in url

    except Exception as e:
        if ref:
            await cleanup_azure_blob(storage, ref).__aexit__(None, None, None)
        raise e


async def test_put_get_string(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test storing and retrieving a string."""
    storage = azure_storage_connection_string
    test_string = "Hello, Azure Blob Storage! This is a test string with Unicode: éàçü."
    mime_type = "text/plain"
    encoding = "utf-8"
    ref = None

    try:
        ref = await storage.put_string(
            test_string, encoding=encoding, mime_type=mime_type
        )
        expected_mime_type = f"{mime_type}; charset={encoding}"

        async with cleanup_azure_blob(storage, ref):
            retrieved_string, retrieved_mime = await storage.get_string(
                ref, encoding=encoding
            )

            assert retrieved_string == test_string
            assert retrieved_mime == expected_mime_type

    except Exception as e:
        if ref:
            await cleanup_azure_blob(storage, ref).__aexit__(None, None, None)
        raise e


async def test_put_get_stream(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test storing data from an async generator stream."""
    storage = azure_storage_connection_string
    test_chunks = [b"azure_chunk1 ", b"azure_chunk2 ", b"azure_chunk3"]
    full_data = b"".join(test_chunks)
    mime_type = "application/json"
    ref = None

    async def _test_stream():
        for chunk in test_chunks:
            yield chunk
            await asyncio.sleep(0.01)  # Simulate async work

    try:
        ref = await storage.put(_test_stream(), mime_type=mime_type)

        async with cleanup_azure_blob(storage, ref):
            stream, retrieved_mime = await storage.get(ref)
            retrieved_data = b""
            async for chunk in stream:
                retrieved_data += chunk

            assert retrieved_data == full_data
            assert retrieved_mime == mime_type

    except Exception as e:
        if ref:
            await cleanup_azure_blob(storage, ref).__aexit__(None, None, None)
        raise e


async def test_put_no_mime_type(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test storing data without providing a mime type."""
    storage = azure_storage_connection_string
    test_data = b"azure data without mime"
    ref = None

    try:
        ref = await storage.put_bytes(test_data)

        async with cleanup_azure_blob(storage, ref):
            retrieved_data, retrieved_mime = await storage.get_bytes(ref)

            assert retrieved_data == test_data
            # Azure might not set a mime type if none provided
            logger.debug(
                "retrieved mime type", mime_type=retrieved_mime, provided=False
            )

    except Exception as e:
        if ref:
            await cleanup_azure_blob(storage, ref).__aexit__(None, None, None)
        raise e


async def test_delete(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test deleting stored data."""
    storage = azure_storage_connection_string
    ref = await storage.put_bytes(b"to be deleted from azure", mime_type="text/plain")

    # Verify blob exists before delete
    try:
        _, _ = await storage.get(ref)
    except FileNotFoundError:
        pytest.fail(f"Blob {ref} should exist before deletion but was not found.")

    # Delete the blob
    await storage.delete(ref)

    # Verify blob is gone after delete
    with pytest.raises(FileNotFoundError):
        await storage.get(ref)

    # Deleting again should be idempotent (no error)
    try:
        await storage.delete(ref)
    except Exception as e:
        pytest.fail(f"Deleting already deleted ref raised an exception: {e}")


async def test_get_non_existent(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test getting a reference that does not exist."""
    storage = azure_storage_connection_string
    non_existent_ref = str(uuid.uuid4())

    with pytest.raises(FileNotFoundError):
        await storage.get(non_existent_ref)


async def test_delete_non_existent(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test deleting a reference that does not exist (should not raise error)."""
    storage = azure_storage_connection_string
    non_existent_ref = str(uuid.uuid4())

    try:
        await storage.delete(non_existent_ref)
    except Exception as e:
        pytest.fail(f"Deleting non-existent ref raised an exception: {e}")


async def test_external_url_connection_string(
    azure_storage_connection_string: AzureBlobStorage,
):
    """Test that external_url returns a valid-looking SAS URL with connection string auth."""
    storage = azure_storage_connection_string
    ref = None

    try:
        ref = await storage.put_bytes(b"some data for url test")

        async with cleanup_azure_blob(storage, ref):
            url = await storage.external_url(ref)
            assert url is not None
            assert ref in url
            assert SESSION_CONTAINER_NAME in url
            # SAS URLs should have these query parameters
            assert "sig=" in url  # Signature
            assert "se=" in url  # Expiry time

    except Exception as e:
        if ref:
            await cleanup_azure_blob(storage, ref).__aexit__(None, None, None)
        raise e


def test_config_validation():
    """Test that the configuration validation works properly."""
    from planar.files.storage.config import AzureBlobConfig

    # These should all validate successfully
    # Test connection string only (valid)
    AzureBlobConfig(
        backend="azure_blob",
        container_name="test",
        connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key;",
    )

    # Test account_url + account_key (valid)
    AzureBlobConfig(
        backend="azure_blob",
        container_name="test",
        account_url="https://test.blob.core.windows.net",
        account_key="test-key",
    )

    # Test account_url + use_azure_ad (valid)
    AzureBlobConfig(
        backend="azure_blob",
        container_name="test",
        account_url="https://test.blob.core.windows.net",
        use_azure_ad=True,
    )

    # Test invalid configs
    with pytest.raises(ValueError, match="connection_string"):
        # Connection string + other options
        AzureBlobConfig(
            backend="azure_blob",
            container_name="test",
            connection_string="test",
            account_url="https://test.blob.core.windows.net",
        )

    with pytest.raises(ValueError, match="account_url must be provided"):
        # No connection string and no account_url
        AzureBlobConfig(
            backend="azure_blob",
            container_name="test",
            use_azure_ad=True,
        )

    with pytest.raises(ValueError, match="exactly one credential method"):
        # Both account_key and use_azure_ad
        AzureBlobConfig(
            backend="azure_blob",
            container_name="test",
            account_url="https://test.blob.core.windows.net",
            account_key="key",
            use_azure_ad=True,
        )
