from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)

formatter = logging.Formatter(LOG_FORMAT)

logger = logging.getLogger("enterprise-rag")

logger.setLevel(logging.INFO)

logger.handlers.clear()

# ==========================================================
# Console
# ==========================================================

console_handler = logging.StreamHandler()

console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# ==========================================================
# Application Log
# ==========================================================

app_handler = RotatingFileHandler(
    f"{LOG_DIR}/app.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)

app_handler.setFormatter(formatter)

logger.addHandler(app_handler)

# ==========================================================
# Error Log
# ==========================================================

error_handler = RotatingFileHandler(
    f"{LOG_DIR}/error.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8",
)

error_handler.setLevel(logging.ERROR)

error_handler.setFormatter(formatter)

logger.addHandler(error_handler)

logger.propagate = False