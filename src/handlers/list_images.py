from src.services.image_service import ImageService
from src.utils.exceptions import AppError
from src.utils.logger import get_logger
from src.utils.response import error_response, success_response

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    """GET /inspections/{inspectionId}/images"""
    try:
        inspection_id = event["pathParameters"]["inspectionId"]

        service = ImageService()
        images = service.list_images(inspection_id)

        return success_response(200, [img.to_response_dict() for img in images])

    except AppError as e:
        return error_response(e.status_code, e.message)

    except KeyError:
        return error_response(400, "Missing inspectionId path parameter")

    except Exception:
        logger.exception("Unexpected error in list_images")
        return error_response(500, "Internal server error")