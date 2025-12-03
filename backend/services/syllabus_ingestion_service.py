"""
Syllabus ingestion service - orchestrates the document processing pipeline.
Takes PDFs from disk, processes them, and uploads to vector database.
"""
from typing import List, Optional, Dict
from dataclasses import dataclass
from pathlib import Path
import logging
import asyncio
from tqdm import tqdm

from .document_parser import DocumentParser, ParsedDocument, DocumentParseError
from .text_chunker import TextChunker, TextChunk
from .embedding_service import EmbeddingService
from .vector_db.base import VectorDatabaseInterface

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """
    Result of ingesting a single document.

    Attributes:
        success: Whether ingestion succeeded
        document_id: Unique identifier for the document
        file_path: Path to the source file
        chunks_created: Number of chunks created
        chunks_uploaded: Number of chunks uploaded to vector DB
        metadata: Document metadata extracted
        error: Error message if failed
    """
    success: bool
    document_id: str
    file_path: str
    chunks_created: int = 0
    chunks_uploaded: int = 0
    metadata: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class BatchIngestionResult:
    """
    Result of batch ingestion operation.

    Attributes:
        total_files: Total number of files processed
        successful: Number of files successfully ingested
        failed: Number of files that failed
        total_chunks: Total chunks created
        results: Individual results for each file
    """
    total_files: int
    successful: int
    failed: int
    total_chunks: int
    results: List[IngestionResult]


class SyllabusIngestionService:
    """
    Orchestrates the syllabus ingestion pipeline.

    Pipeline:
        1. Parse document (PDF, DOCX, TXT)
        2. Extract metadata (course code, instructor, etc.)
        3. Chunk text into semantically meaningful pieces
        4. Generate embeddings for each chunk
        5. Upload chunks + embeddings to vector database

    Design Pattern: Facade Pattern
    Purpose: Simplify complex multi-step process into single interface

    Usage:
        service = SyllabusIngestionService(
            vector_db=pinecone_adapter,
            embedding_service=mistral_embeddings,
            parser=doc_parser,
            chunker=text_chunker
        )

        result = await service.ingest_file("syllabus.pdf")
        print(f"Created {result.chunks_created} chunks")
    """

    def __init__(
        self,
        vector_db: VectorDatabaseInterface,
        embedding_service: EmbeddingService,
        parser: DocumentParser = None,
        chunker: TextChunker = None
    ):
        """
        Initialize ingestion service.

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

        logger.info("SyllabusIngestionService initialized")

    async def ingest_file(
        self,
        file_path: str,
        additional_metadata: Optional[Dict] = None
    ) -> IngestionResult:
        """
        Ingest a single syllabus file.

        Args:
            file_path: Path to the syllabus file
            additional_metadata: Additional metadata to attach (course_code, etc.)

        Returns:
            IngestionResult with processing details

        Example:
            result = await service.ingest_file(
                "CS101_Fall2024.pdf",
                additional_metadata={"semester": "Fall 2024"}
            )
        """
        document_id = self._generate_document_id(file_path)

        try:
            # Step 1: Parse document
            logger.info(f"[{document_id}] Parsing document: {file_path}")
            parsed_doc = self.parser.parse(file_path)

            # Step 2: Merge metadata
            metadata = {
                **parsed_doc.metadata,
                **(additional_metadata or {})
            }

            # Step 3: Chunk text
            logger.info(f"[{document_id}] Chunking text ({len(parsed_doc.content)} chars)")
            chunks = self.chunker.chunk_with_metadata_per_chunk(
                text=parsed_doc.content,
                base_metadata=metadata,
                document_id=document_id
            )

            if not chunks:
                raise Exception("No chunks created from document")

            logger.info(f"[{document_id}] Created {len(chunks)} chunks")

            # Step 4: Generate embeddings
            logger.info(f"[{document_id}] Generating embeddings for {len(chunks)} chunks")
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
            logger.info(f"[{document_id}] Uploading to vector database")
            chunk_ids = [f"{document_id}_chunk_{chunk.index}" for chunk in chunks]
            vectors = [emb.embedding for emb in embeddings]

            # Prepare metadata for vector DB
            # Each chunk's metadata includes the actual text content
            chunk_metadata = []
            for chunk in chunks:
                meta = chunk.metadata.copy()
                meta['content'] = chunk.content  # Store content in metadata
                chunk_metadata.append(meta)

            chunks_uploaded = await self.vector_db.upsert_vectors(
                ids=chunk_ids,
                vectors=vectors,
                metadata=chunk_metadata
            )

            logger.info(f"[{document_id}] Successfully ingested document")

            return IngestionResult(
                success=True,
                document_id=document_id,
                file_path=file_path,
                chunks_created=len(chunks),
                chunks_uploaded=chunks_uploaded,
                metadata=metadata
            )

        except DocumentParseError as e:
            logger.error(f"[{document_id}] Failed to parse document: {e}")
            return IngestionResult(
                success=False,
                document_id=document_id,
                file_path=file_path,
                error=f"Parse error: {str(e)}"
            )

        except Exception as e:
            logger.error(f"[{document_id}] Ingestion failed: {e}", exc_info=True)
            return IngestionResult(
                success=False,
                document_id=document_id,
                file_path=file_path,
                error=str(e)
            )

    async def ingest_directory(
        self,
        directory_path: str,
        file_extensions: Optional[List[str]] = None,
        recursive: bool = False,
        show_progress: bool = True
    ) -> BatchIngestionResult:
        """
        Ingest all syllabus files in a directory.

        Args:
            directory_path: Path to directory containing syllabi
            file_extensions: List of extensions to process (default: ['.pdf', '.docx', '.txt'])
            recursive: Whether to search subdirectories
            show_progress: Whether to show progress bar

        Returns:
            BatchIngestionResult with summary

        Example:
            result = await service.ingest_directory(
                "~/Desktop/syllabi/",
                file_extensions=['.pdf'],
                recursive=True
            )
            print(f"Processed {result.successful}/{result.total_files} files")
        """
        # Default file extensions
        if file_extensions is None:
            file_extensions = ['.pdf', '.docx', '.txt', '.md']

        # Find all files
        directory = Path(directory_path).expanduser()
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        files = []
        if recursive:
            for ext in file_extensions:
                files.extend(directory.rglob(f"*{ext}"))
        else:
            for ext in file_extensions:
                files.extend(directory.glob(f"*{ext}"))

        files = [str(f) for f in files]

        logger.info(f"Found {len(files)} files to process in {directory_path}")

        if not files:
            return BatchIngestionResult(
                total_files=0,
                successful=0,
                failed=0,
                total_chunks=0,
                results=[]
            )

        # Process files with progress bar
        results = []
        total_chunks = 0

        iterator = tqdm(files, desc="Ingesting syllabi") if show_progress else files

        for file_path in iterator:
            result = await self.ingest_file(file_path)
            results.append(result)

            if result.success:
                total_chunks += result.chunks_created

        # Calculate summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        batch_result = BatchIngestionResult(
            total_files=len(files),
            successful=successful,
            failed=failed,
            total_chunks=total_chunks,
            results=results
        )

        logger.info(
            f"Batch ingestion complete: {successful}/{len(files)} succeeded, "
            f"{total_chunks} total chunks"
        )

        return batch_result

    async def delete_document(
        self,
        document_id: str
    ) -> bool:
        """
        Delete all chunks from a document.

        Args:
            document_id: ID of the document to delete

        Returns:
            True if deletion succeeded
        """
        try:
            # Delete by filter (all chunks with this document_id)
            await self.vector_db.delete_by_filter({
                'document_id': document_id
            })

            logger.info(f"Deleted document: {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    def _generate_document_id(self, file_path: str) -> str:
        """
        Generate a unique document ID from file path.

        Uses filename without extension as base ID.
        """
        path = Path(file_path)
        # Use filename without extension
        doc_id = path.stem

        # Clean ID (remove special characters)
        doc_id = doc_id.replace(' ', '_').replace('-', '_')

        return doc_id
