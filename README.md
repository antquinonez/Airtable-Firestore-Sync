# Far-Finer-Airtable-Firestore-Sync
A Python-based ETL pipeline for synchronizing data between Airtable and Google Cloud Firestore. This project offers flexible update strategies to easily manage data flow between these two platforms.

## Status

🚧 **Alpha Software** 🚧

This project is currently in alpha stage. While functional, it may contain bugs and is subject to significant changes. Use with caution.

Known issues:
- Unit and integration tests exist in the `tests/` directory, but additional test coverage would be beneficial

I'm actively working on resolving these issues and adding new features. Contributions and feedback are welcome!


## Features

- Flexible configuration for Airtable and Firestore connections
- Multiple update strategies
- Efficient data processing and type conversion
- Comprehensive logging and error handling

## Prerequisites

- Python 3.7+
- Airtable API key -- API works with a free account
- Google Cloud project with Firestore enabled; permissions setup, etc
- Application Default Credentials for Google Cloud (set up via `gcloud auth application-default login` or service account key)

## Installation

1. Clone this repository

2. Install the required dependencies:
pip install -r requirements.txt

3. Set up your Google Cloud credentials:
gcloud auth application-default login

## Setup

### Environment Variables

Set the following environment variables (or use a `.env` file):

**Required:**
- `AIRTABLE_API_KEY` - Your Airtable API key
- `AIRTABLE_BASE_ID` - Your Airtable base ID
- `GOOGLE_CLOUD_PROJECT` - Your Google Cloud project ID
- `FS_DATABASE_ID` - Your Firestore database ID
- `FS_CONFIGS` - Your Firestore collection name

**For specific tables (as used in try_it_out.py):**
- `AT_STRATEGY_SPEC_TABLE_NAME` - Strategy specification table name
- `AT_STRATEGY_SPEC_VIEW_NAME` - Strategy specification view name
- `AT_STRATEGY_SPEC_PK` - Strategy specification primary key field
- `AT_CANDIDATE_EVAL_TABLE_NAME` - Candidate evaluation table name
- `AT_CANDIDATE_EVAL_VIEW_NAME` - Candidate evaluation view name
- `AT_CANDIDATE_EVAL_PK` - Candidate evaluation primary key field

## Usage

### Quick Start

1. Set up your environment variables
2. Run: `python try_it_out.py`

### Using the Pipeline Directly

```python
from lib.AirtablePipelineConfigs import PipelineConfig, AirtableConfig, DatastoreConfig, UpdateType
from lib.AirtableToDatastore import AirtableToDatastore

# Configure your pipeline
airtable_config = AirtableConfig(
    base_id='your-base-id',
    table_name='your-table',
    view_name='your-view',  # Optional
    api_key='your-api-key'
)

datastore_config = DatastoreConfig(
    project_id='your-project',
    database_id='your-database',
    kind='your-collection'
)

pipeline_config = PipelineConfig(
    airtable=airtable_config,
    datastore=datastore_config,
    primary_key='your-primary-key-field',
    update_type=UpdateType.UPSERT_CHECKSUM
)

# Run the pipeline
pipeline = AirtableToDatastore(pipeline_config)
pipeline.run_pipeline()
```

### Using the Builder Pattern

```python
from lib.AirtableToDatastoreBuilder import AirtableToDatastoreBuilder

pipeline_config = (AirtableToDatastoreBuilder()
    .with_airtable_config(base_id='your-base-id', table_name='your-table', view_name='your-view', api_key='your-api-key')
    .with_datastore_config(project_id='your-project', database_id='your-database', kind='your-collection')
    .with_primary_key('your-primary-key-field')
    .with_update_type(UpdateType.VERSIONED_TABLE_CHECKSUM)
    .build())

pipeline = AirtableToDatastore(pipeline_config)
pipeline.run_pipeline()
```

## Update Strategies

The pipeline supports multiple update strategies at both the record level and table level. Airtable views are fully supported.

### Record Level Strategies

#### Basic Strategies
- **FULL_REFRESH**: Deletes all existing data in the Firestore collection and replaces it with the current Airtable data.

- **REPLACE**: For each record in Airtable, deletes any existing records with the same primary key in Firestore and inserts the new record.

- **SOFT_DELETE**: For each record in Airtable, updates the existing record in Firestore if it exists and there are changes; marks Firestore records as deleted (`is_deleted: true`) if they no longer exist in Airtable.

#### Upsert Strategies
- **UPSERT_CHECKSUM**: Compares each Airtable record with existing Firestore records using a checksum. Updates Firestore if there are changes, or inserts if the record is new.

- **UPSERT_CHECKSUM_WITH_DELETE**: Similar to UPSERT_CHECKSUM, but also deletes Firestore records that no longer exist in Airtable.

#### Versioning Strategies
- **VERSIONED**: Creates a new version of each record in Firestore, marking all previous versions as not latest (`latest: false`). Runs on every execution.

- **VERSIONED_CHECKSUM**: Creates a new version for a record only if changes are detected (via checksum), marking the previous version as not latest.

- **VERSIONED_SET**: Creates a new set of all records if any changes are detected (additions, modifications, or deletions), using a version ID. Marks all previous records as not latest.

### Table Level Strategies

Table-level strategies treat an entire Airtable table (or view) as a single record in Firestore. This is useful when you want to synchronize the complete state of a table as one document.

- **VERSIONED_TABLE_CHECKSUM**: Creates a new versioned document for the entire table if there's a change detected (via table checksum). The document contains the full table data, metadata, and checksum. Previous versions are marked as not latest.

- **UPSERT_TABLE_CHECKSUM**: Updates (or creates) a single document representing the table. If the table checksum matches the existing document, no update is performed. The document contains the full table data, metadata, and checksum.

### Data Type Handling

Airtable data types are automatically converted to appropriate Firestore types:
- `singleLineText`, `multilineText` → string
- `number` → float
- `checkbox` → boolean
- `date` → Python date object
- `dateTime` → Python datetime object
- `multipleAttachments` → list of URLs
- `multipleSelects` → list of values

## Error Handling and Logging
The pipeline includes comprehensive error handling and logging. Check the logs for detailed information about the synchronization process and any issues that may occur.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
