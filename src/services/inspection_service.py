from src.models.inspection import Inspection
from src.repositories.dynamo_repository import DynamoRepository
from src.utils.exceptions import NotFoundError, ValidationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class InspectionService:
    def __init__(self, repository: DynamoRepository | None = None):
        # Accepting an optional repository (dependency injection) makes this
        # class trivially testable: pass a fake/mock repository in unit tests
        # instead of hitting real DynamoDB.
        self.repository = repository or DynamoRepository()

    def create_inspection(
        self, warehouse_id: str, drone_id: str, notes: str = ""
    ) -> Inspection:
        if not warehouse_id or not drone_id:
            raise ValidationError("warehouse_id and drone_id are required")

        # Referential integrity check: DynamoDB has no foreign keys, so the
        # SERVICE layer is responsible for enforcing that the warehouse and
        # drone actually exist before we create an inspection tying them
        # together. This is exactly the kind of check that would be a DB
        # constraint in SQL but must be explicit application code in NoSQL.
        warehouse = self.repository.get_warehouse(warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse '{warehouse_id}' does not exist")

        drone = self.repository.get_drone(warehouse_id, drone_id)
        if not drone:
            raise NotFoundError(
                f"Drone '{drone_id}' does not exist under warehouse '{warehouse_id}'"
            )

        inspection = Inspection(warehouse_id=warehouse_id, drone_id=drone_id, notes=notes)
        self.repository.put_inspection(inspection.to_items())

        logger.info("Created inspection %s", inspection.inspection_id)
        return inspection

    def list_by_warehouse(self, warehouse_id: str) -> list[Inspection]:
        if not warehouse_id:
            raise ValidationError("warehouse_id is required")

        items = self.repository.query_inspections_by_warehouse(warehouse_id)
        return [Inspection.from_item(item) for item in items]

    def list_by_drone(self, drone_id: str) -> list[Inspection]:
        if not drone_id:
            raise ValidationError("drone_id is required")

        items = self.repository.query_inspections_by_drone(drone_id)
        return [Inspection.from_item(item) for item in items]

    def get_inspection(self, inspection_id: str) -> Inspection:
        item = self.repository.get_inspection_by_id(inspection_id)
        if not item:
            raise NotFoundError(f"Inspection '{inspection_id}' does not exist")
        return Inspection.from_item(item)