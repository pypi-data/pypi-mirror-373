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
            List of text strings (all cell values as text)
            
        Raises:
            FileProcessingError: If CSV cannot be read
        """
        try:
            # First, try robust pandas reading with error handling
            separator = "\t" if file_path.suffix.lower() == ".tsv" else ","
            
            # Try multiple parsing strategies
            df = None
            parsing_strategies = [
                # Strategy 1: Flexible parsing with error handling
                {"sep": separator, "on_bad_lines": "skip", "engine": "python"},
                # Strategy 2: Read as string columns to avoid type inference issues  
                {"sep": separator, "dtype": str, "na_filter": False, "on_bad_lines": "skip", "engine": "python"},
                # Strategy 3: Most permissive - let pandas figure it out
                {"sep": None, "engine": "python", "on_bad_lines": "skip"},
            ]
            
            for i, strategy in enumerate(parsing_strategies):
                try:
                    df = pd.read_csv(file_path, **strategy)
                    logger.debug(f"✅ CSV parsed successfully with strategy {i+1}")
                    break
                except Exception as e:
                    logger.debug(f"⚠️  Strategy {i+1} failed: {e}")
                    continue
            
            if df is not None:
                text_content = []
                
                # Add column headers as text
                if not df.columns.empty:
                    header_text = " ".join(str(col) for col in df.columns if str(col) != "nan")
                    if header_text.strip():
                        text_content.append(header_text)
                
                # Add all cell values as text
                for column in df.columns:
                    try:
                        column_values = df[column].astype(str).fillna("").tolist()
                        # Filter out empty strings and 'nan'
                        meaningful_values = [val for val in column_values if val and val.lower() != 'nan']
                        if meaningful_values:
                            column_text = " ".join(meaningful_values)
                            text_content.append(column_text)
                    except Exception as e:
                        logger.debug(f"⚠️  Skipping problematic column {column}: {e}")
                        continue
                
                return text_content
            
            # If pandas fails completely, fall back to text-based extraction
            logger.warning(f"⚠️  Pandas parsing failed, falling back to text extraction for: {file_path}")
            return self._extract_text_fallback(file_path, separator)
            
        except Exception as e:
            logger.warning(f"⚠️  Standard CSV processing failed for {file_path}: {e}")
            # Final fallback to text extraction
            return self._extract_text_fallback(file_path, separator)
    
    def _extract_text_fallback(self, file_path: Path, separator: str) -> List[str]:
        """Fallback method to extract text from CSV by reading as plain text.
        
        Args:
            file_path: Path to the CSV file
            separator: Expected separator character
            
        Returns:
            List of text content extracted from CSV
        """
        try:
            text_content = []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
            
            if not lines:
                return []
            
            # Process each line and extract text content
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Split by separator and extract meaningful text
                parts = line.split(separator)
                meaningful_parts = []
                
                for part in parts:
                    # Clean up the part
                    cleaned = part.strip().strip('"').strip("'").strip()
                    # Skip empty parts, numbers-only, and common CSV artifacts
                    if (cleaned and 
                        len(cleaned) > 1 and 
                        not cleaned.lower() in {'nan', 'null', 'none', '', '""', "''"} and
                        not (cleaned.replace('.', '').replace('-', '').replace(',', '').isdigit())):
                        meaningful_parts.append(cleaned)
                
                if meaningful_parts:
                    line_text = " ".join(meaningful_parts)
                    text_content.append(line_text)
            
            logger.info(f"✅ Extracted text from {len(text_content)} lines using fallback method")
            return text_content
            
        except Exception as e:
            logger.error(f"❌ Even fallback text extraction failed for {file_path}: {e}")
            return []
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process CSV file with enhanced metadata.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            CountResult with CSV-specific statistics
        """
        logger.info(f"🔍 Processing CSV file: {file_path.name}")
        
        # Extract text content (this handles all the robust parsing)
        text_content = self.extract_text(file_path)
        total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
        
        # Get basic file statistics
        file_size = file_path.stat().st_size
        
        # Try to get CSV metadata with fallback
        row_count = 0
        column_count = 0
        
        try:
            separator = "\t" if file_path.suffix.lower() == ".tsv" else ","
            
            # Try the same strategies as extract_text for consistency
            parsing_strategies = [
                {"sep": separator, "on_bad_lines": "skip", "engine": "python"},
                {"sep": separator, "dtype": str, "na_filter": False, "on_bad_lines": "skip", "engine": "python"},
                {"sep": None, "engine": "python", "on_bad_lines": "skip"},
            ]
            
            for strategy in parsing_strategies:
                try:
                    df = pd.read_csv(file_path, **strategy)
                    row_count = len(df)
                    column_count = len(df.columns)
                    break
                except:
                    continue
            
            # If pandas completely fails, estimate from text content
            if row_count == 0 and text_content:
                # Rough estimate: number of text chunks as row count
                row_count = len(text_content)
                column_count = 1  # Default to 1 if we can't determine
                
        except Exception as e:
            logger.debug(f"⚠️  Could not determine CSV structure for {file_path}: {e}")
            # Fallback estimates
            if text_content:
                row_count = len(text_content) 
                column_count = 1
        
        result: CountResult = {
            "file_path": str(file_path),
            "total_tokens": total_tokens,
            "row_count": row_count,
            "column_count": column_count,
            "encoding_model": self.encoding_model,
            "file_size_bytes": file_size,
        }
        
        logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens, ~{row_count} rows, ~{column_count} columns")
        return result