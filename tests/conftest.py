"""
Shared fixtures and configuration for the test suite.
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, date
import pytz


# =============================================================================
# Fixtures for Configuration Objects
# =============================================================================

@pytest.fixture
def airtable_config():
    """Provides a valid AirtableConfig for testing."""
    from lib.AirtablePipelineConfigs import AirtableConfig
    return AirtableConfig(
        base_id="test_base_id",
        table_name="test_table",
        view_name="test_view",
        api_key="test_api_key"
    )


@pytest.fixture
def datastore_config():
    """Provides a valid DatastoreConfig for testing."""
    from lib.AirtablePipelineConfigs import DatastoreConfig
    return DatastoreConfig(
        project_id="test_project",
        database_id="test_database",
        kind="test_collection"
    )


@pytest.fixture
def pipeline_config(airtable_config, datastore_config):
    """Provides a valid PipelineConfig for testing."""
    from lib.AirtablePipelineConfigs import PipelineConfig, UpdateType
    return PipelineConfig(
        airtable=airtable_config,
        datastore=datastore_config,
        primary_key="id",
        update_type=UpdateType.UPSERT_CHECKSUM
    )


@pytest.fixture
def minimal_airtable_config():
    """Provides a minimal AirtableConfig (no optional fields)."""
    from lib.AirtablePipelineConfigs import AirtableConfig
    return AirtableConfig(
        base_id="test_base_id",
        table_name="test_table",
        api_key="test_api_key"
    )


# =============================================================================
# Fixtures for Test Data
# =============================================================================

@pytest.fixture
def sample_airtable_records():
    """Provides sample Airtable records (raw format from pyairtable)."""
    return [
        {
            'id': 'rec123',
            'fields': {
                'Name': 'Record 1',
                'Description': 'First record',
                'Score': 100,
                'IsActive': True,
                'Created': '2024-01-01T00:00:00.000Z',
                'DateField': '2024-01-15',
                'MultiSelect': ['Option1', 'Option2'],
                'Attachments': [{'url': 'http://example.com/file1.jpg'}]
            }
        },
        {
            'id': 'rec456',
            'fields': {
                'Name': 'Record 2',
                'Description': 'Second record',
                'Score': 200,
                'IsActive': False,
                'Created': '2024-01-02T00:00:00.000Z',
                'DateField': '2024-02-15',
                'MultiSelect': ['Option3'],
                'Attachments': []
            }
        }
    ]


@pytest.fixture
def sample_processed_records():
    """Provides sample processed records (after DataProcessor)."""
    return [
        {
            'Name': 'Record 1',
            'Description': 'First record',
            'Score': 100.0,
            'IsActive': True,
            'Created': datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
            'DateField': date(2024, 1, 15),
            'MultiSelect': ['Option1', 'Option2'],
            'Attachments': ['http://example.com/file1.jpg']
        },
        {
            'Name': 'Record 2',
            'Description': 'Second record',
            'Score': 200.0,
            'IsActive': False,
            'Created': datetime(2024, 1, 2, 0, 0, 0, tzinfo=pytz.UTC),
            'DateField': date(2024, 2, 15),
            'MultiSelect': ['Option3'],
            'Attachments': []
        }
    ]


@pytest.fixture
def field_types():
    """Provides sample field types from Airtable metadata."""
    return {
        'Name': 'singleLineText',
        'Description': 'multilineText',
        'Score': 'number',
        'IsActive': 'checkbox',
        'Created': 'dateTime',
        'DateField': 'date',
        'MultiSelect': 'multipleSelects',
        'Attachments': 'multipleAttachments'
    }


@pytest.fixture
def mock_firestore_wrapper():
    """Provides a mock FirestoreWrapper for testing."""
    mock = MagicMock()
    mock.query_documents.return_value = []
    mock.query_documents_not_equal.return_value = []
    mock.add_document.return_value = 'mock_doc_id'
    mock.get_document.return_value = None
    mock.query_all_versions.return_value = []
    return mock


@pytest.fixture
def mock_data_fetcher(sample_airtable_records, field_types):
    """Provides a mock AirtableDataFetcher for testing."""
    mock = MagicMock()
    mock.fetch_data.return_value = sample_airtable_records
    mock.fetch_field_types.return_value = field_types
    return mock


@pytest.fixture
def mock_data_processor(sample_processed_records):
    """Provides a mock DataProcessor for testing."""
    mock = MagicMock()
    mock.process_data.return_value = sample_processed_records
    mock.process_duplicate_names.return_value = sample_processed_records
    mock.calculate_checksum.return_value = 'mock_checksum'
    mock.calculate_table_checksum.return_value = 'mock_table_checksum'
    return mock


# =============================================================================
# Fixtures for Mocking External Services
# =============================================================================

@pytest.fixture
def mock_airtable():
    """Mock for airtable-python-wrapper's Airtable class."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_pyairtable_table():
    """Mock for pyairtable's Table class."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_firestore_client():
    """Mock for google.cloud.firestore Client."""
    mock = MagicMock()
    return mock


# =============================================================================
# Autouse fixtures for test isolation
# =============================================================================

@pytest.fixture(autouse=True)
def reset_update_strategy_version_id():
    """Reset the global version_id before each test to ensure isolation."""
    import lib.UpdateStrategies as update_strategies
    original_version_id = update_strategies.version_id
    
    # Set to a fixed value for testing
    update_strategies.version_id = 1000000000
    
    yield
    
    # Restore original
    update_strategies.version_id = original_version_id


# =============================================================================
# Custom Matchers
# =============================================================================

class DictContainsSubset:
    """Matcher to check if a dict contains all key-value pairs from another dict."""
    def __init__(self, subset):
        self.subset = subset
    
    def __eq__(self, actual):
        if not isinstance(actual, dict):
            return False
        return all(actual.get(k) == v for k, v in self.subset.items())
    
    def __repr__(self):
        return f"DictContainsSubset({self.subset})"


def dict_contains(subset):
    """Returns a matcher that checks if a dict contains the given subset."""
    return DictContainsSubset(subset)
