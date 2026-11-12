"""
Celery application configuration.
Uses RabbitMQ as broker and Redis as result backend.
"""

from celery import Celery

from app.core import get_settings

settings = get_settings()

celery_app = Celery(
    "ecom_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task settings
    task_track_started=True,
    task_time_limit=300,         # 5 minutes hard limit
    task_soft_time_limit=240,    # 4 minutes soft limit
    task_acks_late=True,         # Acknowledge tasks after execution
    worker_prefetch_multiplier=1,

    # Result settings
    result_expires=3600,  # Results expire after 1 hour

    # Retry settings
    task_default_retry_delay=60,  # 1 minute default retry delay
    task_max_retries=3,

    # Auto-discover tasks
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.notification_tasks.*": {"queue": "notification"},
        "app.tasks.payment_tasks.*": {"queue": "payment"},
        "app.tasks.report_tasks.*": {"queue": "report"},
    },
)

# Auto-discover tasks from all registered modules
celery_app.autodiscover_tasks(["app.tasks"])
