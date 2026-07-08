import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Inspection:
    """
    Represents a single drone inspection of a warehouse.

    Design note: an Inspection has THREE access requirements:
      1. List by warehouse         -> main item:   PK=WAREHOUSE#<wid>, SK=INSPECTION#<iid>
      2. List by drone              -> GSI1 on main item: GSI1PK=DRONE#<did>, GSI1SK=INSPECTION#<iid>
      3. Direct lookup by inspection_id only (needed by upload-url and list-images,
         which receive only inspectionId in the URL, no warehouseId/droneId)
                                     -> pointer item: PK=INSPECTION#<iid>, SK=INSPECTION#<iid>

    We write BOTH items in a single call. This is a standard single-table
    design pattern: trading a small amount of extra storage (one small
    pointer item) for O(1) indexed lookups on every access pattern, instead
    of a Scan. Both items are updated only at creation time (status of an
    inspection isn't updated in this assignment's scope), so there's no
    dual-write consistency risk to worry about here.
    """

    warehouse_id: str
    drone_id: str
    inspection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "PENDING"
    notes: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_items(self) -> list[dict]:
        """Returns BOTH DynamoDB items that must be written for this Inspection."""
        base_attrs = {
            "entity_type": "INSPECTION",
            "inspection_id": self.inspection_id,
            "warehouse_id": self.warehouse_id,
            "drone_id": self.drone_id,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
        }

        main_item = {
            "PK": f"WAREHOUSE#{self.warehouse_id}",
            "SK": f"INSPECTION#{self.inspection_id}",
            "GSI1PK": f"DRONE#{self.drone_id}",
            "GSI1SK": f"INSPECTION#{self.inspection_id}",
            **base_attrs,
        }

        pointer_item = {
            "PK": f"INSPECTION#{self.inspection_id}",
            "SK": f"INSPECTION#{self.inspection_id}",
            **base_attrs,
        }

        return [main_item, pointer_item]

    @staticmethod
    def from_item(item: dict) -> "Inspection":
        return Inspection(
            warehouse_id=item["warehouse_id"],
            drone_id=item["drone_id"],
            inspection_id=item["inspection_id"],
            status=item.get("status", "PENDING"),
            notes=item.get("notes", ""),
            created_at=item.get("created_at", ""),
        )

    def to_response_dict(self) -> dict:
        return {
            "inspection_id": self.inspection_id,
            "warehouse_id": self.warehouse_id,
            "drone_id": self.drone_id,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
        }