"""
AlloAI - A framework for seamlessly mixing code and LLM instructions.

This package enables polyglot programming by allowing you to write markdown files
that interleave traditional code with natural language instructions that are
interpreted by an LLM and executed in the same runtime environment.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .parser import parse_markdown
from .execute import execute_markdown

__all__ = [
    "parse_markdown",
    "execute_markdown",
    "__version__",
]
