"""Logging configuration."""
import logging
import os
from logging.handlers import RotatingFileHandler
from config import Config


def setup_logger(app):
    log_dir = os.path.dirname(Config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)

    app.logger.handlers.clear()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(level)

    try:
        file_handler = RotatingFileHandler(
            Config.LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        app.logger.addHandler(file_handler)
    except OSError as e:
        app.logger.warning(f"File logging disabled ({Config.LOG_FILE}): {e}")

    return app.logger
