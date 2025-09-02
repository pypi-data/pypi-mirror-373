import os

from decouple import config


# supportal configuration
SUPPORTAL_SETTINGS = {
    "OPENAI_API_KEY": config("OPENAI_API_KEY", default=""),
    "OPENAI_MODEL": config("OPENAI_MODEL", default="gpt-3.5-turbo"),
    "OPENAI_EMBEDDING_MODEL": config(
        "OPENAI_EMBEDDING_MODEL", default="text-embedding-ada-002"
    ),
    "MAX_TOKENS": config("MAX_TOKENS", default=1000, cast=int),
    "TEMPERATURE": config("TEMPERATURE", default=0.7, cast=float),
    "CHUNK_SIZE": config("CHUNK_SIZE", default=1000, cast=int),
    "CHUNK_OVERLAP": config("CHUNK_OVERLAP", default=200, cast=int),
    "TOP_K_RESULTS": config("TOP_K_RESULTS", default=5, cast=int),
    "VECTOR_DB_PATH": config("VECTOR_DB_PATH", default="vector_db/"),
    "ALLOWED_FILE_TYPES": ["pdf", "docx", "txt"],
    "MAX_FILE_SIZE": config(
        "MAX_FILE_SIZE", default=10 * 1024 * 1024, cast=int
    ),  # 10mb
    "REDIS_URL": config("REDIS_URL", default="redis://localhost:6379/0"),
    "CELERY_BROKER_URL": config(
        "CELERY_BROKER_URL", default="redis://localhost:6379/0"
    ),
    "ENABLE_LOGGING": config("ENABLE_LOGGING", default=True, cast=bool),
    "LOG_LEVEL": config("LOG_LEVEL", default="INFO"),
}

# channel layers configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# celery configuration
CELERY_BROKER_URL = SUPPORTAL_SETTINGS["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = SUPPORTAL_SETTINGS["CELERY_BROKER_URL"]
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/supportal.log",
            "maxBytes": 1024 * 1024 * 5,  # 5mb
            "backupCount": 5,
            "formatter": "verbose",
            "level": SUPPORTAL_SETTINGS["LOG_LEVEL"],
        },
    },
    "loggers": {
        "django_supportal": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
os.makedirs("media", exist_ok=True)
os.makedirs("vector_db", exist_ok=True)
