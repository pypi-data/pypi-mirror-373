# psyborg

[![CI/CD Pipeline](https://github.com/m4xw311/psyborg/actions/workflows/workflow.yml/badge.svg)](https://github.com/m4xw311/psyborg/actions/workflows/workflow.yml)
[![PyPI version](https://badge.fury.io/py/psyborg.svg)](https://badge.fury.io/py/psyborg)
[![Python versions](https://img.shields.io/pypi/pyversions/psyborg.svg)](https://pypi.org/project/psyborg/)
[![License](https://img.shields.io/pypi/l/psyborg.svg)](https://github.com/m4xw311/psyborg/blob/main/LICENSE)

An agentless vibe coding framework for seamlessly mixing code and LLM instructions in executable markdown files. psyborg enables you to write polyglot programs that support both traditional programming languages and natural language instructions, all executed in a shared runtime environment.

## Overview

psyborg lets you write markdown files that mix Python code with natural language instructions. The code blocks execute normally, while text between them becomes prompts for an LLM to generate and execute additional code - all in the same runtime environment with shared variables.

## Features

- **Seamless Integration**: Mix Python code and natural language instructions in markdown files
- **Shared Runtime**: All code blocks and LLM-generated code share the same execution context
- **State Preservation**: Variables and their values persist across code blocks and LLM instructions
- **Simple Syntax**: Use standard markdown code blocks and plain text instructions
- **Flexible LLM Backend**: Supports OpenAI-compatible APIs (including local models)
- **Easy Installation**: Available as a pip-installable package with CLI support
- **Code Export**: Generate standalone Python scripts from your psyborg executions for reuse
- **Smart Caching**: Automatic caching of code execution results and LLM responses for faster iterative development

## Installation

### From PyPI (Recommended)

```bash
pip install psyborg
```

### From Source (Development)

```bash
git clone https://github.com/m4xw311/psyborg.git
cd psyborg
pip install -e .
```

For development with additional tools:
```bash
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in your project directory with your OpenAI API configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # Optional: for custom endpoints
OPENAI_MODEL=gpt-4                          # Optional: defaults to gpt-4
```

Alternatively, you can set these as environment variables:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
export OPENAI_MODEL="gpt-4"                          # Optional
```

## Quick Start

1. **Create a markdown file** (e.g., `hello.md`):

```markdown
# My First psyborg Script

```python
name = "World"
print(f"Hello, {name}!")
```

Now create a greeting function that takes a name parameter and returns a personalized greeting.

```python
print(greeting("psyborg"))
```
```

2. **Run it with psyborg**:

```bash
psyborg hello.md
```

The output will show:
- "Hello, World!" from the first code block
- The LLM will generate a `greeting()` function based on your instruction
- "Hello, psyborg!" from calling the generated function

## How It Works

psyborg processes your markdown file sequentially:

1. **Code blocks** (```python) are executed directly in the Python interpreter
2. **Text sections** between code blocks are sent to the LLM as prompts to generate new code
3. **Generated code** is executed in the same runtime environment
4. **Variables and functions** persist across all code blocks and LLM generations
5. **Results** are displayed in real-time as execution progresses

## Command Line Options

```bash
psyborg [options] <markdown_file>

Options:
  -h, --help     Show help message
  -v, --verbose  Enable verbose output for debugging
  --version      Show version information
  --clear-cache  Clear execution cache before running
  --export FILE  Export executed code to a Python file
  --dry-run      Parse and validate without executing
```

### Examples

```bash
# Basic execution
psyborg script.md

# Export the executed code to a Python file
psyborg script.md --export output.py

# Clear cache and run with verbose output
psyborg script.md --clear-cache --verbose

# Validate syntax without executing
psyborg script.md --dry-run
```

## Advanced Usage

### Working with Variables

Variables defined in code blocks are available to subsequent LLM instructions:

```markdown
```python
data = [1, 2, 3, 4, 5]
```

Create a function to calculate the average of the data list.

```python
print(f"Average: {calculate_average(data)}")
```
```

### Multiple Instructions

You can have multiple instruction sections that build upon each other:

```markdown
```python
import pandas as pd
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
```

Add a new column 'z' that is the sum of columns 'x' and 'y'.

Now create a visualization of all three columns using matplotlib.

```python
print("Final DataFrame:")
print(df)
```
```

### Custom LLM Endpoints

psyborg supports any OpenAI-compatible API endpoint:

```bash
# For local models (e.g., Ollama, LocalAI)
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="not-needed"
export OPENAI_MODEL="llama2"

# For other providers
export OPENAI_BASE_URL="https://your-provider.com/v1"
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="your-model"
```

## Caching

psyborg automatically caches:
- Code execution results
- LLM responses for identical prompts
- Variable states between runs

Cache is stored in `.psyborg_cache/` and persists across sessions. Use `--clear-cache` to reset.

## Code Export

Generate standalone Python scripts from your psyborg executions:

```bash
psyborg script.md --export generated_script.py
```

The exported file includes:
- All original code blocks
- LLM-generated code with comments indicating their source
- Proper imports and structure for standalone execution

## Best Practices

1. **Start Simple**: Begin with basic Python code blocks and simple instructions
2. **Be Specific**: Clear, specific instructions yield better LLM-generated code
3. **Iterative Development**: Use psyborg's caching for fast iteration cycles
4. **Variable Context**: Remember that the LLM can see and use all previously defined variables
5. **Export for Production**: Use `--export` to create deployable Python scripts

## Examples

Check the `examples/` directory for sample psyborg scripts demonstrating various use cases:

- Data analysis and visualization
- Web scraping and API integration
- Machine learning workflows
- File processing and automation
- Mathematical computations

## Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Set `OPENAI_API_KEY` in your environment or `.env` file

**"Module not found" errors**
- Install required Python packages: `pip install package-name`

**Cache-related issues**
- Clear cache with: `psyborg script.md --clear-cache`

**LLM generates incorrect code**
- Be more specific in your instructions
- Provide examples of expected input/output
- Break complex tasks into smaller steps

### Debug Mode

Use verbose mode to see detailed execution information:

```bash
psyborg script.md --verbose
```

This shows:
- Cache hit/miss information
- LLM prompts and responses
- Code execution details
- Variable state changes

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/m4xw311/psyborg.git
cd psyborg
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
pytest --cov=psyborg  # With coverage report
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

**psyborg** - Where code meets natural language in perfect harmony. 🤖✨