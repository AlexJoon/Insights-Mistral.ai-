"""
Error handling middleware.
Centralized error handling and response formatting.
"""
from typing import Callable
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.utils.logger import setup_logger
from backend.services.mistral_service import MistralServiceError
from backend.utils.validators import ValidationError


logger = setup_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and formatting error responses."""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process the request and handle any errors.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response object
        """
        try:
            response = await call_next(request)
            return response

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "message": str(e),
                    "type": "validation_error"
                }
            )

        except MistralServiceError as e:
            logger.error(f"Mistral service error: {str(e)}")
            return JSONResponse(
                status_code=502,
                content={
                    "error": "AI Service Error",
                    "message": str(e),
                    "type": "service_error"
                }
            )

        except ValueError as e:
            logger.warning(f"Value error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(e),
                    "type": "value_error"
                }
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "type": "internal_error"
                }
            )


def create_error_response(status_code: int, message: str, error_type: str = "error") -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        status_code: HTTP status code
        message: Error message
        error_type: Type of error

    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "message": message
        }
    )
