# AlloAI

[![CI/CD Pipeline](https://github.com/m4xw311/AlloAI/actions/workflows/workflow.yml/badge.svg)](https://github.com/m4xw311/AlloAI/actions/workflows/workflow.yml)
[![PyPI version](https://badge.fury.io/py/alloai.svg)](https://badge.fury.io/py/alloai)
[![Python versions](https://img.shields.io/pypi/pyversions/alloai.svg)](https://pypi.org/project/alloai/)
[![License](https://img.shields.io/pypi/l/alloai.svg)](https://github.com/m4xw311/AlloAI/blob/main/LICENSE)

An agentless vibe coding framework for seamlessly mixing code and LLM instructions in executable markdown files. AlloAI enables you to write polyglot programs that support both traditional programming languages and natural language instructions, all executed in a shared runtime environment.

## Overview

AlloAI lets you write markdown files that mix Python code with natural language instructions. The code blocks execute normally, while text between them becomes prompts for an LLM to generate and execute additional code - all in the same runtime environment with shared variables.

## Features

- **Seamless Integration**: Mix Python code and natural language instructions in markdown files
- **Shared Runtime**: All code blocks and LLM-generated code share the same execution context
- **State Preservation**: Variables and their values persist across code blocks and LLM instructions
- **Simple Syntax**: Use standard markdown code blocks and plain text instructions
- **Flexible LLM Backend**: Supports OpenAI-compatible APIs (including local models)
- **Easy Installation**: Available as a pip-installable package with CLI support
- **Code Export**: Generate standalone Python scripts from your AlloAI executions for reuse
- **Smart Caching**: Automatic caching of code execution results and LLM responses for faster iterative development

## Installation

### From PyPI (Recommended)

```bash
pip install alloai
```

### From Source (Development)

```bash
git clone https://github.com/m4xw311/AlloAI.git
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
alloai -o output.py script.md  # Export generated code to a file
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

## Code Generation and Export

AlloAI can generate a standalone Python script containing all the code that was executed during a run, including both the original code blocks and any LLM-generated code. This is useful for:
- Debugging and understanding what code the LLM generated
- Creating reusable scripts from your AlloAI experiments
- Sharing the complete execution flow with others
- Running the same logic without requiring the LLM on subsequent runs

### Exporting Generated Code

Use the `-o` or `--output` flag to save the complete executed code:

```bash
alloai script.md -o generated_script.py
```

This will:
1. Execute your AlloAI script normally
2. Collect all executed code (both from markdown and LLM-generated)
3. Save it to a standalone Python file with helpful comments
4. Make the file executable (on Unix-like systems)

### Example

Given this AlloAI script (`calculation.md`):
````markdown
```python
x = 10
y = 20
```

Calculate the sum of x and y and store it in a variable called result

```python
print(f"The result is: {result}")
```
````

Running with export:
```bash
alloai calculation.md -o calculation_standalone.py
```

Will generate `calculation_standalone.py`:
```python
#!/usr/bin/env python3
# This file was generated by AlloAI
# You can run this file directly with: python3 calculation_standalone.py

# Code block from markdown
x = 10
y = 20

# LLM-generated code for: Calculate the sum of x and y...
result = x + y

# Code block from markdown
print(f"The result is: {result}")
```

You can then run the generated script directly:
```bash
python3 calculation_standalone.py
# Output: The result is: 30
```

## Caching

AlloAI includes intelligent caching to speed up iterative development and testing. Both code execution results and LLM responses are automatically cached using SHA-256 hashing.

### How Caching Works

- **Code Blocks**: Results are cached based on the code content and current variable state
- **LLM Prompts**: Responses are cached based on the instruction and execution context
- **Persistence**: Cache is stored locally in `~/.alloai_cache/` and persists between runs
- **Automatic**: Caching is enabled by default for faster development cycles

### Cache Management

**Disable caching for a single run:**
```bash
alloai script.md --no-cache
```

**Clear the cache:**
```bash
alloai script.md --clear-cache
```

**Clear cache without running a script:**
```bash
alloai --clear-cache
```

### Performance Benefits

Caching provides significant speedup for:
- Iterative development and debugging
- Re-running scripts with unchanged sections
- Testing different parts of your AlloAI scripts
- Expensive computations or API calls

### Example

First run (no cache):
```bash
alloai examples/cache_demo.md
# Execution time: ~5 seconds (includes LLM calls)
```

Second run (with cache):
```bash
alloai examples/cache_demo.md
# Execution time: <1 second (uses cached results)
```

### Programmatic Cache Control

When using the Python API:
```python
from alloai import execute_markdown, clear_cache

# Execute with caching (default)
execute_markdown(parts, use_cache=True)

# Execute without caching
execute_markdown(parts, use_cache=False)

# Clear all cached data
clear_cache()
```

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

# Or, execute and save the generated code
generated_code = execute_markdown(parts, output_file="output.py")
print(f"Generated code:\n{generated_code}")
```

## How It Works

1. **Parse**: AlloAI reads your markdown file and identifies code blocks and text instructions
2. **Execute**: Code blocks run directly in a persistent Python environment
3. **Generate**: Text instructions are sent to the LLM with the current program state
4. **Continue**: LLM-generated code executes in the same environment, preserving all variables

The key insight is that everything shares the same runtime - your code, LLM-generated code, and all variables persist throughout execution.





## Requirements

- Python 3.8+
- OpenAI API key (or compatible API endpoint)

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

- **API Key Not Found**: Create a `.env` file with `OPENAI_API_KEY=your_key_here`
- **Import Errors**: Run `pip install alloai`
- **Connection Issues**: Check your API key and internet connection



## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. For technical details, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes to AlloAI.
