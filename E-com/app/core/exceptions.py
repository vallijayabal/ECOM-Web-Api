"""
Custom exception classes and FastAPI exception handlers.
"""

from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


# ═══════════════════════════════════════════════════
# Custom Exceptions
# ═══════════════════════════════════════════════════

class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id is not None:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)


class AlreadyExistsException(AppException):
    """Resource already exists."""

    def __init__(self, resource: str = "Resource", field: str = "", value: Any = ""):
        message = f"{resource} already exists"
        if field and value:
            message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class UnauthorizedException(AppException):
    """Authentication failure."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    """Authorization failure (insufficient permissions)."""

    def __init__(self, message: str = "You don't have permission to perform this action"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class ValidationException(AppException):
    """Input validation error."""

    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class PaymentException(AppException):
    """Payment processing error."""

    def __init__(self, message: str = "Payment processing failed", details: Any = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            details=details,
        )


class RateLimitException(AppException):
    """Rate limit exceeded."""

    def __init__(self):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ═══════════════════════════════════════════════════
# Exception Handlers (registered on FastAPI app)
# ═══════════════════════════════════════════════════

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle all AppException subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "details": None,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions (500)."""
    import structlog
    logger = structlog.get_logger()
    await logger.aerror("Unhandled exception", error=str(exc), path=str(request.url))

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "details": str(exc) if not request.app.state.settings.IS_PRODUCTION else None,
        },
    )
