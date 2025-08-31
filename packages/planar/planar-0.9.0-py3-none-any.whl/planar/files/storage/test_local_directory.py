import asyncio
import uuid
from pathlib import Path

import aiofiles.os
import pytest

from planar.files.storage.local_directory import LocalDirectoryStorage


@pytest.fixture
async def storage(tmp_path: Path) -> LocalDirectoryStorage:
    """Provides an instance of LocalDirectoryStorage using a temporary directory."""
    storage_instance = LocalDirectoryStorage(tmp_path)
    # Ensure subdirectories exist (though constructor should handle this)
    await aiofiles.os.makedirs(storage_instance.blob_dir, exist_ok=True)
    await aiofiles.os.makedirs(storage_instance.mime_dir, exist_ok=True)
    return storage_instance


async def test_put_get_bytes(storage: LocalDirectoryStorage):
    """Test storing and retrieving raw bytes."""
    test_data = b"some binary data \x00\xff"
    mime_type = "application/octet-stream"

    ref = await storage.put_bytes(test_data, mime_type=mime_type)
    assert isinstance(ref, str)
    try:
        uuid.UUID(ref)  # Check if ref is a valid UUID string
    except ValueError:
        pytest.fail(f"Returned ref '{ref}' is not a valid UUID string")

    retrieved_data, retrieved_mime = await storage.get_bytes(ref)

    assert retrieved_data == test_data
    assert retrieved_mime == mime_type

    # Check underlying files exist
    blob_path = storage._get_path(ref, storage.BLOB_SUBDIR)
    mime_path = storage._get_path(ref, storage.MIME_SUBDIR)
    assert await aiofiles.os.path.exists(blob_path)
    assert await aiofiles.os.path.exists(mime_path)


async def test_put_get_string(storage: LocalDirectoryStorage):
    """Test storing and retrieving a string."""
    test_string = "Hello, world! This is a test string with Unicode: éàçü."
    mime_type = "text/plain"
    encoding = "utf-16"

    # Store with explicit encoding and mime type
    ref = await storage.put_string(test_string, encoding=encoding, mime_type=mime_type)
    expected_mime_type = f"{mime_type}; charset={encoding}"

    retrieved_string, retrieved_mime = await storage.get_string(ref, encoding=encoding)

    assert retrieved_string == test_string
    assert retrieved_mime == expected_mime_type

    # Test default encoding (utf-8)
    ref_utf8 = await storage.put_string(test_string, mime_type="text/html")
    expected_mime_utf8 = "text/html; charset=utf-8"
    retrieved_string_utf8, retrieved_mime_utf8 = await storage.get_string(ref_utf8)
    assert retrieved_string_utf8 == test_string
    assert retrieved_mime_utf8 == expected_mime_utf8


async def test_put_get_stream(storage: LocalDirectoryStorage):
    """Test storing data from an async generator stream."""
    test_chunks = [b"chunk1 ", b"chunk2 ", b"chunk3"]
    full_data = b"".join(test_chunks)
    mime_type = "image/png"

    async def _test_stream():
        for chunk in test_chunks:
            yield chunk
            await asyncio.sleep(0.01)  # Simulate async work

    ref = await storage.put(_test_stream(), mime_type=mime_type)

    stream, retrieved_mime = await storage.get(ref)
    retrieved_data = b""
    async for chunk in stream:
        retrieved_data += chunk

    assert retrieved_data == full_data
    assert retrieved_mime == mime_type


async def test_put_no_mime_type(storage: LocalDirectoryStorage):
    """Test storing data without providing a mime type."""
    test_data = b"data without mime"

    ref = await storage.put_bytes(test_data)
    retrieved_data, retrieved_mime = await storage.get_bytes(ref)

    assert retrieved_data == test_data
    assert retrieved_mime is None

    # Check only blob file exists
    blob_path = storage._get_path(ref, storage.BLOB_SUBDIR)
    mime_path = storage._get_path(ref, storage.MIME_SUBDIR)
    assert await aiofiles.os.path.exists(blob_path)
    assert not await aiofiles.os.path.exists(mime_path)


async def test_delete(storage: LocalDirectoryStorage):
    """Test deleting stored data."""
    ref = await storage.put_bytes(b"to be deleted", mime_type="text/plain")

    blob_path = storage._get_path(ref, storage.BLOB_SUBDIR)
    mime_path = storage._get_path(ref, storage.MIME_SUBDIR)

    # Verify files exist before delete
    assert await aiofiles.os.path.exists(blob_path)
    assert await aiofiles.os.path.exists(mime_path)

    await storage.delete(ref)

    # Verify files are gone after delete
    assert not await aiofiles.os.path.exists(blob_path)
    assert not await aiofiles.os.path.exists(mime_path)

    # Try getting deleted ref
    with pytest.raises(FileNotFoundError):
        await storage.get(ref)


async def test_get_non_existent(storage: LocalDirectoryStorage):
    """Test getting a reference that does not exist."""
    non_existent_ref = str(uuid.uuid4())
    with pytest.raises(FileNotFoundError):
        await storage.get(non_existent_ref)


async def test_delete_non_existent(storage: LocalDirectoryStorage):
    """Test deleting a reference that does not exist (should not raise error)."""
    non_existent_ref = str(uuid.uuid4())
    try:
        await storage.delete(non_existent_ref)
    except Exception as e:
        pytest.fail(f"Deleting non-existent ref raised an exception: {e}")


async def test_invalid_ref_format(storage: LocalDirectoryStorage):
    """Test operations with an invalid storage reference format."""
    invalid_ref = "not-a-uuid"
    with pytest.raises(ValueError):
        await storage.get(invalid_ref)

    with pytest.raises(ValueError):
        await storage.delete(invalid_ref)

    with pytest.raises(ValueError):
        storage._get_path(invalid_ref, storage.BLOB_SUBDIR)


async def test_external_url(storage: LocalDirectoryStorage):
    """Test that external_url returns None for local storage."""
    ref = await storage.put_bytes(b"some data")
    url = await storage.external_url(ref)
    assert url is None
