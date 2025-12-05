"""
File ingestion service - processes uploaded files for RAG and chat context.

Design Pattern: Facade Pattern + Strategy Pattern
Purpose: Unified interface for file processing pipeline
"""
from typing import Optional, Dict
from dataclasses import dataclass
from pathlib import Path
import logging
import hashlib
from datetime import datetime

from .document_parser import DocumentParser, ParsedDocument, DocumentParseError
from .text_chunker import TextChunker
from .embedding_service import EmbeddingService
from .vector_db.base import VectorDatabaseInterface

logger = logging.getLogger(__name__)


@dataclass
class FileIngestionResult:
    """
    Result of ingesting a single file.

    Attributes:
        success: Whether ingestion succeeded
        file_id: Unique identifier for the file
        filename: Original filename
        chunks_created: Number of chunks created
        chunks_uploaded: Number of chunks uploaded to vector DB
        metadata: File metadata extracted
        error: Error message if failed
    """
    success: bool
    file_id: str
    filename: str
    chunks_created: int = 0
    chunks_uploaded: int = 0
    metadata: Optional[Dict] = None
    error: Optional[str] = None


class FileIngestionService:
    """
    Orchestrates file ingestion pipeline for uploaded files.

    Pipeline:
        1. Parse document (PDF, DOCX, TXT, MD)
        2. Extract metadata
        3. Chunk text into semantically meaningful pieces
        4. Generate embeddings for each chunk
        5. Upload chunks + embeddings to vector database
        6. Track file metadata for conversation association

    Design Pattern: Facade Pattern
    Purpose: Simplify complex multi-step process into single interface

    Usage:
        service = FileIngestionService(
            vector_db=pinecone_adapter,
            embedding_service=mistral_embeddings,
            parser=doc_parser,
            chunker=text_chunker
        )

        result = await service.ingest_file(
            file_path="upload.pdf",
            original_filename="syllabus.pdf",
            conversation_id="conv-123"
        )
    """

    def __init__(
        self,
        vector_db: VectorDatabaseInterface,
        embedding_service: EmbeddingService,
        parser: DocumentParser = None,
        chunker: TextChunker = None
    ):
        """
        Initialize file ingestion service.

        Args:
            vector_db: Vector database adapter
            embedding_service: Embedding generation service
            parser: Document parser (default: DocumentParser())
            chunker: Text chunker (default: TextChunker with fixed_size strategy)
        """
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.parser = parser or DocumentParser()
        self.chunker = chunker or TextChunker(
            strategy='fixed_size',
            chunk_size=500,
            overlap=50
        )

        logger.info("FileIngestionService initialized")

    async def ingest_file(
        self,
        file_path: str,
        original_filename: str,
        conversation_id: Optional[str] = None,
        additional_metadata: Optional[Dict] = None
    ) -> FileIngestionResult:
        """
        Ingest an uploaded file.

        Args:
            file_path: Path to the temporary file
            original_filename: Original filename from upload
            conversation_id: Optional conversation ID to associate file with
            additional_metadata: Additional metadata to attach

        Returns:
            FileIngestionResult with processing details

        Example:
            result = await service.ingest_file(
                file_path="/tmp/upload123.pdf",
                original_filename="research_paper.pdf",
                conversation_id="conv-456"
            )
        """
        file_id = self._generate_file_id(original_filename, conversation_id)

        try:
            # Step 1: Parse document
            logger.info(f"[{file_id}] Parsing file: {original_filename}")
            parsed_doc = self.parser.parse(file_path)

            # Step 2: Build metadata
            metadata = {
                'file_id': file_id,
                'filename': original_filename,
                'file_type': parsed_doc.file_type,
                'uploaded_at': datetime.utcnow().isoformat(),
                'conversation_id': conversation_id,
                **parsed_doc.metadata,
                **(additional_metadata or {})
            }

            # Step 3: Chunk text
            logger.info(
                f"[{file_id}] Chunking text ({len(parsed_doc.content)} chars)"
            )
            chunks = self.chunker.chunk_with_metadata_per_chunk(
                text=parsed_doc.content,
                base_metadata=metadata,
                document_id=file_id
            )

            if not chunks:
                raise Exception("No chunks created from document")

            logger.info(f"[{file_id}] Created {len(chunks)} chunks")

            # Step 4: Generate embeddings
            logger.info(
                f"[{file_id}] Generating embeddings for {len(chunks)} chunks"
            )
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.generate_embeddings_batch(
                texts=chunk_texts,
                batch_size=10
            )

            if len(embeddings) != len(chunks):
                raise Exception(
                    f"Embedding count mismatch: {len(embeddings)} != {len(chunks)}"
                )

            # Step 5: Upload to vector database
            logger.info(f"[{file_id}] Uploading to vector database")
            chunk_ids = [f"{file_id}_chunk_{chunk.index}" for chunk in chunks]
            vectors = [emb.embedding for emb in embeddings]

            # Prepare metadata for vector DB
            # Each chunk's metadata includes the actual text content
            chunk_metadata = []
            for chunk in chunks:
                meta = chunk.metadata.copy()
                meta['content'] = chunk.content  # Store content in metadata
                meta['file_id'] = file_id  # Ensure file_id is in metadata
                chunk_metadata.append(meta)

            chunks_uploaded = await self.vector_db.upsert_vectors(
                ids=chunk_ids,
                vectors=vectors,
                metadata=chunk_metadata
            )

            logger.info(f"[{file_id}] Successfully ingested file")

            return FileIngestionResult(
                success=True,
                file_id=file_id,
                filename=original_filename,
                chunks_created=len(chunks),
                chunks_uploaded=chunks_uploaded,
                metadata=metadata
            )

        except DocumentParseError as e:
            logger.error(f"[{file_id}] Failed to parse document: {e}")
            return FileIngestionResult(
                success=False,
                file_id=file_id,
                filename=original_filename,
                error=f"Parse error: {str(e)}"
            )

        except Exception as e:
            logger.error(f"[{file_id}] Ingestion failed: {e}", exc_info=True)
            return FileIngestionResult(
                success=False,
                file_id=file_id,
                filename=original_filename,
                error=str(e)
            )

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete all chunks from an uploaded file.

        Args:
            file_id: ID of the file to delete

        Returns:
            True if deletion succeeded
        """
        try:
            # Delete by filter (all chunks with this file_id)
            await self.vector_db.delete_by_filter({
                'file_id': file_id
            })

            logger.info(f"Deleted file: {file_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {e}")
            return False

    def _generate_file_id(
        self,
        filename: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Generate a unique file ID from filename and timestamp.

        Uses hash of filename + timestamp + conversation_id for uniqueness.
        """
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{filename}_{timestamp}_{conversation_id or ''}"
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()[:12]

        # Clean filename for ID
        path = Path(filename)
        clean_name = path.stem.replace(' ', '_').replace('-', '_')

        return f"file_{clean_name}_{hash_digest}"
