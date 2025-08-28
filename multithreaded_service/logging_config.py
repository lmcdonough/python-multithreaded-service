# Lightweight structured logging using stdlig; JSON like without extra deps
import logging
import os
from typing import Optional

class KeyValueFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        return f"ts={self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} lvl={record.levelname} logger={record.name} msg={base}"
    
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    try:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(KeyValueFormatter("%(message)s"))
            logger.addHander(handler)
        env_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
        logger.setLevel(env_level)
        # Avoid duplicate logs across libs
        logger.propagate = False
        return logger
    except Exception: # Fallback to avoid crashing on logging issues
        return logging.getLogger(name)