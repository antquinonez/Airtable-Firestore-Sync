"""
Unit tests for AirtablePipelineConfigs module.
Tests configuration classes: AirtableConfig, DatastoreConfig, PipelineConfig, UpdateType.
"""
import pytest
from lib.AirtablePipelineConfigs import (
    AirtableConfig,
    DatastoreConfig,
    PipelineConfig,
    UpdateType
)


class TestUpdateType:
    """Tests for UpdateType enum."""

    def test_update_type_has_all_expected_values(self):
        """Verify all expected update types are present."""
        expected_types = [
            'FULL_REFRESH', 'REPLACE', 'VERSIONED', 'SOFT_DELETE',
            'UPSERT_CHECKSUM', 'UPSERT_CHECKSUM_WITH_DELETE',
            'VERSIONED_SET', 'VERSIONED_CHECKSUM',
            'VERSIONED_TABLE_CHECKSUM', 'UPSERT_TABLE_CHECKSUM'
        ]
        for type_name in expected_types:
            assert hasattr(UpdateType, type_name)

    def test_update_type_values_are_strings(self):
        """Verify all UpdateType values are strings."""
        for update_type in UpdateType:
            assert isinstance(update_type.value, str)

    def test_update_type_value_matches_expected(self):
        """Verify UpdateType values match expected string values."""
        assert UpdateType.FULL_REFRESH.value == "full_refresh"
        assert UpdateType.REPLACE.value == "replace"
        assert UpdateType.VERSIONED.value == "versioned"
        assert UpdateType.SOFT_DELETE.value == "soft_delete"
        assert UpdateType.UPSERT_CHECKSUM.value == "upsert_checksum"
        assert UpdateType.UPSERT_CHECKSUM_WITH_DELETE.value == "upsert_checksum_with_delete"
        assert UpdateType.VERSIONED_SET.value == "versioned_set"
        assert UpdateType.VERSIONED_CHECKSUM.value == "versioned_checksum"
        assert UpdateType.VERSIONED_TABLE_CHECKSUM.value == "versioned_table_checksum"
        assert UpdateType.UPSERT_TABLE_CHECKSUM.value == "upsert_table_checksum"


class TestAirtableConfig:
    """Tests for AirtableConfig dataclass."""

    def test_valid_airtable_config_creation(self, airtable_config):
        """Test creating a valid AirtableConfig."""
        assert airtable_config.base_id == "test_base_id"
        assert airtable_config.table_name == "test_table"
        assert airtable_config.view_name == "test_view"
        assert airtable_config.api_key == "test_api_key"

    def test_minimal_airtable_config_creation(self, minimal_airtable_config):
        """Test creating an AirtableConfig with only required fields."""
        assert minimal_airtable_config.base_id == "test_base_id"
        assert minimal_airtable_config.table_name == "test_table"
        assert minimal_airtable_config.api_key == "test_api_key"
        assert minimal_airtable_config.view_name is None

    def test_airtable_config_validate_success(self, airtable_config):
        """Test that validate() succeeds for valid config."""
        # Should not raise
        airtable_config.validate()

    def test_airtable_config_validate_missing_base_id(self):
        """Test validate() raises when base_id is missing."""
        config = AirtableConfig(
            base_id="",
            table_name="test_table",
            api_key="test_key"
        )
        with pytest.raises(ValueError, match="All Airtable configurations must be set"):
            config.validate()

    def test_airtable_config_validate_missing_table_name(self):
        """Test validate() raises when table_name is missing."""
        config = AirtableConfig(
            base_id="test_base_id",
            table_name="",
            api_key="test_key"
        )
        with pytest.raises(ValueError, match="All Airtable configurations must be set"):
            config.validate()

    def test_airtable_config_validate_missing_api_key(self):
        """Test validate() raises when api_key is missing."""
        config = AirtableConfig(
            base_id="test_base_id",
            table_name="test_table",
            api_key=None
        )
        with pytest.raises(ValueError, match="All Airtable configurations must be set"):
            config.validate()

    def test_airtable_config_validate_missing_all(self):
        """Test validate() raises when all fields are missing."""
        config = AirtableConfig(
            base_id=None,
            table_name=None,
            api_key=None
        )
        with pytest.raises(ValueError, match="All Airtable configurations must be set"):
            config.validate()


class TestDatastoreConfig:
    """Tests for DatastoreConfig dataclass."""

    def test_valid_datastore_config_creation(self, datastore_config):
        """Test creating a valid DatastoreConfig."""
        assert datastore_config.project_id == "test_project"
        assert datastore_config.database_id == "test_database"
        assert datastore_config.kind == "test_collection"

    def test_datastore_config_validate_success(self, datastore_config):
        """Test that validate() succeeds for valid config."""
        # Should not raise
        datastore_config.validate()

    def test_datastore_config_validate_missing_project_id(self):
        """Test validate() raises when project_id is missing."""
        config = DatastoreConfig(
            project_id="",
            database_id="test_db",
            kind="test_kind"
        )
        with pytest.raises(ValueError, match="All Datastore configurations must be set"):
            config.validate()

    def test_datastore_config_validate_missing_database_id(self):
        """Test validate() raises when database_id is missing."""
        config = DatastoreConfig(
            project_id="test_project",
            database_id="",
            kind="test_kind"
        )
        with pytest.raises(ValueError, match="All Datastore configurations must be set"):
            config.validate()

    def test_datastore_config_validate_missing_kind(self):
        """Test validate() raises when kind is missing."""
        config = DatastoreConfig(
            project_id="test_project",
            database_id="test_db",
            kind=None
        )
        with pytest.raises(ValueError, match="All Datastore configurations must be set"):
            config.validate()


class TestPipelineConfig:
    """Tests for PipelineConfig dataclass."""

    def test_valid_pipeline_config_creation(self, pipeline_config):
        """Test creating a valid PipelineConfig."""
        assert pipeline_config.airtable.base_id == "test_base_id"
        assert pipeline_config.datastore.project_id == "test_project"
        assert pipeline_config.primary_key == "id"
        assert pipeline_config.update_type == UpdateType.UPSERT_CHECKSUM

    def test_pipeline_config_validate_success(self, pipeline_config):
        """Test that validate() succeeds for valid config."""
        # Should not raise
        pipeline_config.validate()

    def test_pipeline_config_validate_missing_airtable(self):
        """Test validate() raises when airtable config is missing."""
        from lib.AirtablePipelineConfigs import DatastoreConfig
        config = PipelineConfig(
            airtable=None,
            datastore=DatastoreConfig(project_id="p", database_id="d", kind="k"),
            primary_key="id",
            update_type=UpdateType.FULL_REFRESH
        )
        with pytest.raises(ValueError, match="All configurations must be set"):
            config.validate()

    def test_pipeline_config_validate_missing_datastore(self):
        """Test validate() raises when datastore config is missing."""
        from lib.AirtablePipelineConfigs import AirtableConfig
        config = PipelineConfig(
            airtable=AirtableConfig(base_id="b", table_name="t", api_key="k"),
            datastore=None,
            primary_key="id",
            update_type=UpdateType.FULL_REFRESH
        )
        with pytest.raises(ValueError, match="All configurations must be set"):
            config.validate()

    def test_pipeline_config_validate_missing_primary_key(self):
        """Test validate() raises when primary_key is missing."""
        from lib.AirtablePipelineConfigs import AirtableConfig, DatastoreConfig
        config = PipelineConfig(
            airtable=AirtableConfig(base_id="b", table_name="t", api_key="k"),
            datastore=DatastoreConfig(project_id="p", database_id="d", kind="k"),
            primary_key=None,
            update_type=UpdateType.FULL_REFRESH
        )
        with pytest.raises(ValueError, match="All configurations must be set"):
            config.validate()

    def test_pipeline_config_validate_missing_update_type(self):
        """Test validate() raises when update_type is missing."""
        from lib.AirtablePipelineConfigs import AirtableConfig, DatastoreConfig
        config = PipelineConfig(
            airtable=AirtableConfig(base_id="b", table_name="t", api_key="k"),
            datastore=DatastoreConfig(project_id="p", database_id="d", kind="k"),
            primary_key="id",
            update_type=None
        )
        with pytest.raises(ValueError, match="All configurations must be set"):
            config.validate()

    def test_pipeline_config_validates_nested_configs(self):
        """Test that validate() also validates nested configs."""
        from lib.AirtablePipelineConfigs import AirtableConfig, DatastoreConfig
        config = PipelineConfig(
            airtable=AirtableConfig(base_id="", table_name="t", api_key="k"),  # Invalid
            datastore=DatastoreConfig(project_id="p", database_id="d", kind="k"),
            primary_key="id",
            update_type=UpdateType.FULL_REFRESH
        )
        with pytest.raises(ValueError, match="All Airtable configurations must be set"):
            config.validate()
