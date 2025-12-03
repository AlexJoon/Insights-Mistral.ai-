"""
Celery application configuration for background tasks.
Handles scheduled jobs like paper fetching and email digests.
"""
from celery import Celery
from celery.schedules import crontab
import os

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "insights_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "backend.tasks.paper_tasks",
        "backend.tasks.notification_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks configuration
celery_app.conf.beat_schedule = {
    # Fetch new papers daily at 2 AM UTC
    "fetch-new-papers-daily": {
        "task": "backend.tasks.paper_tasks.fetch_new_papers",
        "schedule": crontab(hour=2, minute=0),
        "args": (["Computer Science", "AI", "Machine Learning"], 7)  # Last 7 days
    },
    # Send weekly digest every Monday at 8 AM UTC
    "send-weekly-digest": {
        "task": "backend.tasks.notification_tasks.send_weekly_digest",
        "schedule": crontab(day_of_week=1, hour=8, minute=0)
    },
    # Update paper embeddings daily at 3 AM UTC
    "update-embeddings": {
        "task": "backend.tasks.paper_tasks.update_paper_embeddings",
        "schedule": crontab(hour=3, minute=0)
    },
}

# Optional: Configure logging
celery_app.conf.worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
celery_app.conf.worker_task_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s"
