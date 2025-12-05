"""
Main application module.
Initializes and configures the FastAPI/Starlette application.
"""
from typing import Optional
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from backend.config.settings import load_config
from backend.api.routes import create_routes
from backend.api.chat_routes import ChatRoutes
from backend.api.rag_routes import RAGRoutes
from backend.api.file_routes import FileRoutes
from backend.api.voice_routes import VoiceRoutes
from backend.services.conversation_manager import ConversationManager
from backend.services.mistral_service import MistralService
from backend.services.vector_db.factory import VectorDatabaseFactory
from backend.services.embedding_service import EmbeddingService
from backend.services.rag_service import RAGService
from backend.services.document_parser import DocumentParser
from backend.services.text_chunker import TextChunker
from backend.services.syllabus_ingestion_service import SyllabusIngestionService
from backend.services.file_ingestion_service import FileIngestionService
from backend.services.voxtral_service import VoxtralService
from backend.middleware.error_handler import ErrorHandlerMiddleware
from backend.middleware.request_validator import RequestValidationMiddleware
from backend.middleware.cors import get_cors_config
from backend.utils.logger import setup_logger


logger = setup_logger(__name__)


class Application:
    """Main application class with dependency injection."""

    def __init__(self):
        """Initialize the application."""
        self.config = load_config()
        self.conversation_manager = ConversationManager()
        self.mistral_service = MistralService(self.config.mistral)

        # Initialize RAG services if enabled
        self.rag_service: Optional[RAGService] = None
        self.ingestion_service: Optional[SyllabusIngestionService] = None
        self.file_ingestion_service: Optional[FileIngestionService] = None
        if self.config.pinecone:
            self._initialize_rag_services()

        self.app = self._create_app()

    def _initialize_rag_services(self):
        """Initialize RAG-related services."""
        try:
            logger.info("Initializing RAG services...")

            # Create vector database
            vector_db = VectorDatabaseFactory.create(
                'pinecone',
                {
                    'api_key': self.config.pinecone.api_key,
                    'index_name': self.config.pinecone.index_name,
                    'dimension': self.config.pinecone.dimension,
                    'metric': self.config.pinecone.metric,
                    'cloud': self.config.pinecone.cloud,
                    'region': self.config.pinecone.region
                }
            )

            # Create embedding service
            embedding_service = EmbeddingService(self.config.mistral.api_key)

            # Create RAG service
            self.rag_service = RAGService(
                vector_db=vector_db,
                embedding_service=embedding_service,
                mistral_service=self.mistral_service,
                default_top_k=self.config.rag.top_k_results if self.config.rag else 5,
                similarity_threshold=self.config.rag.similarity_threshold if self.config.rag else 0.7
            )

            # Create ingestion service
            parser = DocumentParser()
            chunker = TextChunker(
                strategy=self.config.rag.chunking_strategy if self.config.rag else 'fixed_size',
                chunk_size=self.config.rag.chunk_size if self.config.rag else 500,
                overlap=self.config.rag.chunk_overlap if self.config.rag else 50
            )

            self.ingestion_service = SyllabusIngestionService(
                vector_db=vector_db,
                embedding_service=embedding_service,
                parser=parser,
                chunker=chunker
            )

            # Create file ingestion service (for uploaded files)
            self.file_ingestion_service = FileIngestionService(
                vector_db=vector_db,
                embedding_service=embedding_service,
                parser=parser,
                chunker=chunker
            )

            logger.info("✓ RAG services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG services: {e}", exc_info=True)
            logger.warning("RAG features will be disabled")
            self.rag_service = None
            self.ingestion_service = None
            self.file_ingestion_service = None

    def _create_app(self) -> Starlette:
        """
        Create and configure the Starlette application.

        Returns:
            Configured Starlette application
        """
        # Initialize route handlers
        chat_routes = ChatRoutes(
            conversation_manager=self.conversation_manager,
            mistral_service=self.mistral_service
        )

        # Initialize RAG routes if service is available
        rag_routes = None
        if self.rag_service:
            rag_routes = RAGRoutes(
                rag_service=self.rag_service,
                ingestion_service=self.ingestion_service
            )

        # Initialize file upload routes if service is available
        file_routes = None
        if self.file_ingestion_service:
            file_routes = FileRoutes(
                ingestion_service=self.file_ingestion_service
            )

        # Initialize voice transcription routes
        voice_routes = None
        try:
            voxtral_service = VoxtralService()
            voice_routes = VoiceRoutes(voxtral_service=voxtral_service)
            logger.info("✓ Voice transcription service initialized")
        except Exception as e:
            logger.warning(f"Voice transcription disabled: {e}")

        # Create routes
        routes = create_routes(chat_routes, rag_routes, file_routes, voice_routes)

        # Create application
        app = Starlette(
            debug=self.config.server.debug,
            routes=routes
        )

        # Add middleware (order matters - last added is executed first)
        # CORS middleware
        cors_config = get_cors_config(self.config.server.cors_origins)
        app.add_middleware(CORSMiddleware, **cors_config)

        # Request validation middleware
        app.add_middleware(RequestValidationMiddleware)

        # Error handling middleware (should be last to catch all errors)
        app.add_middleware(ErrorHandlerMiddleware)

        # Lifecycle events
        @app.on_event("startup")
        async def startup_event():
            """Run on application startup."""
            logger.info("Application starting up...")
            logger.info(f"Using Mistral model: {self.config.mistral.model}")
            logger.info(f"CORS origins: {self.config.server.cors_origins}")

            # Initialize RAG vector database connection
            if self.rag_service:
                try:
                    await self.rag_service.vector_db.initialize()
                    health = await self.rag_service.vector_db.health_check()
                    if health:
                        logger.info("✓ RAG system operational")
                        stats = await self.rag_service.vector_db.get_stats()
                        logger.info(f"  - Vectors: {stats.get('total_vectors', 0)}")
                    else:
                        logger.warning("⚠ RAG system unhealthy")
                except Exception as e:
                    logger.error(f"Failed to initialize RAG on startup: {e}")

        @app.on_event("shutdown")
        async def shutdown_event():
            """Run on application shutdown."""
            logger.info("Application shutting down...")
            await self.mistral_service.close()

        return app

    def get_app(self) -> Starlette:
        """
        Get the configured application instance.

        Returns:
            Starlette application
        """
        return self.app


def create_application() -> Starlette:
    """
    Factory function to create the application.

    Returns:
        Configured Starlette application
    """
    application = Application()
    return application.get_app()


# Create application instance
app = create_application()
