"""Deus LLM Token Stats Guru - Advanced LLM token analysis and statistics toolkit for various data formats."""

__version__ = "0.3.2"
__author__ = "Deus LLM Token Stats Guru"
__email__ = "noreply@example.com"

from .document_processor import DocumentProcessor, CSVTokenCounter
from .core import CSVTokenCounter as LegacyCSVTokenCounter
from .types import CountResult, CountSummary

__all__ = [
    "DocumentProcessor", 
    "CSVTokenCounter",  # Now points to DocumentProcessor for multi-format support
    "LegacyCSVTokenCounter",  # Original CSV-only implementation
    "CountResult", 
    "CountSummary"
]