import uuid
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
import aiofiles.os

from planar.logging import get_logger

from .base import Storage

logger = get_logger(__name__)


class LocalDirectoryStorage(Storage):
    """Stores files and mime types in separate subdirectories on local disk."""

    BLOB_SUBDIR = "blob"
    MIME_SUBDIR = "mime"

    def __init__(self, storage_dir: str | Path):
        """
        Initializes LocalDirectoryStorage.

        Args:
            storage_dir: The root directory where 'blob' and 'mime' subdirs will reside.
                         It will be created if it doesn't exist.
        """
        self.base_dir = Path(storage_dir).resolve()
        self.blob_dir = self.base_dir / self.BLOB_SUBDIR
        self.mime_dir = self.base_dir / self.MIME_SUBDIR
        self.blob_dir.mkdir(parents=True, exist_ok=True)
        self.mime_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, ref: str, subdir: str) -> Path:
        """Constructs the full path for a given storage reference in a specific subdir."""
        try:
            # Validate ref is a UUID string
            ref_uuid = str(uuid.UUID(ref))
        except ValueError:
            raise ValueError(f"Invalid storage reference format: {ref}")

        if subdir == self.BLOB_SUBDIR:
            return self.blob_dir / ref_uuid
        elif subdir == self.MIME_SUBDIR:
            return self.mime_dir / ref_uuid
        else:
            raise ValueError(f"Invalid subdir specified: {subdir}")

    async def put(
        self, stream: AsyncGenerator[bytes, None], mime_type: str | None = None
    ) -> str:
        """
        Stores a stream to a local file and its mime type in separate files.

        The storage reference returned is the unique filename (UUID).
        """
        ref = str(uuid.uuid4())
        blob_path = self._get_path(ref, self.BLOB_SUBDIR)
        mime_path = self._get_path(ref, self.MIME_SUBDIR)

        try:
            # Write blob data
            async with aiofiles.open(blob_path, mode="wb") as f:
                async for chunk in stream:
                    await f.write(chunk)

            # Write mime type if provided
            if mime_type:
                async with aiofiles.open(mime_path, mode="w", encoding="utf-8") as f:
                    await f.write(mime_type)

            return ref
        except Exception as e:
            logger.exception("error during put operation", ref=ref)
            # Attempt to clean up potentially partially written files
            if await aiofiles.os.path.exists(blob_path):
                try:
                    await aiofiles.os.remove(blob_path)
                except OSError as e2:
                    logger.warning(
                        "failed to cleanup blob file",
                        path=str(blob_path),
                        os_error=str(e2),
                    )
            if await aiofiles.os.path.exists(mime_path):
                try:
                    await aiofiles.os.remove(mime_path)
                except OSError as e2:
                    logger.warning(
                        "failed to cleanup mime file",
                        path=str(mime_path),
                        os_error=str(e2),
                    )
            raise IOError(f"Failed to store file or mime type for ref {ref}") from e

    async def get(self, ref: str) -> tuple[AsyncGenerator[bytes, None], str | None]:
        """
        Retrieves a stream and its mime type from local files.
        """
        blob_path = self._get_path(ref, self.BLOB_SUBDIR)
        mime_path = self._get_path(ref, self.MIME_SUBDIR)

        if not await aiofiles.os.path.isfile(blob_path):
            raise FileNotFoundError(f"Storage reference blob not found: {ref}")

        # Read mime type first
        mime_type: str | None = None
        if await aiofiles.os.path.isfile(mime_path):
            try:
                async with aiofiles.open(mime_path, mode="r", encoding="utf-8") as f:
                    mime_type = (await f.read()).strip()
            except Exception:
                logger.exception(
                    "failed to read mime type file",
                    path=str(mime_path),
                    ref=ref,
                )
                # Proceed without mime type if reading fails

        async def _stream():
            try:
                async with aiofiles.open(blob_path, mode="rb") as f:
                    while True:
                        chunk = await f.read(0xFFFF)  # Read in 64k chunks
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                logger.exception(
                    "error reading blob file", path=str(blob_path), ref=ref
                )
                raise IOError(f"Failed to read blob file for ref {ref}") from e

        return _stream(), mime_type

    async def delete(self, ref: str) -> None:
        """
        Deletes the blob file and its corresponding mime type file.
        """
        blob_path = self._get_path(ref, self.BLOB_SUBDIR)
        mime_path = self._get_path(ref, self.MIME_SUBDIR)
        deleted_blob = False
        deleted_mime = False

        # Delete blob file
        if await aiofiles.os.path.isfile(blob_path):
            try:
                await aiofiles.os.remove(blob_path)
                deleted_blob = True
            except Exception as e:
                raise IOError(f"Failed to delete blob file {blob_path}: {e}") from e
        else:
            # If blob doesn't exist, we consider it 'deleted' in terms of state
            deleted_blob = True

        # Delete mime file if it exists
        if await aiofiles.os.path.isfile(mime_path):
            try:
                await aiofiles.os.remove(mime_path)
                deleted_mime = True
            except Exception as e:
                # Log warning but don't raise if blob was successfully deleted or didn't exist
                logger.exception(
                    "failed to delete mime file",
                    path=str(mime_path),
                )
                if not deleted_blob:  # Re-raise if blob deletion also failed
                    raise IOError(
                        f"Failed to delete mime file {mime_path} after blob deletion failure: {e}"
                    ) from e

        # Raise FileNotFoundError only if neither file existed initially
        if (
            not await aiofiles.os.path.exists(blob_path)
            and not await aiofiles.os.path.exists(mime_path)
            and not deleted_blob
            and not deleted_mime
        ):
            # Check existence again to handle race conditions, though unlikely here
            # If we get here, it means the initial check passed but deletion failed somehow,
            # OR the files never existed. We treat the latter as FileNotFoundError.
            # This logic might need refinement based on desired atomicity guarantees.
            # For now, if the blob path doesn't exist after trying to delete, assume success or prior non-existence.
            pass  # Or raise FileNotFoundError if strict check is needed: raise FileNotFoundError(f"Storage reference not found: {ref}")

    async def external_url(self, ref: str) -> str | None:
        return None
