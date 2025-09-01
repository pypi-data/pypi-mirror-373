"""
AlloAI - Mix Python code with natural language instructions in markdown files.

Write markdown files where code blocks execute normally and text between them
becomes prompts for an LLM to generate and execute additional code - all in
the same runtime environment with shared variables.
"""

__version__ = "0.2.0"
__author__ = "Maxwell Felix"

from .parser import parse_markdown
from .execute import execute_markdown

__all__ = [
    "parse_markdown",
    "execute_markdown",
    "__version__",
]
