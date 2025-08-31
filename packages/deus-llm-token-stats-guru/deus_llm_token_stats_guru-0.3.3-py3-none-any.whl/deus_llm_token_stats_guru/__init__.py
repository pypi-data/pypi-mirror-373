"""Deus LLM Token Stats Guru - Advanced LLM token analysis and statistics toolkit for various data formats."""

__version__ = "0.3.3"
__author__ = "deus-global"
__email__ = "sean@deus.com.tw"

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