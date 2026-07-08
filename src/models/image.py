 import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Image:
    """
    Represents a single image captured during an inspection.
    Only ever queried by inspection_id (AP5), so it needs no GSI.
    """

    inspection_id: str
    s3_key: str
    image_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    uploaded_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_item(self) -> dict:
        return {
            "PK": f"INSPECTION#{self.inspection_id}",
            "SK": f"IMAGE#{self.image_id}",
            "entity_type": "IMAGE",
            "image_id": self.image_id,
            "inspection_id": self.inspection_id,
            "s3_key": self.s3_key,
            "uploaded_at": self.uploaded_at,
        }

    @staticmethod
    def from_item(item: dict) -> "Image":
        return Image(
            inspection_id=item["inspection_id"],
            s3_key=item["s3_key"],
            image_id=item["image_id"],
            uploaded_at=item.get("uploaded_at", ""),
        )

    def to_response_dict(self) -> dict:
        return {
            "image_id": self.image_id,
            "inspection_id": self.inspection_id,
            "s3_key": self.s3_key,
            "uploaded_at": self.uploaded_at,
        }