# Dictionary Patterns

A template engine for data in dictionaries – useful for tests!

## Overview

Dictionary Patterns is a Python library that allows you to match dictionary objects using pattern-based templates. It's particularly useful for testing scenarios where you need to verify that dictionary responses match expected patterns while allowing for dynamic values.

## Features

- **Pattern-based matching**: Use placeholders like `{string:name}` to match dynamic values
- **Value consistency**: Ensure the same pattern identifier has consistent values across matches
- **Nested structure support**: Handle complex nested dictionary objects and arrays
- **Custom exceptions**: Rich error handling with specific exception types
- **Flexible patterns**: Define your own regex patterns for different data types

## When to Use This Library

**This library does not replace JSON Schema validation.** It's designed for different use cases:

- **String-based pattern matching**: This library works exclusively with string values and regex patterns, making it ideal for validating string-based data structures
- **Non-deterministic outputs**: Perfect for testing APIs or functions that return dynamic data where exact values aren't predictable but patterns are known
- **Repeating value validation**: Useful when the same values can appear multiple times across a document and you need to ensure consistency
- **Simple validation scenarios**: Great for lightweight testing where full JSON Schema validation might be overkill

For complex data validation, type checking, or when you need to validate non-string data types, consider using JSON Schema or other validation libraries too.

## Installation

```bash
pip install dict-patterns
```

## Quick Start

```python
from dict_patterns import DictMatcher

# Define your patterns
patterns = {
    'string': r'[a-zA-Z]+',
    'number': r'\d+',
    'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
}

# Create a matcher
matcher = DictMatcher(patterns)

# Define your template with placeholders
template = {
    'user': {
        'name': '{string:user_name}',
        'age': '{number:user_age}',
        'id': '{uuid:user_id}'
    }
}

# Your actual data
actual = {
    'user': {
        'name': 'John',
        'age': '25',
        'id': '1d408610-f129-47a8-a4c1-1a6e0ca2d16f'
    }
}

# Match them
matcher.match(template, actual)

# Access matched values
print(matcher.values['string']['user_name'])  # 'John'
print(matcher.values['number']['user_age'])   # '25'
print(matcher.values['uuid']['user_id'])      # '1d408610-f129-47a8-a4c1-1a6e0ca2d16f'
```

## Pattern Syntax

Patterns use the format `{pattern_name:identifier}` where:

- `pattern_name` is the type of pattern to match (must be defined in your patterns dict)
- `identifier` is an optional name for the captured value (used for consistency checking)

### Examples

```python
# Simple patterns
'{string:name}'           # Matches alphabetic strings
'{number:age}'            # Matches numeric strings
'{uuid:user_id}'          # Matches UUID format

# Patterns without identifiers (no consistency checking)
'{string}'                # Matches any string, no identifier
'{number}'                # Matches any number, no identifier
```

Note that in the above example, the the patterns `string`, `number` and `uuid` must be previously defined.

## Error Handling

The library provides custom exceptions for better error handling and debugging:

### Exception Hierarchy

```
DictPatternError (base)
├── DictStructureError
│   ├── DictKeyMismatchError
│   └── DictListLengthMismatchError
├── DictValueMismatchError
├── DictPatternMatchError
├── DictPatternValueInconsistencyError
└── DictPatternTypeError
```

### Example Error Handling

```python
from dict_patterns import (
    DictMatcher,
    DictPatternError,
    DictStructureError,
    DictKeyMismatchError,
    DictPatternMatchError
)

try:
    matcher = DictMatcher({'email': r'[^@]+@[^@]+\.[^@]+'})
    template = {'email': '{email:user_email}'}
    actual = {'email': 'invalid-email'}
    matcher.match(template, actual)
except DictPatternMatchError as e:
    print(f"Pattern match failed at {e.path}")
    print(f"Expected pattern: {e.template}")
    print(f"Actual value: {e.actual}")
except DictStructureError as e:
    print(f"Structure mismatch: {e}")
except DictPatternError as e:
    print(f"Any dictionary pattern error: {e}")
```

### Exception Types

- **`DictKeyMismatchError`**: Dictionary keys don't match between template and actual
- **`DictListLengthMismatchError`**: Lists have different lengths
- **`DictValueMismatchError`**: Simple values don't match (with optional template/actual values)
- **`DictPatternMatchError`**: String doesn't match the pattern template
- **`DictPatternValueInconsistencyError`**: Same pattern identifier has different values
- **`DictPatternTypeError`**: Unknown pattern type encountered

## Advanced Usage

### Value Consistency

The library ensures that the same pattern identifier has consistent values across matches:

```python
template = {
    'parent_id': '{uuid:shared_id}',
    'child': {'parent_id': '{uuid:shared_id}'}  # Same identifier
}

actual = {
    'parent_id': '1d408610-f129-47a8-a4c1-1a6e0ca2d16f',
    'child': {'parent_id': '1d408610-f129-47a8-a4c1-1a6e0ca2d16f'}  # Same value
}

# This will work
matcher.match(template, actual)

# This will raise DictPatternValueInconsistencyError
actual['child']['parent_id'] = 'different-uuid'
matcher.match(template, actual)
```

### Complex Nested Structures

```python
template = {
    'users': [
        {'name': '{string}', 'email': '{email}'},
        {'name': '{string}', 'email': '{email}'}
    ],
    'metadata': {
        'total': '{number:total_count}',
        'created_at': '{timestamp:creation_time}'
    }
}
```

### Custom Patterns

```python
# Define your own patterns
patterns = {
    'string': r'[a-zA-Z]+',
    'number': r'\d+',
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'phone': r'\+?1?\d{9,15}',
    'timestamp': r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',
    'slug': r'[a-z0-9]+(?:-[a-z0-9]+)*'
}
```

## API Reference

### DictMatcher

The main class for matching dictionary objects.

#### Constructor

```python
DictMatcher(pattern_handlers: dict)
```

- `pattern_handlers`: Dictionary mapping pattern names to regex patterns

#### Methods

- `match(template: dict, actual: dict)`: Match template against actual dictionary
- `values`: Property containing matched values organized by pattern type


## Pytest Plugin

Dictionary Patterns includes a pytest plugin that provides convenient fixtures for testing. The plugin automatically registers when you install the package.

### Available Fixtures

#### `pattern_handlers`

Provides an empty dictionary for regex pattern definitions. Override this fixture in your tests to define custom patterns:

```python
import pytest

class TestWithCustomPatterns:
    @pytest.fixture
    def pattern_handlers(self):
        return {
            "string": r"[a-zA-Z]+",
            "number": r"\d+",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        }
```

#### `dict_matcher`

Provides a `DictMatcher` instance configured with the pattern handlers from the `pattern_handlers` fixture:

```python
def test_basic_matching(dict_matcher):
    template = {"name": "{string:name}", "age": "{number:age}"}
    actual = {"name": "John", "age": "25"}
    
    dict_matcher.match(template, actual)
    
    assert dict_matcher.values["string"]["name"] == "John"
    assert dict_matcher.values["number"]["age"] == "25"
```

#### `dict_match`

Provides a convenience function that performs pattern matching and returns the extracted values:

```python
def test_convenience_matching(dict_match):
    template = {"name": "{string:name}", "age": "{number:age}"}
    actual = {"name": "John", "age": "25"}
    
    extracted_values = dict_match(template, actual)
    
    assert extracted_values == {
        "string": {"name": "John"},
        "number": {"age": "25"},
    }
```

### Complete Example

```python
import pytest

class TestUserAPI:
    @pytest.fixture
    def pattern_handlers(self):
        return {
            "string": r"[a-zA-Z]+",
            "number": r"\d+",
            "uuid": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        }
    
    def test_user_response_structure(self, dict_match):
        # API response template
        template = {
            "user": {
                "id": "{uuid:user_id}",
                "name": "{string:user_name}",
                "age": "{number:user_age}",
            },
            "created_at": "{string:timestamp}",
        }
        
        # Actual API response
        actual = {
            "user": {
                "id": "1d408610-f129-47a8-a4c1-1a6e0ca2d16f",
                "name": "John Doe",
                "age": "30",
            },
            "created_at": "2024-01-15T10:30:00Z",
        }
        
        # Extract and verify values
        extracted = dict_match(template, actual)
        
        assert extracted["uuid"]["user_id"] == "1d408610-f129-47a8-a4c1-1a6e0ca2d16f"
        assert extracted["string"]["user_name"] == "John Doe"
        assert extracted["number"]["user_age"] == "30"
        assert extracted["string"]["timestamp"] == "2024-01-15T10:30:00Z"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
