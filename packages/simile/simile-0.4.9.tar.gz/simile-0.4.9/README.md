# Simile API Python Client

A Python client for interacting with the Simile API server.

## Installation

```bash
pip install simile
```

## Dependencies

- `httpx>=0.20.0`
- `pydantic>=2.0.0`

## Usage

```python
from simile import Simile

client = Simile(api_key="your_api_key")
```

## Publishing

First, bump the version in `pyproject.toml`. Then, create the distribution files:
```bash
python3 -m build
```

Afterwards, use [Twine](https://pypi.org/project/twine/) to upload the package:
```bash
pip install twine
twine upload dist/*
```

If you need the PyPI credentials, please ask Carolyn or Chris.