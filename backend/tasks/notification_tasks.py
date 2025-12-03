"""
Background tasks for sending notifications and digests.
"""
from backend.tasks.celery_app import celery_app
from backend.services.email_service import EmailService, EmailConfig
from backend.services.vector_service import VectorService
from backend.services.paper_summarization_service import PaperSummarizationService
from backend.config.settings import load_config
from typing import List, Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.tasks.notification_tasks.send_weekly_digest", bind=True)
def send_weekly_digest(self):
    """
    Send weekly research digest to all subscribed users.

    Runs every Monday at 8 AM UTC.
    """
    try:
        config = load_config()

        # Initialize services
        email_service = EmailService(EmailConfig(
            api_key=config.email.api_key,
            from_email=config.email.from_email,
            from_name=config.email.from_name
        ))
        vector_service = VectorService()
        summarization_service = PaperSummarizationService(config.mistral.api_key)

        logger.info("Starting weekly digest task")

        # TODO: Query database for subscribed users and their topics
        # For now, using mock data
        subscribers = [
            {
                "email": "user@example.com",
                "name": "Research User",
                "topics": ["Computer Science", "AI"]
            }
        ]

        total_sent = 0
        total_failed = 0

        for subscriber in subscribers:
            try:
                # Get recent papers for user's topics
                user_papers = []

                for topic in subscriber["topics"]:
                    # Search vector DB for recent papers in this topic
                    # This would ideally filter by date metadata
                    # For now, we'll get top papers

                    # TODO: Implement actual search with date filtering
                    # papers = await vector_service.search_papers(
                    #     query_embedding=topic_embedding,
                    #     n_results=10,
                    #     where={"fields_of_study": topic}
                    # )

                    pass

                # Send digest if we have papers
                if user_papers:
                    success = email_service.send_weekly_digest(
                        to_email=subscriber["email"],
                        user_name=subscriber["name"],
                        papers=user_papers,
                        topic=", ".join(subscriber["topics"])
                    )

                    if success:
                        total_sent += 1
                    else:
                        total_failed += 1

            except Exception as e:
                logger.error(f"Failed to send digest to {subscriber['email']}: {e}")
                total_failed += 1
                continue

        logger.info(f"Weekly digest complete: {total_sent} sent, {total_failed} failed")

        return {
            "status": "success",
            "sent": total_sent,
            "failed": total_failed,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Weekly digest task failed: {e}")
        # Retry once after 5 minutes
        raise self.retry(exc=e, countdown=300, max_retries=1)


@celery_app.task(name="backend.tasks.notification_tasks.send_paper_alert")
def send_paper_alert(user_email: str, paper_id: str):
    """
    Send immediate alert about a highly relevant paper.

    Args:
        user_email: User email address
        paper_id: Paper to alert about
    """
    try:
        config = load_config()

        email_service = EmailService(EmailConfig(
            api_key=config.email.api_key,
            from_email=config.email.from_email,
            from_name=config.email.from_name
        ))

        vector_service = VectorService()

        # Get paper details
        paper = vector_service.get_paper(paper_id)

        if not paper:
            logger.error(f"Paper not found: {paper_id}")
            return {"status": "failed", "error": "Paper not found"}

        # Send alert email
        subject = f"New Paper Alert: {paper.title}"

        html_content = f"""
<html>
<body>
    <h2>🔔 New Paper Alert</h2>
    <p>A new paper matching your interests has been published:</p>

    <h3>{paper.title}</h3>
    <p>{paper.abstract[:300]}...</p>

    <a href="{paper.metadata.get('url', '#')}">Read full paper</a>
</body>
</html>
"""

        success = email_service.send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )

        return {
            "status": "success" if success else "failed",
            "paper_id": paper_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Paper alert failed: {e}")
        return {"status": "failed", "error": str(e)}
