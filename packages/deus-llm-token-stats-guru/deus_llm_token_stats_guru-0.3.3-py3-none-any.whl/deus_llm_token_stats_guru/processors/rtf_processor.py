"""RTF (Rich Text Format) file processor."""

from pathlib import Path
from typing import Set, List
import logging
import re

from .base import BaseFileProcessor
from ..types import CountResult
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class RTFProcessor(BaseFileProcessor):
    """Processor for RTF (Rich Text Format) files."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {".rtf"}
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "RTF"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from RTF file.
        
        Args:
            file_path: Path to the RTF file
            
        Returns:
            List of text strings from the RTF document
            
        Raises:
            FileProcessingError: If RTF cannot be read
        """
        try:
            # Try striprtf first (dedicated RTF parser)
            try:
                from striprtf.striprtf import rtf_to_text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    rtf_content = file.read()
                    plain_text = rtf_to_text(rtf_content)
                    return self._split_text_into_chunks(plain_text)
            except ImportError:
                logger.debug("striprtf not available, using manual parsing")
                pass
            
            # Fallback to manual RTF parsing
            return self._extract_with_manual_parsing(file_path)
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to extract text from {file_path}: {e}")
            return []
    
    def _extract_with_manual_parsing(self, file_path: Path) -> List[str]:
        """Extract text using manual RTF parsing."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Basic RTF parsing - remove control codes and extract text
            # RTF control codes start with backslash
            
            # Remove RTF header and font table
            content = re.sub(r'\\rtf1[^{]*{', '', content)
            
            # Remove font table
            content = re.sub(r'{\\fonttbl[^}]*}', '', content)
            
            # Remove color table
            content = re.sub(r'{\\colortbl[^}]*}', '', content)
            
            # Remove other RTF control groups
            content = re.sub(r'{\\[^}]*}', '', content)
            
            # Remove RTF control words
            content = re.sub(r'\\[a-zA-Z]+\d*\s*', ' ', content)
            
            # Remove remaining control characters
            content = re.sub(r'\\[^a-zA-Z]', '', content)
            
            # Remove extra braces
            content = content.replace('{', '').replace('}', '')
            
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
            return self._split_text_into_chunks(content)
            
        except Exception as e:
            logger.debug(f"⚠️  Manual RTF parsing failed: {e}")
            return []
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into meaningful chunks."""
        if not text or not text.strip():
            return []
        
        # Split by paragraphs (double newlines) or sentences
        chunks = []
        
        # First try splitting by paragraphs
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        if paragraphs:
            chunks.extend(paragraphs)
        else:
            # Fallback: split by sentences
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            chunks.extend(sentences)
        
        # Filter out very short chunks
        meaningful_chunks = [chunk for chunk in chunks if len(chunk) > 10]
        
        return meaningful_chunks if meaningful_chunks else [text.strip()]
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process RTF file with enhanced metadata.
        
        Args:
            file_path: Path to the RTF file
            
        Returns:
            CountResult with RTF-specific statistics
        """
        logger.info(f"📝 Processing RTF file: {file_path.name}")
        
        # Extract text content
        text_content = self.extract_text(file_path)
        total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
        
        # Get basic file statistics
        file_size = file_path.stat().st_size
        
        # Estimate paragraphs/chunks
        chunk_count = len(text_content)
        
        result: CountResult = {
            "file_path": str(file_path),
            "total_tokens": total_tokens,
            "row_count": chunk_count,
            "column_count": 1,
            "encoding_model": self.encoding_model,
            "file_size_bytes": file_size,
        }
        
        logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens, {chunk_count} paragraphs")
        return result