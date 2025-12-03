"""
RAG (Retrieval-Augmented Generation) service for answering questions about syllabi.
Combines vector search with LLM generation for accurate, context-aware answers.
"""
from typing import List, Optional, Dict
from dataclasses import dataclass
import logging

from .vector_db.base import VectorDatabaseInterface, VectorSearchResult
from .embedding_service import EmbeddingService
from .mistral_service import MistralService

logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """
    Response from RAG query.

    Attributes:
        answer: Generated answer from LLM
        sources: Retrieved source chunks used for context
        question: Original user question
        metadata: Additional metadata (tokens used, etc.)
    """
    answer: str
    sources: List[VectorSearchResult]
    question: str
    metadata: Dict


class RAGService:
    """
    Retrieval-Augmented Generation service.

    This service implements the RAG pattern:
    1. User asks a question
    2. Embed the question
    3. Search vector DB for relevant syllabus content
    4. Construct prompt with retrieved context
    5. Generate answer using LLM
    6. Return answer with source citations

    Design Pattern: Facade Pattern
    Purpose: Simplify complex RAG pipeline into simple interface

    Usage:
        rag = RAGService(vector_db, embedding_service, mistral_service)

        response = await rag.query(
            "What is the grading policy for CS101?",
            filters={"course_code": "CS101"}
        )

        print(response.answer)
        for source in response.sources:
            print(f"- {source.metadata['source_file']}")
    """

    def __init__(
        self,
        vector_db: VectorDatabaseInterface,
        embedding_service: EmbeddingService,
        mistral_service: MistralService,
        default_top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize RAG service.

        Args:
            vector_db: Vector database for retrieval
            embedding_service: Service for embedding queries
            mistral_service: Service for generating answers
            default_top_k: Default number of chunks to retrieve
            similarity_threshold: Minimum similarity score to include
        """
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.mistral_service = mistral_service
        self.default_top_k = default_top_k
        self.similarity_threshold = similarity_threshold

        logger.info("RAGService initialized")

    async def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None,
        include_sources: bool = True
    ) -> RAGResponse:
        """
        Answer a question using RAG.

        Args:
            question: User's question
            top_k: Number of chunks to retrieve (default: self.default_top_k)
            filters: Metadata filters (e.g., {"course_code": "CS101"})
            include_sources: Whether to include source chunks in response

        Returns:
            RAGResponse with answer and sources

        Example:
            # General question
            response = await rag.query("What are the prerequisites?")

            # Course-specific question
            response = await rag.query(
                "What is the grading policy?",
                filters={"course_code": "CS101"}
            )

            # Instructor-specific question
            response = await rag.query(
                "What courses does Dr. Smith teach?",
                filters={"instructor": "Dr. Smith"}
            )
        """
        try:
            # Step 1: Embed the question
            logger.info(f"Processing RAG query: {question[:100]}...")
            query_embedding = await self.embedding_service.embed_query(question)

            if not query_embedding:
                raise Exception("Failed to generate query embedding")

            # Step 2: Search vector database
            top_k = top_k or self.default_top_k
            search_results = await self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k,
                filter=filters
            )

            # Filter by similarity threshold
            search_results = [
                r for r in search_results
                if r.similarity_score >= self.similarity_threshold
            ]

            logger.info(f"Retrieved {len(search_results)} relevant chunks")

            # Step 3: Build context from search results
            context = self._build_context(search_results)

            # Step 4: Build RAG prompt
            prompt = self._build_prompt(question, context, filters)

            # Step 5: Generate answer
            answer = await self._generate_answer(prompt)

            # Step 6: Build response
            response = RAGResponse(
                answer=answer,
                sources=search_results if include_sources else [],
                question=question,
                metadata={
                    "num_sources": len(search_results),
                    "filters_applied": filters or {},
                    "top_k": top_k
                }
            )

            logger.info(f"RAG query completed successfully")
            return response

        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)

            # Return error response
            return RAGResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                sources=[],
                question=question,
                metadata={"error": str(e)}
            )

    async def stream_query(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None
    ):
        """
        Answer a question using RAG with streaming response.

        This method is useful for real-time chat interfaces where you want
        to stream the answer as it's being generated.

        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            filters: Metadata filters

        Yields:
            str: Chunks of the answer as they're generated

        Example:
            async for chunk in rag.stream_query("What is the grading policy?"):
                print(chunk, end='', flush=True)
        """
        try:
            # Step 1-3: Same as regular query (retrieve and build context)
            query_embedding = await self.embedding_service.embed_query(question)

            if not query_embedding:
                yield "Error: Failed to generate query embedding"
                return

            top_k = top_k or self.default_top_k
            search_results = await self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k,
                filter=filters
            )

            search_results = [
                r for r in search_results
                if r.similarity_score >= self.similarity_threshold
            ]

            context = self._build_context(search_results)
            prompt = self._build_prompt(question, context, filters)

            # Step 4: Stream answer generation
            async for chunk in self.mistral_service.stream_response(prompt):
                yield chunk

        except Exception as e:
            logger.error(f"Streaming RAG query failed: {e}")
            yield f"\n\nError: {str(e)}"

    def _build_context(self, search_results: List[VectorSearchResult]) -> str:
        """
        Build context string from search results.

        Format:
            [Source 1: CS101_Fall2024.pdf]
            Course grading policy: Exams 40%, Projects 60%...

            [Source 2: CS101_Spring2024.pdf]
            Office hours: Monday 2-4pm...

        Args:
            search_results: List of search results

        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant information found in the syllabi."

        context_parts = []

        for i, result in enumerate(search_results, 1):
            source_file = result.metadata.get('source_file', 'Unknown')
            course_code = result.metadata.get('course_code', '')
            semester = result.metadata.get('semester', '')

            # Build source header
            source_header = f"[Source {i}: {source_file}"
            if course_code:
                source_header += f" ({course_code}"
                if semester:
                    source_header += f", {semester}"
                source_header += ")"
            source_header += "]"

            # Add source and content
            context_parts.append(
                f"{source_header}\n{result.content}\n"
            )

        return "\n---\n".join(context_parts)

    def _build_prompt(
        self,
        question: str,
        context: str,
        filters: Optional[Dict] = None
    ) -> str:
        """
        Build RAG prompt for the LLM.

        The prompt includes:
        - System instructions
        - Retrieved context from syllabi
        - User's question
        - Response guidelines

        Args:
            question: User's question
            context: Retrieved context from vector search
            filters: Applied filters (for context)

        Returns:
            Complete prompt string
        """
        # Add filter context if applicable
        filter_context = ""
        if filters:
            filter_parts = []
            if 'course_code' in filters:
                filter_parts.append(f"course {filters['course_code']}")
            if 'instructor' in filters:
                filter_parts.append(f"instructor {filters['instructor']}")
            if 'semester' in filters:
                filter_parts.append(f"semester {filters['semester']}")

            if filter_parts:
                filter_context = f"\n(Question is about {', '.join(filter_parts)})"

        prompt = f"""You are a helpful academic assistant that answers student questions about course syllabi.

SYLLABI CONTENT:
{context}

STUDENT QUESTION{filter_context}:
{question}

INSTRUCTIONS:
- Answer based ONLY on the provided syllabus content above
- If the answer is not in the syllabi, say "I don't have that information in the available syllabi"
- Be specific and cite which course/syllabus you're referencing when relevant
- If multiple syllabi have different information, mention the differences
- Be concise but complete
- Use a helpful, professional tone

ANSWER:"""

        return prompt

    async def _generate_answer(self, prompt: str) -> str:
        """
        Generate answer using Mistral LLM.

        Args:
            prompt: Complete RAG prompt

        Returns:
            Generated answer
        """
        try:
            # Use the existing Mistral service to generate response
            # Assuming MistralService has a method like this
            response = await self.mistral_service.generate_response(prompt)

            return response

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return f"I encountered an error while generating the answer: {str(e)}"

    async def get_relevant_courses(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find courses relevant to a query.

        Useful for:
        - "Show me all CS courses"
        - "What math courses are available?"
        - "Find courses about machine learning"

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of course metadata dicts
        """
        try:
            query_embedding = await self.embedding_service.embed_query(query)

            if not query_embedding:
                return []

            results = await self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k
            )

            # Extract unique courses
            courses_seen = set()
            courses = []

            for result in results:
                course_code = result.metadata.get('course_code')
                if course_code and course_code not in courses_seen:
                    courses_seen.add(course_code)
                    courses.append({
                        'course_code': course_code,
                        'source_file': result.metadata.get('source_file'),
                        'instructor': result.metadata.get('instructor'),
                        'semester': result.metadata.get('semester'),
                        'relevance_score': result.similarity_score
                    })

            return courses

        except Exception as e:
            logger.error(f"Failed to get relevant courses: {e}")
            return []
