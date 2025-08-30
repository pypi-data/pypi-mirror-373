from celery import Celery

from app.core.config import settings

celery_dbname = "uniplore_va_ai"
result_backend_store = f"db+mysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_SERVER}:{settings.DB_PORT}/{celery_dbname}"

redis_db_index = 5
broker_store = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_SERVER}:{settings.REDIS_PORT}/{redis_db_index}"
celery_app = Celery('tasks', broker=broker_store, result_backend=result_backend_store)
