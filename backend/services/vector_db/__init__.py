"""
Vector database module for RAG implementation.
Provides abstract interface and concrete adapters for multiple vector databases.
"""
from .base import VectorDatabaseInterface, VectorSearchResult
from .factory import VectorDatabaseFactory

__all__ = [
    "VectorDatabaseInterface",
    "VectorSearchResult",
    "VectorDatabaseFactory",
]
