import mimetypes
import os
from pathlib import Path
from typing import AsyncGenerator, Union
from uuid import UUID, uuid4

import aiofiles
from pydantic import BaseModel
from sqlmodel import Field

from planar.db import PlanarInternalBase
from planar.files.storage.context import get_storage
from planar.logging import get_logger
from planar.modeling.mixins import TimestampMixin
from planar.session import get_session

logger = get_logger(__name__)


class PlanarFile(BaseModel):
    id: UUID
    filename: str
    content_type: str
    size: int

    async def get_metadata(self) -> "PlanarFileMetadata":
        """
        Retrieves the metadata for this file from the database.
        """
        logger.debug("getting metadata for file", file_id=self.id)
        session = get_session()
        async with session.begin_read():
            result = await session.get(PlanarFileMetadata, self.id)
        if result is None:
            logger.warning("file metadata not found in database", file_id=self.id)
            raise ValueError(f"File with ID {self.id} not found in the database.")
        return result

    async def get_content(self) -> bytes:
        """
        Retrieves the content of this file from the storage backend.
        """
        logger.debug("getting content for file", file_id=self.id)
        storage = get_storage()
        metadata = await self.get_metadata()
        data, _ = await storage.get_bytes(metadata.storage_ref)
        return data

    @staticmethod
    async def upload(
        content: Union[bytes, AsyncGenerator[bytes, None], Path, str],
        filename: str,
        content_type: str | None = None,
        size: int | None = None,
    ) -> "PlanarFile":
        """
        Uploads file content to storage and creates its metadata record.

        Args:
            content: File content as bytes, an async iterator, or a file path (str or Path).
            filename: The desired filename for storage and metadata.
            content_type: The MIME type of the file. If None, it's inferred from the filename
                          for paths or defaults to 'application/octet-stream'.
            size: The size of the file in bytes. If None, it's calculated for bytes/paths
                  or defaults to -1 for streams.

        Returns:
            The created PlanarFile object with metadata.

        Raises:
            FileNotFoundError: If content is a path and the file doesn't exist.
            TypeError: If the content type is not supported.
        """
        logger.debug(
            "uploading file",
            filename=filename,
            content_type=content_type,
            size=size,
        )
        storage = get_storage()
        session = get_session()

        storage_ref: str
        actual_size: int = -1
        final_content_type: str = content_type or "application/octet-stream"

        if isinstance(content, (str, Path)):
            file_path = Path(content)
            logger.debug("uploading from path", path=file_path)
            if not file_path.is_file():
                logger.warning("file not found at path for upload", path=file_path)
                raise FileNotFoundError(f"File not found at path: {file_path}")

            actual_size = size if size is not None else os.path.getsize(file_path)

            if content_type is None:
                guessed_type, _ = mimetypes.guess_type(filename)
                final_content_type = guessed_type or "application/octet-stream"

            async def file_stream():
                async with aiofiles.open(file_path, "rb") as afp:
                    chunk_size = 65536  # 64KB chunk size
                    while chunk := await afp.read(chunk_size):
                        yield chunk

            storage_ref = await storage.put(
                stream=file_stream(), mime_type=final_content_type
            )

        elif isinstance(content, bytes):
            logger.debug("uploading from bytes")
            actual_size = size if size is not None else len(content)
            # Keep provided content_type or default
            final_content_type = content_type or "application/octet-stream"
            storage_ref = await storage.put_bytes(content, mime_type=final_content_type)

        elif isinstance(content, AsyncGenerator):  # Check for async iterator
            logger.debug("uploading from async generator stream")
            actual_size = size if size is not None else -1  # Size required or unknown
            # Keep provided content_type or default
            final_content_type = content_type or "application/octet-stream"
            storage_ref = await storage.put(
                stream=content, mime_type=final_content_type
            )
        else:
            logger.warning(
                "unsupported content type for upload", content_type=type(content)
            )
            raise TypeError(
                "Unsupported content type. Must be bytes, AsyncGenerator, str path, or Path object."
            )

        # Create the metadata record
        planar_file_metadata = PlanarFileMetadata(
            filename=filename,
            content_type=final_content_type,
            size=actual_size,
            storage_ref=storage_ref,
        )
        session.add(planar_file_metadata)
        await session.commit()
        await session.refresh(planar_file_metadata)
        logger.info(
            "file uploaded and metadata created",
            id=planar_file_metadata.id,
            filename=filename,
            storage_ref=storage_ref,
        )

        # We return the metadata instance which also satisfies the PlanarFile structure
        return planar_file_metadata


class PlanarFileMetadata(PlanarFile, TimestampMixin, PlanarInternalBase, table=True):
    """
    Database model storing the authoritative mapping between a PlanarFile.file_id
    and its storage details. Acts as the single, central file manifest.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # storage_ref is a storage backend specifid identifier for the file
    storage_ref: str = Field(index=True)
