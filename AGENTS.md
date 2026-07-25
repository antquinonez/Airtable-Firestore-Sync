# AGENTS.md - Working with Airtable-Firestore-Sync

This file provides essential information for agents (AI assistants, CI/CD systems, or human developers) working with this repository.

---

## Repository Overview

**Project**: Far-Finer-Airtable-Firestore-Sync
**Type**: Python ETL Pipeline
**Purpose**: Synchronize data between Airtable and Google Cloud Firestore
**Status**: Alpha (functional but needs hardening)

---

## Project Structure

```
Airtable-Firestore-Sync/
├── lib/                          # Core library code
│   ├── AirtableToDatastore.py      # Main pipeline orchestrator
│   ├── AirtableToDatastoreBuilder.py # Builder pattern for configuration
│   ├── AirtableDataFetcher.py     # Fetches data from Airtable
│   ├── AirtablePipelineConfigs.py  # Configuration dataclasses
│   ├── DataProcessor.py            # Type conversion & data processing
│   ├── FirestoreWrapper.py         # Firestore operations
│   ├── UpdateStrategies.py         # 10 update strategy implementations
│   └── Secrets.py                 # Secret management (GCP)
├── tests/                        # Test suite (121 unit tests)
│   ├── unit/                      # Unit tests
│   │   ├── test_configs.py
│   │   ├── test_data_processor.py
│   │   ├── test_update_strategies.py
│   │   └── test_airtable_to_datastore.py
│   ├── conftest.py                # Shared fixtures
│   └── README.md                  # Test documentation
├── try_it_out.py                 # Example usage script
├── requirements.txt              # Production dependencies
├── requirements-test.txt         # Test dependencies
├── pytest.ini                    # Pytest configuration
└── .venv/                        # Python virtual environment
```

---

## Quick Start

### 1. Set Up Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 2. Configure API Keys

Create a `.env` file:
```bash
# Airtable
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id

# Google Cloud
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Firestore
FS_DATABASE_ID=your_database_id
FS_CONFIGS=your_collection_name

# Optional table-specific configs
AT_STRATEGY_SPEC_TABLE_NAME=table_name
AT_STRATEGY_SPEC_VIEW_NAME=view_name
AT_STRATEGY_SPEC_PK=primary_key_field
AT_CANDIDATE_EVAL_TABLE_NAME=table_name
AT_CANDIDATE_EVAL_VIEW_NAME=view_name
AT_CANDIDATE_EVAL_PK=primary_key_field
```

Or set environment variables directly:
```bash
export AIRTABLE_API_KEY="your_key"
export AIRTABLE_BASE_ID="your_base_id"
# ... etc
```

### 3. Run Tests

```bash
# Run all unit tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test module
python -m pytest tests/unit/test_data_processor.py

# Run with coverage
python -m pytest --cov=lib --cov-report=term-missing
```

### 4. Run Pipeline

Edit `try_it_out.py` to configure your tables, then:
```bash
python try_it_out.py
```

---

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AIRTABLE_API_KEY` | Airtable API key | `keyXXXXXXXXXXXXXX` |
| `AIRTABLE_BASE_ID` | Airtable base ID | `appXXXXXXXXXXXXXX` |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | `my-project-123` |
| `FS_DATABASE_ID` | Firestore database ID | `(default)` |
| `FS_CONFIGS` | Firestore collection name | `configs` |

### Optional Table Configuration

Each Airtable table you want to sync needs:
- `AT_*_TABLE_NAME`: The table name in Airtable
- `AT_*_VIEW_NAME`: The view name (optional)
- `AT_*_PK`: The primary key field name

---

## Update Strategies

The pipeline supports 10 update strategies:

### Record-Level Strategies

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `FULL_REFRESH` | Delete all, insert all | Complete sync, idempotent |
| `REPLACE` | Delete by PK, insert | Replace specific records |
| `SOFT_DELETE` | Update if changed, mark deleted | Track deletions without removing |
| `UPSERT_CHECKSUM` | Update if checksum differs, insert new | Efficient updates |
| `UPSERT_CHECKSUM_WITH_DELETE` | Like above + delete missing | Full sync with deletion |
| `VERSIONED` | Create new version, mark old as not latest | Audit trail |
| `VERSIONED_CHECKSUM` | New version only if changed | Versioned changes only |
| `VERSIONED_SET` | New set version if any change | Atomic set updates |

### Table-Level Strategies

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `VERSIONED_TABLE_CHECKSUM` | Single versioned record for entire table | Table as single entity |
| `UPSERT_TABLE_CHECKSUM` | Update single record if table changed | Table-level upsert |

---

## Development Guidelines

### Code Style

- Use type hints throughout
- Use dataclasses for configuration
- Use Strategy pattern for extensibility
- Use Builder pattern for complex configuration
- Log at appropriate levels (DEBUG for details, INFO for progress, ERROR for failures)

### Testing

- All code should have unit tests
- Tests use `pytest` and `unittest.mock`
- Fixtures in `tests/conftest.py`
- Run tests before committing: `python -m pytest`

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes, test
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature

# Create PR to main
```

### Branch Protection

- `main` branch is protected
- All PRs require review
- All PRs must pass tests

---

## Common Tasks

### Add New Update Strategy

1. Add enum value to `UpdateType` in `AirtablePipelineConfigs.py`
2. Create strategy class in `UpdateStrategies.py`
3. Register in `UpdateStrategyFactory._strategies`
4. Add tests in `tests/unit/test_update_strategies.py`

### Add New Field Type

1. Add type conversion in `DataProcessor._convert_value_to_firestore_type()`
2. Add tests in `tests/unit/test_data_processor.py`

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Dependencies

### Production Dependencies (`requirements.txt`)

- `airtable-python-wrapper` - Airtable API client
- `pyairtable` - Alternative Airtable client
- `requests` - HTTP requests
- `pytz` - Timezone handling
- `google-cloud-firestore` - Firestore client
- `google-cloud-secret-manager` - GCP secrets
- `google-cloud-resource-manager` - GCP resources
- `glom` - Data path access
- `python-dotenv` - .env file loading
- `dateutil` - Date parsing (implicit dependency)

### Test Dependencies (`requirements-test.txt`)

- `pytest` - Test framework
- `pytest-mock` - Mock support
- `pytest-cov` - Coverage reporting

---

## Important Notes

### Known Issues (from README.md)

1. **No tests** - RESOLVED: 121 unit tests now exist
2. **Airtable Date-time fields are currently represented as strings** - Needs native Firestore timestamp conversion
3. **The pipeline works with Airtable tables, but does not yet support Airtable views** - Partially resolved (some strategies support views)

### Global State Warning

- `UpdateStrategies.py` has a module-level `version_id` variable
- This is set once at import time
- Tests reset this via fixture to ensure isolation
- In production, this could cause issues with multiple pipeline instances

### Memory Considerations

- Large Airtable tables are loaded entirely into memory
- Consider implementing pagination for production use with large datasets

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `python -m pytest` | Run all tests |
| `python -m pytest -v` | Run tests with verbose output |
| `python -m pytest tests/unit/test_configs.py` | Run specific test file |
| `python -m pytest --cov=lib` | Run tests with coverage |
| `python -c "import lib.AirtableToDatastore; print('OK')"` | Quick import check |
| `python try_it_out.py` | Run example pipeline |
| `git status` | Check git status |
| `git log --oneline` | View commit history |

---

## Contact & Support

- **Primary Maintainer**: Anthony Quinonez
- **Repository**: Airtable-Firestore-Sync
- **License**: MIT

---

*This file is for agents (human or AI) working with this repository. Keep it updated with essential information.*
