"""
File upload API routes.
Handles file uploads for RAG ingestion and chat context.

Design Pattern: Controller Pattern
Purpose: Separate routing logic from business logic
"""
from typing import Optional
import logging
import tempfile
import os
from pathlib import Path
from datetime import datetime

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import UploadFile

from backend.services.file_ingestion_service import FileIngestionService

logger = logging.getLogger(__name__)


class FileRoutes:
    """
    File upload route handlers.

    Responsibilities:
    - Accept file uploads via multipart/form-data
    - Validate file types and sizes
    - Coordinate with FileIngestionService for processing
    - Track file metadata
    """

    def __init__(self, ingestion_service: FileIngestionService):
        """
        Initialize file routes.

        Args:
            ingestion_service: Service for processing and ingesting files
        """
        self.ingestion_service = ingestion_service
        self.uploaded_files = {}  # In-memory store for file metadata
        logger.info("FileRoutes initialized")

    async def upload_file(self, request: Request) -> JSONResponse:
        """
        Handle file upload.

        Accepts: multipart/form-data with 'file' field
        Optional: conversation_id field

        Returns:
            JSON response with file metadata and ingestion results
        """
        try:
            # Parse multipart form data
            form = await request.form()
            file: UploadFile = form.get('file')
            conversation_id: Optional[str] = form.get('conversation_id')

            if not file:
                return JSONResponse(
                    {'success': False, 'error': 'No file provided'},
                    status_code=400
                )

            # Validate file
            filename = file.filename
            if not filename:
                return JSONResponse(
                    {'success': False, 'error': 'Invalid filename'},
                    status_code=400
                )

            # Check file extension
            file_extension = Path(filename).suffix.lower()
            allowed_extensions = {'.pdf', '.docx', '.txt', '.md'}
            if file_extension not in allowed_extensions:
                return JSONResponse(
                    {
                        'success': False,
                        'error': f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}'
                    },
                    status_code=400
                )

            logger.info(f"Receiving file upload: {filename} ({file_extension})")

            # Read file content
            file_content = await file.read()
            file_size = len(file_content)

            # Validate file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                return JSONResponse(
                    {
                        'success': False,
                        'error': f'File too large. Maximum size: 10MB'
                    },
                    status_code=400
                )

            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(
                mode='wb',
                suffix=file_extension,
                delete=False
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                # Process file through ingestion service
                logger.info(f"Processing file: {filename}")
                result = await self.ingestion_service.ingest_file(
                    file_path=temp_file_path,
                    original_filename=filename,
                    conversation_id=conversation_id
                )

                # Store file metadata
                file_id = result.file_id
                self.uploaded_files[file_id] = {
                    'file_id': file_id,
                    'filename': filename,
                    'file_type': file_extension[1:],  # Remove dot
                    'file_size': file_size,
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'conversation_id': conversation_id,
                    'chunks_created': result.chunks_created
                }

                logger.info(
                    f"File processed successfully: {filename} "
                    f"({result.chunks_created} chunks created)"
                )

                return JSONResponse({
                    'success': True,
                    'file_id': file_id,
                    'filename': filename,
                    'file_type': file_extension[1:],
                    'file_size': file_size,
                    'chunks_created': result.chunks_created,
                    'message': 'File uploaded and processed successfully'
                })

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

        except Exception as e:
            logger.error(f"File upload error: {e}", exc_info=True)
            return JSONResponse(
                {
                    'success': False,
                    'error': str(e)
                },
                status_code=500
            )

    async def get_conversation_files(self, request: Request) -> JSONResponse:
        """
        Get all files associated with a conversation.

        Path param: conversation_id

        Returns:
            JSON response with array of file metadata
        """
        try:
            conversation_id = request.path_params.get('conversation_id')

            if not conversation_id:
                return JSONResponse(
                    {'error': 'Conversation ID required'},
                    status_code=400
                )

            # Filter files by conversation ID
            files = [
                file_meta
                for file_meta in self.uploaded_files.values()
                if file_meta.get('conversation_id') == conversation_id
            ]

            return JSONResponse({
                'conversation_id': conversation_id,
                'files': files
            })

        except Exception as e:
            logger.error(f"Error fetching conversation files: {e}")
            return JSONResponse(
                {'error': str(e)},
                status_code=500
            )

    async def delete_file(self, request: Request) -> JSONResponse:
        """
        Delete an uploaded file and its vector embeddings.

        Path param: file_id

        Returns:
            JSON response with success status
        """
        try:
            file_id = request.path_params.get('file_id')

            if not file_id:
                return JSONResponse(
                    {'error': 'File ID required'},
                    status_code=400
                )

            # Delete from ingestion service (removes from vector DB)
            success = await self.ingestion_service.delete_file(file_id)

            if success:
                # Remove from metadata store
                self.uploaded_files.pop(file_id, None)

                logger.info(f"File deleted: {file_id}")
                return JSONResponse({
                    'success': True,
                    'message': 'File deleted successfully'
                })
            else:
                return JSONResponse(
                    {'success': False, 'error': 'File not found'},
                    status_code=404
                )

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return JSONResponse(
                {'success': False, 'error': str(e)},
                status_code=500
            )

    async def get_file_metadata(self, request: Request) -> JSONResponse:
        """
        Get metadata for a specific file.

        Path param: file_id

        Returns:
            JSON response with file metadata
        """
        try:
            file_id = request.path_params.get('file_id')

            if not file_id:
                return JSONResponse(
                    {'error': 'File ID required'},
                    status_code=400
                )

            file_meta = self.uploaded_files.get(file_id)

            if not file_meta:
                return JSONResponse(
                    {'error': 'File not found'},
                    status_code=404
                )

            return JSONResponse(file_meta)

        except Exception as e:
            logger.error(f"Error fetching file metadata: {e}")
            return JSONResponse(
                {'error': str(e)},
                status_code=500
            )
