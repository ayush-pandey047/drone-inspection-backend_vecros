import json

from src.services.image_service import ImageService
from src.utils.exceptions import AppError
from src.utils.logger import get_logger
from src.utils.response import error_response, success_response

logger = get_logger(__name__)


def lambda_handler(event: dict, context) -> dict:
    """
    POST /inspections/{inspectionId}/upload-url
    Body (optional): { "file_extension": str }  -- defaults to "jpg"
    """
    try:
        inspection_id = event["pathParameters"]["inspectionId"]
        body = json.loads(event.get("body") or "{}")
        file_extension = body.get("file_extension", "jpg")

        service = ImageService()
        result = service.generate_upload_url(inspection_id, file_extension)

        return success_response(200, result)

    except AppError as e:
        return error_response(e.status_code, e.message)

    except KeyError:
        return error_response(400, "Missing inspectionId path parameter")

    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON in request body")

    except Exception:
        logger.exception("Unexpected error in generate_upload_url")
        return error_response(500, "Internal server error")