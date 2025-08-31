import mimetypes
import uuid
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse

from planar.files.models import PlanarFile, PlanarFileMetadata
from planar.files.storage.context import get_storage
from planar.logging import get_logger
from planar.session import get_session

logger = get_logger(__name__)


router = APIRouter(tags=["Files"])

# Add Parquet MIME type
mimetypes.add_type("application/x-parquet", ".parquet")


@router.post("/upload", response_model=list[PlanarFile])
async def upload_files(files: list[UploadFile] = File(...)):
    """
    Uploads one or more files to the configured storage backend and records their metadata.
    Returns a list of file IDs for the successfully uploaded files.
    """
    storage = get_storage()
    session = get_session()
    uploaded_files: list[PlanarFile] = []

    for file in files:
        # Define an async generator to stream the file content efficiently
        async def file_stream_generator(current_file: UploadFile):
            # Read in chunks to avoid loading the whole file into memory
            chunk_size = 65536  # 64KB
            while chunk := await current_file.read(chunk_size):
                yield chunk
            # Reset file pointer if needed for potential retries or other operations,
            # though not strictly necessary for this single pass upload.
            await current_file.seek(0)

        try:
            guessed_type, _ = mimetypes.guess_type(file.filename or "")
            final_content_type = (
                guessed_type or file.content_type or "application/octet-stream"
            )

            # Store the file content using the storage backend
            storage_ref = await storage.put(
                stream=file_stream_generator(file), mime_type=final_content_type
            )

            # Create the metadata record in the database
            planar_file = PlanarFileMetadata(
                filename=file.filename
                or str(uuid.uuid4()),  # Use filename or default to random UUID
                content_type=final_content_type,
                size=file.size
                if file.size is not None
                else -1,  # Store size if available
                storage_ref=storage_ref,
            )
            session.add(planar_file)
            await session.commit()
            await session.refresh(planar_file)  # Ensure file_id is populated

            logger.info(
                "uploaded file",
                filename=planar_file.filename,
                file_id=planar_file.id,
                storage_ref=storage_ref,
            )
            uploaded_files.append(planar_file)

        except Exception:
            # Log the error for the specific file but continue with others
            logger.exception("failed to upload file", filename=file.filename)
            # Optionally, rollback the session changes for this specific file if needed,
            # though commit happens per file here. If atomicity across all files is desired,
            # collect all PlanarFile objects and commit once outside the loop.
            await (
                session.rollback()
            )  # Rollback potential partial changes for the failed file

    if not uploaded_files and files:
        # If no files were successfully uploaded but some were provided, raise an error
        raise HTTPException(status_code=500, detail="All file uploads failed")

    return uploaded_files


@router.get("/{file_id}/content")
async def get_file_content(file_id: UUID):
    """
    Retrieves the content of a file.

    If the storage backend provides an external URL, it redirects the client.
    Otherwise, it streams the file content directly.
    """
    storage = get_storage()
    session = get_session()

    # Retrieve file metadata
    planar_file = await session.get(PlanarFileMetadata, file_id)
    if not planar_file:
        raise HTTPException(status_code=404, detail="File not found")

    storage_ref = planar_file.storage_ref

    try:
        # Check for an external URL first
        external_url = await storage.external_url(storage_ref)
        if external_url:
            return RedirectResponse(url=external_url)

        # If no external URL, get the stream from storage
        stream, mime_type = await storage.get(storage_ref)

        # Ensure mime_type defaults correctly if storage didn't return one
        media_type = mime_type or planar_file.content_type or "application/octet-stream"

        return StreamingResponse(stream, media_type=media_type)

    except FileNotFoundError:
        logger.warning(
            "file content not found in storage",
            file_id=file_id,
            storage_ref=storage_ref,
        )
        raise HTTPException(status_code=404, detail="File content not found in storage")
    except Exception:
        logger.exception("failed to retrieve file content", file_id=file_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve file content")


@router.get("/{file_id}/metadata", response_model=PlanarFile)
async def get_file_metadata(file_id: UUID):
    session = get_session()

    # Retrieve file metadata
    planar_file = await session.get(PlanarFileMetadata, file_id)
    if not planar_file:
        logger.warning("file metadata not found", file_id=file_id)
        raise HTTPException(status_code=404, detail="File not found")
    return planar_file


def create_files_router() -> APIRouter:
    """Factory function to create and return the files router."""
    return router
