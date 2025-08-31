"""Command-line interface for CSV token counter."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .core import CSVTokenCounter
from ._exceptions import CSVTokenCounterError
from ._logging import setup_logging


@click.command()
@click.argument('directory', type=click.Path(exists=True, path_type=Path))
@click.option('--model', '-m', default='gpt-4', 
              help='OpenAI model for tiktoken encoding (default: gpt-4)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file for JSON results (default: stdout)')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--log-file', type=click.Path(path_type=Path),
              help='Log file path')
@click.option('--quiet', '-q', is_flag=True, help='Suppress progress output')
@click.version_option(version=__version__)
def main(
    directory: Path,
    model: str,
    output: Optional[Path],
    debug: bool,
    log_file: Optional[Path],
    quiet: bool,
) -> None:
    """Count OpenAI tokens in CSV files recursively using tiktoken.
    
    DIRECTORY: Path to directory containing CSV files to analyze
    
    Examples:
    
        # Count tokens in current directory
        csv-token-count .
        
        # Count tokens using gpt-3.5-turbo encoding
        csv-token-count /path/to/data --model gpt-3.5-turbo
        
        # Save results to JSON file
        csv-token-count /path/to/data --output results.json
        
        # Enable debug logging
        csv-token-count /path/to/data --debug --log-file debug.log
    """
    # Setup logging
    if not quiet:
        setup_logging(debug=debug, log_file=str(log_file) if log_file else None)
    
    try:
        # Initialize token counter
        counter = CSVTokenCounter(encoding_model=model)
        
        # Process directory
        if not quiet:
            click.echo(f"🚀 Counting tokens in CSV files: {directory}")
            click.echo(f"📊 Using encoding model: {model}")
        
        summary = counter.count_tokens_in_directory(directory)
        
        # Prepare output
        output_data = {
            "summary": {
                "total_files": summary["total_files"],
                "total_tokens": summary["total_tokens"],
                "total_rows": summary["total_rows"],
                "total_file_size_mb": round(summary["total_file_size_bytes"] / (1024 * 1024), 2),
                "encoding_model": summary["encoding_model"],
                "processing_time_seconds": round(summary["processing_time_seconds"], 2),
            },
            "file_details": [
                {
                    "file_path": result["file_path"],
                    "tokens": result["total_tokens"],
                    "rows": result["row_count"],
                    "columns": result["column_count"],
                    "size_mb": round(result["file_size_bytes"] / (1024 * 1024), 2),
                }
                for result in summary["file_results"]
            ]
        }
        
        # Output results
        json_output = json.dumps(output_data, indent=2)
        
        if output:
            output.write_text(json_output)
            if not quiet:
                click.echo(f"📄 Results saved to: {output}")
        else:
            click.echo(json_output)
        
        # Summary output to stderr if not quiet
        if not quiet:
            click.echo(f"\n📈 Summary:", err=True)
            click.echo(f"   Files processed: {summary['total_files']:,}", err=True)
            click.echo(f"   Total tokens: {summary['total_tokens']:,}", err=True)
            click.echo(f"   Total rows: {summary['total_rows']:,}", err=True)
            click.echo(f"   Processing time: {summary['processing_time_seconds']:.2f}s", err=True)
        
    except CSVTokenCounterError as e:
        click.echo(f"❌ Error: {e}", err=True)
        if debug and e.details:
            click.echo(f"   Details: {e.details}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if debug:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()