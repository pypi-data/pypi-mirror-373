# AlloAI

[![CI/CD Pipeline](https://github.com/yourusername/AlloAI/actions/workflows/workflow.yml/badge.svg)](https://github.com/yourusername/AlloAI/actions/workflows/workflow.yml)
[![PyPI version](https://badge.fury.io/py/alloai.svg)](https://badge.fury.io/py/alloai)
[![Python versions](https://img.shields.io/pypi/pyversions/alloai.svg)](https://pypi.org/project/alloai/)
[![License](https://img.shields.io/pypi/l/alloai.svg)](https://github.com/yourusername/AlloAI/blob/main/LICENSE)

A framework for seamlessly mixing code and LLM instructions in markdown files. AlloAI enables you to write polyglot programs that support both traditional programming languages and natural language instructions, all executed in a shared runtime environment.

## Overview

AlloAI allows you to:
- Write code as you normally would in markdown files
- Interleave natural language instructions that are interpreted by an LLM
- Execute both code and LLM-generated code in the same runtime environment
- Maintain state across code blocks and LLM instructions
- Create dynamic, AI-enhanced scripts without complex pipelines

## Features

- **Seamless Integration**: Mix Python code and natural language instructions in markdown files
- **Shared Runtime**: All code blocks and LLM-generated code share the same execution context
- **State Preservation**: Variables and their values persist across code blocks and LLM instructions
- **Simple Syntax**: Use standard markdown code blocks and plain text instructions
- **Flexible LLM Backend**: Supports OpenAI-compatible APIs (including local models)
- **Easy Installation**: Available as a pip-installable package with CLI support

## Installation

### From PyPI (Recommended)

```bash
pip install alloai
```

### From Source (Development)

```bash
git clone https://github.com/yourusername/AlloAI.git
cd AlloAI
pip install -e .
```

For development with additional tools:
```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in your project directory with your OpenAI API configuration:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: for custom endpoints
OPENAI_MODEL=gpt-3.5-turbo  # Optional: specify model
```

You can copy the provided example:
```bash
cp .env.example .env
# Then edit .env with your API key
```

**Configuration Options:**
- `OPENAI_API_KEY`: Required. Your OpenAI API key
- `OPENAI_BASE_URL`: Optional. Custom API endpoint for OpenAI-compatible services
- `OPENAI_MODEL`: Optional. Model to use (default: gpt-3.5-turbo)

## Usage

### Basic Usage

Once installed, you can run AlloAI scripts directly from the command line:

```bash
alloai script.md
```

### Command-Line Options

```bash
alloai --help  # Show help message
alloai --version  # Show version
alloai -v script.md  # Run with verbose output
alloai --env /path/to/.env script.md  # Use specific .env file
```

### Writing AlloAI Scripts

Create a markdown file with interleaved code blocks and natural language instructions:

**example.md:**
````markdown
```python
x = 5
```

Increment x by 1

```python
print(x)
```

Multiply x by 10 and display it
````

Run it:
```bash
alloai example.md
```

Output:
```
6
60
```

### More Examples

**Data Processing Example:**
````markdown
```python
data = [1, 2, 3, 4, 5]
```

Calculate the sum and average of the data list, store them in variables called total and average

```python
print(f"Final sum: {total}")
print(f"Final average: {average}")
```
````

**String Manipulation Example:**
````markdown
```python
text = "hello world"
```

Convert the text to uppercase and reverse it, update the text variable

```python
print(f"Result: {text}")
```
````

**Working with Files:**
````markdown
```python
import json
data = {"name": "AlloAI", "version": "0.1.0"}
```

Write the data dictionary to a file called output.json with proper formatting

```python
with open("output.json", "r") as f:
    loaded = json.load(f)
    print(f"Loaded: {loaded}")
```
````

## Python API

You can also use AlloAI programmatically in your Python code:

```python
from alloai import parse_markdown, execute_markdown

# Read and parse markdown content
with open("script.md", "r") as f:
    content = f.read()

# Parse the markdown
parts = parse_markdown(content)

# Execute the parsed content
execute_markdown(parts)
```

## How It Works

AlloAI operates through three main components:

1. **Parser** (`alloai/parser.py`): 
   - Parses markdown files to extract code blocks and text sections
   - Identifies code language (if specified) and content
   - Returns structured data for execution

2. **Executor** (`alloai/execute.py`): 
   - Maintains a shared Python runtime environment
   - Executes code blocks and captures output
   - Sends natural language instructions to the LLM along with current state
   - Executes LLM-generated code in the same environment

3. **CLI** (`alloai/cli.py`): 
   - Command-line interface for running AlloAI scripts
   - Handles argument parsing and environment setup
   - Provides user-friendly error messages

### Execution Flow

1. The markdown file is parsed into alternating code blocks and text instructions
2. Code blocks are executed directly in a persistent Python environment
3. Text instructions are sent to the LLM along with:
   - The previous code block
   - Console output from that code
   - Current variable state
4. The LLM generates Python code to fulfill the instruction
5. The generated code is executed in the same environment
6. Process continues until all blocks are processed

## Project Structure

```
AlloAI/
├── alloai/               # Main package directory
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   ├── parser.py         # Markdown parsing logic
│   └── execute.py        # Code execution and LLM integration
├── examples/             # Example AlloAI scripts
│   └── example.md        # Basic usage example
├── pyproject.toml        # Package configuration
├── requirements.txt      # Python dependencies
├── LICENSE               # License file
├── .env.example          # Example environment configuration
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/AlloAI.git
cd AlloAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=alloai  # With coverage
```

### Code Formatting

```bash
black alloai/
flake8 alloai/
mypy alloai/
```

### Building and Publishing

The project uses GitHub Actions for automated testing and publishing:

- **Automatic Testing**: Every push and PR triggers tests across multiple Python versions and OS platforms
- **TestPyPI Publishing**: Pushes to main branch automatically publish to TestPyPI
- **PyPI Publishing**: Creating a version tag (e.g., `v0.1.0`) automatically publishes to PyPI

#### Manual Publishing

```bash
# Build the package
python -m build

# Upload to TestPyPI (for testing)
twine upload -r testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

#### Automated Release Process

1. Update version in `alloai/__init__.py` and `pyproject.toml`
2. Commit and push to main:
   ```bash
   git add -A
   git commit -m "Bump version to 0.1.0"
   git push origin main
   ```
3. Create and push a version tag:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```
4. GitHub Actions will automatically:
   - Run tests on multiple platforms
   - Build the package
   - Publish to PyPI
   - Create a GitHub release

See `.github/workflows/workflow.yml` for the complete CI/CD pipeline configuration.

## Requirements

- Python 3.8+
- OpenAI API key (or compatible API endpoint)
- Dependencies:
  - `openai>=1.0.0` - OpenAI API client
  - `python-dotenv>=0.19.0` - Environment variable management

## Supported LLM Providers

AlloAI works with any OpenAI-compatible API:

- **OpenAI**: GPT-3.5, GPT-4, etc.
- **Azure OpenAI**: Use custom `OPENAI_BASE_URL`
- **Local Models**: Via LM Studio, Ollama, llama.cpp, etc.
- **Alternative Providers**: Any service with OpenAI-compatible endpoints

## Limitations

- Currently supports only Python code blocks
- LLM instructions are limited by the model's code generation capabilities
- Error handling in LLM-generated code may require manual intervention
- Large variable states may exceed LLM context limits

## Troubleshooting

### API Key Not Found
```
Error: OPENAI_API_KEY not found in environment variables
```
**Solution**: Create a `.env` file with your API key or set it as an environment variable:
```bash
export OPENAI_API_KEY=your_key_here
```

### Import Errors
```
ModuleNotFoundError: No module named 'alloai'
```
**Solution**: Install the package:
```bash
pip install alloai
```

### LLM Connection Errors
Check your internet connection and API key validity. For custom endpoints, verify the `OPENAI_BASE_URL` is correct.

## Future Enhancements

- [ ] Support for multiple programming languages (JavaScript, Ruby, etc.)
- [ ] Advanced error handling and recovery
- [ ] Interactive debugging mode
- [ ] Streaming output for long-running operations
- [ ] Code block dependencies and execution order control
- [ ] Export to standalone Python scripts
- [ ] VSCode extension for syntax highlighting
- [ ] Web-based playground

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

All pull requests will be automatically tested via GitHub Actions across multiple Python versions and operating systems.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project explores the concept of polyglot programming, combining traditional code with natural language processing to create more intuitive and flexible scripting experiences.

## Changelog

### Version 0.1.0 (Initial Release)
- Basic markdown parsing for code blocks and text
- Python code execution with shared runtime
- LLM integration for natural language instructions
- CLI tool for running AlloAI scripts
- PyPI package distribution