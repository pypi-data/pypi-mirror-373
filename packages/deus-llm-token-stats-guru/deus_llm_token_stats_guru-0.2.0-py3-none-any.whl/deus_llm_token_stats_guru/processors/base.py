"""Base file processor interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Set, List
import logging

import tiktoken

from ..types import CountResult
from .._exceptions import FileProcessingError, EncodingError

logger = logging.getLogger(__name__)


class BaseFileProcessor(ABC):
    """Abstract base class for file processors."""
    
    def __init__(self, encoding_model: str = "gpt-4") -> None:
        """Initialize processor.
        
        Args:
            encoding_model: The tiktoken encoding model to use
        """
        self.encoding_model = encoding_model
        self._encoder = self._initialize_encoder()
    
    def _initialize_encoder(self) -> tiktoken.Encoding:
        """Initialize tiktoken encoder."""
        try:
            return tiktoken.encoding_for_model(self.encoding_model)
        except KeyError:
            try:
                logger.warning(f"Unknown model {self.encoding_model}, using cl100k_base encoding")
                return tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                raise EncodingError(f"Failed to initialize tiktoken encoder: {e}") from e
    
    def count_tokens_in_text(self, text: str) -> int:
        """Count tokens in a text string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens in the text
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        return len(self._encoder.encode(text))
    
    @property
    @abstractmethod
    def supported_extensions(self) -> Set[str]:
        """Return set of supported file extensions (lowercase, with dots)."""
        pass
    
    @property
    @abstractmethod
    def processor_name(self) -> str:
        """Return human-readable name of this processor."""
        pass
    
    def supports_file(self, file_path: Path) -> bool:
        """Check if this processor supports the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this processor can handle the file
        """
        return file_path.suffix.lower() in self.supported_extensions
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of text strings extracted from the file
            
        Raises:
            FileProcessingError: If file cannot be processed
        """
        pass
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process a file and return token count results.
        
        Args:
            file_path: Path to the file
            
        Returns:
            CountResult with token count and file statistics
            
        Raises:
            FileProcessingError: If file cannot be processed
        """
        logger.info(f"🔍 Processing {self.processor_name} file: {file_path.name}")
        
        try:
            # Extract text content
            text_content = self.extract_text(file_path)
            
            # Count tokens in all extracted text
            total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
            
            # Get file statistics
            file_size = file_path.stat().st_size
            
            result: CountResult = {
                "file_path": str(file_path),
                "total_tokens": total_tokens,
                "row_count": len(text_content),  # Number of text segments
                "column_count": 1,  # Most formats have single content stream
                "encoding_model": self.encoding_model,
                "file_size_bytes": file_size,
            }
            
            logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens")
            return result
            
        except Exception as e:
            error_msg = f"Failed to process {self.processor_name} file {file_path}: {e}"
            logger.error(f"❌ {error_msg}")
            raise FileProcessingError(error_msg, details={
                "file_path": str(file_path),
                "processor": self.processor_name
            }) from e