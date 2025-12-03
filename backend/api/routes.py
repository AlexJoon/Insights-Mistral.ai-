"""
API route definitions.
Centralized route registration and organization.
"""
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from backend.api.chat_routes import ChatRoutes


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "mistral-chat-api"})


def create_routes(chat_routes: ChatRoutes) -> list:
    """
    Create all application routes.

    Args:
        chat_routes: Chat routes handler instance

    Returns:
        List of Route objects
    """
    return [
        # Health check
        Route("/health", health_check, methods=["GET"]),

        # Chat endpoints
        Route("/api/chat/stream", chat_routes.stream_chat, methods=["POST"]),
        Route("/api/conversations", chat_routes.get_all_conversations, methods=["GET"]),
        Route("/api/conversations", chat_routes.create_conversation, methods=["POST"]),
        Route(
            "/api/conversations/{conversation_id}",
            chat_routes.get_conversation,
            methods=["GET"]
        ),
        Route(
            "/api/conversations/{conversation_id}",
            chat_routes.update_conversation,
            methods=["PUT"]
        ),
        Route(
            "/api/conversations/{conversation_id}",
            chat_routes.delete_conversation,
            methods=["DELETE"]
        ),
    ]
