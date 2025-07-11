from celery import Celery

from apps.core.settings import settings

celery_app = Celery(main="apps", broker=settings.redis_settings.redis_url, backend=settings.redis_settings.redis_url)

celery_app.autodiscover_tasks(packages=["apps.apps"])