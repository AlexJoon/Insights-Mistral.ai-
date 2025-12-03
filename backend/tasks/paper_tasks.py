"""
Background tasks for fetching and processing academic papers.
Scheduled jobs run by Celery.
"""
from backend.tasks.celery_app import celery_app
from backend.services.semantic_scholar_service import SemanticScholarService
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_service import VectorService
from backend.services.paper_summarization_service import PaperSummarizationService
from backend.config.settings import load_config
from typing import List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.tasks.paper_tasks.fetch_new_papers", bind=True, max_retries=3)
def fetch_new_papers(self, fields_of_study: List[str], days_back: int = 7):
    """
    Fetch new papers from Semantic Scholar.

    Args:
        fields_of_study: Academic fields to monitor
        days_back: How many days back to search

    Returns:
        Dict with stats about papers fetched
    """
    try:
        config = load_config()

        # Initialize services
        scholar_service = SemanticScholarService()
        embedding_service = EmbeddingService(config.mistral.api_key)
        vector_service = VectorService()

        logger.info(f"Fetching papers from last {days_back} days in fields: {fields_of_study}")

        # Fetch papers
        papers = []
        for field in fields_of_study:
            field_papers = scholar_service.search_papers(
                query=field,
                fields_of_study=[field],
                limit=50
            )
            papers.extend(field_papers)

        logger.info(f"Found {len(papers)} total papers")

        # Remove duplicates
        unique_papers = {p.paper_id: p for p in papers}.values()

        # Generate embeddings and store in vector DB
        stored_count = 0
        for paper in unique_papers:
            if not paper.abstract:
                continue

            try:
                # Generate embedding
                embedding_response = embedding_service.embed_paper(
                    title=paper.title,
                    abstract=paper.abstract
                )

                if not embedding_response:
                    continue

                # Store in vector DB
                vector_service.add_paper(
                    paper_id=paper.paper_id,
                    title=paper.title,
                    abstract=paper.abstract,
                    embedding=embedding_response.embedding,
                    metadata={
                        "authors": paper.authors,
                        "year": paper.year,
                        "venue": paper.venue,
                        "citation_count": paper.citation_count,
                        "url": paper.url,
                        "fields_of_study": paper.fields_of_study,
                        "fetched_at": datetime.utcnow().isoformat()
                    }
                )

                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to process paper {paper.paper_id}: {e}")
                continue

        # Persist vector DB
        vector_service.persist()

        logger.info(f"Successfully stored {stored_count} papers")

        return {
            "status": "success",
            "papers_found": len(unique_papers),
            "papers_stored": stored_count,
            "fields": fields_of_study,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Paper fetching task failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="backend.tasks.paper_tasks.update_paper_embeddings")
def update_paper_embeddings():
    """
    Update embeddings for papers that don't have them yet.
    Runs daily to catch any papers that failed initial processing.
    """
    try:
        logger.info("Starting embedding update task")

        # TODO: Query database for papers without embeddings
        # For now, this is a placeholder

        return {
            "status": "success",
            "papers_updated": 0,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Embedding update failed: {e}")
        return {"status": "failed", "error": str(e)}


@celery_app.task(name="backend.tasks.paper_tasks.summarize_papers_for_topic")
def summarize_papers_for_topic(topic: str, paper_ids: List[str]):
    """
    Generate summaries for a list of papers on a specific topic.

    Args:
        topic: Research topic
        paper_ids: List of paper IDs to summarize

    Returns:
        Dict with summaries
    """
    try:
        config = load_config()

        # Initialize services
        vector_service = VectorService()
        summarization_service = PaperSummarizationService(config.mistral.api_key)

        summaries = []

        for paper_id in paper_ids:
            # Get paper from vector DB
            paper = vector_service.get_paper(paper_id)

            if not paper:
                continue

            # Generate summary
            summary = summarization_service.summarize_paper(
                title=paper.title,
                abstract=paper.abstract,
                authors=paper.metadata.get("authors", [])
            )

            summary.paper_id = paper_id
            summaries.append(summary.to_dict())

        logger.info(f"Generated {len(summaries)} summaries for topic: {topic}")

        return {
            "status": "success",
            "summaries": summaries,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Summarization task failed: {e}")
        return {"status": "failed", "error": str(e)}
