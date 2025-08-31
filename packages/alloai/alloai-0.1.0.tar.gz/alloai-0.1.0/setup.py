#!/usr/bin/env python
"""
Setup script for AlloAI package.

This is a fallback for older pip versions that don't support pyproject.toml.
Modern installations should use pyproject.toml directly.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from __init__.py
version = "0.1.0"
init_file = this_directory / "alloai" / "__init__.py"
if init_file.exists():
    with open(init_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

setup(
    name="alloai",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="A framework for seamlessly mixing code and LLM instructions in markdown files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AlloAI",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/AlloAI/issues",
        "Documentation": "https://github.com/yourusername/AlloAI#readme",
        "Source Code": "https://github.com/yourusername/AlloAI",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "build>=0.10.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "alloai=alloai.cli:main",
        ],
    },
    keywords="llm ai markdown code-execution polyglot scripting",
    include_package_data=True,
    zip_safe=False,
)
