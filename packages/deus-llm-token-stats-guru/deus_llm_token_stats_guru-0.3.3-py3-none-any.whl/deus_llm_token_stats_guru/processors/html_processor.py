"""HTML file processor (especially for Google Docs exports)."""

from pathlib import Path
from typing import Set, List
import logging
import re

from .base import BaseFileProcessor
from ..types import CountResult
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class HTMLProcessor(BaseFileProcessor):
    """Processor for HTML files, especially Google Docs exports."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {".html", ".htm", ".xhtml"}
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "HTML"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from HTML file.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            List of text strings from the HTML document
            
        Raises:
            FileProcessingError: If HTML cannot be read
        """
        try:
            # Try BeautifulSoup first (most comprehensive HTML parser)
            try:
                from bs4 import BeautifulSoup
                return self._extract_with_beautifulsoup(file_path)
            except ImportError:
                logger.debug("BeautifulSoup not available, trying html.parser")
                pass
            
            # Fallback to built-in html.parser
            try:
                from html.parser import HTMLParser
                return self._extract_with_html_parser(file_path)
            except Exception as e:
                logger.debug(f"html.parser failed: {e}")
                pass
            
            # Final fallback: regex-based HTML stripping
            return self._extract_with_regex(file_path)
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to extract text from {file_path}: {e}")
            return []
    
    def _extract_with_beautifulsoup(self, file_path: Path) -> List[str]:
        """Extract text using BeautifulSoup."""
        from bs4 import BeautifulSoup
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "head", "title", "meta"]):
                script.decompose()
            
            text_content = []
            
            # Extract text from different HTML elements
            
            # Headings (h1-h6)
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = heading.get_text(strip=True)
                if text and len(text) > 1:
                    text_content.append(f"Heading: {text}")
            
            # Paragraphs
            for paragraph in soup.find_all('p'):
                text = paragraph.get_text(strip=True)
                if text and len(text) > 10:  # Longer threshold for paragraphs
                    text_content.append(text)
            
            # List items
            for list_item in soup.find_all('li'):
                text = list_item.get_text(strip=True)
                if text and len(text) > 1:
                    text_content.append(f"• {text}")
            
            # Table cells
            for cell in soup.find_all(['td', 'th']):
                text = cell.get_text(strip=True)
                if text and len(text) > 1:
                    text_content.append(text)
            
            # Blockquotes
            for quote in soup.find_all('blockquote'):
                text = quote.get_text(strip=True)
                if text and len(text) > 1:
                    text_content.append(f"Quote: {text}")
            
            # Divs and spans (for Google Docs content)
            for div in soup.find_all(['div', 'span']):
                text = div.get_text(strip=True)
                # Only add if it's not already captured by other elements
                if text and len(text) > 10 and text not in [t.replace("Heading: ", "").replace("Quote: ", "").replace("• ", "") for t in text_content]:
                    text_content.append(text)
            
            # If no structured content found, get all text
            if not text_content:
                body_text = soup.get_text(strip=True)
                if body_text:
                    # Split into sentences or paragraphs
                    sentences = [s.strip() for s in re.split(r'[.!?]+', body_text) if s.strip() and len(s) > 10]
                    text_content.extend(sentences)
            
            return text_content
            
        except Exception as e:
            logger.debug(f"⚠️  BeautifulSoup extraction failed: {e}")
            return []
    
    def _extract_with_html_parser(self, file_path: Path) -> List[str]:
        """Extract text using built-in HTML parser."""
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_content = []
                self.current_text = []
                self.in_script = False
                self.in_style = False
            
            def handle_starttag(self, tag, attrs):
                if tag.lower() in ['script', 'style']:
                    self.in_script = True
                    self.in_style = True
                elif tag.lower() in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    if self.current_text:
                        text = ' '.join(self.current_text).strip()
                        if text and len(text) > 1:
                            self.text_content.append(text)
                        self.current_text = []
            
            def handle_endtag(self, tag):
                if tag.lower() in ['script', 'style']:
                    self.in_script = False
                    self.in_style = False
                elif tag.lower() in ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    if self.current_text:
                        text = ' '.join(self.current_text).strip()
                        if text and len(text) > 1:
                            self.text_content.append(text)
                        self.current_text = []
            
            def handle_data(self, data):
                if not self.in_script and not self.in_style:
                    data = data.strip()
                    if data:
                        self.current_text.append(data)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            extractor = TextExtractor()
            extractor.feed(content)
            
            # Add any remaining text
            if extractor.current_text:
                text = ' '.join(extractor.current_text).strip()
                if text and len(text) > 1:
                    extractor.text_content.append(text)
            
            return extractor.text_content
            
        except Exception as e:
            logger.debug(f"⚠️  HTML parser extraction failed: {e}")
            return []
    
    def _extract_with_regex(self, file_path: Path) -> List[str]:
        """Extract text using regex-based HTML tag removal."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Remove script and style content
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove HTML comments
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            
            # Remove HTML tags
            content = re.sub(r'<[^>]+>', ' ', content)
            
            # Decode HTML entities
            try:
                import html
                content = html.unescape(content)
            except ImportError:
                # Basic entity decoding
                content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
            
            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Split into sentences
            sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip() and len(s) > 10]
            
            return sentences if sentences else [content] if content else []
            
        except Exception as e:
            logger.debug(f"⚠️  Regex extraction failed: {e}")
            return []
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process HTML file with enhanced metadata.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            CountResult with HTML-specific statistics
        """
        logger.info(f"🌐 Processing HTML file: {file_path.name}")
        
        # Extract text content
        text_content = self.extract_text(file_path)
        total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
        
        # Get basic file statistics
        file_size = file_path.stat().st_size
        
        # Count different content types
        headings = len([t for t in text_content if t.startswith("Heading:")])
        paragraphs = len([t for t in text_content if not t.startswith(("Heading:", "Quote:", "•"))])
        
        result: CountResult = {
            "file_path": str(file_path),
            "total_tokens": total_tokens,
            "row_count": paragraphs,
            "column_count": headings,
            "encoding_model": self.encoding_model,
            "file_size_bytes": file_size,
        }
        
        logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens, {paragraphs} paragraphs, {headings} headings")
        return result