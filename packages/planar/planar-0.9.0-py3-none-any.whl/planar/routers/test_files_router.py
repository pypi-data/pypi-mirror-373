import io
from uuid import UUID

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from planar import PlanarApp, sqlite_config
from planar.files.models import PlanarFileMetadata
from planar.testing.planar_test_client import PlanarTestClient


@pytest.fixture(name="app")
def app_fixture():
    return PlanarApp(
        config=sqlite_config(":memory:"),
        title="Test app for files router",
        description="Testing files endpoints",
    )


async def test_upload_parquet_sets_content_type(
    client: PlanarTestClient, session: AsyncSession
):
    """Uploading a .parquet file should persist application/x-parquet in metadata."""

    # Prepare a small in-memory payload and intentionally send an octet-stream
    # to simulate browsers that don't know parquet. The route should override
    # this using mimetypes.guess_type.
    filename = "test_data.parquet"
    payload = b"PAR1"  # content doesn't matter for MIME guessing by filename

    files = {
        "files": (filename, io.BytesIO(payload), "application/octet-stream"),
    }

    resp = await client.post("/planar/v1/file/upload", files=files)
    assert resp.status_code == 200

    body = resp.json()
    assert isinstance(body, list) and len(body) == 1
    file_item = body[0]
    assert file_item["filename"] == filename

    # Verify the database record has the correct MIME type
    file_id = UUID(file_item["id"])
    meta = await session.get(PlanarFileMetadata, file_id)

    assert meta is not None
    assert meta.content_type == "application/x-parquet"
