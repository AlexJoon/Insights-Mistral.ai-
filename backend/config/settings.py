"""
Configuration settings for the application.
Centralized configuration management with environment variable support.
"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class MistralConfig:
    """Mistral AI API configuration."""
    api_key: str
    api_base_url: str = "https://api.mistral.ai/v1"
    model: str = "mistral-large-latest"
    max_tokens: int = 4096
    temperature: float = 0.7
    stream: bool = True


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000"]


@dataclass
class PineconeConfig:
    """Pinecone vector database configuration."""
    api_key: str
    index_name: str = "syllabi"
    dimension: int = 1024  # Mistral embedding dimension
    metric: str = "cosine"
    cloud: str = "aws"
    region: str = "us-east-1"


@dataclass
class RAGConfig:
    """RAG (Retrieval-Augmented Generation) configuration."""
    chunk_size: int = 500
    chunk_overlap: int = 50
    chunking_strategy: str = "fixed_size"  # 'fixed_size', 'sentence', 'section'
    top_k_results: int = 5
    similarity_threshold: float = 0.7


@dataclass
class AppConfig:
    """Main application configuration."""
    mistral: MistralConfig
    server: ServerConfig
    pinecone: Optional[PineconeConfig] = None
    rag: Optional[RAGConfig] = None


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    mistral_api_key = os.getenv("MISTRAL_API_KEY", "")

    if not mistral_api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is required")

    mistral_config = MistralConfig(
        api_key=mistral_api_key,
        api_base_url=os.getenv("MISTRAL_API_BASE_URL", "https://api.mistral.ai/v1"),
        model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
        max_tokens=int(os.getenv("MISTRAL_MAX_TOKENS", "4096")),
        temperature=float(os.getenv("MISTRAL_TEMPERATURE", "0.7"))
    )

    server_config = ServerConfig(
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", "8000")),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    )

    # Optional Pinecone configuration (for RAG)
    pinecone_config = None
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if pinecone_api_key:
        pinecone_config = PineconeConfig(
            api_key=pinecone_api_key,
            index_name=os.getenv("PINECONE_INDEX_NAME", "syllabi"),
            dimension=int(os.getenv("PINECONE_DIMENSION", "1024")),
            metric=os.getenv("PINECONE_METRIC", "cosine"),
            cloud=os.getenv("PINECONE_CLOUD", "aws"),
            region=os.getenv("PINECONE_REGION", "us-east-1")
        )

    # Optional RAG configuration
    rag_config = None
    if os.getenv("ENABLE_RAG", "false").lower() == "true":
        rag_config = RAGConfig(
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "500")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "50")),
            chunking_strategy=os.getenv("RAG_CHUNKING_STRATEGY", "fixed_size"),
            top_k_results=int(os.getenv("RAG_TOP_K", "5")),
            similarity_threshold=float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))
        )

    return AppConfig(
        mistral=mistral_config,
        server=server_config,
        pinecone=pinecone_config,
        rag=rag_config
    )
