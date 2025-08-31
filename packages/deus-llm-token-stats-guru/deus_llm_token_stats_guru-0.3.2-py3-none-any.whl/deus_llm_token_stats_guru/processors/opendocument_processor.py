"""OpenDocument (LibreOffice/OpenOffice) file processor."""

from pathlib import Path
from typing import Set, List
import logging

from .base import BaseFileProcessor
from ..types import CountResult
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class OpenDocumentProcessor(BaseFileProcessor):
    """Processor for OpenDocument files (ODT, ODS, ODP)."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {".odt", ".ods", ".odp", ".odg", ".odf"}
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "OpenDocument"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from OpenDocument file.
        
        Args:
            file_path: Path to the OpenDocument file
            
        Returns:
            List of text strings from the document
            
        Raises:
            FileProcessingError: If document cannot be read
        """
        try:
            # Try odfpy first (dedicated OpenDocument library)
            try:
                from odf.opendocument import load
                from odf.text import P, H, S, Tab
                from odf.table import Table, TableRow, TableCell
                return self._extract_with_odfpy(file_path)
            except ImportError:
                logger.debug("odfpy not available, trying ZIP extraction")
                pass
            
            # Fallback to ZIP-based extraction
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                return self._extract_with_zip(file_path)
            except Exception as e:
                logger.debug(f"ZIP extraction failed: {e}")
                pass
            
            # Final fallback - try as plain text
            try:
                return self._extract_as_text(file_path)
            except Exception:
                pass
            
            logger.warning(f"⚠️  No suitable OpenDocument processing method found for {file_path}")
            return []
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to extract text from {file_path}: {e}")
            return []
    
    def _extract_with_odfpy(self, file_path: Path) -> List[str]:
        """Extract text using odfpy library."""
        from odf.opendocument import load
        from odf.text import P, H
        from odf.table import Table, TableRow, TableCell
        
        text_content = []
        doc = load(file_path)
        
        # Determine document type and extract accordingly
        extension = file_path.suffix.lower()
        
        if extension == ".odt":  # Text document
            text_content.extend(self._extract_odt_content(doc))
        elif extension == ".ods":  # Spreadsheet
            text_content.extend(self._extract_ods_content(doc))
        elif extension == ".odp":  # Presentation
            text_content.extend(self._extract_odp_content(doc))
        else:  # Generic extraction
            text_content.extend(self._extract_generic_content(doc))
        
        return text_content
    
    def _extract_odt_content(self, doc) -> List[str]:
        """Extract content from ODT (text) document."""
        from odf.text import P, H
        
        text_content = []
        
        # Extract paragraphs and headings
        for element in doc.getElementsByType(P) + doc.getElementsByType(H):
            text = str(element).strip()
            if text and len(text) > 1:
                # Clean up the text (remove XML tags)
                import re
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                if clean_text and len(clean_text) > 1:
                    text_content.append(clean_text)
        
        return text_content
    
    def _extract_ods_content(self, doc) -> List[str]:
        """Extract content from ODS (spreadsheet) document."""
        from odf.table import Table, TableRow, TableCell
        
        text_content = []
        
        # Extract tables
        for table in doc.getElementsByType(Table):
            table_name = table.getAttribute('name') or "Sheet"
            text_content.append(f"Table: {table_name}")
            
            for row in table.getElementsByType(TableRow):
                row_text = []
                for cell in row.getElementsByType(TableCell):
                    cell_text = str(cell).strip()
                    if cell_text:
                        import re
                        clean_text = re.sub(r'<[^>]+>', '', cell_text).strip()
                        if clean_text and len(clean_text) > 1:
                            row_text.append(clean_text)
                
                if row_text:
                    text_content.append(" ".join(row_text))
        
        return text_content
    
    def _extract_odp_content(self, doc) -> List[str]:
        """Extract content from ODP (presentation) document."""
        from odf.draw import Page
        from odf.text import P, H
        
        text_content = []
        
        # Extract slides (pages)
        pages = doc.getElementsByType(Page)
        for page_num, page in enumerate(pages, 1):
            text_content.append(f"Slide {page_num}")
            
            # Extract text from the slide
            for element in page.getElementsByType(P) + page.getElementsByType(H):
                text = str(element).strip()
                if text and len(text) > 1:
                    import re
                    clean_text = re.sub(r'<[^>]+>', '', text).strip()
                    if clean_text and len(clean_text) > 1:
                        text_content.append(clean_text)
        
        return text_content
    
    def _extract_generic_content(self, doc) -> List[str]:
        """Generic content extraction for any OpenDocument file."""
        from odf.text import P, H
        
        text_content = []
        
        # Extract all text elements
        for element in doc.getElementsByType(P) + doc.getElementsByType(H):
            text = str(element).strip()
            if text and len(text) > 1:
                import re
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                if clean_text and len(clean_text) > 1:
                    text_content.append(clean_text)
        
        return text_content
    
    def _extract_with_zip(self, file_path: Path) -> List[str]:
        """Extract text using ZIP-based parsing (OpenDocument files are ZIP archives)."""
        import zipfile
        import xml.etree.ElementTree as ET
        
        text_content = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Try to read content.xml (main content)
                if 'content.xml' in zip_file.namelist():
                    with zip_file.open('content.xml') as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        
                        # Extract text from all elements
                        for elem in root.iter():
                            if elem.text and elem.text.strip():
                                text = elem.text.strip()
                                if len(text) > 1:
                                    text_content.append(text)
                
                # Also try styles.xml for additional text
                if 'styles.xml' in zip_file.namelist():
                    try:
                        with zip_file.open('styles.xml') as xml_file:
                            tree = ET.parse(xml_file)
                            root = tree.getroot()
                            
                            for elem in root.iter():
                                if elem.text and elem.text.strip():
                                    text = elem.text.strip()
                                    if len(text) > 1 and text not in text_content:
                                        text_content.append(text)
                    except Exception:
                        pass  # Styles extraction is optional
        
        except Exception as e:
            logger.debug(f"⚠️  ZIP extraction failed: {e}")
        
        return text_content
    
    def _extract_as_text(self, file_path: Path) -> List[str]:
        """Final fallback: try to extract as plain text."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                # Split into meaningful chunks
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                return [line for line in lines if len(line) > 1]
        except Exception:
            return []
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process OpenDocument file with enhanced metadata.
        
        Args:
            file_path: Path to the OpenDocument file
            
        Returns:
            CountResult with document-specific statistics
        """
        extension = file_path.suffix.lower()
        doc_type = {
            '.odt': 'Text Document',
            '.ods': 'Spreadsheet', 
            '.odp': 'Presentation',
            '.odg': 'Drawing',
            '.odf': 'Formula'
        }.get(extension, 'OpenDocument')
        
        logger.info(f"📄 Processing {doc_type}: {file_path.name}")
        
        # Extract text content
        text_content = self.extract_text(file_path)
        total_tokens = sum(self.count_tokens_in_text(text) for text in text_content)
        
        # Get basic file statistics
        file_size = file_path.stat().st_size
        
        # Estimate structure based on content
        if extension == ".ods":
            # For spreadsheets, count tables and rows
            table_count = len([line for line in text_content if line.startswith("Table:")])
            row_count = len([line for line in text_content if not line.startswith("Table:")])
            column_count = table_count
        elif extension == ".odp":
            # For presentations, count slides and content
            slide_count = len([line for line in text_content if line.startswith("Slide ")])
            content_count = len([line for line in text_content if not line.startswith("Slide ")])
            row_count = content_count
            column_count = slide_count
        else:
            # For text documents, count paragraphs
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
        
        logger.info(f"✅ Processed {file_path.name}: {total_tokens:,} tokens, {row_count} items")
        return result