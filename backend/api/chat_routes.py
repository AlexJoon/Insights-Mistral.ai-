"""
Chat API route handlers.
Handles HTTP endpoints for chat functionality.
"""
from typing import Dict, Any
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from backend.models.chat import ChatRequest
from backend.services.conversation_manager import ConversationManager
from backend.services.mistral_service import MistralService
from backend.utils.validators import validate_message, validate_conversation_id, validate_model_params
from backend.utils.logger import setup_logger
from backend.middleware.error_handler import create_error_response


logger = setup_logger(__name__)


class ChatRoutes:
    """Handler class for chat-related routes."""

    def __init__(
        self,
        conversation_manager: ConversationManager,
        mistral_service: MistralService
    ):
        """
        Initialize chat routes handler.

        Args:
            conversation_manager: Conversation management service
            mistral_service: Mistral AI service
        """
        self.conversation_manager = conversation_manager
        self.mistral_service = mistral_service

    async def stream_chat(self, request: Request) -> StreamingResponse:
        """
        Handle streaming chat requests.

        Args:
            request: The HTTP request

        Returns:
            StreamingResponse with SSE data
        """
        try:
            body = await request.json()
            chat_request = ChatRequest.from_dict(body)

            # Validate inputs
            is_valid, error = validate_message(chat_request.message)
            if not is_valid:
                return create_error_response(400, error, "validation_error")

            is_valid, error = validate_conversation_id(chat_request.conversation_id)
            if not is_valid:
                return create_error_response(400, error, "validation_error")

            is_valid, error = validate_model_params(
                chat_request.temperature,
                chat_request.max_tokens
            )
            if not is_valid:
                return create_error_response(400, error, "validation_error")

            # Get or create conversation
            conversation = self.conversation_manager.get_or_create_conversation(
                chat_request.conversation_id
            )

            # Add user message
            user_message = conversation.add_message("user", chat_request.message)

            # Prepare messages for API
            api_messages = conversation.get_messages_for_api()

            # Create assistant message placeholder
            assistant_message = conversation.add_message("assistant", "")

            async def generate():
                """Generator function for SSE streaming."""
                try:
                    accumulated_content = ""

                    async for chunk in self.mistral_service.stream_chat_completion(
                        messages=api_messages,
                        conversation_id=conversation.id,
                        message_id=assistant_message.id,
                        model=chat_request.model,
                        temperature=chat_request.temperature,
                        max_tokens=chat_request.max_tokens
                    ):
                        if not chunk.is_final:
                            accumulated_content += chunk.content

                        # Update chunk with conversation details
                        chunk.conversation_id = conversation.id
                        chunk.message_id = assistant_message.id

                        yield chunk.to_sse_format()

                    # Update assistant message with complete content
                    assistant_message.content = accumulated_content

                    logger.info(
                        f"Completed stream for conversation {conversation.id}, "
                        f"message {assistant_message.id}"
                    )

                except Exception as e:
                    logger.error(f"Error during streaming: {e}", exc_info=True)
                    error_chunk = {
                        "error": str(e),
                        "conversation_id": conversation.id,
                        "is_final": True
                    }
                    import json
                    yield f"data: {json.dumps(error_chunk)}\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )

        except Exception as e:
            logger.error(f"Error in stream_chat: {e}", exc_info=True)
            return create_error_response(500, str(e), "internal_error")

    async def get_conversation(self, request: Request) -> JSONResponse:
        """
        Get a specific conversation by ID.

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with conversation data
        """
        conversation_id = request.path_params.get("conversation_id")

        if not conversation_id:
            return create_error_response(400, "Conversation ID is required", "validation_error")

        conversation = self.conversation_manager.get_conversation(conversation_id)

        if not conversation:
            return create_error_response(404, "Conversation not found", "not_found")

        return JSONResponse(conversation.to_dict())

    async def get_all_conversations(self, request: Request) -> JSONResponse:
        """
        Get all conversations.

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with list of conversations
        """
        conversations = self.conversation_manager.get_all_conversations()
        return JSONResponse({
            "conversations": [conv.to_dict() for conv in conversations]
        })

    async def create_conversation(self, request: Request) -> JSONResponse:
        """
        Create a new conversation.

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with created conversation
        """
        body = await request.json()
        title = body.get("title", "New Conversation")

        conversation = self.conversation_manager.create_conversation(title)

        return JSONResponse(
            conversation.to_dict(),
            status_code=201
        )

    async def delete_conversation(self, request: Request) -> JSONResponse:
        """
        Delete a conversation.

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with deletion status
        """
        conversation_id = request.path_params.get("conversation_id")

        if not conversation_id:
            return create_error_response(400, "Conversation ID is required", "validation_error")

        deleted = self.conversation_manager.delete_conversation(conversation_id)

        if not deleted:
            return create_error_response(404, "Conversation not found", "not_found")

        return JSONResponse({"message": "Conversation deleted successfully"})

    async def update_conversation(self, request: Request) -> JSONResponse:
        """
        Update a conversation's metadata.

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with updated conversation
        """
        conversation_id = request.path_params.get("conversation_id")

        if not conversation_id:
            return create_error_response(400, "Conversation ID is required", "validation_error")

        body = await request.json()
        title = body.get("title")

        if not title:
            return create_error_response(400, "Title is required", "validation_error")

        updated = self.conversation_manager.update_conversation_title(conversation_id, title)

        if not updated:
            return create_error_response(404, "Conversation not found", "not_found")

        conversation = self.conversation_manager.get_conversation(conversation_id)

        return JSONResponse(conversation.to_dict())
