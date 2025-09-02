# Outerport Python SDK

## Installation

```
pip install outerport
```

or 

```
uv add outerport
```

## Usage

```
from outerport import OuterportClient

client = OuterportClient(
    api_key="your_api_key",
    base_url="https://api.outerport.com"
)
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/outerport/outerport.git
cd outerport/outerport-python

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

The SDK includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Run with coverage report
pytest --cov=outerport
```

For integration tests, you'll need to set up your API key:

```bash
export OUTERPORT_API_KEY="your_api_key"
pytest tests/integration
```

See the [tests/README.md](tests/README.md) file for more details on testing.

