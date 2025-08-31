import io
from abc import ABC, abstractmethod
from typing import AsyncGenerator


class Storage(ABC):
    @abstractmethod
    async def put(
        self, stream: AsyncGenerator[bytes, None], mime_type: str | None = None
    ) -> str:
        """Store a stream and its mime type, returning a storage ref."""
        ...

    @abstractmethod
    async def get(self, ref: str) -> tuple[AsyncGenerator[bytes, None], str | None]:
        """Get a stream and its mime type from a storage ref."""
        ...

    @abstractmethod
    async def delete(self, ref: str) -> None:
        """Delete the object associated with the storage ref."""
        ...

    @abstractmethod
    async def external_url(self, ref: str) -> str | None:
        """If available, return an external URL to read the file."""
        ...

    async def put_bytes(self, data: bytes, mime_type: str | None = None) -> str:
        """Store bytes and optional mime type, returning a storage ref."""

        async def _stream():
            yield data

        return await self.put(_stream(), mime_type=mime_type)

    async def get_bytes(self, ref: str) -> tuple[bytes, str | None]:
        """Get bytes and mime type from a storage ref."""
        buffer = io.BytesIO()
        stream, mime_type = await self.get(ref)
        async for chunk in stream:
            buffer.write(chunk)
        return buffer.getvalue(), mime_type

    async def put_string(
        self, data: str, encoding: str = "utf-8", mime_type: str | None = None
    ) -> str:
        """Store a string and optional mime type, returning a storage ref."""
        # Ensure mime_type includes encoding if not already specified
        final_mime_type = mime_type
        if mime_type and "charset=" not in mime_type and mime_type.startswith("text/"):
            final_mime_type = f"{mime_type}; charset={encoding}"
        return await self.put_bytes(data.encode(encoding), mime_type=final_mime_type)

    async def get_string(
        self, ref: str, encoding: str = "utf-8"
    ) -> tuple[str, str | None]:
        """Get a string and mime type from a storage ref."""
        data_bytes, mime_type = await self.get_bytes(ref)
        # TODO: Potentially use encoding from mime_type if available?
        return data_bytes.decode(encoding), mime_type

    async def close(self) -> None:
        """
        Optional cleanup method for storage implementations.
        Override this if your storage backend needs explicit cleanup.
        """
        pass
