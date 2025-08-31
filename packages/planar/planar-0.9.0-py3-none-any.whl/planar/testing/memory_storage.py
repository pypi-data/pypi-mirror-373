import io
import uuid
from typing import AsyncGenerator, Dict, Tuple

from planar.files.storage.base import Storage
from planar.logging import get_logger

logger = get_logger(__name__)


class MemoryStorage(Storage):
    """Stores files and mime types entirely in memory."""

    def __init__(self):
        """Initializes MemoryStorage."""
        self._blobs: Dict[str, bytes] = {}
        self._mime_types: Dict[str, str] = {}

    async def put(
        self, stream: AsyncGenerator[bytes, None], mime_type: str | None = None
    ) -> str:
        """
        Stores a stream and its mime type in memory dictionaries.

        The storage reference returned is a unique UUID string.
        """
        ref = str(uuid.uuid4())
        buffer = io.BytesIO()
        try:
            async for chunk in stream:
                buffer.write(chunk)
            self._blobs[ref] = buffer.getvalue()
            if mime_type:
                self._mime_types[ref] = mime_type
            logger.debug("stored ref in memory", ref=ref)
            return ref
        except Exception as e:
            logger.exception("error during memory put operation", ref=ref)
            # Clean up if storage failed mid-way (though less likely in memory)
            self._blobs.pop(ref, None)
            self._mime_types.pop(ref, None)
            raise IOError(
                f"Failed to store file or mime type in memory for ref {ref}"
            ) from e

    async def get(self, ref: str) -> Tuple[AsyncGenerator[bytes, None], str | None]:
        """
        Retrieves a stream and its mime type from memory.
        """
        if ref not in self._blobs:
            raise FileNotFoundError(f"Storage reference not found in memory: {ref}")

        blob_data = self._blobs[ref]
        mime_type = self._mime_types.get(ref)

        async def _stream():
            # Yield the entire blob data as a single chunk for simplicity
            # Could be chunked if needed, but for memory storage, this is fine.
            yield blob_data

        logger.debug("retrieved ref from memory", ref=ref)
        return _stream(), mime_type

    async def delete(self, ref: str) -> None:
        """
        Deletes the blob data and mime type from memory. Idempotent.
        """
        blob_deleted = self._blobs.pop(ref, None) is not None
        mime_deleted = self._mime_types.pop(ref, None) is not None
        if blob_deleted or mime_deleted:
            logger.debug("deleted ref from memory", ref=ref)
        else:
            logger.debug("attempted to delete non-existent ref from memory", ref=ref)
        # No FileNotFoundError raised if ref doesn't exist, deletion is idempotent.

    async def external_url(self, ref: str) -> str | None:
        """Memory storage does not provide external URLs."""
        return None
