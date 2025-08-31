"""Logging configuration for CSV token counter."""

import logging
import sys
from pathlib import Path
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """Structured log formatter with emoji indicators."""
    
    EMOJI_MAP = {
        'DEBUG': '🔍',
        'INFO': '📋',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🛑'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        emoji = self.EMOJI_MAP.get(record.levelname, '📋')
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        return f"{timestamp} | {emoji} {record.levelname:8} | {record.name} | {record.getMessage()}"


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """Setup structured logging for the application.
    
    Args:
        debug: Enable debug mode logging
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if debug else logging.INFO
    formatter = StructuredFormatter()
    
    # Configure root logger
    logger = logging.getLogger('csv_token_counter')
    logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger