#!/usr/bin/env python3
"""Setup script for deus-llm-token-stats-guru."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read version from __init__.py
version = "0.1.1"

setup(
    name="deus-llm-token-stats-guru",
    version=version,
    description="Advanced LLM token analysis and statistics toolkit for various data formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Deus LLM Token Stats Guru",
    author_email="noreply@example.com",
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