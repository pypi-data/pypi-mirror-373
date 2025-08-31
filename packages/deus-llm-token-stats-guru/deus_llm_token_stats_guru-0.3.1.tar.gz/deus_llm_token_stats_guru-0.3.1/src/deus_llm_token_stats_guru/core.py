"""Core CSV token counting functionality using tiktoken."""

import time
import logging
from pathlib import Path
from typing import List, Optional, Generator
import pandas as pd
import tiktoken

from .types import CountResult, CountSummary
from ._exceptions import FileProcessingError, EncodingError, ConfigurationError


logger = logging.getLogger(__name__)


class CSVTokenCounter:
    """Count OpenAI tokens in CSV files using tiktoken."""
    
    def __init__(self, encoding_model: str = "gpt-4") -> None:
        """Initialize CSV token counter.
        
        Args:
            encoding_model: The tiktoken encoding model to use (default: "gpt-4")
        """
        self.encoding_model = encoding_model
        self._encoder = self._initialize_encoder()
        
    def _initialize_encoder(self) -> tiktoken.Encoding:
        """Initialize tiktoken encoder."""
        try:
            return tiktoken.encoding_for_model(self.encoding_model)
        except KeyError:
            try:
                # Fallback to cl100k_base for unknown models
                logger.warning(f"Unknown model {self.encoding_model}, using cl100k_base encoding")
                return tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                raise EncodingError(f"Failed to initialize tiktoken encoder: {e}") from e
    
    def count_tokens_in_text(self, text: str) -> int:
        """Count tokens in a single text string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens in the text
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        return len(self._encoder.encode(text))
    
    def count_tokens_in_csv(self, file_path: Path) -> CountResult:
        """Count tokens in a single CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            CountResult with token count and file statistics
            
        Raises:
            FileProcessingError: If file cannot be processed
        """
        logger.info(f"🔍 Processing CSV file: {file_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Convert all data to string and count tokens
            total_tokens = 0
            
            # Count tokens in column headers
            header_text = " ".join(df.columns.astype(str))
            total_tokens += self.count_tokens_in_text(header_text)
            
            # Count tokens in all cell values
            for column in df.columns:
                column_text = " ".join(df[column].astype(str).fillna(""))
                total_tokens += self.count_tokens_in_text(column_text)
            
            # Get file statistics
            file_size = file_path.stat().st_size
            
            result: CountResult = {
                "file_path": str(file_path),
                "total_tokens": total_tokens,
                "row_count": len(df),
                "column_count": len(df.columns),
                "encoding_model": self.encoding_model,
                "file_size_bytes": file_size,
            }
            
            logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens")
            return result
            
        except pd.errors.EmptyDataError:
            logger.warning(f"⚠️  Empty CSV file: {file_path}")
            return CountResult(
                file_path=str(file_path),
                total_tokens=0,
                row_count=0,
                column_count=0,
                encoding_model=self.encoding_model,
                file_size_bytes=file_path.stat().st_size,
            )
        except Exception as e:
            error_msg = f"Failed to process CSV file {file_path}: {e}"
            logger.error(f"❌ {error_msg}")
            raise FileProcessingError(error_msg, details={"file_path": str(file_path)}) from e
    
    def find_csv_files(self, directory: Path) -> Generator[Path, None, None]:
        """Find all CSV files in directory recursively.
        
        Args:
            directory: Directory to search in
            
        Yields:
            Path objects for each CSV file found
        """
        if not directory.exists():
            raise ConfigurationError(f"Directory does not exist: {directory}")
        
        if not directory.is_dir():
            raise ConfigurationError(f"Path is not a directory: {directory}")
        
        logger.info(f"🔍 Searching for CSV files in: {directory}")
        
        csv_files = list(directory.rglob("*.csv"))
        logger.info(f"📊 Found {len(csv_files)} CSV files")
        
        yield from csv_files
    
    def count_tokens_in_directory(self, directory: Path, recursive: bool = True) -> CountSummary:
        """Count tokens in all CSV files within a directory.
        
        Args:
            directory: Directory to search for CSV files
            recursive: Whether to search recursively (default: True)
            
        Returns:
            CountSummary with aggregated results
        """
        start_time = time.time()
        logger.info(f"🚀 Starting token count in directory: {directory}")
        
        directory = Path(directory)
        file_results: List[CountResult] = []
        
        # Process each CSV file
        for csv_file in self.find_csv_files(directory):
            try:
                result = self.count_tokens_in_csv(csv_file)
                file_results.append(result)
            except FileProcessingError as e:
                logger.error(f"❌ Failed to process {csv_file}: {e}")
                # Continue processing other files
                continue
        
        # Calculate summary statistics
        total_tokens = sum(result["total_tokens"] for result in file_results)
        total_rows = sum(result["row_count"] for result in file_results)
        total_file_size = sum(result["file_size_bytes"] for result in file_results)
        processing_time = time.time() - start_time
        
        summary: CountSummary = {
            "total_files": len(file_results),
            "total_tokens": total_tokens,
            "total_rows": total_rows,
            "total_file_size_bytes": total_file_size,
            "encoding_model": self.encoding_model,
            "file_results": file_results,
            "processing_time_seconds": processing_time,
        }
        
        logger.info(f"✅ Completed: {len(file_results)} files, {total_tokens:,} tokens in {processing_time:.2f}s")
        return summary