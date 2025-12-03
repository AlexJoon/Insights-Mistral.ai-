"""
Abstract base class for vector database operations.
Defines the contract that all vector database adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class VectorSearchResult:
    """
    Standardized search result across all vector database implementations.

    Attributes:
        id: Unique identifier for the chunk
        content: The actual text content
        metadata: Additional information (course_code, instructor, etc.)
        similarity_score: Relevance score (0-1, higher is better)
    """
    id: str
    content: str
    metadata: Dict
    similarity_score: float

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "similarity_score": self.similarity_score
        }


class VectorDatabaseInterface(ABC):
    """
    Abstract interface for vector database operations.

    This interface allows swapping between different vector databases
    (Pinecone, ChromaDB, Qdrant, etc.) without changing application code.

    Design Pattern: Strategy Pattern
    SOLID Principle: Dependency Inversion (depend on abstraction, not concrete)
    """

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the vector database connection and create index/collection.

        Raises:
            VectorDatabaseError: If initialization fails
        """
        pass

    @abstractmethod
    async def upsert_vectors(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: List[Dict]
    ) -> int:
        """
        Insert or update vectors in the database.

        Args:
            ids: List of unique identifiers
            vectors: List of embedding vectors
            metadata: List of metadata dicts (must include 'content' field)

        Returns:
            Number of vectors successfully upserted

        Raises:
            VectorDatabaseError: If upsert fails

        Note:
            All lists must have the same length
        """
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[VectorSearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter (e.g., {"course_code": "CS101"})

        Returns:
            List of search results ordered by similarity (highest first)

        Raises:
            VectorDatabaseError: If search fails
        """
        pass

    @abstractmethod
    async def delete_by_id(self, ids: List[str]) -> int:
        """
        Delete vectors by their IDs.

        Args:
            ids: List of vector IDs to delete

        Returns:
            Number of vectors deleted

        Raises:
            VectorDatabaseError: If deletion fails
        """
        pass

    @abstractmethod
    async def delete_by_filter(self, filter: Dict) -> int:
        """
        Delete vectors matching a metadata filter.

        Args:
            filter: Metadata filter (e.g., {"course_code": "CS101"})

        Returns:
            Number of vectors deleted

        Raises:
            VectorDatabaseError: If deletion fails
        """
        pass

    @abstractmethod
    async def get_stats(self) -> Dict:
        """
        Get statistics about the vector database.

        Returns:
            Dict with stats like total_vectors, dimension, etc.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the database is accessible and healthy.

        Returns:
            True if healthy, False otherwise
        """
        pass


class VectorDatabaseError(Exception):
    """Base exception for vector database operations."""
    pass


class VectorDatabaseConnectionError(VectorDatabaseError):
    """Raised when connection to vector database fails."""
    pass


class VectorDatabaseOperationError(VectorDatabaseError):
    """Raised when a vector database operation fails."""
    pass
