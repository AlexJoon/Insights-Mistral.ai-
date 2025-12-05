"""
Voice API routes.
Handles voice transcription requests using Voxtral.

Design Pattern: Controller Pattern
Purpose: Separate routing logic from business logic
"""
import logging
import tempfile
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import UploadFile

from backend.services.voxtral_service import VoxtralService

logger = logging.getLogger(__name__)


class VoiceRoutes:
    """
    Voice transcription route handlers.

    Responsibilities:
    - Accept audio uploads via multipart/form-data
    - Validate audio file types
    - Coordinate with VoxtralService for transcription
    """

    def __init__(self, voxtral_service: VoxtralService):
        """
        Initialize voice routes.

        Args:
            voxtral_service: Service for Voxtral API integration
        """
        self.voxtral_service = voxtral_service
        logger.info("VoiceRoutes initialized")

    async def transcribe_audio(self, request: Request) -> JSONResponse:
        """
        Handle audio transcription request.

        Accepts: multipart/form-data with 'audio' field
        Optional: language field

        Returns:
            JSON response with transcribed text
        """
        try:
            # Parse multipart form data
            form = await request.form()
            audio_file: UploadFile = form.get('audio')
            language: str = form.get('language')  # Optional

            if not audio_file:
                return JSONResponse(
                    {'success': False, 'error': 'No audio file provided'},
                    status_code=400
                )

            # Validate file
            filename = audio_file.filename or 'audio.webm'

            # Check file extension
            file_extension = Path(filename).suffix.lower()
            allowed_extensions = {'.webm', '.mp3', '.wav', '.m4a', '.ogg', '.flac'}

            if file_extension not in allowed_extensions:
                return JSONResponse(
                    {
                        'success': False,
                        'error': f'Unsupported audio type. Allowed: {", ".join(allowed_extensions)}'
                    },
                    status_code=400
                )

            logger.info(f"Receiving audio transcription request: {filename}")

            # Read audio content
            audio_content = await audio_file.read()
            audio_size = len(audio_content)

            # Validate file size (max 25MB for Voxtral)
            max_size = 25 * 1024 * 1024  # 25MB
            if audio_size > max_size:
                return JSONResponse(
                    {
                        'success': False,
                        'error': 'Audio file too large. Maximum size: 25MB'
                    },
                    status_code=400
                )

            # Save to temporary file for processing
            suffix = file_extension or '.webm'

            with tempfile.NamedTemporaryFile(
                mode='wb',
                suffix=suffix,
                delete=False
            ) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name

            try:
                # Transcribe audio through Voxtral service
                logger.info(f"Transcribing audio: {filename}")
                result = await self.voxtral_service.transcribe_audio(
                    audio_path=temp_file_path,
                    language=language
                )

                logger.info(
                    f"Transcription successful: {len(result['text'])} characters"
                )

                return JSONResponse({
                    'success': True,
                    'text': result['text'],
                    'language': result.get('language'),
                    'model': result.get('model')
                })

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")

        except Exception as e:
            logger.error(f"Audio transcription error: {e}", exc_info=True)
            return JSONResponse(
                {
                    'success': False,
                    'error': str(e)
                },
                status_code=500
            )

    async def health_check(self, request: Request) -> JSONResponse:
        """
        Check if voice transcription service is available.

        Returns:
            JSON response with service status
        """
        try:
            is_available = self.voxtral_service.is_available()

            return JSONResponse({
                'available': is_available,
                'model': self.voxtral_service.model if is_available else None
            })

        except Exception as e:
            logger.error(f"Voice service health check error: {e}")
            return JSONResponse(
                {'available': False, 'error': str(e)},
                status_code=500
            )
