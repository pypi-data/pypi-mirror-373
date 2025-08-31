"""CSV file processor."""

from pathlib import Path
from typing import Set, List
import logging

import pandas as pd

from .base import BaseFileProcessor
from ..types import CountResult
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class CSVProcessor(BaseFileProcessor):
    """Processor for CSV files."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {".csv", ".tsv"}
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "CSV"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of text strings (headers + all cell values)
            
        Raises:
            FileProcessingError: If CSV cannot be read
        """
        try:
            # Read CSV file
            separator = "\t" if file_path.suffix.lower() == ".tsv" else ","
            df = pd.read_csv(file_path, sep=separator)
            
            text_content = []
            
            # Add column headers as text
            header_text = " ".join(df.columns.astype(str))
            text_content.append(header_text)
            
            # Add all cell values as text
            for column in df.columns:
                column_text = " ".join(df[column].astype(str).fillna(""))
                text_content.append(column_text)
            
            return text_content
            
        except pd.errors.EmptyDataError:
            logger.warning(f"⚠️  Empty CSV file: {file_path}")
            return []
        except Exception as e:
            raise FileProcessingError(f"Failed to read CSV file: {e}") from e
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process CSV file with enhanced metadata.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            CountResult with CSV-specific statistics
        """
        logger.info(f"🔍 Processing CSV file: {file_path.name}")
        
        try:
            # Read CSV for metadata
            separator = "\t" if file_path.suffix.lower() == ".tsv" else ","
            df = pd.read_csv(file_path, sep=separator)
            
            # Extract text and count tokens
            text_content = self.extract_text(file_path)
            total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
            
            # Get file statistics
            file_size = file_path.stat().st_size
            
            result: CountResult = {
                "file_path": str(file_path),
                "total_tokens": total_tokens,
                "row_count": len(df),  # Actual row count for CSV
                "column_count": len(df.columns),  # Actual column count
                "encoding_model": self.encoding_model,
                "file_size_bytes": file_size,
            }
            
            logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens, {len(df)} rows, {len(df.columns)} columns")
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