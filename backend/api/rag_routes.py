"""
RAG API route handlers.
Handles HTTP endpoints for RAG (Retrieval-Augmented Generation) functionality.
"""
from typing import Optional, Dict, Any, Union
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from backend.services.rag_service import RAGService
from backend.services.syllabus_ingestion_service import SyllabusIngestionService
from backend.utils.logger import setup_logger
from backend.middleware.error_handler import create_error_response
import json


logger = setup_logger(__name__)


class RAGQueryRequest(BaseModel):
    """Request model for RAG queries."""
    question: str = Field(..., min_length=1, max_length=1000)
    course_code: Optional[str] = Field(None, max_length=20)
    instructor: Optional[str] = Field(None, max_length=100)
    semester: Optional[str] = Field(None, max_length=50)
    top_k: int = Field(5, ge=1, le=20)
    stream: bool = Field(False)


class RAGRoutes:
    """Handler class for RAG-related routes."""

    def __init__(
        self,
        rag_service: RAGService,
        ingestion_service: Optional[SyllabusIngestionService] = None
    ):
        """
        Initialize RAG routes handler.

        Args:
            rag_service: RAG service for querying
            ingestion_service: Optional ingestion service for management
        """
        self.rag_service = rag_service
        self.ingestion_service = ingestion_service

    async def query_syllabi(self, request: Request) -> Union[JSONResponse, StreamingResponse]:
        """
        Query syllabi using RAG.

        POST /api/rag/query
        Body: {
            "question": "What is the grading policy?",
            "course_code": "CS101",  // optional
            "instructor": "Dr. Smith",  // optional
            "semester": "Fall 2024",  // optional
            "top_k": 5,  // optional, default 5
            "stream": false  // optional, default false
        }

        Args:
            request: The HTTP request

        Returns:
            JSONResponse or StreamingResponse with answer and sources
        """
        try:
            body = await request.json()
            query_request = RAGQueryRequest(**body)

            # Build filters from request
            filters = {}
            if query_request.course_code:
                filters["course_code"] = query_request.course_code
            if query_request.instructor:
                filters["instructor"] = query_request.instructor
            if query_request.semester:
                filters["semester"] = query_request.semester

            logger.info(
                f"RAG query: '{query_request.question[:50]}...' "
                f"with filters: {filters}"
            )

            # Handle streaming response
            if query_request.stream:
                return await self._stream_query(
                    query_request.question,
                    filters,
                    query_request.top_k
                )

            # Regular response
            response = await self.rag_service.query(
                question=query_request.question,
                top_k=query_request.top_k,
                filters=filters if filters else None,
                include_sources=True
            )

            # Format response
            return JSONResponse({
                "answer": response.answer,
                "sources": [
                    {
                        "id": source.id,
                        "content": source.content,
                        "similarity_score": source.similarity_score,
                        "metadata": source.metadata
                    }
                    for source in response.sources
                ],
                "metadata": response.metadata
            })

        except ValueError as e:
            logger.error(f"Validation error in query_syllabi: {e}")
            return create_error_response(400, str(e), "validation_error")
        except Exception as e:
            logger.error(f"Error in query_syllabi: {e}", exc_info=True)
            return create_error_response(500, str(e), "internal_error")

    async def _stream_query(
        self,
        question: str,
        filters: Optional[Dict],
        top_k: int
    ) -> StreamingResponse:
        """
        Stream RAG query response.

        Args:
            question: User's question
            filters: Metadata filters
            top_k: Number of results to retrieve

        Returns:
            StreamingResponse with SSE data
        """
        async def generate():
            """Generator function for SSE streaming."""
            try:
                async for chunk in self.rag_service.stream_query(
                    question=question,
                    top_k=top_k,
                    filters=filters
                ):
                    data = {
                        "content": chunk,
                        "is_final": False
                    }
                    yield f"data: {json.dumps(data)}\n\n"

                # Send final message
                final_data = {"is_final": True}
                yield f"data: {json.dumps(final_data)}\n\n"

            except Exception as e:
                logger.error(f"Error during RAG streaming: {e}", exc_info=True)
                error_data = {
                    "error": str(e),
                    "is_final": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    async def get_relevant_courses(self, request: Request) -> JSONResponse:
        """
        Find courses relevant to a search query.

        GET /api/rag/courses?q=machine+learning&top_k=10

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with list of relevant courses
        """
        try:
            query = request.query_params.get("q", "")
            top_k = int(request.query_params.get("top_k", "10"))

            if not query:
                return create_error_response(
                    400,
                    "Query parameter 'q' is required",
                    "validation_error"
                )

            courses = await self.rag_service.get_relevant_courses(
                query=query,
                top_k=top_k
            )

            return JSONResponse({
                "courses": courses,
                "count": len(courses)
            })

        except Exception as e:
            logger.error(f"Error in get_relevant_courses: {e}", exc_info=True)
            return create_error_response(500, str(e), "internal_error")

    async def get_stats(self, request: Request) -> JSONResponse:
        """
        Get RAG system statistics.

        GET /api/rag/stats

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with system statistics
        """
        try:
            stats = await self.rag_service.vector_db.get_stats()

            return JSONResponse({
                "vector_db": stats,
                "status": "operational"
            })

        except Exception as e:
            logger.error(f"Error in get_stats: {e}", exc_info=True)
            return create_error_response(500, str(e), "internal_error")

    async def health_check(self, request: Request) -> JSONResponse:
        """
        Health check for RAG system.

        GET /api/rag/health

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with health status
        """
        try:
            is_healthy = await self.rag_service.vector_db.health_check()

            if is_healthy:
                return JSONResponse({
                    "status": "healthy",
                    "vector_db": "connected"
                })
            else:
                return JSONResponse(
                    {
                        "status": "unhealthy",
                        "vector_db": "disconnected"
                    },
                    status_code=503
                )

        except Exception as e:
            logger.error(f"Error in health_check: {e}", exc_info=True)
            return JSONResponse(
                {
                    "status": "unhealthy",
                    "error": str(e)
                },
                status_code=503
            )

    async def delete_syllabus(self, request: Request) -> JSONResponse:
        """
        Delete a syllabus from the vector database.

        DELETE /api/rag/syllabi/{document_id}

        Args:
            request: The HTTP request

        Returns:
            JSONResponse with deletion status
        """
        if not self.ingestion_service:
            return create_error_response(
                503,
                "Ingestion service not available",
                "service_unavailable"
            )

        try:
            document_id = request.path_params.get("document_id")

            if not document_id:
                return create_error_response(
                    400,
                    "Document ID is required",
                    "validation_error"
                )

            success = await self.ingestion_service.delete_document(document_id)

            if success:
                return JSONResponse({
                    "message": "Syllabus deleted successfully",
                    "document_id": document_id
                })
            else:
                return create_error_response(
                    404,
                    "Syllabus not found or deletion failed",
                    "not_found"
                )

        except Exception as e:
            logger.error(f"Error in delete_syllabus: {e}", exc_info=True)
            return create_error_response(500, str(e), "internal_error")
