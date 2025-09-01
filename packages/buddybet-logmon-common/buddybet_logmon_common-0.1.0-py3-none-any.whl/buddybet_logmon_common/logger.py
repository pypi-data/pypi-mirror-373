import logging
import json
import traceback
import os
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "data"):
            log_record["data"] = record.data

        return json.dumps(log_record)


def get_logger(name: str = "buddybet-logger", level: str | int | None = None) -> logging.Logger:
    """
    Crea un logger que emite logs en formato JSON.

    - Si `level` no está definido, se toma de la variable de entorno LOG_LEVEL.
    - Si tampoco existe, se usa INFO por defecto.
    """
    logger = logging.getLogger(name)

    if isinstance(level, str):
        level = level.upper()
        level = getattr(logging, level, logging.INFO)

    # Nivel desde variable de entorno si no se pasa por parámetro
    env_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level = level or getattr(logging, env_level, logging.INFO)

    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger
