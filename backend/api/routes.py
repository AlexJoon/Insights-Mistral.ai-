"""
API route definitions.
Centralized route registration and organization.
"""
from typing import Optional
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from backend.api.chat_routes import ChatRoutes
from backend.api.rag_routes import RAGRoutes


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "mistral-chat-api"})


def create_routes(
    chat_routes: ChatRoutes,
    rag_routes: Optional[RAGRoutes] = None
) -> list:
    """
    Create all application routes.

    Args:
        chat_routes: Chat routes handler instance
        rag_routes: Optional RAG routes handler instance

    Returns:
        List of Route objects
    """
    routes = [
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

    # Add RAG routes if available
    if rag_routes:
        rag_endpoints = [
            # RAG query endpoints
            Route("/api/rag/query", rag_routes.query_syllabi, methods=["POST"]),
            Route("/api/rag/courses", rag_routes.get_relevant_courses, methods=["GET"]),

            # RAG system endpoints
            Route("/api/rag/stats", rag_routes.get_stats, methods=["GET"]),
            Route("/api/rag/health", rag_routes.health_check, methods=["GET"]),

            # RAG management endpoints
            Route(
                "/api/rag/syllabi/{document_id}",
                rag_routes.delete_syllabus,
                methods=["DELETE"]
            ),
        ]
        routes.extend(rag_endpoints)

    return routes
