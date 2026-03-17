"""Setup script for Lumina."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="lumina",
    version="1.0.0",
    author="Mundai",
    description="Lightweight AI Agent Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lumina",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.12.0",
        "anthropic>=0.21.0",
        "google-generativeai>=0.4.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "pylint>=3.0.0",
        ],
        "web": [
            "requests>=2.31.0",
            "beautifulsoup4>=4.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lumina=lumina.cli:cli_main",
        ],
    },
)
