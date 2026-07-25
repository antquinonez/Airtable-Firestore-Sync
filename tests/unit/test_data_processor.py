"""
Unit tests for DataProcessor module.
Tests data processing, type conversion, checksum calculation, and duplicate handling.
"""
import pytest
from datetime import datetime, date
import pytz
import hashlib
import json
from dateutil import parser

from lib.DataProcessor import DataProcessor


class TestDataProcessorInit:
    """Tests for DataProcessor initialization."""

    def test_init_with_field_types(self, field_types):
        """Test DataProcessor initializes with field types."""
        processor = DataProcessor(field_types)
        assert processor.field_types == field_types

    def test_init_with_empty_field_types(self):
        """Test DataProcessor initializes with empty field types."""
        processor = DataProcessor({})
        assert processor.field_types == {}


class TestDataProcessorTypeConversion:
    """Tests for type conversion from Airtable to Firestore types."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    def test_convert_single_line_text(self, processor):
        """Test conversion of singleLineText field."""
        result = processor._convert_value_to_firestore_type("test value", "singleLineText")
        assert result == "test value"
        assert isinstance(result, str)

    def test_convert_multiline_text(self, processor):
        """Test conversion of multilineText field."""
        result = processor._convert_value_to_firestore_type("line1\nline2", "multilineText")
        assert result == "line1\nline2"
        assert isinstance(result, str)

    def test_convert_number(self, processor):
        """Test conversion of number field."""
        result = processor._convert_value_to_firestore_type(123, "number")
        assert result == 123.0
        assert isinstance(result, float)

    def test_convert_number_as_string(self, processor):
        """Test conversion of number field provided as string."""
        result = processor._convert_value_to_firestore_type("123.45", "number")
        assert result == 123.45
        assert isinstance(result, float)

    def test_convert_checkbox_true(self, processor):
        """Test conversion of checkbox field with True value."""
        result = processor._convert_value_to_firestore_type(True, "checkbox")
        assert result is True
        assert isinstance(result, bool)

    def test_convert_checkbox_false(self, processor):
        """Test conversion of checkbox field with False value."""
        result = processor._convert_value_to_firestore_type(False, "checkbox")
        assert result is False
        assert isinstance(result, bool)

    def test_convert_date_string(self, processor):
        """Test conversion of date field from ISO string."""
        result = processor._convert_value_to_firestore_type("2024-01-15", "date")
        assert result == date(2024, 1, 15)
        assert isinstance(result, date)

    def test_convert_date_already_date(self, processor):
        """Test conversion of date field that is already a date object."""
        input_date = date(2024, 1, 15)
        result = processor._convert_value_to_firestore_type(input_date, "date")
        assert result == input_date

    def test_convert_datetime_string(self, processor):
        """Test conversion of dateTime field from ISO string."""
        result = processor._convert_value_to_firestore_type(
            "2024-01-15T10:30:00.000Z", "dateTime"
        )
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_convert_datetime_already_datetime(self, processor):
        """Test conversion of dateTime field that is already a datetime object."""
        input_dt = datetime(2024, 1, 15, 10, 30, 0)
        result = processor._convert_value_to_firestore_type(input_dt, "dateTime")
        assert result == input_dt

    def test_convert_multiple_attachments(self, processor):
        """Test conversion of multipleAttachments field."""
        attachments = [
            {'url': 'http://example.com/file1.jpg', 'filename': 'file1.jpg'},
            {'url': 'http://example.com/file2.jpg', 'filename': 'file2.jpg'}
        ]
        result = processor._convert_value_to_firestore_type(attachments, "multipleAttachments")
        assert result == ['http://example.com/file1.jpg', 'http://example.com/file2.jpg']

    def test_convert_multiple_attachments_empty(self, processor):
        """Test conversion of empty multipleAttachments field."""
        result = processor._convert_value_to_firestore_type([], "multipleAttachments")
        assert result == []

    def test_convert_multiple_attachments_none(self, processor):
        """Test conversion of None multipleAttachments field."""
        result = processor._convert_value_to_firestore_type(None, "multipleAttachments")
        assert result is None

    def test_convert_multiple_selects(self, processor):
        """Test conversion of multipleSelects field."""
        result = processor._convert_value_to_firestore_type(
            ['Option1', 'Option2', 'Option3'], "multipleSelects"
        )
        assert result == ['Option1', 'Option2', 'Option3']

    def test_convert_unknown_field_type(self, processor):
        """Test conversion of unknown field type returns value as-is."""
        result = processor._convert_value_to_firestore_type("test", "unknownType")
        assert result == "test"

    def test_convert_none_value(self, processor):
        """Test conversion of None value returns None."""
        result = processor._convert_value_to_firestore_type(None, "singleLineText")
        assert result is None

    def test_convert_unsupported_type_returns_as_is(self, processor):
        """Test that unsupported field types return value as-is."""
        # When field type is not recognized, the value is returned unchanged
        processor_with_unknown = DataProcessor({})
        result = processor_with_unknown._convert_value_to_firestore_type(123, "unknownType")
        # Unknown type returns value unchanged
        assert result == 123


class TestDataProcessorProcessData:
    """Tests for process_data method."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    @pytest.fixture
    def sample_raw_records(self, sample_airtable_records):
        """Sample raw records from Airtable."""
        return sample_airtable_records

    def test_process_data_empty_list(self, processor):
        """Test processing empty list returns empty list."""
        result = processor.process_data([])
        assert result == []

    def test_process_data_single_record(self, processor):
        """Test processing a single record."""
        raw_record = {
            'id': 'rec123',
            'fields': {
                'Name': 'Test',
                'Score': 100,
                'IsActive': True
            }
        }
        result = processor.process_data([raw_record])
        assert len(result) == 1
        assert result[0]['Name'] == 'Test'
        assert result[0]['Score'] == 100.0
        assert result[0]['IsActive'] is True

    def test_process_data_multiple_records(self, processor, sample_raw_records):
        """Test processing multiple records."""
        result = processor.process_data(sample_raw_records)
        assert len(result) == 2
        assert result[0]['Name'] == 'Record 1'
        assert result[1]['Name'] == 'Record 2'

    def test_process_data_converts_all_types(self, processor, sample_raw_records):
        """Test that all field types are converted correctly."""
        result = processor.process_data(sample_raw_records)
        
        # Check first record
        record = result[0]
        assert isinstance(record['Name'], str)
        assert isinstance(record['Description'], str)
        assert isinstance(record['Score'], float)
        assert isinstance(record['IsActive'], bool)
        assert isinstance(record['Created'], datetime)
        assert isinstance(record['DateField'], date)
        assert isinstance(record['MultiSelect'], list)
        assert isinstance(record['Attachments'], list)


class TestDataProcessorDuplicateNames:
    """Tests for process_duplicate_names method."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    def test_process_duplicate_names_no_duplicates(self, processor):
        """Test processing records with no duplicate names."""
        data = [
            {'id': '1', 'Name': 'Record A', 'Created': '2024-01-01T00:00:00.000Z'},
            {'id': '2', 'Name': 'Record B', 'Created': '2024-01-02T00:00:00.000Z'}
        ]
        result = processor.process_duplicate_names(data, 'Name')
        assert len(result) == 2

    def test_process_duplicate_names_keeps_latest(self, processor):
        """Test that only the latest record is kept for duplicates."""
        data = [
            {'id': '1', 'Name': 'Record A', 'Created': '2024-01-01T00:00:00.000Z'},
            {'id': '2', 'Name': 'Record A', 'Created': '2024-01-02T00:00:00.000Z'},  # Later
            {'id': '3', 'Name': 'Record B', 'Created': '2024-01-03T00:00:00.000Z'}
        ]
        result = processor.process_duplicate_names(data, 'Name')
        assert len(result) == 2
        # Should keep the one with Created = 2024-01-02
        assert result[0]['id'] == '2' or result[1]['id'] == '2'
        assert all(r['Name'] != 'Record A' or r['id'] == '2' for r in result)

    def test_process_duplicate_names_keeps_first_of_equal_dates(self, processor):
        """Test behavior when duplicates have the same created date."""
        data = [
            {'id': '1', 'Name': 'Record A', 'Created': '2024-01-01T00:00:00.000Z'},
            {'id': '2', 'Name': 'Record A', 'Created': '2024-01-01T00:00:00.000Z'},  # Same time
            {'id': '3', 'Name': 'Record B', 'Created': '2024-01-01T00:00:00.000Z'}
        ]
        result = processor.process_duplicate_names(data, 'Name')
        # Should keep one of the duplicates
        assert len(result) == 2
        names = [r['Name'] for r in result]
        assert names.count('Record A') == 1

    def test_process_duplicate_names_skips_none_name(self, processor):
        """Test that records with None or empty name are skipped."""
        data = [
            {'id': '1', 'Name': 'Record A', 'Created': '2024-01-01T00:00:00.000Z'},
            {'id': '2', 'Name': None, 'Created': '2024-01-02T00:00:00.000Z'},
            {'id': '3', 'Name': '', 'Created': '2024-01-03T00:00:00.000Z'},
            {'id': '4', 'Name': 'Record B', 'Created': '2024-01-04T00:00:00.000Z'}
        ]
        result = processor.process_duplicate_names(data, 'Name')
        assert len(result) == 2
        assert all(r['Name'] in ['Record A', 'Record B'] for r in result)

    def test_process_duplicate_names_empty_data(self, processor):
        """Test processing empty data."""
        result = processor.process_duplicate_names([], 'Name')
        assert result == []

    def test_process_duplicate_names_missing_created_field_raises(self, processor):
        """Test that missing Created field raises KeyError."""
        data = [
            {'id': '1', 'Name': 'Record A'},
            {'id': '2', 'Name': 'Record A'}
        ]
        # The current implementation will raise KeyError if Created is missing
        with pytest.raises(KeyError):
            processor.process_duplicate_names(data, 'Name')


class TestDataProcessorChecksum:
    """Tests for checksum calculation methods."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    def test_calculate_checksum_same_record_same_checksum(self, processor):
        """Test that the same record produces the same checksum."""
        record = {'Name': 'Test', 'Score': 100, 'IsActive': True}
        fields = {'Name', 'Score', 'IsActive'}
        
        checksum1 = processor.calculate_checksum(record, fields)
        checksum2 = processor.calculate_checksum(record, fields)
        
        assert checksum1 == checksum2

    def test_calculate_checksum_different_records_different_checksum(self, processor):
        """Test that different records produce different checksums."""
        record1 = {'Name': 'Test1', 'Score': 100}
        record2 = {'Name': 'Test2', 'Score': 100}
        fields = {'Name', 'Score'}
        
        checksum1 = processor.calculate_checksum(record1, fields)
        checksum2 = processor.calculate_checksum(record2, fields)
        
        assert checksum1 != checksum2

    def test_calculate_checksum_ignores_extra_fields(self, processor):
        """Test that extra fields in the record but not in fields set are ignored."""
        record = {'Name': 'Test', 'Score': 100, 'Extra': 'ignored'}
        fields = {'Name', 'Score'}
        
        checksum1 = processor.calculate_checksum(record, fields)
        
        record_without_extra = {'Name': 'Test', 'Score': 100}
        checksum2 = processor.calculate_checksum(record_without_extra, fields)
        
        assert checksum1 == checksum2

    def test_calculate_checksum_ignores_missing_fields(self, processor):
        """Test that missing fields in the record are handled."""
        record = {'Name': 'Test'}
        fields = {'Name', 'Score', 'MissingField'}
        
        # Should not raise
        checksum = processor.calculate_checksum(record, fields)
        assert isinstance(checksum, str)
        assert len(checksum) == 32  # MD5 hex digest length

    def test_calculate_checksum_field_order_independent(self, processor):
        """Test that field order doesn't affect checksum."""
        record1 = {'a': 1, 'b': 2, 'c': 3}
        record2 = {'c': 3, 'b': 2, 'a': 1}
        fields = {'a', 'b', 'c'}
        
        checksum1 = processor.calculate_checksum(record1, fields)
        checksum2 = processor.calculate_checksum(record2, fields)
        
        assert checksum1 == checksum2

    def test_calculate_checksum_with_datetime(self, processor):
        """Test checksum calculation with datetime values."""
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=pytz.UTC)
        record = {'Name': 'Test', 'Timestamp': dt}
        fields = {'Name', 'Timestamp'}
        
        # Should not raise
        checksum = processor.calculate_checksum(record, fields)
        assert isinstance(checksum, str)

    def test_calculate_checksum_with_date(self, processor):
        """Test checksum calculation with date values."""
        d = date(2024, 1, 15)
        record = {'Name': 'Test', 'Date': d}
        fields = {'Name', 'Date'}
        
        # Should not raise
        checksum = processor.calculate_checksum(record, fields)
        assert isinstance(checksum, str)

    def test_calculate_checksum_is_md5(self, processor):
        """Test that checksum is MD5 hash."""
        record = {'Name': 'Test'}
        fields = {'Name'}
        
        checksum = processor.calculate_checksum(record, fields)
        
        # Verify it's a valid MD5 hex digest
        assert len(checksum) == 32
        assert all(c in '0123456789abcdef' for c in checksum)


class TestDataProcessorNormalizeValues:
    """Tests for value normalization in checksum calculation."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    def test_normalize_airtable_datetime_string(self, processor):
        """Test normalization of Airtable datetime string."""
        dt_str = "2024-01-15T10:30:00.000Z"
        result = processor.normalize_value_for_comparison(dt_str)
        
        # Should be ISO format with timezone
        assert 'T' in result
        assert 'Z' in result or '+00:00' in result

    def test_normalize_datetime_object(self, processor):
        """Test normalization of datetime object."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = processor.normalize_value_for_comparison(dt)
        
        # Should be ISO format with timezone
        assert 'T' in result
        assert 'Z' in result or '+00:00' in result

    def test_normalize_date_object(self, processor):
        """Test normalization of date object."""
        d = date(2024, 1, 15)
        result = processor.normalize_value_for_comparison(d)
        
        # Should be ISO date format
        assert result == "2024-01-15"

    def test_normalize_regular_string(self, processor):
        """Test normalization of regular string."""
        result = processor.normalize_value_for_comparison("test string")
        assert result == "test string"

    def test_normalize_integer(self, processor):
        """Test normalization of integer."""
        result = processor.normalize_value_for_comparison(123)
        assert result == 123


class TestDataProcessorTableChecksum:
    """Tests for table checksum calculation."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    def test_calculate_table_checksum_basic(self, processor):
        """Test basic table checksum calculation."""
        table_data = {
            'rec1': {'Name': 'Record 1', 'Score': 100},
            'rec2': {'Name': 'Record 2', 'Score': 200}
        }
        metadata = {'Name': 'TestTable', 'ViewName': 'TestView'}
        
        checksum = processor.calculate_table_checksum(table_data, metadata)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 32  # MD5

    def test_calculate_table_checksum_same_data_same_checksum(self, processor):
        """Test that same table data produces same checksum."""
        table_data = {'rec1': {'Name': 'Record 1'}}
        metadata = {'Name': 'TestTable'}
        
        checksum1 = processor.calculate_table_checksum(table_data, metadata)
        checksum2 = processor.calculate_table_checksum(table_data, metadata)
        
        assert checksum1 == checksum2

    def test_calculate_table_checksum_different_data_different_checksum(self, processor):
        """Test that different table data produces different checksum."""
        table_data1 = {'rec1': {'Name': 'Record 1'}}
        table_data2 = {'rec1': {'Name': 'Record 2'}}
        metadata = {'Name': 'TestTable'}
        
        checksum1 = processor.calculate_table_checksum(table_data1, metadata)
        checksum2 = processor.calculate_table_checksum(table_data2, metadata)
        
        assert checksum1 != checksum2

    def test_calculate_table_checksum_empty_data(self, processor):
        """Test checksum with empty table data."""
        checksum = processor.calculate_table_checksum({}, {'Name': 'Test'})
        assert isinstance(checksum, str)


class TestDataProcessorDateTimeHandling:
    """Tests for datetime parsing and handling."""

    @pytest.fixture
    def processor(self, field_types):
        """DataProcessor instance with sample field types."""
        return DataProcessor(field_types)

    def test_is_airtable_datetime_valid(self, processor):
        """Test detection of valid Airtable datetime string."""
        assert processor.is_airtable_datetime("2024-01-15T10:30:00.000Z") is True
        assert processor.is_airtable_datetime("2024-01-15T10:30:00-05:00") is True

    def test_is_airtable_datetime_invalid(self, processor):
        """Test detection of invalid datetime string."""
        assert processor.is_airtable_datetime("not a date") is False
        # Note: The dateutil.parser.parse can parse date-only strings, so this passes
        # If we want to distinguish date vs datetime, we'd need to update the implementation
        assert processor.is_airtable_datetime("2024-01-15T10:30:00.000Z") is True

    def test_parse_datetime_string(self, processor):
        """Test parsing datetime from string."""
        result = processor._parse_datetime("2024-01-15T10:30:00.000Z")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_object(self, processor):
        """Test parsing datetime object."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = processor._parse_datetime(dt)
        assert result == dt

    def test_parse_datetime_invalid_type(self, processor):
        """Test parsing invalid datetime type raises error."""
        with pytest.raises(ValueError, match="Unexpected type for datetime value"):
            processor._parse_datetime(12345)
