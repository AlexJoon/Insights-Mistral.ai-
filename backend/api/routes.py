"""
API route definitions.
Centralized route registration and organization.
"""
from typing import Optional
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from backend.api.chat_routes import ChatRoutes
from backend.api.rag_routes import RAGRoutes
from backend.api.file_routes import FileRoutes
from backend.api.voice_routes import VoiceRoutes


async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "mistral-chat-api"})


def create_routes(
    chat_routes: ChatRoutes,
    rag_routes: Optional[RAGRoutes] = None,
    file_routes: Optional[FileRoutes] = None,
    voice_routes: Optional[VoiceRoutes] = None
) -> list:
    """
    Create all application routes.

    Args:
        chat_routes: Chat routes handler instance
        rag_routes: Optional RAG routes handler instance
        file_routes: Optional file upload routes handler instance
        voice_routes: Optional voice transcription routes handler instance

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

    # Add file upload routes if available
    if file_routes:
        file_endpoints = [
            # File upload endpoint
            Route("/api/files/upload", file_routes.upload_file, methods=["POST"]),

            # File management endpoints
            Route(
                "/api/files/conversation/{conversation_id}",
                file_routes.get_conversation_files,
                methods=["GET"]
            ),
            Route(
                "/api/files/{file_id}",
                file_routes.get_file_metadata,
                methods=["GET"]
            ),
            Route(
                "/api/files/{file_id}",
                file_routes.delete_file,
                methods=["DELETE"]
            ),
        ]
        routes.extend(file_endpoints)

    # Add voice transcription routes if available
    if voice_routes:
        voice_endpoints = [
            # Voice transcription endpoint
            Route("/api/voice/transcribe", voice_routes.transcribe_audio, methods=["POST"]),

            # Voice service health check
            Route("/api/voice/health", voice_routes.health_check, methods=["GET"]),
        ]
        routes.extend(voice_endpoints)

    return routes
