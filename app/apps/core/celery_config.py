from celery import Celery

from app.apps.core.settings import redis_settings

celery_app = Celery(main="app", broker=redis_settings.redis_url, backend=redis_settings.redis_url)

celery_app.autodiscover_tasks(packages=["app.apps"])