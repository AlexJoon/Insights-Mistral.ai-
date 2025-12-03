"""
Request validation middleware.
Validates incoming requests before they reach route handlers.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Callable
from backend.utils.logger import setup_logger


logger = setup_logger(__name__)


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for validating incoming requests."""

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Validate the request before processing.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            Response object
        """
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")

            # Skip validation for SSE endpoints
            if "/chat/stream" not in request.url.path:
                if not content_type.startswith("application/json"):
                    logger.warning(f"Invalid content type: {content_type}")
                    return JSONResponse(
                        status_code=415,
                        content={
                            "error": "Unsupported Media Type",
                            "message": "Content-Type must be application/json"
                        }
                    )

        # Log request
        logger.info(f"{request.method} {request.url.path}")

        response = await call_next(request)
        return response
