#!/usr/bin/env python
"""
Setup script for psyborg package.

This is a fallback for older pip versions that don't support pyproject.toml.
Modern installations should use pyproject.toml directly.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Create a concise long description
this_directory = Path(__file__).parent
long_description = """# psyborg

A framework for seamlessly mixing Python code and natural language instructions in markdown files.

## Overview

psyborg lets you write markdown files that mix Python code with natural language instructions.
The code blocks execute normally, while text between them becomes prompts for an LLM to generate
and execute additional code - all in the same runtime environment with shared variables.

## Key Features

- **Seamless Integration**: Mix Python code and natural language instructions in markdown files
- **Shared Runtime**: All code blocks and LLM-generated code share the same execution context
- **State Preservation**: Variables and their values persist across code blocks and LLM instructions
- **Code Export**: Generate standalone Python scripts from your psyborg executions for reuse
- **Flexible LLM Backend**: Supports OpenAI-compatible APIs (including local models)

## Quick Start

1. Install: `pip install psyborg`
2. Set your OpenAI API key: `export OPENAI_API_KEY=your_key`
3. Create a markdown file with code and instructions
4. Run: `psyborg script.md`

## Example

```markdown
```python
x = 5
```

Increment x by 1

```python
print(x)  # Will print 6
```
```

## Documentation

Full documentation, examples, and contribution guidelines are available at:
https://github.com/m4xw311/psyborg

## License

MIT License - see LICENSE file for details.
"""

# Read version from __init__.py
version = "0.4.0"
init_file = this_directory / "psyborg" / "__init__.py"
if init_file.exists():
    with open(init_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

setup(
    name="psyborg",
    version=version,
    author="Maxwell Felix",
    author_email="max@alloai.io",
    description="A framework for seamlessly mixing code and LLM instructions in markdown files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/m4xw311/psyborg",
    project_urls={
        "Bug Tracker": "https://github.com/m4xw311/psyborg/issues",
        "Documentation": "https://github.com/m4xw311/psyborg#readme",
        "Source Code": "https://github.com/m4xw311/psyborg",
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
        "cloudpickle>=3.1.1",
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
            "psyborg=psyborg.cli:main",
        ],
    },
    keywords="llm ai markdown code-execution polyglot scripting",
    include_package_data=True,
    zip_safe=False,
)
