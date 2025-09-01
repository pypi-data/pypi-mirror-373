#!/usr/bin/env python3
"""
Command-line interface for AlloAI.

This module provides the main entry point for running AlloAI scripts
from the command line.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

from . import parser
from . import execute
from . import __version__


def setup_logging(verbose: bool = False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point for the AlloAI CLI."""
    # Set up argument parser
    arg_parser = argparse.ArgumentParser(
        prog='alloai',
        description='Execute AlloAI scripts that mix code and LLM instructions.',
        epilog='Example: alloai script.md'
    )

    arg_parser.add_argument(
        'file',
        help='Path to the markdown file to execute'
    )

    arg_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for debugging'
    )

    arg_parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    arg_parser.add_argument(
        '--env',
        default=None,
        help='Path to .env file (defaults to current directory .env if exists)'
    )

    arg_parser.add_argument(
        '-o', '--output',
        default=None,
        nargs='?',
        const=None,
        help='Path to save the generated Python code for reuse'
    )

    # Parse arguments
    args = arg_parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)

    # Handle .env file
    if args.env:
        env_path = Path(args.env)
        if not env_path.exists():
            print(f"Error: Specified .env file '{args.env}' not found.")
            sys.exit(1)
        # Load the specified .env file
        from dotenv import load_dotenv
        load_dotenv(env_path)
    else:
        # Try to load .env from current directory if it exists
        from dotenv import load_dotenv
        load_dotenv()

    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file or environment.")
        print("Example: export OPENAI_API_KEY=your_api_key_here")

    # Process the markdown file
    md_file = Path(args.file)

    if not md_file.exists():
        print(f"Error: File '{md_file}' not found.")
        sys.exit(1)

    if not md_file.suffix.lower() in ['.md', '.markdown']:
        print(f"Warning: File '{md_file}' does not have a .md extension.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    try:
        # Read the markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Parse the markdown content
        md_parts = parser.parse_markdown(md_content)

        # Execute the parsed markdown
        generated_code = execute.execute_markdown(md_parts, output_file=args.output)
        # If the flag -o is set but no output file is provided following it, print the generated code to stdout.
        if args.output is None:
            print(generated_code)

    except FileNotFoundError:
        print(f"Error: File '{md_file}' not found.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Error processing file: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def run():
    """Wrapper function for console script entry point."""
    main()


if __name__ == "__main__":
    main()
