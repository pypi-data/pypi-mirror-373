import asyncio
import os
import uuid
from contextlib import asynccontextmanager

import boto3
import botocore
import botocore.client
import botocore.exceptions
import pytest

from planar.files.storage.s3 import S3Storage

pytestmark = pytest.mark.skipif(
    os.getenv("PLANAR_TEST_S3_STORAGE", "0") != "1",
    reason="S3 tests must be enabled via PLANAR_TEST_S3_STORAGE env var",
)

# --- Configuration for LocalStack/S3 Compatible Service ---

S3_PORT = 4566
# LocalStack S3 endpoint
S3_ENDPOINT_URL = f"http://127.0.0.1:{S3_PORT}"
# Dummy credentials for LocalStack (usually not strictly required)
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"
AWS_REGION = "us-east-1"
# Generate a unique bucket name for each test run session
SESSION_BUCKET_NAME = f"planar-test-bucket-{uuid.uuid4()}"


@pytest.fixture()
def s3_boto_client():  # Synchronous client
    """Provides a boto3 S3 client for direct interaction (e.g., bucket creation)."""
    client = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
        config=botocore.client.Config(signature_version="s3v4"),
    )
    return client


@pytest.fixture(autouse=True)
async def ensure_s3_bucket(s3_boto_client):
    """
    Ensures the S3 bucket exists before tests run.
    This runs automatically due to autouse=True.
    """
    print(f"Attempting to create bucket: {SESSION_BUCKET_NAME} at {S3_ENDPOINT_URL}")

    create_kwargs = {
        "Bucket": SESSION_BUCKET_NAME,
    }

    try:
        await asyncio.to_thread(s3_boto_client.create_bucket, **create_kwargs)
        print(f"Bucket {SESSION_BUCKET_NAME} created or confirmed existing.")
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print(f"Bucket {SESSION_BUCKET_NAME} already exists.")
        else:
            pytest.fail(
                f"Failed to create S3 bucket {SESSION_BUCKET_NAME} "
                f"at {S3_ENDPOINT_URL}: {e}. Is LocalStack running?"
            )
    except Exception as e:
        pytest.fail(
            f"An unexpected error occurred during bucket creation for {SESSION_BUCKET_NAME}: {e}"
        )

    yield  # Tests run here


@pytest.fixture
async def s3_storage() -> S3Storage:
    """Provides an instance of S3Storage configured for the test bucket."""
    storage_instance = S3Storage(
        bucket_name=SESSION_BUCKET_NAME,
        endpoint_url=S3_ENDPOINT_URL,
        access_key_id=AWS_ACCESS_KEY_ID,
        secret_access_key=AWS_SECRET_ACCESS_KEY,
        region=AWS_REGION,
        presigned_url_ttl=60,
    )
    return storage_instance


@asynccontextmanager
async def cleanup_s3_object(storage: S3Storage, ref: str):
    """Context manager to ensure an S3 object is deleted after use."""
    try:
        yield
    finally:
        try:
            print(f"Cleaning up S3 object: {ref}")
            await storage.delete(ref)
        except FileNotFoundError:
            print(f"Cleanup: S3 object {ref} already deleted or not found.")
        except Exception as e:
            print(f"Warning: Failed to cleanup S3 object {ref}: {e}")


# --- Test Cases ---


async def test_put_get_bytes(s3_storage: S3Storage):
    """Test storing and retrieving raw bytes."""
    test_data = b"some binary data \x00\xff for s3"
    mime_type = "application/octet-stream"
    ref = None
    try:
        ref = await s3_storage.put_bytes(test_data, mime_type=mime_type)
        assert isinstance(ref, str)
        # S3 keys don't have to be UUIDs, but our implementation generates them
        try:
            uuid.UUID(ref)
        except ValueError:
            pytest.fail(f"Returned ref '{ref}' is not a valid UUID string")

        async with cleanup_s3_object(s3_storage, ref):
            retrieved_data, retrieved_mime = await s3_storage.get_bytes(ref)

            assert retrieved_data == test_data
            # S3 might add charset or other params, check starts with
            assert retrieved_mime is not None
            assert retrieved_mime.startswith(mime_type)

            # Check external URL (should be a presigned URL)
            url = await s3_storage.external_url(ref)
            assert url is not None
            base_expected_url = f"{S3_ENDPOINT_URL}/{SESSION_BUCKET_NAME}/{ref}"
            assert url.startswith(base_expected_url)
            assert "X-Amz-Signature" in url
            assert "X-Amz-Expires" in url

    except Exception as e:
        if ref:
            await cleanup_s3_object(s3_storage, ref).__aexit__(None, None, None)
        raise e


async def test_put_get_string(s3_storage: S3Storage):
    """Test storing and retrieving a string."""
    test_string = "Hello, S3! This is a test string with Unicode: éàçü."
    mime_type = "text/plain"
    encoding = "utf-16"
    ref = None
    try:
        # Store with explicit encoding and mime type
        ref = await s3_storage.put_string(
            test_string, encoding=encoding, mime_type=mime_type
        )
        expected_mime_type = f"{mime_type}; charset={encoding}"

        async with cleanup_s3_object(s3_storage, ref):
            retrieved_string, retrieved_mime = await s3_storage.get_string(
                ref, encoding=encoding
            )

            assert retrieved_string == test_string
            assert retrieved_mime == expected_mime_type

    except Exception as e:
        if ref:
            await cleanup_s3_object(s3_storage, ref).__aexit__(None, None, None)
        raise e

    # Test default encoding (utf-8)
    ref_utf8 = None
    try:
        ref_utf8 = await s3_storage.put_string(test_string, mime_type="text/html")
        expected_mime_utf8 = "text/html; charset=utf-8"

        async with cleanup_s3_object(s3_storage, ref_utf8):
            retrieved_string_utf8, retrieved_mime_utf8 = await s3_storage.get_string(
                ref_utf8
            )
            assert retrieved_string_utf8 == test_string
            assert retrieved_mime_utf8 == expected_mime_utf8
    except Exception as e:
        if ref_utf8:
            await cleanup_s3_object(s3_storage, ref_utf8).__aexit__(None, None, None)
        raise e


async def test_put_get_stream(s3_storage: S3Storage):
    """Test storing data from an async generator stream."""
    test_chunks = [b"s3_chunk1 ", b"s3_chunk2 ", b"s3_chunk3"]
    full_data = b"".join(test_chunks)
    mime_type = "image/jpeg"  # Different mime type for variety
    ref = None

    async def _test_stream():
        for chunk in test_chunks:
            yield chunk
            await asyncio.sleep(0.01)  # Simulate async work

    try:
        ref = await s3_storage.put(_test_stream(), mime_type=mime_type)

        async with cleanup_s3_object(s3_storage, ref):
            stream, retrieved_mime = await s3_storage.get(ref)
            retrieved_data = b""
            async for chunk in stream:
                retrieved_data += chunk

            assert retrieved_data == full_data
            assert retrieved_mime is not None
            assert retrieved_mime.startswith(mime_type)
    except Exception as e:
        if ref:
            await cleanup_s3_object(s3_storage, ref).__aexit__(None, None, None)
        raise e


async def test_put_no_mime_type(s3_storage: S3Storage):
    """Test storing data without providing a mime type."""
    test_data = b"s3 data without mime"
    ref = None
    try:
        ref = await s3_storage.put_bytes(test_data)
        async with cleanup_s3_object(s3_storage, ref):
            retrieved_data, retrieved_mime = await s3_storage.get_bytes(ref)

            assert retrieved_data == test_data
            # S3 might assign a default mime type (like binary/octet-stream) or none
            # Depending on the S3 provider, this might be None or a default
            print(f"Retrieved mime type (no mime put): {retrieved_mime}")
            # assert retrieved_mime is None or retrieved_mime == 'binary/octet-stream'
            # For now, let's just check the data
    except Exception as e:
        if ref:
            await cleanup_s3_object(s3_storage, ref).__aexit__(None, None, None)
        raise e


async def test_delete(s3_storage: S3Storage):
    """Test deleting stored data."""
    ref = await s3_storage.put_bytes(b"to be deleted from s3", mime_type="text/plain")

    # Verify object exists before delete (optional, get raises if not found)
    try:
        _, _ = await s3_storage.get(ref)
    except FileNotFoundError:
        pytest.fail(f"Object {ref} should exist before deletion but was not found.")

    # Delete the object
    await s3_storage.delete(ref)

    # Verify object is gone after delete
    with pytest.raises(FileNotFoundError):
        await s3_storage.get(ref)

    # Deleting again should be idempotent (no error)
    try:
        await s3_storage.delete(ref)
    except Exception as e:
        pytest.fail(f"Deleting already deleted ref raised an exception: {e}")


async def test_get_non_existent(s3_storage: S3Storage):
    """Test getting a reference that does not exist."""
    non_existent_ref = str(uuid.uuid4())
    with pytest.raises(FileNotFoundError):
        await s3_storage.get(non_existent_ref)


async def test_delete_non_existent(s3_storage: S3Storage):
    """Test deleting a reference that does not exist (should not raise error)."""
    non_existent_ref = str(uuid.uuid4())
    try:
        await s3_storage.delete(non_existent_ref)
    except Exception as e:
        pytest.fail(f"Deleting non-existent ref raised an exception: {e}")


async def test_external_url(s3_storage: S3Storage):
    """Test that external_url returns a valid-looking presigned S3 object URL."""
    ref = None
    try:
        ref = await s3_storage.put_bytes(b"some data for url test")
        async with cleanup_s3_object(s3_storage, ref):
            url = await s3_storage.external_url(ref)
            assert url is not None
            base_expected_url = f"{S3_ENDPOINT_URL}/{SESSION_BUCKET_NAME}/{ref}"
            assert url.startswith(base_expected_url)
            assert "X-Amz-Algorithm" in url
            assert "X-Amz-Credential" in url
            assert "X-Amz-Date" in url
            assert "X-Amz-Expires" in url
            assert "X-Amz-Signature" in url
    except Exception as e:
        if ref:
            await cleanup_s3_object(s3_storage, ref).__aexit__(None, None, None)
        raise e
