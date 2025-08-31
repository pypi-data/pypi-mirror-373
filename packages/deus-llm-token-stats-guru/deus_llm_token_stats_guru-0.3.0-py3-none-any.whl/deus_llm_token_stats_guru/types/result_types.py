"""Result type definitions for CSV token counting operations."""

from typing import TypedDict, List
from pathlib import Path


class CountResult(TypedDict):
    """Result of counting tokens in a single CSV file."""
    file_path: str
    total_tokens: int
    row_count: int
    column_count: int
    encoding_model: str
    file_size_bytes: int


class CountSummary(TypedDict):
    """Summary of counting tokens across multiple CSV files."""
    total_files: int
    total_tokens: int
    total_rows: int
    total_file_size_bytes: int
    encoding_model: str
    file_results: List[CountResult]
    processing_time_seconds: float