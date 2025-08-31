#!/usr/bin/env python3
"""Setup script for deus-llm-token-stats-guru."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from __init__.py
version = "0.3.3"

setup(
    name="deus_llm_token_stats_guru",
    version=version,
    description="Advanced LLM token analysis and statistics toolkit for various data formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="deus-global",
    author_email="sean@deus.com.tw",
    url="https://github.com/yourusername/deus-llm-token-stats-guru",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/deus-llm-token-stats-guru/issues",
        "Repository": "https://github.com/yourusername/deus-llm-token-stats-guru.git",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "deus_llm_token_stats_guru": ["py.typed"],
    },
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "tiktoken>=0.5.0",
        "click>=8.0.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
        "pdf": [
            "PyMuPDF>=1.21.0",  # Primary PDF processor
            "PyPDF2>=3.0.0",    # Fallback PDF processor
            "pdfplumber>=0.7.0", # Alternative PDF processor
        ],
        "docx": [
            "python-docx>=0.8.11",
            "docx2txt>=0.8",
        ],
        "excel": [
            "openpyxl>=3.0.0",   # Primary Excel processor
            "xlrd>=2.0.0",       # Legacy .xls support
        ],
        "powerpoint": [
            "python-pptx>=0.6.0", # PowerPoint processor
        ],
        "opendocument": [
            "odfpy>=1.4.0",      # OpenDocument processor
        ],
        "rtf": [
            "striprtf>=0.0.10",  # RTF processor
        ],
        "html": [
            "beautifulsoup4>=4.9.0", # HTML processor
            "lxml>=4.6.0",       # XML parser for BeautifulSoup
        ],
        "office": [
            # MS Office formats
            "python-docx>=0.8.11",
            "docx2txt>=0.8",
            "openpyxl>=3.0.0",
            "xlrd>=2.0.0", 
            "python-pptx>=0.6.0",
            # OpenDocument formats
            "odfpy>=1.4.0",
            # Rich Text Format
            "striprtf>=0.0.10",
            # HTML processing
            "beautifulsoup4>=4.9.0",
            "lxml>=4.6.0",
        ],
        "all": [
            # PDF support
            "PyMuPDF>=1.21.0",
            "PyPDF2>=3.0.0", 
            "pdfplumber>=0.7.0",
            # MS Office formats
            "python-docx>=0.8.11",
            "docx2txt>=0.8",
            "openpyxl>=3.0.0",
            "xlrd>=2.0.0",
            "python-pptx>=0.6.0",
            # OpenDocument formats
            "odfpy>=1.4.0",
            # Rich Text Format
            "striprtf>=0.0.10",
            # HTML processing
            "beautifulsoup4>=4.9.0",
            "lxml>=4.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "deus-llm-token-guru=deus_llm_token_stats_guru.cli:main",
            "llm-token-stats=deus_llm_token_stats_guru.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="llm tokens tiktoken csv analysis statistics",
)