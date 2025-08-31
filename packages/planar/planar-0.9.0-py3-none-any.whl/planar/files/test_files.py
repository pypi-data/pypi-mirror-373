"""
Test file handling in Planar workflows.
"""

import uuid
from pathlib import Path
from typing import AsyncGenerator, cast

import pytest
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from planar.app import PlanarApp
from planar.config import sqlite_config
from planar.files import PlanarFile
from planar.files.models import PlanarFileMetadata
from planar.files.storage.base import Storage
from planar.workflows.decorators import workflow
from planar.workflows.execution import execute
from planar.workflows.models import Workflow

app = PlanarApp(
    config=sqlite_config(":memory:"),
    title="Planar app for testing file workflows",
    description="Testing",
)


@pytest.fixture(name="app")
def app_fixture():
    yield app


@pytest.fixture
async def planar_file(
    storage: Storage,
    session: AsyncSession,  # Change type hint
) -> PlanarFile:
    """Create a PlanarFile instance for testing."""
    # Store test content
    test_data = b"Test file content for workflow"
    mime_type = "text/plain"

    # Store the file and get a reference
    storage_ref = await storage.put_bytes(test_data, mime_type=mime_type)

    # Create and store the file metadata
    file_metadata = PlanarFileMetadata(
        filename="test_file.txt",
        content_type=mime_type,
        size=len(test_data),
        storage_ref=storage_ref,
    )
    session.add(file_metadata)
    await session.commit()
    await session.refresh(file_metadata)

    # Return a PlanarFile reference (not the full metadata)
    return PlanarFile(
        id=file_metadata.id,
        filename=file_metadata.filename,
        content_type=file_metadata.content_type,
        size=file_metadata.size,
    )


# Define models for workflow testing
class FileProcessingInput(BaseModel):
    """Input model for a workflow that processes a file."""

    title: str = Field(description="Title of the processing job")
    file: PlanarFile = Field(description="The file to process")
    max_chars: int = Field(description="Maximum characters to extract", default=100)


class FileProcessingResult(BaseModel):
    """Result model for a file processing workflow."""

    title: str = Field(description="Title of the processing job")
    characters: int = Field(description="Number of characters in the file")
    content_preview: str = Field(description="Preview of the file content")
    file_id: uuid.UUID = Field(description="ID of the processed file")


async def test_workflow_with_planar_file(
    session: AsyncSession,
    planar_file: PlanarFile,
):
    """Test that a workflow can accept and process a PlanarFile input."""

    @workflow()
    async def file_processing_workflow(input_data: PlanarFile):
        file_content = await input_data.get_content()
        char_count = len(file_content)
        content_str = file_content.decode("utf-8")
        preview = content_str[:100]

        # Return structured result
        return FileProcessingResult(
            title="Test File Processing",
            characters=char_count,
            content_preview=preview,
            file_id=input_data.id,
        )

    wf = await file_processing_workflow.start(planar_file)
    result = await execute(wf)

    # Verify the result
    assert isinstance(result, FileProcessingResult)
    assert result.title == "Test File Processing"
    assert result.characters == len(b"Test file content for workflow")
    assert result.content_preview == "Test file content for workflow"
    assert result.file_id == planar_file.id

    # Verify the workflow completed successfully
    updated_wf = await session.get(Workflow, wf.id)
    assert updated_wf is not None
    assert updated_wf.status == "succeeded"
    assert updated_wf.args == [planar_file.model_dump(mode="json")]

    # Verify that the result stored in the workflow is correct
    workflow_result = cast(dict, updated_wf.result)
    assert workflow_result["title"] == "Test File Processing"
    assert workflow_result["characters"] == len(b"Test file content for workflow")
    assert workflow_result["content_preview"] == "Test file content for workflow"
    assert workflow_result["file_id"] == str(planar_file.id)


TEST_BYTES = b"Test data for upload"
TEST_FILENAME = "upload_test.txt"
TEST_CONTENT_TYPE = "text/plain"
TEST_SIZE = len(TEST_BYTES)
DEFAULT_CONTENT_TYPE = "application/octet-stream"


async def assert_upload_success(
    uploaded_file: PlanarFile,
    expected_filename: str,
    expected_content: bytes,
    expected_content_type: str,
    expected_size: int,
    session: AsyncSession,
):
    """Helper function to assert successful file upload."""
    assert isinstance(uploaded_file, PlanarFile)
    assert uploaded_file.filename == expected_filename
    assert uploaded_file.content_type == expected_content_type
    assert uploaded_file.size == expected_size
    assert isinstance(uploaded_file.id, uuid.UUID)

    # Verify database record
    metadata = await session.get(PlanarFileMetadata, uploaded_file.id)
    assert metadata is not None
    assert metadata.filename == expected_filename
    assert metadata.content_type == expected_content_type
    assert metadata.size == expected_size
    assert metadata.storage_ref is not None

    # Verify stored content
    retrieved_content = await uploaded_file.get_content()
    assert retrieved_content == expected_content


async def test_planar_file_upload_bytes(storage: Storage, session: AsyncSession):
    """Test PlanarFile.upload with bytes content."""
    uploaded_file = await PlanarFile.upload(
        content=TEST_BYTES,
        filename=TEST_FILENAME,
        content_type="text/plain",
        size=100,
    )
    await assert_upload_success(
        uploaded_file,
        TEST_FILENAME,
        TEST_BYTES,
        "text/plain",
        100,
        session,
    )


async def test_planar_file_upload_bytes_defaults(
    storage: Storage, session: AsyncSession
):
    """Test PlanarFile.upload with bytes content using default size/type."""
    uploaded_file = await PlanarFile.upload(content=TEST_BYTES, filename=TEST_FILENAME)
    await assert_upload_success(
        uploaded_file,
        TEST_FILENAME,
        TEST_BYTES,
        DEFAULT_CONTENT_TYPE,  # Default type expected
        TEST_SIZE,  # Size should be calculated
        session,
    )


async def test_planar_file_upload_path(
    storage: Storage, session: AsyncSession, tmp_path: Path
):
    """Test PlanarFile.upload with Path content."""
    test_file = tmp_path / TEST_FILENAME
    test_file.write_bytes(TEST_BYTES)

    uploaded_file = await PlanarFile.upload(
        content=test_file,
        filename=TEST_FILENAME,
        content_type=TEST_CONTENT_TYPE,
        size=TEST_SIZE,
    )
    await assert_upload_success(
        uploaded_file,
        TEST_FILENAME,
        TEST_BYTES,
        TEST_CONTENT_TYPE,
        TEST_SIZE,
        session,
    )


async def test_planar_file_upload_path_defaults(
    storage: Storage, session: AsyncSession, tmp_path: Path
):
    """Test PlanarFile.upload with Path content using default/inferred size/type."""
    test_file = tmp_path / "another_test.json"  # Use different extension for inference
    test_data = b'{"key": "value"}'
    test_file.write_bytes(test_data)

    uploaded_file = await PlanarFile.upload(
        content=test_file,
        filename="data.json",  # Ensure filename matches for inference
    )
    await assert_upload_success(
        uploaded_file,
        "data.json",
        test_data,
        "application/json",  # Inferred type expected
        len(test_data),  # Size should be calculated
        session,
    )


async def simple_byte_stream(
    data: bytes, chunk_size: int = 10
) -> AsyncGenerator[bytes, None]:
    """Helper async generator for stream tests."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


async def test_planar_file_upload_stream(storage: Storage, session: AsyncSession):
    """Test PlanarFile.upload with AsyncGenerator content."""
    uploaded_file = await PlanarFile.upload(
        content=simple_byte_stream(TEST_BYTES),
        filename=TEST_FILENAME,
        content_type=TEST_CONTENT_TYPE,
        size=TEST_SIZE,
    )
    await assert_upload_success(
        uploaded_file,
        TEST_FILENAME,
        TEST_BYTES,
        TEST_CONTENT_TYPE,
        TEST_SIZE,
        session,
    )


async def test_planar_file_upload_stream_defaults(
    storage: Storage, session: AsyncSession
):
    """Test PlanarFile.upload with AsyncGenerator content using default size/type."""
    uploaded_file = await PlanarFile.upload(
        content=simple_byte_stream(TEST_BYTES), filename=TEST_FILENAME
    )
    await assert_upload_success(
        uploaded_file,
        TEST_FILENAME,
        TEST_BYTES,
        DEFAULT_CONTENT_TYPE,  # Default type expected
        -1,  # Size should be unknown (-1)
        session,
    )
