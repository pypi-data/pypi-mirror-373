import asyncio
import io
import uuid
from typing import Any, AsyncGenerator, Dict, Tuple

import boto3
from botocore.client import Config as BotoConfig
from botocore.exceptions import ClientError

from planar.logging import get_logger

from .base import Storage

logger = get_logger(__name__)


class S3Storage(Storage):
    """Stores files and mime types in an S3-compatible bucket using boto3."""

    def __init__(
        self,
        bucket_name: str,
        region: str,
        endpoint_url: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        session_token: str | None = None,  # For temporary credentials
        boto_config: Dict[str, Any] | None = None,  # Additional boto3 client config
        presigned_url_ttl: int = 3600,
    ):
        """
        Initializes S3Storage.

        Args:
            bucket_name: The name of the S3 bucket.
            endpoint_url: The S3 endpoint URL (e.g., 'https://s3.amazonaws.com' or custom).
            access_key_id: AWS Access Key ID.
            secret_access_key: AWS Secret Access Key.
            region: The AWS region of the bucket.
            session_token: AWS Session Token (for temporary credentials).
            boto_config: Additional configuration options for boto3 client.
            presigned_url_ttl: Time in seconds for which the presigned URL is valid.
        """
        self.bucket_name = bucket_name
        self.endpoint_url = (
            endpoint_url  # Boto3 generally prefers endpoint_url without trailing slash
        )
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region
        self.session_token = session_token
        self.presigned_url_ttl = presigned_url_ttl

        # Initialize boto3 S3 client
        # Using s3v4 signature is often necessary for S3 compatible services like MinIO/LocalStack
        config_options = {"signature_version": "s3v4"}
        if boto_config:
            config_options.update(boto_config)
        config = BotoConfig(**config_options)
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            aws_session_token=self.session_token,
            region_name=self.region,
            config=config,
        )

    async def _get_object_url(self, ref: str) -> str | None:
        """Generates a presigned URL for a given object reference."""
        try:
            # generate_presigned_url is synchronous, so we run it in a thread
            url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": ref},
                ExpiresIn=self.presigned_url_ttl,
            )
            return url
        except ClientError:
            logger.exception(
                "failed to generate presigned url",
                ref=ref,
                bucket_name=self.bucket_name,
            )
            # Returning None is a safe default if URL generation fails.
            return None

    async def put(
        self, stream: AsyncGenerator[bytes, None], mime_type: str | None = None
    ) -> str:
        """
        Stores a stream and optional mime type to an S3 object with a unique name.

        The storage reference returned is the unique object key (UUID).
        The mime_type is stored as the Content-Type metadata.
        """
        ref = str(uuid.uuid4())

        # Collect data from async generator into bytes
        data_bytes_list = []
        async for chunk in stream:
            data_bytes_list.append(chunk)
        data_bytes = b"".join(data_bytes_list)

        extra_args = {}
        if mime_type:
            extra_args["ContentType"] = mime_type

        try:
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=ref,
                Body=data_bytes,
                **extra_args,
            )
            return ref
        except ClientError as e:
            logger.exception(
                "failed s3 put object",
                ref=ref,
                bucket_name=self.bucket_name,
                error_response=e.response,
            )
            raise IOError(f"Failed to upload to S3 object {ref}. Error: {e}") from e
        except Exception as e:
            logger.exception(
                "an unexpected error occurred during s3 upload",
                ref=ref,
            )
            raise IOError(f"An error occurred during S3 upload for {ref}") from e

    async def get(self, ref: str) -> Tuple[AsyncGenerator[bytes, None], str | None]:
        """
        Retrieves a stream and its mime type (Content-Type) from an S3 object
        using its storage reference (object key).
        """
        try:
            response = await asyncio.to_thread(
                self.s3_client.get_object, Bucket=self.bucket_name, Key=ref
            )

            streaming_body = response["Body"]
            mime_type = response.get("ContentType")

            async def _stream_wrapper(body):
                try:
                    while True:
                        # Read a chunk in the executor
                        chunk = await asyncio.to_thread(
                            body.read, io.DEFAULT_BUFFER_SIZE
                        )
                        if not chunk:
                            break
                        yield chunk
                finally:
                    # Ensure the boto3 stream is closed
                    await asyncio.to_thread(body.close)

            return _stream_wrapper(streaming_body), mime_type

        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                logger.warning(
                    "s3 object not found", ref=ref, bucket_name=self.bucket_name
                )
                raise FileNotFoundError(f"S3 object not found: {ref}") from e
            else:
                logger.exception(
                    "failed s3 get object",
                    ref=ref,
                    bucket_name=self.bucket_name,
                    error_response=e.response,
                )
                raise IOError(
                    f"Failed to download from S3 object {ref}. Error: {e}"
                ) from e
        except Exception as e:
            logger.exception(
                "an unexpected error occurred during s3 download",
                ref=ref,
            )
            raise IOError(f"An error occurred during S3 download for {ref}") from e

    async def delete(self, ref: str) -> None:
        """
        Deletes an object from the S3 bucket using its storage reference (object key).
        Boto3's delete_object is idempotent and does not error if the object is not found.
        """
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object, Bucket=self.bucket_name, Key=ref
            )
        except ClientError as e:
            # delete_object is generally idempotent. Log and raise if it's not a 'not found' scenario
            # (though boto3 usually handles 'NoSuchKey' gracefully for delete).
            logger.exception(
                "failed s3 delete object",
                ref=ref,
                bucket_name=self.bucket_name,
                error_response=e.response,
            )
            raise IOError(f"Failed to delete S3 object {ref}. Error: {e}") from e
        except Exception as e:
            logger.exception(
                "an unexpected error occurred during s3 delete",
                ref=ref,
            )
            raise IOError(f"An error occurred during S3 delete for {ref}") from e

    async def external_url(self, ref: str) -> str | None:
        """
        Returns a presigned URL to access the S3 object.

        The URL is temporary and its validity is determined by the `presigned_url_ttl`
        parameter set during initialization.
        """
        return await self._get_object_url(ref)
