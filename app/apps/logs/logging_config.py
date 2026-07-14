import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # Важно! Не отключаем логи FastAPI/Uvicorn
    "formatters": {
        # Форматтер для локальной разработки (читаемый текст)
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        # Форматтер для продакшена (JSON)
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(module)s %(message)s",
            "json_ensure_ascii": False,
        }
    },
    "handlers": {
        # Вывод в консоль
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default", # Для продакшена поменяйте на "json"
            "stream": "ext://sys.stdout"
        },
        # Ротация в файл (полезно, если нет систем сбора логов типа ELK)
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json", # В файл всегда пишем JSON
            "filename": "app/apps/logs/memospace_service.log",
            "maxBytes": 5000000, # 5 MB
            "backupCount": 3
        }
    },
    "loggers": {
        # Наш основной логгер для приложения
        "memospace_app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        # Переопределяем логи сервера Uvicorn, чтобы они писались в наш файл
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

memospace_logger = logging.getLogger("memospace_app")