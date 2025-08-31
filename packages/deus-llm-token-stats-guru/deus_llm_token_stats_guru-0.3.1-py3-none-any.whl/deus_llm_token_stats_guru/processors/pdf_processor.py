"""PDF file processor."""

from pathlib import Path
from typing import Set, List
import logging

from .base import BaseFileProcessor
from .._exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class PDFProcessor(BaseFileProcessor):
    """Processor for PDF files."""
    
    @property
    def supported_extensions(self) -> Set[str]:
        """Return supported file extensions."""
        return {".pdf"}
    
    @property
    def processor_name(self) -> str:
        """Return processor name."""
        return "PDF"
    
    def extract_text(self, file_path: Path) -> List[str]:
        """Extract text content from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of text strings (one per page)
            
        Raises:
            FileProcessingError: If PDF cannot be processed
        """
        try:
            # Try PyMuPDF first (faster and more reliable)
            try:
                import fitz  # PyMuPDF
                
                doc = fitz.open(file_path)
                text_content = []
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    
                    if text.strip():  # Only add non-empty pages
                        text_content.append(text)
                
                doc.close()
                return text_content
                
            except ImportError:
                # Fallback to PyPDF2
                try:
                    import PyPDF2
                    
                    text_content = []
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        
                        for page_num, page in enumerate(pdf_reader.pages):
                            try:
                                text = page.extract_text()
                                if text.strip():
                                    text_content.append(text)
                            except Exception as e:
                                logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                                continue
                    
                    return text_content
                    
                except ImportError:
                    # Final fallback to pdfplumber
                    try:
                        import pdfplumber
                        
                        text_content = []
                        with pdfplumber.open(file_path) as pdf:
                            for page_num, page in enumerate(pdf.pages):
                                try:
                                    text = page.extract_text()
                                    if text and text.strip():
                                        text_content.append(text)
                                except Exception as e:
                                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                                    continue
                        
                        return text_content
                        
                    except ImportError:
                        raise FileProcessingError(
                            "No PDF processing library available. "
                            "Please install one of: PyMuPDF (fitz), PyPDF2, or pdfplumber"
                        )
        
        except Exception as e:
            raise FileProcessingError(f"Failed to extract text from PDF: {e}") from e