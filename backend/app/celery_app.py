from celery import Celery
from app.config import settings

celery_app = Celery(
    "smarteval_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Autodiscover tasks from the app folder
celery_app.autodiscover_tasks(["app"])
