from celery import Celery

from apps.core.settings import redis_settings

celery_app = Celery(main="apps", broker=redis_settings.redis_url, backend=redis_settings.redis_url)

celery_app.autodiscover_tasks(packages=["apps.apps"])