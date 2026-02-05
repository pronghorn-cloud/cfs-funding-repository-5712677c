"""Custom exceptions and global exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
import structlog

logger = structlog.get_logger()


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str | None = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code or "UNKNOWN_ERROR"


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=403, detail=detail, error_code="FORBIDDEN")


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=409, detail=detail, error_code="CONFLICT")


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")


class ExternalServiceException(AppException):
    def __init__(self, detail: str = "External service unavailable"):
        super().__init__(status_code=502, detail=detail, error_code="EXTERNAL_SERVICE_ERROR")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> ORJSONResponse:
        await logger.awarning(
            "app_exception",
            status_code=exc.status_code,
            error_code=exc.error_code,
            detail=exc.detail,
            path=str(request.url),
        )
        return ORJSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
        await logger.aerror(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=str(request.url),
        )
        return ORJSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_SERVER_ERROR",
                "detail": "An unexpected error occurred",
            },
        )
