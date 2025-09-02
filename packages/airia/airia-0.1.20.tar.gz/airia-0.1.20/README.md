# Airia Python API Library

[![PyPI version](https://badge.fury.io/py/airia.svg)](https://badge.fury.io/py/airia)
[![Python versions](https://img.shields.io/pypi/pyversions/airia.svg)](https://pypi.org/project/airia/)
[![License](https://img.shields.io/pypi/l/airia.svg)](https://pypi.org/project/airia/)

The Airia Python library provides a clean and intuitive interface to interact with Airia API. The library offers both synchronous and asynchronous clients for maximum flexibility in your applications.

## Features

- **Dual Client Support**: Choose between synchronous (`AiriaClient`) and asynchronous (`AiriaAsyncClient`) implementations
- **Pipeline Execution**: Easily run AI pipelines with customizable parameters
- **Gateway Support**: Seamlessly integrate with OpenAI and Anthropic services through Airia gateways
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Logging**: Built-in configurable logging with correlation ID support for request tracing
- **Flexible Authentication**: Support for both API keys and bearer tokens with flexible configuration

## Documentation and Quick Start Guides

Full documentation and quick start guides are available [here](https://airiallc.github.io/airia-python).

You can also run the documentation page locally with `mkdocs`:

1. [Install development dependencies](#install-with-development-dependencies)
2. Run `mkdocs serve` to start the local server

## Installation

You can install the package using pip or uv:

<table>
<tr>
<th>pip</th>
<th>uv</th>
</tr>
<tr>
<td>

```bash
pip install airia
```

</td>
<td>

```bash
uv add airia
```

</td>
</tr>
</table>

### Install with optional dependencies

The package supports optional dependencies for gateway functionality:

<table>
<tr>
<th>OpenAI Gateway</th>
<th>Anthropic Gateway</th>
<th>All Gateways</th>
</tr>
<tr>
<td>

```bash
pip install "airia[openai]"
```

</td>
<td>

```bash
pip install "airia[anthropic]"
```

</td>
<td>

```bash
pip install "airia[all]"
```

</td>
</tr>
</table>

### Install with development dependencies

Clone the repository:

```bash
git clone https://github.com/AiriaLLC/airia-python.git
cd airia-python
```

Then, run one of the following commands:

<table>
<tr>
<th>pip</th>
<th>uv</th>
</tr>
<tr>
<td>

```bash
pip install dependency-groups
dev=$(python -m dependency_groups dev)
pip install -e .
pip install $dev
```

</td>
<td>

```bash
uv sync --frozen --group dev
```

</td>
</tr>
</table>

## Building from Source

First make sure you have already cloned the repository, then run one of the following commands:

<table>
<tr>
<th>pip</th>
<th>uv</th>
</tr>
<tr>
<td>

```bash
pip install build
python -m build
```

</td>
<td>

```bash
uv build
```

</td>
</tr>
</table>

This will create both wheel and source distribution in the `dist/` directory.

## Requirements

- Python 3.9 or higher
- Core dependencies:
  - requests
  - aiohttp
  - loguru
  - pydantic

- Optional dependencies:
  - OpenAI gateway: `openai>=1.74.0`
  - Anthropic gateway: `anthropic>=0.49.0`

## Development

To run tests (make sure you have development dependencies installed):

```bash
pytest
```

For testing gateway functionality, install the optional dependencies:

```bash
# For OpenAI gateway tests
pip install -e .[openai]
pytest tests/test_openai_gateway.py

# For Anthropic gateway tests
pip install -e .[anthropic]
pytest tests/test_anthropic_gateway.py

# For all tests
pip install -e .[all]
pytest
```
