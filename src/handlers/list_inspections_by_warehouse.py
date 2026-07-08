from src.services.inspection_service import InspectionService
from src.utils.exceptions import AppError
from src.utils.logger import get_logger
from src.utils.response import error_response, success_response

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    """GET /warehouses/{warehouseId}/inspections"""
    try:
        warehouse_id = event["pathParameters"]["warehouseId"]

        service = InspectionService()
        inspections = service.list_by_warehouse(warehouse_id)

        return success_response(200, [i.to_response_dict() for i in inspections])

    except AppError as e:
        return error_response(e.status_code, e.message)

    except KeyError:
        return error_response(400, "Missing warehouseId path parameter")

    except Exception:
        logger.exception("Unexpected error in list_inspections_by_warehouse")
        return error_response(500, "Internal server error")