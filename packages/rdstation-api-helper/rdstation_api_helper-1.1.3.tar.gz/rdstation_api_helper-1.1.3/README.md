## RD Station API Helper

A Python library for interacting with the RD Station API, providing ORM models, authentication, segmentation, contact, and event retrieval, as well as batch and parallel data fetching utilities.

[![PyPI version](https://img.shields.io/pypi/v/rdstation-api-helper)](https://pypi.org/project/rdstation-api-helper/)
[![Last Commit](https://img.shields.io/github/last-commit/machado000/rdstation-api-helper)](https://github.com/machado000/rdstation-api-helper/commits/main)
[![Issues](https://img.shields.io/github/issues/machado000/rdstation-api-helper)](https://github.com/machado000/rdstation-api-helper/issues)
[![License](https://img.shields.io/badge/License-GPL-yellow.svg)](https://github.com/machado000/rdstation-api-helper/blob/main/LICENSE)

## Features

- **RD Station API v2 support**: Query segmentations, contacts, leads, and conversion events
- **Batch & Parallel Fetching**: Utilities for efficient data extraction with configurable workers
- **Robust Error Handling**: Comprehensive error handling and retry logic with coordinated barriers
- **Webhook Data Processing**: Fetch and process webhook events from SQL databases
- **PostgreSQL Integration**: Built-in PostgreSQL utilities for data storage and retrieval
- **ORM Models**: SQLAlchemy models for RD Station entities (Segmentation, Contact, Lead, etc.)
- **Logging & Config Utilities**: Easy configuration and logging
- **Type Hints**: Full type hint support for better IDE experience

## Installation

```bash
pip install rdstation-api-helper
```

## Quick Start

### 1. Set up credentials

Create a `secrets/rdstation_secret.json` file with your RD Station API credentials:

```json
{
  "RDSTATION_CLIENT_ID": "YOUR_CLIENT_ID",
  "RDSTATION_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
  "RDSTATION_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
}
```

### 2. Basic usage

```python
from rdstation_api_helper import RDStationAPI

# Initialize API client (loads credentials from environment or .env)
client = RDStationAPI()

# Fetch all segmentations
segmentations = client.get_segmentations()

# Fetch contacts for each segmentation
contacts = client.get_segmentation_contacts("segmentations_id")

# Fetch contact data for a specific UUID
status_code, contact_data = client.get_contact_data("contact_uuid")

# Fetch conversion events for a contact
status_code, events = client.get_contact_events("some-contact_uuid")

# Fetch webhook events from database
from rdstation_api_helper.utils import PostgresDB, PgConfig

# Initialize database connection
db = PostgresDB()

# Fetch webhook events within date range
webhook_events = client.get_webhook_events(
    start_date="2025-08-01",
    end_date="2025-08-28", 
    engine=db.engine,
    table_name="rd_webhook_v1",
    api_version="v1"
)
```
## ORM Models

The package provides SQLAlchemy ORM models for RD Station entities, which can be used for database integration.

- `Segmentation`
- `SegmentationContact`
- `Contact`
- `ContactFunnelStatus`
- `ConversionEvents`
- `Lead`

## Database Integration

The library includes PostgreSQL utilities for easy database integration:

```python
from rdstation_api_helper.utils import PostgresDB, PgConfig

# Using environment variables (PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD)
db = PostgresDB()

# Or with custom configuration
config = PgConfig(
    host="localhost",
    port="5432", 
    dbname="mydb",
    user="myuser",
    password="mypass"
)
db = PostgresDB(config=config)

# Save data to database with upsert support
db.save_to_sql(data, Contact, upsert_values=True)
```

## Examples

Check the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Simple report extraction

## Parallel & Batch Fetching

The library provides a `parallel_decorator` utility to easily parallelize API calls for batch data fetching. This is used in the following methods of `RDStationAPI`:

- `get_contact_data_parallel(uuids: list[str])`
- `get_contact_events_parallel(uuids: list[str])`
- `get_contact_funnel_status_parallel(uuids: list[str])`

These methods accept a list of UUIDs and fetch the corresponding data in parallel, handling rate limits and transient errors automatically. The decorator coordinates retries for 429/5xx/network errors and ensures each result is tagged with its UUID.

### Usage Example

```python
from rdstation_api_helper import RDStationAPI

client = RDStationAPI()
uuids = ["uuid1", "uuid2", "uuid3"]

# Fetch contact data in parallel
_, contact_results = client.get_contact_data_parallel(uuids)

# Fetch contact events in parallel
_, events_results = client.get_contact_events_parallel(uuids)

# Fetch funnel status in parallel
_, funnel_results = client.get_contact_funnel_status_parallel(uuids)

print(contact_results)
print(events_results)
print(funnel_results)
```

**Features:**
- Automatic parallelization with configurable worker count
- Handles 429/5xx/network errors with coordinated retries
- Appends the UUID to each result for traceability

See the `rdstation_api_helper/utils.py` source for details.

## Requirements

- Python 3.10-3.12
- pandas >= 2.0.0
- python-dotenv >= 1.0.0
- requests >= 2.32.4
- sqlalchemy >= 2.0.0
- psycopg2-binary >= 2.9.0
- tqdm >= 4.65.0


## License

This project is licensed under the GPL License. See [LICENSE](LICENSE) file for details.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.