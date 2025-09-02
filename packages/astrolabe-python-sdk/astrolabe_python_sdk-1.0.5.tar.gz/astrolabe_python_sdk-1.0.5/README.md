# Astrolabe Python SDK

A Python SDK for the Astrolabe feature flag system, supporting number, string, boolean, and JSON flags with environment-based configuration.

## Installation

```bash
pip install astrolabe-python-sdk
```

## Quick Start

```python
from astrolabe import AstrolabeClient

# Initialize the client with your environment
client = AstrolabeClient(env="development")  # or "staging", "production"

# Evaluate different types of flags
boolean_flag = client.get_boolean_flag("feature_enabled", default=False)
string_flag = client.get_string_flag("welcome_message", default="Hello!")
number_flag = client.get_number_flag("max_items", default=10)
json_flag = client.get_json_flag("config", default={"theme": "light"})

# Generic flag evaluation (type inferred from default)
flag_value = client.get_flag("any_flag", default="default_value")
```

## Usage

### Initialization

```python
from astrolabe import AstrolabeClient
from astrolabe.client import Environment

# Using string
client = AstrolabeClient("production")

# Using enum
client = AstrolabeClient(Environment.PRODUCTION)
```

### Flag Evaluation with Attributes

```python
# Pass attributes for context-aware flag evaluation
attributes = {
    "user_id": "12345",
    "region": "us-east-1",
    "plan": "premium"
}

result = client.get_boolean_flag(
    key="premium_feature", 
    default=False, 
    attributes=attributes
)
```

### Supported Flag Types

- **Boolean flags**: `get_boolean_flag(key, default, attributes=None)`
- **String flags**: `get_string_flag(key, default, attributes=None)`
- **Number flags**: `get_number_flag(key, default, attributes=None)` (supports int and float)
- **JSON flags**: `get_json_flag(key, default, attributes=None)` (returns dict)
- **Generic flags**: `get_flag(key, default, attributes=None)` (type inferred from default)

### Environments

Supported environments:
- `development`
- `staging` 
- `production`

## Development

This SDK is currently in development. Flag evaluation logic is stubbed and will be implemented in future versions.

## License

MIT License
