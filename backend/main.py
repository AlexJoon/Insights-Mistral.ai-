"""
Application entry point.
Runs the Uvicorn server with the configured application.
"""
import uvicorn
import sys
from backend.config.settings import load_config
from backend.utils.logger import setup_logger


logger = setup_logger(__name__)


def main():
    """Main entry point for the application."""
    try:
        config = load_config()

        logger.info("="*60)
        logger.info("Starting Mistral Chat API Server")
        logger.info("="*60)
        logger.info(f"Host: {config.server.host}")
        logger.info(f"Port: {config.server.port}")
        logger.info(f"Debug: {config.server.debug}")
        logger.info(f"Model: {config.mistral.model}")
        logger.info("="*60)

        uvicorn.run(
            "backend.app:app",
            host=config.server.host,
            port=config.server.port,
            reload=config.server.debug,
            log_level="info",
            access_log=True
        )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
