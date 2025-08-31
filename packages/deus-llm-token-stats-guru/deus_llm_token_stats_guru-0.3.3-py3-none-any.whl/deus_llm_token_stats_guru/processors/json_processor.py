"""JSON file processor with intelligent text extraction."""

import json
from pathlib import Path
from typing import Set, List, Any, Dict, Union
import logging

from .base import BaseFileProcessor
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class JSONProcessor(BaseFileProcessor):
    """Processor for JSON files with intelligent text extraction."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {".json", ".jsonl", ".ndjson"}
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "JSON"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of text strings extracted from JSON values
            
        Raises:
            FileProcessingError: If JSON cannot be processed
        """
        try:
            extension = file_path.suffix.lower()
            
            if extension in {".jsonl", ".ndjson"}:
                return self._process_jsonlines(file_path)
            else:
                return self._process_json(file_path)
                
        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from JSON: {e}") from e
    
    def _process_json(self, file_path: Path) -> List[str]:
        """Process regular JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            text_content = []
            self._extract_text_recursive(data, text_content)
            
            return text_content
            
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {e}") from e
    
    def _process_jsonlines(self, file_path: Path) -> List[str]:
        """Process JSON Lines (.jsonl) file."""
        text_content = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        line_text = []
                        self._extract_text_recursive(data, line_text)
                        
                        if line_text:
                            # Combine all text from this line into one string
                            text_content.append(" ".join(line_text))
                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON on line {line_num}: {e}")
                        continue
            
            return text_content
            
        except Exception as e:
            raise FileProcessingError(f"Failed to process JSON Lines file: {e}") from e
    
    def _extract_text_recursive(self, obj: Any, text_content: List[str]) -> None:
        """Recursively extract text content from JSON object.
        
        Args:
            obj: JSON object (dict, list, or primitive)
            text_content: List to append text strings to
        """
        if isinstance(obj, str):
            # Extract meaningful text (skip very short strings that might be IDs/codes)
            if len(obj.strip()) > 2:  # Arbitrary threshold for meaningful text
                text_content.append(obj.strip())
        
        elif isinstance(obj, (int, float, bool)):
            # Convert numbers and booleans to strings
            text_content.append(str(obj))
        
        elif isinstance(obj, dict):
            # Process dictionary values
            for key, value in obj.items():
                # Include key names if they're descriptive
                if len(key) > 2 and key.replace('_', '').replace('-', '').isalpha():
                    text_content.append(key.replace('_', ' ').replace('-', ' '))
                
                self._extract_text_recursive(value, text_content)
        
        elif isinstance(obj, list):
            # Process list items
            for item in obj:
                self._extract_text_recursive(item, text_content)
        
        # Skip null values and other types
    
    def process_file(self, file_path: Path) -> "CountResult":
        """Process JSON file with enhanced metadata.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            CountResult with JSON-specific statistics
        """
        logger.info(f"🔍 Processing JSON file: {file_path.name}")
        
        try:
            # Extract text and count tokens
            text_content = self.extract_text(file_path)
            total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
            
            # Get file statistics
            file_size = file_path.stat().st_size
            
            # Try to get JSON object count
            row_count = len(text_content)  # Number of text segments
            column_count = 1  # JSON is typically single-structure
            
            # For JSON Lines, each line is a separate record
            if file_path.suffix.lower() in {".jsonl", ".ndjson"}:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        row_count = sum(1 for line in file if line.strip())
                except Exception:
                    pass  # Fall back to text segment count
            
            from ..types import CountResult
            result: CountResult = {
                "file_path": str(file_path),
                "total_tokens": total_tokens,
                "row_count": row_count,
                "column_count": column_count,
                "encoding_model": self.encoding_model,
                "file_size_bytes": file_size,
            }
            
            logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens")
            return result
            
        except Exception as e:
            error_msg = f"Failed to process JSON file {file_path}: {e}"
            logger.error(f"❌ {error_msg}")
            raise FileProcessingError(error_msg, details={"file_path": str(file_path)}) from e