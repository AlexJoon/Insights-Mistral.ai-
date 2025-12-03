"""
Mistral AI service module.
Handles all interactions with the Mistral AI API.
"""
import httpx
import json
from typing import AsyncGenerator, Optional, List, Dict
from backend.config.settings import MistralConfig
from backend.models.chat import StreamChunk
from backend.utils.logger import setup_logger


logger = setup_logger(__name__)


class MistralServiceError(Exception):
    """Custom exception for Mistral service errors."""
    pass


class MistralService:
    """Service for interacting with Mistral AI API."""

    def __init__(self, config: MistralConfig):
        """
        Initialize the Mistral service.

        Args:
            config: Mistral configuration
        """
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        conversation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream a chat completion from Mistral AI.

        Args:
            messages: List of message dictionaries
            conversation_id: Optional conversation ID for tracking
            message_id: Optional message ID for tracking
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Yields:
            StreamChunk objects containing response content
        """
        url = f"{self.config.api_base_url}/chat/completions"

        payload = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": True
        }

        logger.info(f"Initiating stream for model {payload['model']}")

        try:
            async with self.client.stream(
                "POST",
                url,
                json=payload,
                timeout=120.0
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"Mistral API error: {response.status_code} - {error_text}")
                    raise MistralServiceError(
                        f"API request failed with status {response.status_code}: {error_text.decode()}"
                    )

                accumulated_content = ""

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str.strip() == "[DONE]":
                            # Send final chunk
                            yield StreamChunk(
                                content="",
                                is_final=True,
                                conversation_id=conversation_id,
                                message_id=message_id
                            )
                            break

                        try:
                            data = json.loads(data_str)
                            choices = data.get("choices", [])

                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")

                                if content:
                                    accumulated_content += content
                                    yield StreamChunk(
                                        content=content,
                                        is_final=False,
                                        conversation_id=conversation_id,
                                        message_id=message_id
                                    )

                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse JSON: {e} - Line: {data_str}")
                            continue

                logger.info(f"Stream completed. Total content length: {len(accumulated_content)}")

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise MistralServiceError("Request to Mistral AI timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise MistralServiceError(f"Failed to connect to Mistral AI: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}")
            raise MistralServiceError(f"Unexpected error: {str(e)}")

    async def non_streaming_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Get a non-streaming chat completion.

        Args:
            messages: List of message dictionaries
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            The complete response content
        """
        url = f"{self.config.api_base_url}/chat/completions"

        payload = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": False
        }

        try:
            response = await self.client.post(url, json=payload)

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Mistral API error: {response.status_code} - {error_text}")
                raise MistralServiceError(
                    f"API request failed with status {response.status_code}: {error_text}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise MistralServiceError("Request to Mistral AI timed out")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise MistralServiceError(f"Failed to connect to Mistral AI: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format: {e}")
            raise MistralServiceError("Unexpected response format from Mistral AI")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise MistralServiceError(f"Unexpected error: {str(e)}")
