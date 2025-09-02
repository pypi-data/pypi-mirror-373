"""
Markdown Parser for Alloy
Takes a markdown file content as input and creates string arrays of text parts and code blocks.
"""

import re
from typing import List, Dict


def parse_markdown(md_content: str) -> List[Dict[str, str]]:
    """
    Parse markdown content and return array of text parts and code blocks.

    Args:
        md_content (str): The markdown content to parse

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing parsed text and code blocks.
    """
    md_parts = []

    # Pattern to match fenced code blocks with optional language
    code_block_pattern = r'```(\w+)?\n(.*?)```\n'

    # Find all code blocks
    code_matches = list(re.finditer(code_block_pattern, md_content, re.DOTALL))

    # Extract text parts (everything outside code blocks)
    last_end = 0
    for match in code_matches:
        # Get text before this code block
        if match.start() > last_end:
            text_part = md_content[last_end:match.start()]
            if text_part:
                md_parts.append({
                    "type": "prompt",
                    "content": text_part,
                    "pos": last_end
                })

        # Get the code block content and language
        language = match.group(1) if match.group(1) else ""
        code_content = match.group(2) if match.group(2) else ""

        if code_content:
            md_parts.append({
                "type": "code",
                "language": language,
                "content": code_content,
                "pos": match.start()
            })

        last_end = match.end()

    # Handle remaining text after last code block
    if last_end < len(md_content):
        remaining_text = md_content[last_end:]
        if remaining_text:
            md_parts.append({
                "type": "prompt",
                "content": remaining_text,
                "pos": last_end
            })

    return md_parts
