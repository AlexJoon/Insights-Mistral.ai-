#!/usr/bin/env python3
"""
Bulk upload script for ingesting syllabi PDFs into Pinecone.

Usage:
    python upload_syllabi.py /path/to/syllabi/folder/
    python upload_syllabi.py /path/to/syllabi/folder/ --recursive
    python upload_syllabi.py single_file.pdf
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_db.factory import VectorDatabaseFactory
from backend.services.embedding_service import EmbeddingService
from backend.services.document_parser import DocumentParser
from backend.services.text_chunker import TextChunker
from backend.services.syllabus_ingestion_service import SyllabusIngestionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for bulk upload script."""
    parser = argparse.ArgumentParser(
        description='Bulk upload syllabi to Pinecone vector database'
    )
    parser.add_argument(
        'path',
        help='Path to syllabus file or directory'
    )
    parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        help='Search subdirectories recursively'
    )
    parser.add_argument(
        '--api-key',
        help='Pinecone API key (or set PINECONE_API_KEY env var)'
    )
    parser.add_argument(
        '--index-name',
        default='syllabi',
        help='Pinecone index name (default: syllabi)'
    )
    parser.add_argument(
        '--mistral-api-key',
        help='Mistral API key for embeddings (or set MISTRAL_API_KEY env var)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='Chunk size in characters (default: 500)'
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=50,
        help='Chunk overlap in characters (default: 50)'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.pdf', '.docx', '.txt', '.md'],
        help='File extensions to process (default: .pdf .docx .txt .md)'
    )

    args = parser.parse_args()

    # Get API keys from args or environment
    import os
    pinecone_api_key = args.api_key or os.getenv('PINECONE_API_KEY')
    mistral_api_key = args.mistral_api_key or os.getenv('MISTRAL_API_KEY')

    if not pinecone_api_key:
        logger.error("Pinecone API key required. Set PINECONE_API_KEY env var or use --api-key")
        sys.exit(1)

    if not mistral_api_key:
        logger.error("Mistral API key required. Set MISTRAL_API_KEY env var or use --mistral-api-key")
        sys.exit(1)

    try:
        # Initialize services
        logger.info("Initializing services...")

        # 1. Vector database (Pinecone)
        vector_db = VectorDatabaseFactory.create(
            'pinecone',
            {
                'api_key': pinecone_api_key,
                'index_name': args.index_name,
                'dimension': 1024,  # Mistral embedding dimension
                'metric': 'cosine'
            }
        )
        await vector_db.initialize()

        # Check health
        health = await vector_db.health_check()
        if not health:
            logger.error("Pinecone connection failed")
            sys.exit(1)

        logger.info(f"✓ Connected to Pinecone index: {args.index_name}")

        # 2. Embedding service (Mistral)
        embedding_service = EmbeddingService(api_key=mistral_api_key)
        logger.info("✓ Mistral embedding service initialized")

        # 3. Document parser
        parser_service = DocumentParser()
        logger.info("✓ Document parser initialized")

        # 4. Text chunker
        chunker = TextChunker(
            strategy='fixed_size',
            chunk_size=args.chunk_size,
            overlap=args.chunk_overlap
        )
        logger.info(f"✓ Text chunker initialized (size={args.chunk_size}, overlap={args.chunk_overlap})")

        # 5. Ingestion service (orchestrator)
        ingestion_service = SyllabusIngestionService(
            vector_db=vector_db,
            embedding_service=embedding_service,
            parser=parser_service,
            chunker=chunker
        )

        # Process files
        path = Path(args.path).expanduser()

        if path.is_file():
            # Single file upload
            logger.info(f"\nUploading single file: {path}")
            result = await ingestion_service.ingest_file(str(path))

            if result.success:
                logger.info(f"✓ Success! Created {result.chunks_created} chunks")
                logger.info(f"  Document ID: {result.document_id}")
                logger.info(f"  Metadata: {result.metadata}")
            else:
                logger.error(f"✗ Failed: {result.error}")
                sys.exit(1)

        elif path.is_dir():
            # Directory upload
            logger.info(f"\nUploading directory: {path}")
            logger.info(f"Recursive: {args.recursive}")
            logger.info(f"Extensions: {', '.join(args.extensions)}\n")

            result = await ingestion_service.ingest_directory(
                directory_path=str(path),
                file_extensions=args.extensions,
                recursive=args.recursive,
                show_progress=True
            )

            # Print summary
            print("\n" + "=" * 60)
            print("UPLOAD SUMMARY")
            print("=" * 60)
            print(f"Total files:       {result.total_files}")
            print(f"Successful:        {result.successful}")
            print(f"Failed:            {result.failed}")
            print(f"Total chunks:      {result.total_chunks}")
            print("=" * 60)

            # Print failures if any
            if result.failed > 0:
                print("\nFailed files:")
                for r in result.results:
                    if not r.success:
                        print(f"  ✗ {r.file_path}")
                        print(f"    Error: {r.error}")

            # Get vector DB stats
            stats = await vector_db.get_stats()
            print(f"\nPinecone index stats:")
            print(f"  Total vectors: {stats.get('total_vectors', 'N/A')}")
            print(f"  Dimension: {stats.get('dimension', 'N/A')}")

        else:
            logger.error(f"Path does not exist: {path}")
            sys.exit(1)

        logger.info("\n✓ Upload complete!")

    except KeyboardInterrupt:
        logger.info("\n\nUpload interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"\n✗ Upload failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
