# Entity Linker Client

[![PyPI version](https://badge.fury.io/py/entity-linker-client.svg)](https://badge.fury.io/py/entity-linker-client)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client library for the Entity Linker service that provides intelligent entity matching and linking capabilities. This library enables developers to easily integrate powerful entity resolution features into their applications.

## Features

- **Intelligent Entity Matching**: Supports multiple matching strategies including lexical similarity, semantic similarity, and exact matching
- **Flexible Configuration**: Customizable matching rules and thresholds
- **Batch Operations**: Efficient batch processing for large datasets
- **Type Safety**: Full type annotations for better development experience
- **Simple API**: Clean and intuitive interface for easy integration

## Installation

Install the package using pip:

```bash
pip install entity-linker-client
```

## Quick Start

Here's a simple example to get you started:

```python
from entity_linker_client import EntityLinker

# Initialize the client
linker = EntityLinker(
    base_url="http://localhost:6000",
    source_columns=["name", "address", "phone"],
    target_columns=["business_name", "business_address", "contact_number"]
)

# Add some entities
entities = [
    {
        "canonical_name": "Acme Corporation",
        "aliases": ["Acme Corp", "Acme Inc"],
        "metadata": {
            "address": "123 Business Ave",
            "phone": "+1-555-0123"
        }
    }
]

added_entities = linker.add_entities_batch(entities)
print(f"Added {len(added_entities)} entities")

# Link a new entity
entity_to_link = {
    "canonical_name": "Acme Corp",
    "aliases": [],
    "metadata": {
        "address": "123 Business Avenue",
        "phone": "+1-555-0123"
    }
}

result = linker.link_entity(entity_to_link)
if result.get("linked_entity_id"):
    print(f"Found match: {result['linked_entity_id']}")
else:
    print("No match found")
```

## Configuration

### Basic Configuration

The simplest way to create a linker is by providing source and target columns:

```python
from entity_linker_client import EntityLinker

linker = EntityLinker(
    base_url="http://localhost:6000",
    source_columns=["name", "industry", "location"],
    target_columns=["company_name", "sector", "address"]
)
```

### Advanced Configuration

For more control, you can provide a custom configuration:

```python
from entity_linker_client import (
    EntityLinker, EntityLinkingConfig, OrCondition, 
    FieldCondition, MatchCondition, MatchType
)

# Create custom configuration
config = EntityLinkingConfig(
    quick_creation_config=OrCondition(
        conditions=[
            FieldCondition(
                field="canonical_name",
                condition=MatchCondition(
                    match_type=MatchType.LEXICAL_SIMILARITY,
                    threshold=80
                )
            )
        ]
    ),
    # ... other configurations
)

linker = EntityLinker(base_url="http://localhost:6000", config=config)
```

## API Reference

### EntityLinker Class

The main class for interacting with the Entity Linker service.

#### Methods

- `add_entity(entity_data)`: Add a single entity
- `add_entities_batch(entities_data)`: Add multiple entities in batch
- `get_entity(entity_id)`: Retrieve an entity by ID
- `modify_entity(entity_id, entity_data)`: Update an existing entity
- `delete_entity(entity_id)`: Delete an entity
- `link_entity(entity_data, add_entity=False)`: Find matching entities
- `link_entity_with_id(entity_id)`: Link using an existing entity ID
- `get_info()`: Get linker information
- `update_config(config)`: Update linker configuration
- `delete_linker()`: Delete the linker instance

#### Static Methods

- `list_available_linkers(base_url)`: List all available linkers
- `get_linker_info(linker_id, base_url)`: Get information about a specific linker
- `generate_config(initial_config, source_columns, target_columns, base_url)`: Generate configuration

### Configuration Classes

#### EntityLinkingConfig

Main configuration class containing:
- `quick_creation_config`: Configuration for quick entity creation
- `quick_linking_config`: Configuration for quick entity linking  
- `llm_linking_config`: Configuration for LLM-based linking
- `llm_top_k`: Number of top results for LLM linking

#### MatchType Enum

Available matching strategies:
- `STRICT_MATCH`: Exact string matching
- `LEXICAL_SIMILARITY`: Token-based similarity
- `SEMANTIC_SIMILARITY`: Embedding-based similarity
- `DICT_MATCH`: Dictionary field matching

## Examples

### Working with Entities

```python
# Add a single entity
entity = {
    "canonical_name": "OpenAI Inc",
    "aliases": ["OpenAI", "OpenAI LP"],
    "metadata": {
        "industry": "AI Research",
        "founded": "2015"
    }
}

added_entity = linker.add_entity(entity)
entity_id = added_entity["id"]

# Modify the entity
updated_data = {
    "canonical_name": "OpenAI Inc",
    "aliases": ["OpenAI", "OpenAI LP", "OpenAI L.P."],
    "metadata": {
        "industry": "Artificial Intelligence",
        "founded": "2015",
        "headquarters": "San Francisco"
    }
}

modified_entity = linker.modify_entity(entity_id, updated_data)
```

### Batch Operations

```python
# Add multiple entities at once
companies = [
    {
        "canonical_name": "Google LLC",
        "aliases": ["Google", "Alphabet Inc"],
        "metadata": {"industry": "Technology"}
    },
    {
        "canonical_name": "Microsoft Corporation", 
        "aliases": ["Microsoft", "MSFT"],
        "metadata": {"industry": "Technology"}
    }
]

batch_result = linker.add_entities_batch(companies)
print(f"Added {len(batch_result)} companies")
```

### Entity Linking

```python
# Try to link a potentially matching entity
candidate = {
    "canonical_name": "Alphabet",
    "aliases": ["Google Inc"],
    "metadata": {"industry": "Tech"}
}

# Link without adding to database
link_result = linker.link_entity(candidate, add_entity=False)

if link_result.get("linked_entity_id"):
    print(f"Found existing entity: {link_result['linked_entity_id']}")
else:
    # Add as new entity if no match found
    link_result = linker.link_entity(candidate, add_entity=True)
    print(f"Created new entity: {link_result.get('linked_entity_id', 'Failed')}")
```

## Environment Variables

You can configure the client using environment variables:

```bash
export ENTITY_LINKER_BASE_URL="http://your-entity-linker-service:6000"
```

## Error Handling

The client includes proper error handling for common scenarios:

```python
from entity_linker_client import EntityLinker
import httpx

try:
    linker = EntityLinker(base_url="http://localhost:6000")
    entity = linker.get_entity("non-existent-id")
except httpx.HTTPStatusError as e:
    print(f"HTTP error: {e.response.status_code}")
except httpx.RequestError as e:
    print(f"Request error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Requirements

- Python 3.8 or higher
- httpx >= 0.24.0
- python-dotenv >= 0.19.0

## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies: `pip install -e .[dev]`
3. Run tests: `pytest`
4. Format code: `black .`
5. Check types: `mypy .`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@godel-ai.com
- Issues: [GitHub Issues](https://github.com/godel-ai/entity-linker-client/issues)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.
