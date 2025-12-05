"""
Pinecone vector database adapter.
Implements VectorDatabaseInterface for Pinecone cloud vector database.
"""
from typing import List, Dict, Optional
import logging
from pinecone import Pinecone, ServerlessSpec
from .base import (
    VectorDatabaseInterface,
    VectorSearchResult,
    VectorDatabaseError,
    VectorDatabaseConnectionError,
    VectorDatabaseOperationError
)

logger = logging.getLogger(__name__)


class PineconeAdapter(VectorDatabaseInterface):
    """
    Pinecone vector database adapter.

    Pinecone is a cloud-native vector database optimized for similarity search.
    Free tier supports up to 300K vectors, which is sufficient for ~500 syllabi.

    Configuration:
        - api_key: Pinecone API key
        - environment: Cloud region (e.g., 'us-east-1')
        - index_name: Name of the Pinecone index
        - dimension: Vector dimension (1024 for Mistral embeddings)
        - metric: Similarity metric ('cosine' recommended)
    """

    def __init__(
        self,
        api_key: str,
        index_name: str = "syllabi",
        dimension: int = 1024,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ):
        """
        Initialize Pinecone adapter.

        Args:
            api_key: Pinecone API key
            index_name: Name of the index to create/use
            dimension: Embedding dimension (must match your embedding model)
            metric: Distance metric ('cosine', 'euclidean', 'dotproduct')
            cloud: Cloud provider ('aws', 'gcp', 'azure')
            region: Cloud region
        """
        self.api_key = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.cloud = cloud
        self.region = region

        self.pc = None
        self.index = None

        logger.info(f"Initialized PineconeAdapter for index: {index_name}")

    async def initialize(self) -> None:
        """
        Initialize Pinecone connection and create index if it doesn't exist.

        This method:
        1. Connects to Pinecone
        2. Creates index if it doesn't exist (serverless, free tier)
        3. Connects to the index

        Raises:
            VectorDatabaseConnectionError: If connection fails
        """
        try:
            # Initialize Pinecone client
            self.pc = Pinecone(api_key=self.api_key)

            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]

            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")

                # Create serverless index (free tier)
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(
                        cloud=self.cloud,
                        region=self.region
                    )
                )

                logger.info(f"Index '{self.index_name}' created successfully")
            else:
                logger.info(f"Index '{self.index_name}' already exists")

            # Connect to index
            self.index = self.pc.Index(self.index_name)

            # Verify connection
            stats = self.index.describe_index_stats()
            logger.info(f"Connected to Pinecone index. Stats: {stats}")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise VectorDatabaseConnectionError(f"Pinecone initialization failed: {e}")

    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """
        Sanitize metadata for Pinecone compatibility.

        Pinecone requirements:
        - All values must be JSON-serializable (str, int, float, bool, list of primitives)
        - No nested dicts
        - No datetime objects
        - No null/None values
        - String values must be <40KB

        Args:
            metadata: Raw metadata dict

        Returns:
            Sanitized metadata dict
        """
        sanitized = {}
        for key, value in metadata.items():
            # Skip None values - Pinecone doesn't accept null
            if value is None:
                continue
            # Convert datetime to ISO string
            elif hasattr(value, 'isoformat'):
                sanitized[key] = value.isoformat()
            # Handle primitive types
            elif isinstance(value, (str, int, float, bool)):
                # Truncate long strings to avoid Pinecone limits
                if isinstance(value, str) and len(value) > 40000:
                    sanitized[key] = value[:40000]
                else:
                    sanitized[key] = value
            elif isinstance(value, list):
                # Only keep lists of primitives (no None values in list)
                if all(isinstance(v, (str, int, float, bool)) and v is not None for v in value):
                    sanitized[key] = value
                else:
                    sanitized[key] = str(value)
            else:
                # Convert complex objects to strings
                sanitized[key] = str(value)

        return sanitized

    async def upsert_vectors(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadata: List[Dict]
    ) -> int:
        """
        Upsert vectors into Pinecone.

        Args:
            ids: List of unique IDs
            vectors: List of embedding vectors
            metadata: List of metadata dicts (must include 'content' field)

        Returns:
            Number of vectors upserted

        Raises:
            VectorDatabaseOperationError: If upsert fails

        Note:
            Pinecone expects metadata with the actual text content.
            Each metadata dict should have a 'content' field.
        """
        try:
            if not self.index:
                raise VectorDatabaseError("Index not initialized. Call initialize() first.")

            if not (len(ids) == len(vectors) == len(metadata)):
                raise ValueError("ids, vectors, and metadata must have the same length")

            # Prepare vectors for Pinecone format
            # Pinecone expects: [(id, vector, metadata), ...]
            # Sanitize metadata to ensure Pinecone compatibility
            vectors_to_upsert = [
                (id, vector, self._sanitize_metadata(meta))
                for id, vector, meta in zip(ids, vectors, metadata)
            ]

            # Upsert in batches (Pinecone recommends batch size of 100-1000)
            batch_size = 100
            total_upserted = 0

            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                response = self.index.upsert(vectors=batch)
                total_upserted += response.upserted_count

                logger.debug(f"Upserted batch {i // batch_size + 1}: {len(batch)} vectors")

            logger.info(f"Successfully upserted {total_upserted} vectors to Pinecone")
            return total_upserted

        except Exception as e:
            logger.error(f"Failed to upsert vectors to Pinecone: {e}")
            raise VectorDatabaseOperationError(f"Upsert failed: {e}")

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict] = None
    ) -> List[VectorSearchResult]:
        """
        Search for similar vectors in Pinecone.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of VectorSearchResult objects

        Raises:
            VectorDatabaseOperationError: If search fails

        Example filter:
            {"course_code": "CS101"}
            {"instructor": "Dr. Smith", "semester": "Fall 2024"}
        """
        try:
            if not self.index:
                raise VectorDatabaseError("Index not initialized. Call initialize() first.")

            # Prepare query
            query_params = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": True
            }

            if filter:
                query_params["filter"] = filter

            # Execute search
            response = self.index.query(**query_params)

            # Convert to VectorSearchResult objects
            results = []
            for match in response.matches:
                # Extract content from metadata
                content = match.metadata.get("content", "")

                result = VectorSearchResult(
                    id=match.id,
                    content=content,
                    metadata=match.metadata,
                    similarity_score=match.score
                )
                results.append(result)

            logger.info(f"Found {len(results)} results for query")
            return results

        except Exception as e:
            logger.error(f"Failed to search Pinecone: {e}")
            raise VectorDatabaseOperationError(f"Search failed: {e}")

    async def delete_by_id(self, ids: List[str]) -> int:
        """
        Delete vectors by their IDs.

        Args:
            ids: List of vector IDs to delete

        Returns:
            Number of vectors deleted

        Raises:
            VectorDatabaseOperationError: If deletion fails
        """
        try:
            if not self.index:
                raise VectorDatabaseError("Index not initialized. Call initialize() first.")

            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors from Pinecone")
            return len(ids)

        except Exception as e:
            logger.error(f"Failed to delete vectors from Pinecone: {e}")
            raise VectorDatabaseOperationError(f"Deletion failed: {e}")

    async def delete_by_filter(self, filter: Dict) -> int:
        """
        Delete vectors matching a metadata filter.

        Args:
            filter: Metadata filter (e.g., {"course_code": "CS101"})

        Returns:
            Number of vectors deleted (always returns 0 as Pinecone doesn't report count)

        Raises:
            VectorDatabaseOperationError: If deletion fails

        Note:
            Pinecone filter-based deletion doesn't return the count of deleted vectors.
        """
        try:
            if not self.index:
                raise VectorDatabaseError("Index not initialized. Call initialize() first.")

            self.index.delete(filter=filter)
            logger.info(f"Deleted vectors matching filter: {filter}")
            return 0  # Pinecone doesn't return deletion count for filter-based deletes

        except Exception as e:
            logger.error(f"Failed to delete vectors from Pinecone: {e}")
            raise VectorDatabaseOperationError(f"Deletion failed: {e}")

    async def get_stats(self) -> Dict:
        """
        Get Pinecone index statistics.

        Returns:
            Dict with index statistics
        """
        try:
            if not self.index:
                raise VectorDatabaseError("Index not initialized. Call initialize() first.")

            stats = self.index.describe_index_stats()

            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }

        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {"error": str(e)}

    async def health_check(self) -> bool:
        """
        Check if Pinecone is accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self.index:
                return False

            # Try to get index stats as a health check
            self.index.describe_index_stats()
            return True

        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False
