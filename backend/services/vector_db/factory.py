"""
Factory for creating vector database instances.
Implements Factory Pattern for dependency injection and easy swapping.
"""
from typing import Dict, Optional
import logging
from .base import VectorDatabaseInterface
from .pinecone_adapter import PineconeAdapter

logger = logging.getLogger(__name__)


class VectorDatabaseFactory:
    """
    Factory for creating vector database instances.

    Design Pattern: Factory Pattern
    Purpose: Decouple creation logic from business logic
    Benefit: Easy to swap vector databases without changing application code

    Usage:
        config = {
            "api_key": "your-pinecone-key",
            "index_name": "syllabi"
        }
        db = VectorDatabaseFactory.create("pinecone", config)
        await db.initialize()
    """

    _supported_providers = {
        "pinecone": PineconeAdapter,
        # Future: Add more providers
        # "chromadb": ChromaDBAdapter,
        # "qdrant": QdrantAdapter,
        # "weaviate": WeaviateAdapter,
    }

    @classmethod
    def create(
        cls,
        provider: str,
        config: Dict
    ) -> VectorDatabaseInterface:
        """
        Create a vector database instance.

        Args:
            provider: Name of the vector database provider
                     ('pinecone', 'chromadb', 'qdrant')
            config: Provider-specific configuration dict

        Returns:
            VectorDatabaseInterface instance

        Raises:
            ValueError: If provider is not supported

        Example:
            # Pinecone
            db = VectorDatabaseFactory.create("pinecone", {
                "api_key": "pk_xxx",
                "index_name": "syllabi",
                "dimension": 1024
            })

            # ChromaDB (future)
            db = VectorDatabaseFactory.create("chromadb", {
                "persist_directory": "./chroma_db"
            })
        """
        provider_lower = provider.lower()

        if provider_lower not in cls._supported_providers:
            supported = ", ".join(cls._supported_providers.keys())
            raise ValueError(
                f"Unsupported vector database provider: {provider}. "
                f"Supported providers: {supported}"
            )

        adapter_class = cls._supported_providers[provider_lower]

        logger.info(f"Creating {provider} vector database adapter")

        return adapter_class(**config)

    @classmethod
    def create_from_env(cls, provider: str) -> VectorDatabaseInterface:
        """
        Create a vector database instance from environment variables.

        Args:
            provider: Name of the vector database provider

        Returns:
            VectorDatabaseInterface instance

        Raises:
            ValueError: If required environment variables are missing

        Note:
            This method is useful for production deployment where
            configuration is stored in environment variables.
        """
        import os

        if provider.lower() == "pinecone":
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY environment variable is required")

            config = {
                "api_key": api_key,
                "index_name": os.getenv("PINECONE_INDEX_NAME", "syllabi"),
                "dimension": int(os.getenv("PINECONE_DIMENSION", "1024")),
                "metric": os.getenv("PINECONE_METRIC", "cosine"),
                "cloud": os.getenv("PINECONE_CLOUD", "aws"),
                "region": os.getenv("PINECONE_REGION", "us-east-1")
            }

            return cls.create("pinecone", config)

        # Add more providers as needed
        raise ValueError(f"Environment-based config not implemented for: {provider}")

    @classmethod
    def list_supported_providers(cls) -> list:
        """
        Get list of supported vector database providers.

        Returns:
            List of provider names
        """
        return list(cls._supported_providers.keys())
