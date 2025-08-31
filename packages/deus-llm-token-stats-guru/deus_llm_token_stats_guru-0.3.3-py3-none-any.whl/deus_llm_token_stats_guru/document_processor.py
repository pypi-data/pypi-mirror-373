"""Multi-format document processor for token counting."""

import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Generator, Set

from .processors import (
    BaseFileProcessor,
    CSVProcessor,
    PDFProcessor,
    DOCXProcessor,
    XLSXProcessor,
    PPTXProcessor,
    OpenDocumentProcessor,
    RTFProcessor,
    HTMLProcessor,
    TextProcessor,
    JSONProcessor,
)
from .types import CountResult, CountSummary
from ._exceptions import FileProcessingError, ConfigurationError

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Multi-format document processor for token counting."""
    
    def __init__(self, encoding_model: str = "gpt-4") -> None:
        """Initialize document processor.
        
        Args:
            encoding_model: The tiktoken encoding model to use (default: "gpt-4")
        """
        self.encoding_model = encoding_model
        self._processors: List[BaseFileProcessor] = []
        self._initialize_processors()
    
    def _initialize_processors(self) -> None:
        """Initialize all file processors."""
        processor_classes = [
            CSVProcessor,
            PDFProcessor,
            DOCXProcessor,
            XLSXProcessor,
            PPTXProcessor,
            OpenDocumentProcessor,
            RTFProcessor,
            HTMLProcessor,  # HTML processor before TextProcessor to handle HTML files specifically
            JSONProcessor,
            TextProcessor,  # TextProcessor should be last as it handles many extensions as fallback
        ]
        
        for processor_class in processor_classes:
            try:
                processor = processor_class(self.encoding_model)
                self._processors.append(processor)
                logger.debug(f"Initialized {processor.processor_name} processor")
            except Exception as e:
                logger.warning(f"Failed to initialize {processor_class.__name__}: {e}")
    
    def get_processor_for_file(self, file_path: Path) -> Optional[BaseFileProcessor]:
        """Get the appropriate processor for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            BaseFileProcessor instance or None if no processor supports the file
        """
        for processor in self._processors:
            if processor.supports_file(file_path):
                return processor
        return None
    
    def get_supported_extensions(self) -> Set[str]:
        """Get all supported file extensions.
        
        Returns:
            Set of supported extensions (lowercase, with dots)
        """
        extensions = set()
        for processor in self._processors:
            extensions.update(processor.supported_extensions)
        return extensions
    
    def get_processor_info(self) -> Dict[str, List[str]]:
        """Get information about available processors.
        
        Returns:
            Dictionary mapping processor names to supported extensions
        """
        info = {}
        for processor in self._processors:
            info[processor.processor_name] = sorted(processor.supported_extensions)
        return info
    
    def process_file(self, file_path: Path) -> CountResult:
        """Process a single file and return token count results.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            CountResult with token count and file statistics
            
        Raises:
            FileProcessingError: If file cannot be processed
            ConfigurationError: If no processor supports the file type
        """
        processor = self.get_processor_for_file(file_path)
        
        if processor is None:
            supported_exts = sorted(self.get_supported_extensions())
            raise ConfigurationError(
                f"No processor available for file type: {file_path.suffix}. "
                f"Supported extensions: {', '.join(supported_exts)}"
            )
        
        return processor.process_file(file_path)
    
    def find_supported_files(self, directory: Path, recursive: bool = True) -> Generator[Path, None, None]:
        """Find all supported files in directory.
        
        Args:
            directory: Directory to search in
            recursive: Whether to search recursively (default: True)
            
        Yields:
            Path objects for each supported file found
            
        Raises:
            ConfigurationError: If directory doesn't exist or isn't a directory
        """
        if not directory.exists():
            raise ConfigurationError(f"Directory does not exist: {directory}")
        
        if not directory.is_dir():
            raise ConfigurationError(f"Path is not a directory: {directory}")
        
        logger.info(f"🔍 Searching for supported files in: {directory}")
        
        supported_extensions = self.get_supported_extensions()
        
        # Find files based on search mode
        pattern = "**/*" if recursive else "*"
        all_files = directory.glob(pattern)
        
        supported_files = []
        for file_path in all_files:
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                supported_files.append(file_path)
        
        # Group by processor for logging
        processor_counts = {}
        for file_path in supported_files:
            processor = self.get_processor_for_file(file_path)
            if processor:
                processor_name = processor.processor_name
                processor_counts[processor_name] = processor_counts.get(processor_name, 0) + 1
        
        # Log summary
        total_files = len(supported_files)
        logger.info(f"📊 Found {total_files} supported files:")
        for processor_name, count in processor_counts.items():
            logger.info(f"   {processor_name}: {count} files")
        
        yield from supported_files
    
    def process_directory(self, directory: Path, recursive: bool = True) -> CountSummary:
        """Process all supported files in a directory.
        
        Args:
            directory: Directory to search for files
            recursive: Whether to search recursively (default: True)
            
        Returns:
            CountSummary with aggregated results
        """
        start_time = time.time()
        logger.info(f"🚀 Starting multi-format token analysis in: {directory}")
        
        directory = Path(directory)
        file_results: List[CountResult] = []
        processor_stats = {}
        
        # Process each supported file
        for file_path in self.find_supported_files(directory, recursive):
            try:
                result = self.process_file(file_path)
                file_results.append(result)
                
                # Track processor usage
                processor = self.get_processor_for_file(file_path)
                if processor:
                    processor_name = processor.processor_name
                    if processor_name not in processor_stats:
                        processor_stats[processor_name] = {"files": 0, "tokens": 0}
                    processor_stats[processor_name]["files"] += 1
                    processor_stats[processor_name]["tokens"] += result["total_tokens"]
                
            except (FileProcessingError, ConfigurationError) as e:
                logger.error(f"❌ Failed to process {file_path}: {e}")
                # Continue processing other files
                continue
            except Exception as e:
                logger.error(f"❌ Unexpected error processing {file_path}: {e}")
                continue
        
        # Calculate summary statistics
        total_tokens = sum(result["total_tokens"] for result in file_results)
        total_rows = sum(result["row_count"] for result in file_results)
        total_file_size = sum(result["file_size_bytes"] for result in file_results)
        processing_time = time.time() - start_time
        
        # Log processor statistics
        logger.info("📊 Processing summary by format:")
        for processor_name, stats in processor_stats.items():
            logger.info(f"   {processor_name}: {stats['files']} files, {stats['tokens']:,} tokens")
        
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
    
    # Backward compatibility methods
    def count_tokens_in_text(self, text: str) -> int:
        """Count tokens in a text string (backward compatibility).
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens in the text
        """
        if self._processors:
            return self._processors[0].count_tokens_in_text(text)
        else:
            # Fallback implementation
            import tiktoken
            encoder = tiktoken.encoding_for_model(self.encoding_model)
            return len(encoder.encode(str(text) if text else ""))
    
    def count_tokens_in_csv(self, file_path: Path) -> CountResult:
        """Count tokens in a CSV file (backward compatibility).
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            CountResult with token count and file statistics
        """
        csv_processor = next((p for p in self._processors if isinstance(p, CSVProcessor)), None)
        if csv_processor is None:
            raise ConfigurationError("CSV processor not available")
        
        return csv_processor.process_file(file_path)
    
    def find_csv_files(self, directory: Path) -> Generator[Path, None, None]:
        """Find CSV files in directory (backward compatibility).
        
        Args:
            directory: Directory to search in
            
        Yields:
            Path objects for each CSV file found
        """
        csv_extensions = {".csv", ".tsv"}
        for file_path in self.find_supported_files(directory):
            if file_path.suffix.lower() in csv_extensions:
                yield file_path
    
    def count_tokens_in_directory(self, directory: Path, recursive: bool = True) -> CountSummary:
        """Count tokens in directory (backward compatibility).
        
        This method now processes ALL supported file types, not just CSV.
        
        Args:
            directory: Directory to search for files
            recursive: Whether to search recursively (default: True)
            
        Returns:
            CountSummary with aggregated results
        """
        return self.process_directory(directory, recursive)


# Backward compatibility alias
CSVTokenCounter = DocumentProcessor