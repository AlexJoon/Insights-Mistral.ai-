"""
Main application module.
Initializes and configures the FastAPI/Starlette application.
"""
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from backend.config.settings import load_config
from backend.api.routes import create_routes
from backend.api.chat_routes import ChatRoutes
from backend.services.conversation_manager import ConversationManager
from backend.services.mistral_service import MistralService
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
        self.app = self._create_app()

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

        # Create routes
        routes = create_routes(chat_routes)

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
