"""
Text chunking service for splitting documents into semantically meaningful chunks.
Implements multiple chunking strategies for optimal retrieval.
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """
    Represents a chunk of text with metadata.

    Attributes:
        content: The chunk text
        index: Chunk index within the document
        start_char: Starting character position in original document
        end_char: Ending character position in original document
        metadata: Additional metadata (document_id, etc.)
    """
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: dict


class ChunkingStrategy(ABC):
    """
    Abstract base class for text chunking strategies.

    Design Pattern: Strategy Pattern
    Purpose: Different chunking algorithms for different use cases
    """

    @abstractmethod
    def chunk(self, text: str, **kwargs) -> List[TextChunk]:
        """Chunk text using this strategy."""
        pass


class FixedSizeChunkingStrategy(ChunkingStrategy):
    """
    Fixed-size chunking with overlap.

    This is the most common strategy for RAG systems:
    - Splits text into fixed-size chunks (by character or token count)
    - Includes overlap between chunks to preserve context
    - Good for general-purpose retrieval

    Parameters:
        chunk_size: Number of characters per chunk (default: 500)
        overlap: Number of characters to overlap between chunks (default: 50)
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Initialize fixed-size chunking strategy.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk_size")

    def chunk(self, text: str, **kwargs) -> List[TextChunk]:
        """
        Chunk text into fixed-size pieces with overlap.

        Args:
            text: Text to chunk
            **kwargs: Additional metadata to attach to chunks

        Returns:
            List of TextChunk objects
        """
        chunks = []
        step_size = self.chunk_size - self.overlap

        for i in range(0, len(text), step_size):
            chunk_text = text[i:i + self.chunk_size]

            # Skip very small chunks at the end
            if len(chunk_text) < 50:
                continue

            chunk = TextChunk(
                content=chunk_text.strip(),
                index=len(chunks),
                start_char=i,
                end_char=min(i + self.chunk_size, len(text)),
                metadata=kwargs.get('metadata', {})
            )
            chunks.append(chunk)

        logger.debug(f"Created {len(chunks)} fixed-size chunks")
        return chunks


class SentenceChunkingStrategy(ChunkingStrategy):
    """
    Sentence-based chunking strategy.

    Splits text at sentence boundaries to preserve semantic meaning:
    - Chunks are aligned with sentence endings
    - Target size is approximate (may vary to keep sentences whole)
    - Better semantic coherence than fixed-size chunking

    Parameters:
        target_size: Target chunk size in characters (default: 500)
        tolerance: How much chunks can vary from target size (default: 0.2)
    """

    def __init__(self, target_size: int = 500, tolerance: float = 0.2):
        """
        Initialize sentence chunking strategy.

        Args:
            target_size: Target chunk size in characters
            tolerance: Allowed variation from target (0.2 = ±20%)
        """
        self.target_size = target_size
        self.tolerance = tolerance
        self.min_size = int(target_size * (1 - tolerance))
        self.max_size = int(target_size * (1 + tolerance))

    def chunk(self, text: str, **kwargs) -> List[TextChunk]:
        """
        Chunk text at sentence boundaries.

        Args:
            text: Text to chunk
            **kwargs: Additional metadata to attach to chunks

        Returns:
            List of TextChunk objects
        """
        # Split text into sentences
        sentences = self._split_into_sentences(text)

        chunks = []
        current_chunk = []
        current_length = 0
        start_char = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence would exceed max size, create a chunk
            if current_length + sentence_length > self.max_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(TextChunk(
                    content=chunk_text,
                    index=len(chunks),
                    start_char=start_char,
                    end_char=start_char + len(chunk_text),
                    metadata=kwargs.get('metadata', {})
                ))

                # Start new chunk
                current_chunk = [sentence]
                current_length = sentence_length
                start_char += len(chunk_text) + 1
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(TextChunk(
                content=chunk_text,
                index=len(chunks),
                start_char=start_char,
                end_char=start_char + len(chunk_text),
                metadata=kwargs.get('metadata', {})
            ))

        logger.debug(f"Created {len(chunks)} sentence-based chunks")
        return chunks

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Uses simple heuristics for sentence boundaries.
        """
        # Simple sentence splitting (can be improved with nltk or spacy)
        # Split on periods, exclamation marks, question marks
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences


class SectionChunkingStrategy(ChunkingStrategy):
    """
    Section-based chunking for structured documents.

    Splits text based on section headings (useful for syllabi):
    - Preserves document structure
    - Each chunk is a complete section
    - Ideal for documents with clear headings

    Detects headings by patterns like:
    - "Course Description"
    - "Grading Policy"
    - "1. Introduction"
    - "Section 2: Requirements"
    """

    def chunk(self, text: str, **kwargs) -> List[TextChunk]:
        """
        Chunk text by sections.

        Args:
            text: Text to chunk
            **kwargs: Additional metadata to attach to chunks

        Returns:
            List of TextChunk objects
        """
        sections = self._split_into_sections(text)

        chunks = []
        current_pos = 0

        for i, section in enumerate(sections):
            chunk = TextChunk(
                content=section.strip(),
                index=i,
                start_char=current_pos,
                end_char=current_pos + len(section),
                metadata=kwargs.get('metadata', {})
            )
            chunks.append(chunk)
            current_pos += len(section)

        logger.debug(f"Created {len(chunks)} section-based chunks")
        return chunks

    def _split_into_sections(self, text: str) -> List[str]:
        """
        Split text into sections based on headings.

        Detects common syllabus section patterns:
        - ALL CAPS HEADINGS
        - Numbered sections (1., 2., etc.)
        - Common syllabus headers
        """
        # Common syllabus section headers
        section_patterns = [
            r'^[A-Z][A-Z\s]{3,}$',  # ALL CAPS HEADINGS
            r'^\d+\.\s+[A-Z]',  # 1. Introduction
            r'^[IVX]+\.\s+[A-Z]',  # I. Introduction (Roman numerals)
            r'^(?:Course|Grading|Schedule|Prerequisites|Textbook|Office Hours)',  # Common headers
        ]

        # Combine patterns
        combined_pattern = '|'.join(f'({p})' for p in section_patterns)

        # Split by section headers
        lines = text.split('\n')
        sections = []
        current_section = []

        for line in lines:
            # Check if line is a section header
            if re.match(combined_pattern, line.strip(), re.MULTILINE):
                # Save previous section
                if current_section:
                    sections.append('\n'.join(current_section))
                # Start new section with this header
                current_section = [line]
            else:
                current_section.append(line)

        # Add final section
        if current_section:
            sections.append('\n'.join(current_section))

        # Filter out very small sections
        sections = [s for s in sections if len(s.strip()) > 50]

        # If no sections found, return entire text as one section
        if not sections:
            sections = [text]

        return sections


class TextChunker:
    """
    Main text chunking service with configurable strategies.

    Design Pattern: Strategy Pattern
    Purpose: Flexible chunking with different algorithms

    Usage:
        chunker = TextChunker(strategy='fixed_size', chunk_size=500, overlap=50)
        chunks = chunker.chunk(document.content, metadata={'doc_id': '123'})
    """

    STRATEGIES = {
        'fixed_size': FixedSizeChunkingStrategy,
        'sentence': SentenceChunkingStrategy,
        'section': SectionChunkingStrategy,
    }

    def __init__(self, strategy: str = 'fixed_size', **strategy_params):
        """
        Initialize text chunker with a strategy.

        Args:
            strategy: Name of chunking strategy ('fixed_size', 'sentence', 'section')
            **strategy_params: Parameters to pass to the strategy

        Raises:
            ValueError: If strategy is not supported
        """
        if strategy not in self.STRATEGIES:
            supported = ', '.join(self.STRATEGIES.keys())
            raise ValueError(
                f"Unsupported chunking strategy: {strategy}. "
                f"Supported strategies: {supported}"
            )

        strategy_class = self.STRATEGIES[strategy]
        self.strategy = strategy_class(**strategy_params)
        self.strategy_name = strategy

        logger.info(f"TextChunker initialized with '{strategy}' strategy")

    def chunk(self, text: str, metadata: dict = None) -> List[TextChunk]:
        """
        Chunk text using the configured strategy.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to all chunks

        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []

        return self.strategy.chunk(text, metadata=metadata or {})

    def chunk_with_metadata_per_chunk(
        self,
        text: str,
        base_metadata: dict,
        document_id: str
    ) -> List[TextChunk]:
        """
        Chunk text and attach enriched metadata to each chunk.

        Args:
            text: Text to chunk
            base_metadata: Base metadata for all chunks
            document_id: Unique document identifier

        Returns:
            List of TextChunk objects with enriched metadata
        """
        chunks = self.chunk(text, metadata=base_metadata)

        # Enrich each chunk's metadata
        for chunk in chunks:
            chunk.metadata.update({
                'document_id': document_id,
                'chunk_index': chunk.index,
                'total_chunks': len(chunks),
                'chunking_strategy': self.strategy_name
            })

        return chunks
