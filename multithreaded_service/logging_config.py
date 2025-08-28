# Lightweight structured logging using stdlig; JSON like without extra deps
import logging
import os
from typing import Optional

# Purpose: provide a tiny formatter that outputs logs as key=value pairs.
# How: subclasses logging.Formatter and prefixes the formatted message with ts, lvl, logger, and msg.
# Use: human-readable structured logs that are easy to parse with simple tools.
class KeyValueFormatter(logging.Formatter):
    # Purpose: format a LogRecord into a single-line, key=value string.
    # How: call base Formatter.format to get the message, then add standardized fields.
    # Use: keeps timestamp, level, logger name, and message visible in consistent order.
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        return f"ts={self.formatTime(record, '%Y-%m-%dT%H:%M:%S')} lvl={record.levelname} logger={record.name} msg={base}"
    
# Purpose: return a configured logger instance with KeyValueFormatter attached.
# How: creates a StreamHandler with KeyValueFormatter if the logger has no handlers, sets level from arg or LOG_LEVEL env var, and disables propagation to avoid duplicate logs.
# Use: call get_logger(name) to get a ready-to-use, non-duplicating logger for modules.
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    try:
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(KeyValueFormatter("%(message)s"))
            logger.addHandler(handler)
        env_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
        logger.setLevel(env_level)
        # Avoid duplicate logs across libs
        logger.propagate = False
        return logger
    except Exception: # Fallback to avoid crashing on logging issues
        return logging.getLogger(name)