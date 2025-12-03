"""
Embedding generation service using Mistral AI.
Generates vector embeddings for semantic search.
"""
import httpx
from typing import List, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResponse:
    """Embedding response."""
    embedding: List[float]
    tokens_used: int
    dimension: int


class EmbeddingServiceError(Exception):
    """Embedding service errors."""
    pass


class EmbeddingService:
    """
    Service for generating embeddings using Mistral AI.

    Uses Mistral's embedding models for semantic search.
    """

    EMBEDDING_MODEL = "mistral-embed"  # Mistral's embedding model
    EMBEDDING_API_URL = "https://api.mistral.ai/v1/embeddings"

    def __init__(self, api_key: str):
        """
        Initialize embedding service.

        Args:
            api_key: Mistral API key
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def generate_embedding(self, text: str) -> EmbeddingResponse:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding response with vector

        Example:
            embedding = await service.generate_embedding(
                "Large language models are transforming AI research."
            )
            vector = embedding.embedding  # Use this for vector DB
        """
        try:
            # Truncate text if too long (Mistral has token limits)
            truncated_text = text[:8000]  # Roughly 2000 tokens

            payload = {
                "model": self.EMBEDDING_MODEL,
                "input": [truncated_text]
            }

            response = await self.client.post(
                self.EMBEDDING_API_URL,
                json=payload
            )
            response.raise_for_status()

            data = response.json()

            # Extract embedding from response
            embedding_data = data["data"][0]
            embedding_vector = embedding_data["embedding"]

            return EmbeddingResponse(
                embedding=embedding_vector,
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                dimension=len(embedding_vector)
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Mistral API error: {e.response.status_code}")
            raise EmbeddingServiceError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingServiceError(f"Failed to generate embedding: {e}")

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 10
    ) -> List[EmbeddingResponse]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch (to avoid rate limits)

        Returns:
            List of embedding responses

        Note:
            Processes in batches to respect API rate limits.
        """
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                payload = {
                    "model": self.EMBEDDING_MODEL,
                    "input": [text[:8000] for text in batch]
                }

                response = await self.client.post(
                    self.EMBEDDING_API_URL,
                    json=payload
                )
                response.raise_for_status()

                data = response.json()

                for item in data["data"]:
                    embeddings.append(EmbeddingResponse(
                        embedding=item["embedding"],
                        tokens_used=data.get("usage", {}).get("total_tokens", 0) // len(batch),
                        dimension=len(item["embedding"])
                    ))

                logger.info(f"Generated embeddings for batch {i // batch_size + 1}")

            except Exception as e:
                logger.error(f"Batch embedding failed: {e}")
                # Continue with next batch instead of failing completely
                continue

        return embeddings

    async def embed_paper(
        self,
        title: str,
        abstract: str
    ) -> Optional[EmbeddingResponse]:
        """
        Generate embedding for an academic paper.

        Combines title and abstract for better semantic representation.

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Embedding response or None if failed
        """
        try:
            # Combine title and abstract with emphasis on title
            combined_text = f"Title: {title}\n\nAbstract: {abstract}"

            return await self.generate_embedding(combined_text)

        except Exception as e:
            logger.error(f"Failed to embed paper: {e}")
            return None

    async def embed_query(self, query: str) -> Optional[List[float]]:
        """
        Generate embedding for a search query.

        Args:
            query: User search query

        Returns:
            Embedding vector or None if failed
        """
        try:
            result = await self.generate_embedding(query)
            return result.embedding
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Alternative: Using OpenAI embeddings (if preferred)
class OpenAIEmbeddingService:
    """
    Alternative embedding service using OpenAI.

    More expensive but potentially higher quality for academic text.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding service.

        Args:
            api_key: OpenAI API key
            model: Embedding model (text-embedding-3-small or text-embedding-3-large)
        """
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def generate_embedding(self, text: str) -> EmbeddingResponse:
        """Generate embedding using OpenAI."""
        try:
            payload = {
                "model": self.model,
                "input": text[:8000]  # OpenAI token limit
            }

            response = await self.client.post(
                "https://api.openai.com/v1/embeddings",
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            embedding = data["data"][0]["embedding"]

            return EmbeddingResponse(
                embedding=embedding,
                tokens_used=data["usage"]["total_tokens"],
                dimension=len(embedding)
            )

        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise EmbeddingServiceError(f"Failed to generate embedding: {e}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
