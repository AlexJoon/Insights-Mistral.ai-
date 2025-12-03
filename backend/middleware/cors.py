"""
CORS middleware configuration.
Handles Cross-Origin Resource Sharing for frontend communication.
"""
from starlette.middleware.cors import CORSMiddleware
from typing import List


def create_cors_middleware(allowed_origins: List[str]) -> type:
    """
    Create CORS middleware with specified configuration.

    Args:
        allowed_origins: List of allowed origin URLs

    Returns:
        Configured CORS middleware class
    """
    return CORSMiddleware


def get_cors_config(allowed_origins: List[str]) -> dict:
    """
    Get CORS configuration dictionary.

    Args:
        allowed_origins: List of allowed origin URLs

    Returns:
        CORS configuration dictionary
    """
    return {
        "allow_origins": allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With"
        ],
        "expose_headers": ["Content-Type"],
        "max_age": 600
    }
