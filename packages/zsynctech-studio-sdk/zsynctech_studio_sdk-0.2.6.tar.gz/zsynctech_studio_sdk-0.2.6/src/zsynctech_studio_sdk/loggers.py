import logging
from logging.config import dictConfig
from typing import Any


LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {
            "format": "%(asctime)s %(levelname)s [module:(%(module)s) line:%(lineno)d]: %(message)s",
            "datefmt": "%d-%m-%Y %H:%M"
        },
        "console": {
            "format": "[module:(%(module)s) %(lineno)d]: %(message)s", 
            "datefmt": "[%X]"
        },
    },
    "handlers": {
        "console": {
            "()": "rich.logging.RichHandler",
            "formatter": "console",
            "rich_tracebacks": False,
            "tracebacks_show_locals": False,
            "show_time": True,
            "show_level": True,
            "omit_repeated_times": False,
            "markup": False,
            "enable_link_path": True,
            "show_path": True,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "filename": "log.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": [
            "console",
            "file"
        ]
    },
    "loggers": {
        "zsynctech-studio-sdk": {
            "level": "DEBUG"
        }
    },
}

dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("zsynctech-studio-sdk")