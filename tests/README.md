# Test Suite

This directory contains the test suite for the Airtable-Firestore-Sync project.

## Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── README.md            # This file
├── unit/               # Unit tests
│   ├── __init__.py
│   ├── test_configs.py           # Configuration classes tests
│   ├── test_data_processor.py    # DataProcessor tests
│   ├── test_update_strategies.py # Update strategy tests
│   └── test_airtable_to_datastore.py # Main pipeline tests
└── integration/         # Integration tests (future)
    └── __init__.py
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

Or install all dependencies (including main project dependencies):
```bash
pip install -r requirements.txt -r requirements-test.txt
```

### Running All Tests

```bash
pytest
```

Or with verbose output:
```bash
pytest -v
```

### Running Specific Test Modules

```bash
# Run only configuration tests
pytest tests/unit/test_configs.py

# Run only data processor tests
pytest tests/unit/test_data_processor.py

# Run only update strategy tests
pytest tests/unit/test_update_strategies.py

# Run only main pipeline tests
pytest tests/unit/test_airtable_to_datastore.py
```

### Running with Coverage

First install pytest-cov:
```bash
pip install pytest-cov
```

Then run tests with coverage:
```bash
pytest --cov=lib --cov-report=term-missing
```

For HTML report:
```bash
pytest --cov=lib --cov-report=html
open htmlcov/index.html
```

## Test Coverage

The current test suite covers:

- **test_configs.py**: All configuration classes (AirtableConfig, DatastoreConfig, PipelineConfig, UpdateType)
  - Creation and validation
  - Error handling for missing required fields

- **test_data_processor.py**: DataProcessor class
  - Type conversion (text, number, boolean, date, datetime, attachments, multiselect)
  - Data processing pipeline
  - Duplicate name handling
  - Checksum calculation (MD5-based)
  - Table checksum calculation
  - DateTime parsing and normalization

- **test_update_strategies.py**: All update strategy classes
  - Factory pattern (UpdateStrategyFactory)
  - FullRefreshStrategy
  - ReplaceStrategy
  - SoftDeleteStrategy
  - UpsertChecksumStrategy
  - UpsertChecksumWithDeleteStrategy
  - VersionedStrategy
  - VersionedSetStrategy
  - VersionedChecksumStrategy
  - VersionedTableChecksumStrategy
  - UpsertTableChecksumStrategy

- **test_airtable_to_datastore.py**: Main pipeline class
  - Initialization
  - Pipeline orchestration
  - Error handling
  - Logging
  - Integration with builder pattern

## Fixtures

Shared fixtures are defined in `conftest.py`:

- `airtable_config`: Valid AirtableConfig
- `datastore_config`: Valid DatastoreConfig
- `pipeline_config`: Valid PipelineConfig
- `sample_airtable_records`: Sample raw Airtable records
- `sample_processed_records`: Sample processed records
- `field_types`: Sample Airtable field types
- `mock_firestore_wrapper`: Mock FirestoreWrapper
- `mock_data_fetcher`: Mock AirtableDataFetcher
- `mock_data_processor`: Mock DataProcessor

## Test Markers

Custom markers can be used to categorize tests:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

Example:
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Notes

- Tests use `unittest.mock.MagicMock` extensively for isolation
- The `reset_update_strategy_version_id` fixture ensures test isolation by resetting the global `version_id`
- All tests are designed to run without external dependencies (Airtable API, Firestore, etc.)
