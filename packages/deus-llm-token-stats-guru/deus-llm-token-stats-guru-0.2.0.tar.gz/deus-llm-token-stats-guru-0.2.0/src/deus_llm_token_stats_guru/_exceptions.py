"""Custom exceptions for CSV token counting operations."""

from typing import Optional, Dict, Any


class CSVTokenCounterError(Exception):
    """Base exception for CSV token counter operations."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class FileProcessingError(CSVTokenCounterError):
    """Error processing a specific file."""
    pass


class EncodingError(CSVTokenCounterError):
    """Error with tiktoken encoding."""
    pass


class ConfigurationError(CSVTokenCounterError):
    """Configuration error."""
    pass