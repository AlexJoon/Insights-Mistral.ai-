"""
Voxtral Service - Mistral voice transcription API integration.

Design Pattern: Service Layer Pattern
Purpose: Encapsulate Voxtral API calls for voice-to-text transcription
"""
import httpx
import logging
import os
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class VoxtralService:
    """
    Service for transcribing audio using Mistral's Voxtral API.

    Uses Voxtral Mini for cost-efficient, high-quality transcription.

    Attributes:
        client: httpx AsyncClient instance
        model: Voxtral model to use (default: voxtral-mini-latest)
        api_base_url: Mistral API base URL
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: str = "https://api.mistral.ai/v1",
        model: str = "voxtral-mini-latest"
    ):
        """
        Initialize Voxtral service.

        Args:
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
            api_base_url: Mistral API base URL
            model: Voxtral model name (default: voxtral-mini-latest)
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")

        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment")

        self.api_base_url = api_base_url
        self.model = model
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}"
            }
        )

        logger.info(f"VoxtralService initialized with model: {self.model}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (webm, mp3, wav, etc.)
            language: Optional language code (auto-detected if not provided)

        Returns:
            Dictionary containing:
                - text: Transcribed text
                - language: Detected/specified language
                - duration: Audio duration in seconds (if available)

        Raises:
            Exception: If transcription fails

        Example:
            result = await service.transcribe_audio("recording.webm")
            print(result['text'])
        """
        try:
            logger.info(f"Transcribing audio file: {audio_path}")

            url = f"{self.api_base_url}/audio/transcriptions"

            # Prepare multipart form data
            with open(audio_path, 'rb') as audio_file:
                files = {
                    'file': (Path(audio_path).name, audio_file, 'audio/webm')
                }
                data = {
                    'model': self.model
                }

                # Add language if specified
                if language:
                    data['language'] = language

                # Make API request
                response = await self.client.post(
                    url,
                    files=files,
                    data=data
                )

            # Check response status
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Voxtral API error: {response.status_code} - {error_text}")
                raise Exception(
                    f"API request failed with status {response.status_code}: {error_text}"
                )

            # Parse response
            result = response.json()
            transcription_text = result.get('text', '')

            if not transcription_text:
                raise Exception("No transcription text received from API")

            logger.info(
                f"Transcription successful: {len(transcription_text)} characters"
            )

            return {
                'text': transcription_text,
                'language': result.get('language', language or 'auto'),
                'model': self.model
            }

        except httpx.TimeoutException as e:
            logger.error(f"Transcription timeout: {e}")
            raise Exception("Request to Voxtral API timed out")
        except httpx.RequestError as e:
            logger.error(f"Transcription request error: {e}")
            raise Exception(f"Failed to connect to Voxtral API: {str(e)}")
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio from bytes.

        Creates a temporary file to store audio bytes for API call.

        Args:
            audio_bytes: Audio file bytes
            filename: Original filename (for file type detection)
            language: Optional language code

        Returns:
            Dictionary with transcription results

        Example:
            result = await service.transcribe_audio_bytes(
                audio_data,
                filename="recording.webm"
            )
        """
        # Create temporary file
        suffix = Path(filename).suffix or '.webm'

        with tempfile.NamedTemporaryFile(
            mode='wb',
            suffix=suffix,
            delete=False
        ) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        try:
            # Transcribe temporary file
            result = await self.transcribe_audio(temp_path, language)
            return result

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

    def is_available(self) -> bool:
        """
        Check if Voxtral service is properly configured.

        Returns:
            True if API key is configured
        """
        return bool(self.api_key)
