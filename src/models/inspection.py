import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Inspection:
    """
    Represents a single drone inspection of a warehouse.

    Design note: an Inspection has TWO logical parents (Warehouse and Drone).
    In DynamoDB this is modeled as:
      - Main table:  PK = WAREHOUSE#<warehouse_id>, SK = INSPECTION#<inspection_id>
      - GSI1:        GSI1PK = DRONE#<drone_id>,     GSI1SK = INSPECTION#<inspection_id>
    This lets the same item be queried efficiently both ways.
    """

    warehouse_id: str
    drone_id: str
    inspection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "PENDING"
    notes: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_item(self) -> dict:
        """Convert this Inspection into a DynamoDB item (with key overloading)."""
        return {
            "PK": f"WAREHOUSE#{self.warehouse_id}",
            "SK": f"INSPECTION#{self.inspection_id}",
            "GSI1PK": f"DRONE#{self.drone_id}",
            "GSI1SK": f"INSPECTION#{self.inspection_id}",
            "entity_type": "INSPECTION",
            "inspection_id": self.inspection_id,
            "warehouse_id": self.warehouse_id,
            "drone_id": self.drone_id,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_item(item: dict) -> "Inspection":
        """Reconstruct an Inspection object from a raw DynamoDB item."""