import logging
from pythonjsonlogger import jsonlogger


def logger(name_logger=None, level=logging.INFO):
    logger = logging.getLogger(name_logger or __name__)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
