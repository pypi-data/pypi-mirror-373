# Finder Enrichment DB Client

This package provides a Python client for interacting with the Finder Enrichment DB API.

## Features

- Complete API client for all endpoints
- Type-safe with Pydantic models
- Automatic authentication handling
- Comprehensive error handling
- Support for all enrichment operations

## Installation

```bash
pip install finder-enrichment-db-client
```

## Usage

```python
from finder_enrichment_db_client import FinderEnrichmentDBAPIClient

# Initialize client
client = FinderEnrichmentDBAPIClient(
    base_url="http://localhost:8200",
    api_key="your-api-key"
)

# Get listings
listings = client.get_listings()

# Create a new listing
# ... (see API documentation for full examples)
```

## Dependencies

- pydantic
- httpx
- finder-enrichment-db-contracts 