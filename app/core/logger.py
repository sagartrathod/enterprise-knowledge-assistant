import sys
import logging
from app.core.config import settings

def setup_logger(name: str = "app") -> logging.Logger:
    """Configures structured terminal stream log output formatters."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if initialized multiple times
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s] - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()