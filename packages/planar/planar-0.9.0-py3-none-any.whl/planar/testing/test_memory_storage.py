import asyncio
import uuid

import pytest

from planar.testing.memory_storage import MemoryStorage


@pytest.fixture
async def storage() -> MemoryStorage:
    """Provides an instance of MemoryStorage."""
    return MemoryStorage()


async def test_put_get_bytes(storage: MemoryStorage):
    """Test storing and retrieving raw bytes."""
    test_data = b"some binary data \x00\xff for memory"
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

    # Check internal state (optional)
    assert ref in storage._blobs
    assert ref in storage._mime_types
    assert storage._blobs[ref] == test_data
    assert storage._mime_types[ref] == mime_type


async def test_put_get_string(storage: MemoryStorage):
    """Test storing and retrieving a string."""
    test_string = "Hello, memory! This is a test string with Unicode: éàçü."
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


async def test_put_get_stream(storage: MemoryStorage):
    """Test storing data from an async generator stream."""
    test_chunks = [b"mem_chunk1 ", b"mem_chunk2 ", b"mem_chunk3"]
    full_data = b"".join(test_chunks)
    mime_type = "image/gif"

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


async def test_put_no_mime_type(storage: MemoryStorage):
    """Test storing data without providing a mime type."""
    test_data = b"memory data without mime"

    ref = await storage.put_bytes(test_data)
    retrieved_data, retrieved_mime = await storage.get_bytes(ref)

    assert retrieved_data == test_data
    assert retrieved_mime is None

    # Check internal state
    assert ref in storage._blobs
    assert ref not in storage._mime_types


async def test_delete(storage: MemoryStorage):
    """Test deleting stored data."""
    ref = await storage.put_bytes(b"to be deleted from memory", mime_type="text/plain")

    # Verify data exists before delete (optional)
    assert ref in storage._blobs
    assert ref in storage._mime_types

    await storage.delete(ref)

    # Verify data is gone after delete
    assert ref not in storage._blobs
    assert ref not in storage._mime_types

    # Try getting deleted ref
    with pytest.raises(FileNotFoundError):
        await storage.get(ref)


async def test_get_non_existent(storage: MemoryStorage):
    """Test getting a reference that does not exist."""
    non_existent_ref = str(uuid.uuid4())
    with pytest.raises(FileNotFoundError):
        await storage.get(non_existent_ref)


async def test_delete_non_existent(storage: MemoryStorage):
    """Test deleting a reference that does not exist (should not raise error)."""
    non_existent_ref = str(uuid.uuid4())
    initial_blob_count = len(storage._blobs)
    initial_mime_count = len(storage._mime_types)
    try:
        await storage.delete(non_existent_ref)
        # Ensure no data was actually deleted
        assert len(storage._blobs) == initial_blob_count
        assert len(storage._mime_types) == initial_mime_count
    except Exception as e:
        pytest.fail(f"Deleting non-existent ref raised an exception: {e}")


async def test_external_url(storage: MemoryStorage):
    """Test that external_url returns None for memory storage."""
    ref = await storage.put_bytes(b"some data for url test")
    url = await storage.external_url(ref)
    assert url is None
