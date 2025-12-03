"""
Vector database service for semantic search over academic papers.
Supports ChromaDB (local) and Pinecone (cloud).
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Vector search result."""
    paper_id: str
    title: str
    abstract: str
    similarity_score: float
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "abstract": self.abstract,
            "similarity_score": self.similarity_score,
            "metadata": self.metadata
        }


class VectorServiceError(Exception):
    """Vector service errors."""
    pass


class VectorService:
    """
    Vector database service for storing and searching paper embeddings.

    Uses ChromaDB for local development and can be swapped for Pinecone
    in production.
    """

    def __init__(
        self,
        collection_name: str = "research_papers",
        persist_directory: str = "./chroma_db"
    ):
        """
        Initialize vector database.

        Args:
            collection_name: Name of the collection
            persist_directory: Local storage directory for ChromaDB
        """
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.Client(
                Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_directory
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Academic research papers"}
            )

            logger.info(f"Initialized vector DB collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize vector DB: {e}")
            raise VectorServiceError(f"Initialization failed: {e}")

    async def add_paper(
        self,
        paper_id: str,
        title: str,
        abstract: str,
        embedding: List[float],
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a paper to the vector database.

        Args:
            paper_id: Unique paper identifier
            title: Paper title
            abstract: Paper abstract
            embedding: Vector embedding of the paper
            metadata: Additional metadata (authors, year, venue, etc.)
        """
        try:
            # Prepare document text (title + abstract for better search)
            document_text = f"{title}\n\n{abstract}"

            # Prepare metadata
            paper_metadata = metadata or {}
            paper_metadata.update({
                "title": title,
                "paper_id": paper_id
            })

            # Add to collection
            self.collection.add(
                ids=[paper_id],
                embeddings=[embedding],
                documents=[document_text],
                metadatas=[paper_metadata]
            )

            logger.info(f"Added paper to vector DB: {paper_id}")

        except Exception as e:
            logger.error(f"Failed to add paper {paper_id}: {e}")
            raise VectorServiceError(f"Failed to add paper: {e}")

    async def add_papers_batch(
        self,
        papers: List[Dict]
    ) -> int:
        """
        Add multiple papers in batch for better performance.

        Args:
            papers: List of paper dicts with keys: paper_id, title, abstract, embedding, metadata

        Returns:
            Number of papers added
        """
        try:
            ids = [p["paper_id"] for p in papers]
            embeddings = [p["embedding"] for p in papers]
            documents = [
                f"{p['title']}\n\n{p['abstract']}"
                for p in papers
            ]
            metadatas = []

            for p in papers:
                meta = p.get("metadata", {})
                meta.update({
                    "title": p["title"],
                    "paper_id": p["paper_id"]
                })
                metadatas.append(meta)

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(f"Added {len(papers)} papers to vector DB")
            return len(papers)

        except Exception as e:
            logger.error(f"Batch add failed: {e}")
            raise VectorServiceError(f"Batch add failed: {e}")

    async def search_papers(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Search for similar papers using vector similarity.

        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            where: Optional metadata filter (e.g., {"year": "2023"})

        Returns:
            List of search results with similarity scores

        Example:
            results = await vector_service.search_papers(
                query_embedding=embedding,
                n_results=10,
                where={"fields_of_study": "Computer Science"}
            )
        """
        try:
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }

            if where:
                query_params["where"] = where

            results = self.collection.query(**query_params)

            # Parse results
            search_results = []
            for i in range(len(results["ids"][0])):
                paper_id = results["ids"][0][i]
                document = results["documents"][0][i]
                distance = results["distances"][0][i]
                metadata = results["metadatas"][0][i]

                # Convert distance to similarity score (0-1, higher is better)
                similarity_score = 1.0 - min(distance, 1.0)

                # Extract title and abstract from document
                parts = document.split("\n\n", 1)
                title = parts[0] if len(parts) > 0 else ""
                abstract = parts[1] if len(parts) > 1 else ""

                search_results.append(SearchResult(
                    paper_id=paper_id,
                    title=title,
                    abstract=abstract,
                    similarity_score=similarity_score,
                    metadata=metadata
                ))

            logger.info(f"Found {len(search_results)} similar papers")
            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorServiceError(f"Search failed: {e}")

    async def get_paper(self, paper_id: str) -> Optional[SearchResult]:
        """
        Get a specific paper by ID.

        Args:
            paper_id: Paper identifier

        Returns:
            Search result or None if not found
        """
        try:
            results = self.collection.get(
                ids=[paper_id],
                include=["documents", "metadatas"]
            )

            if not results["ids"]:
                return None

            document = results["documents"][0]
            metadata = results["metadatas"][0]

            parts = document.split("\n\n", 1)
            title = parts[0] if len(parts) > 0 else ""
            abstract = parts[1] if len(parts) > 1 else ""

            return SearchResult(
                paper_id=paper_id,
                title=title,
                abstract=abstract,
                similarity_score=1.0,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Failed to get paper {paper_id}: {e}")
            return None

    async def delete_paper(self, paper_id: str) -> bool:
        """
        Delete a paper from the vector database.

        Args:
            paper_id: Paper identifier

        Returns:
            True if deleted, False otherwise
        """
        try:
            self.collection.delete(ids=[paper_id])
            logger.info(f"Deleted paper: {paper_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete paper {paper_id}: {e}")
            return False

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "total_papers": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def persist(self):
        """Persist the database to disk (ChromaDB only)."""
        try:
            self.client.persist()
            logger.info("Vector database persisted to disk")
        except Exception as e:
            logger.error(f"Failed to persist: {e}")
