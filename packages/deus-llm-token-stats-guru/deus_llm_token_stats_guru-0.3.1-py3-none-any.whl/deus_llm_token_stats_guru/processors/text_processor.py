"""Text and Markdown file processor."""

from pathlib import Path
from typing import Set, List
import logging

from .base import BaseFileProcessor
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class TextProcessor(BaseFileProcessor):
    """Processor for plain text and markdown files."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {
            ".txt", ".text", 
            ".md", ".markdown", ".mdown", ".mkd",
            ".rst", ".rtf",
            ".log",
            ".py", ".js", ".html", ".css", ".xml", ".json",
            ".yml", ".yaml", ".toml", ".ini", ".cfg",
            ".sh", ".bat", ".ps1",
            ".c", ".cpp", ".h", ".hpp", ".java", ".cs", ".php", ".rb", ".go", ".rs",
        }
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "Text"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from text-based file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of text strings (paragraphs or logical sections)
            
        Raises:
            FileProcessingError: If file cannot be read
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
            
            content = None
            encoding_used = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        encoding_used = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise FileProcessingError(f"Could not decode file with any supported encoding")
            
            if encoding_used != 'utf-8':
                logger.info(f"Used {encoding_used} encoding for {file_path.name}")
            
            # Handle different file types
            extension = file_path.suffix.lower()
            
            if extension in {'.md', '.markdown', '.mdown', '.mkd'}:
                return self._process_markdown(content)
            elif extension in {'.py', '.js', '.java', '.c', '.cpp', '.cs', '.php', '.rb', '.go', '.rs'}:
                return self._process_code_file(content)
            elif extension in {'.html', '.xml'}:
                return self._process_markup(content)
            elif extension in {'.json', '.yml', '.yaml', '.toml'}:
                return self._process_structured_data(content)
            else:
                return self._process_plain_text(content)
            
        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from file: {e}") from e
    
    def _process_markdown(self, content: str) -> List[str]:
        """Process Markdown content into logical sections."""
        sections = []
        current_section = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Split on headers
            if line.startswith('#'):
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = [line]
                else:
                    current_section.append(line)
            elif line:
                current_section.append(line)
            elif current_section:
                # Empty line - end current section if it has content
                sections.append('\n'.join(current_section))
                current_section = []
        
        # Add final section
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections if sections else [content]
    
    def _process_code_file(self, content: str) -> List[str]:
        """Process code files by functions/classes or logical blocks."""
        # For now, split by empty lines to create logical blocks
        blocks = []
        current_block = []
        
        for line in content.split('\n'):
            if line.strip():
                current_block.append(line)
            elif current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks if blocks else [content]
    
    def _process_markup(self, content: str) -> List[str]:
        """Process HTML/XML content."""
        # Try to extract text content without HTML tags
        try:
            import re
            # Simple HTML tag removal
            text_content = re.sub(r'<[^>]+>', ' ', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Split into sentences or paragraphs
            sentences = [s.strip() for s in re.split(r'[.!?]+', text_content) if s.strip()]
            return sentences if sentences else [text_content]
            
        except Exception:
            # Fallback to treating as plain text
            return self._process_plain_text(content)
    
    def _process_structured_data(self, content: str) -> List[str]:
        """Process structured data files (JSON, YAML, etc.)."""
        # Split by logical structure
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        # Group lines into logical blocks
        blocks = []
        current_block = []
        
        for line in lines:
            current_block.append(line)
            
            # End block on closing braces/brackets or YAML document separators
            if line.endswith(('}', ']')) or line == '---' or line == '...':
                blocks.append('\n'.join(current_block))
                current_block = []
        
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks if blocks else [content]
    
    def _process_plain_text(self, content: str) -> List[str]:
        """Process plain text content."""
        # Split by paragraphs (double newlines)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # If no clear paragraphs, split by single newlines
        if len(paragraphs) <= 1 and '\n' in content:
            paragraphs = [line.strip() for line in content.split('\n') if line.strip()]
        
        return paragraphs if paragraphs else [content]