# CSV Token Counter

Count OpenAI tokens in CSV files recursively using tiktoken.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Accurate Token Counting**: Uses OpenAI's tiktoken library for precise token counts
- **Recursive Processing**: Automatically finds and processes all CSV files in directories
- **Multiple Encoding Models**: Supports different OpenAI models (gpt-4, gpt-3.5-turbo, etc.)
- **CLI Interface**: Easy-to-use command-line tool
- **Comprehensive Output**: Detailed statistics including file sizes, row counts, and processing times
- **JSON Export**: Results can be exported to JSON format
- **Type Safety**: Full type hints and modern Python features

## Installation

```bash
pip install csv-token-counter
```

## Quick Start

### Command Line Usage

```bash
# Count tokens in current directory
csv-token-count .

# Count tokens using specific model
csv-token-count /path/to/csv/files --model gpt-3.5-turbo

# Save results to JSON file
csv-token-count /path/to/csv/files --output results.json

# Enable debug logging
csv-token-count /path/to/csv/files --debug --log-file debug.log
```

### Python API Usage

```python
from csv_token_counter import CSVTokenCounter
from pathlib import Path

# Initialize counter
counter = CSVTokenCounter(encoding_model="gpt-4")

# Count tokens in a single CSV file
result = counter.count_tokens_in_csv(Path("data.csv"))
print(f"Total tokens: {result['total_tokens']:,}")

# Process entire directory
summary = counter.count_tokens_in_directory(Path("./csv_files"))
print(f"Processed {summary['total_files']} files")
print(f"Total tokens: {summary['total_tokens']:,}")
```

## API Reference

### CSVTokenCounter

Main class for counting tokens in CSV files.

#### Methods

- `__init__(encoding_model: str = "gpt-4")`: Initialize with specific encoding model
- `count_tokens_in_text(text: str) -> int`: Count tokens in a text string
- `count_tokens_in_csv(file_path: Path) -> CountResult`: Count tokens in single CSV file
- `count_tokens_in_directory(directory: Path) -> CountSummary`: Process all CSV files in directory

#### Type Definitions

```python
class CountResult(TypedDict):
    file_path: str
    total_tokens: int
    row_count: int
    column_count: int
    encoding_model: str
    file_size_bytes: int

class CountSummary(TypedDict):
    total_files: int
    total_tokens: int
    total_rows: int
    total_file_size_bytes: int
    encoding_model: str
    file_results: List[CountResult]
    processing_time_seconds: float
```

## Examples

### Basic File Processing

```python
from csv_token_counter import CSVTokenCounter
import pandas as pd
from pathlib import Path

# Create sample data
data = {
    'title': ['AI Introduction', 'Machine Learning'],
    'content': [
        'Artificial intelligence is transforming industries',
        'ML enables computers to learn from data'
    ]
}

# Save to CSV
df = pd.DataFrame(data)
df.to_csv('articles.csv', index=False)

# Count tokens
counter = CSVTokenCounter()
result = counter.count_tokens_in_csv(Path('articles.csv'))

print(f"File: articles.csv")
print(f"Tokens: {result['total_tokens']:,}")
print(f"Rows: {result['row_count']}")
print(f"Columns: {result['column_count']}")
```

### Directory Processing with Different Models

```python
from csv_token_counter import CSVTokenCounter
from pathlib import Path

models = ["gpt-4", "gpt-3.5-turbo"]
directory = Path("./data")

for model in models:
    counter = CSVTokenCounter(encoding_model=model)
    summary = counter.count_tokens_in_directory(directory)
    
    print(f"Model: {model}")
    print(f"Total tokens: {summary['total_tokens']:,}")
    print(f"Processing time: {summary['processing_time_seconds']:.2f}s")
    print()
```

### CLI Output Format

The CLI tool outputs JSON with the following structure:

```json
{
  "summary": {
    "total_files": 3,
    "total_tokens": 15420,
    "total_rows": 150,
    "total_file_size_mb": 2.1,
    "encoding_model": "gpt-4",
    "processing_time_seconds": 0.85
  },
  "file_details": [
    {
      "file_path": "/path/to/file1.csv",
      "tokens": 5140,
      "rows": 50,
      "columns": 4,
      "size_mb": 0.7
    }
  ]
}
```

## Environment Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
```

### 2. Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_core.py
```

### Code Quality

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Building Package

```bash
# Build package
python -m build

# Check package
python -m twine check dist/*

# Test installation
pip install dist/*.whl
```

## Supported Models

The package supports all OpenAI tiktoken encoding models:

- `gpt-4` (default)
- `gpt-3.5-turbo`
- `text-davinci-003`
- `text-davinci-002`
- `code-davinci-002`
- Custom encodings via tiktoken

## Performance

- Processes ~1000 rows/second on typical hardware
- Memory usage scales with CSV file size
- Supports files with millions of rows
- Recursive directory scanning with progress tracking

## Error Handling

The package includes comprehensive error handling:

- `FileProcessingError`: Issues reading or processing CSV files
- `EncodingError`: Problems with tiktoken encoding
- `ConfigurationError`: Invalid configuration or paths

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes with tests
4. Run quality checks: `make lint test`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial release
- Core CSV token counting functionality
- CLI interface with click
- Support for multiple encoding models
- Comprehensive test suite
- JSON output format