import logging
import logging.handlers
import pathlib
import sys
from datetime import datetime
from typing import Dict, Any

# Load config once (import-time). Adjust as needed
from core.config_loader import Config  # noqa: E402

_cfg: Dict[str, Any] = Config.get_config().get("logging", {})
LEVEL_NAME = _cfg.get("level", "INFO").upper()
LEVEL = getattr(logging, LEVEL_NAME, logging.INFO)
KEEP_DAYS = int(_cfg.get("keep_days", 7))


LOG_DIR = pathlib.Path("./logs/")

LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"{datetime.now():%Y-%m-%d}.log"

file_handler = logging.handlers.TimedRotatingFileHandler(
    LOG_FILE, when="midnight", backupCount=KEEP_DAYS, encoding="utf-8"
)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s: %(message)s", "%H:%M:%S"
    )
)

logging.basicConfig(level=LEVEL, handlers=[file_handler])
logging.captureWarnings(True)  # capture warnings to log file


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with the specified name.

    Args:
        name (str): The name of the logger to retrieve.

    Returns:
        logging.Logger: A logger object corresponding to the given name.
    """
    return logging.getLogger(name)
