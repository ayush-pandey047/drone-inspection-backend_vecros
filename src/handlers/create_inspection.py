import json

from src.services.inspection_service import InspectionService
from src.utils.exceptions import AppError
from src.utils.logger import get_logger
from src.utils.response import error_response, success_response

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    """
    POST /inspections
    Body: { "warehouse_id": str, "drone_id": str, "notes": str (optional) }
    """
    try:
        body = json.loads(event.get("body") or "{}")

        service = InspectionService()
        inspection = service.create_inspection(
            warehouse_id=body.get("warehouse_id"),
            drone_id=body.get("drone_id"),
            notes=body.get("notes", ""),
        )

        return success_response(201, inspection.to_response_dict())

    except AppError as e:
        logger.warning("Business error: %s", e.message)
        return error_response(e.status_code, e.message)

    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON in request body")

    except Exception as e:
        logger.exception("Unexpected error in create_inspection")
        return error_response(500, "Internal server error")