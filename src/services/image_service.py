import os
import uuid

import boto3
from botocore.exceptions import ClientError

from src.models.image import Image
from src.repositories.dynamo_repository import DynamoRepository
from src.utils.exceptions import NotFoundError
from src.utils.logger import get_logger

logger = get_logger(__name__)

BUCKET_NAME = os.environ.get("BUCKET_NAME", "drone-inspection-images-local")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")  # set only for local testing
PRESIGNED_URL_EXPIRY_SECONDS = 300  # 5 minutes


class ImageService:
    def __init__(self, repository: DynamoRepository | None = None):
        self.repository = repository or DynamoRepository()
        if S3_ENDPOINT_URL:
            self.s3_client = boto3.client("s3", endpoint_url=S3_ENDPOINT_URL)
        else:
            self.s3_client = boto3.client("s3")

    def generate_upload_url(self, inspection_id: str, file_extension: str = "jpg") -> dict:
        # Validate the inspection exists before minting a URL for it —
        # otherwise anyone could request an upload slot for a nonexistent
        # inspection and end up with orphaned S3 objects.
        inspection_item = self.repository.get_inspection_by_id(inspection_id)
        if not inspection_item:
            raise NotFoundError(f"Inspection '{inspection_id}' does not exist")

        image_id = str(uuid.uuid4())
        s3_key = f"inspections/{inspection_id}/{image_id}.{file_extension}"

        try:
            presigned_url = self.s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={"Bucket": BUCKET_NAME, "Key": s3_key},
                ExpiresIn=PRESIGNED_URL_EXPIRY_SECONDS,
            )
        except ClientError as e:
            logger.error("Failed to generate presigned URL: %s", e)
            raise

        # Save the Image metadata record immediately. The actual binary
        # upload happens later, directly from the client to S3 — this
        # record just reserves the image's identity/location so
        # list_images can return it right away. (Trade-off worth knowing:
        # this means an Image row can exist even if the client never
        # actually completes the upload. Production systems often handle
        # this with an S3 event trigger that confirms/flags upload
        # completion — noted as a Future Improvement.)
        image = Image(inspection_id=inspection_id, s3_key=s3_key, image_id=image_id)
        self.repository.put_image(image.to_item())

        logger.info("Generated upload URL for inspection %s, image %s", inspection_id, image_id)

        return {
            "upload_url": presigned_url,
            "image_id": image_id,
            "s3_key": s3_key,
            "expires_in_seconds": PRESIGNED_URL_EXPIRY_SECONDS,
        }

    def list_images(self, inspection_id: str) -> list[Image]:
        inspection_item = self.repository.get_inspection_by_id(inspection_id)
        if not inspection_item:
            raise NotFoundError(f"Inspection '{inspection_id}' does not exist")

        items = self.repository.query_images_by_inspection(inspection_id)
        return [Image.from_item(item) for item in items]