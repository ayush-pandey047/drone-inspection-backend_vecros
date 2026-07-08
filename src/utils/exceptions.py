class AppError(Exception):
    """Base exception for all application-level errors. Carries an HTTP status code."""

    status_code: int = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource (warehouse, drone, inspection) doesn't exist."""

    status_code = 404


class ValidationError(AppError):
    """Raised when the request body/params fail validation."""

    status_code = 400


class ConflictError(AppError):
    """Raised when a business rule is violated, e.g. drone doesn't belong to warehouse."""

    status_code = 409