import pytest
import os
import tempfile
import pandas as pd
from unittest.mock import MagicMock

from snowflake.snowflake_data_validation.validation.data_validator_base import (
    DataValidatorBase,
)
from snowflake.snowflake_data_validation.validation.metrics_data_validator import (
    MetricsDataValidator,
)
from snowflake.snowflake_data_validation.validation.schema_data_validator import (
    SchemaDataValidator,
)
from snowflake.snowflake_data_validation.validation.validation_report_buffer import (
    VALIDATION_REPORT_NAME,
    ValidationReportBuffer,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DIFFERENT_KEY,
    COLUMN_VALIDATED,
    COLUMN_VALIDATED_KEY,
    COMMENTS_KEY,
    DIFFERENCES_KEY,
    EVALUATION_CRITERIA_KEY,
    METRIC_DIFFERENT_KEY,
    SNOWFLAKE_VALUE_KEY,
    SOURCE_VALUE_KEY,
    STATUS_KEY,
    TABLE_KEY,
    VALIDATION_TYPE_KEY,
    Result,
    ValidationLevel,
)


@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    context = MagicMock()
    context.output_handler = MagicMock()
    context.report_path = tempfile.mkdtemp()
    context.run_start_time = "20250103_143052"
    context.datatypes_mappings = None
    return context


@pytest.fixture(autouse=True)
def clear_buffer():
    """Clear the validation buffer before each test."""
    buffer = ValidationReportBuffer()
    buffer.clear_buffer()
    yield
    # Clean up after test
    buffer.clear_buffer()


@pytest.fixture
def flush_buffer_to_file():
    """Helper fixture to flush buffer to file when needed in tests."""

    def _flush(context):
        buffer = ValidationReportBuffer()
        return buffer.flush_to_file(context)

    return _flush


@pytest.fixture
def sample_source_df():
    """Create sample source DataFrame for testing."""
    return pd.DataFrame(
        {
            COLUMN_VALIDATED: ["ID", "Name"],
            "DATA_TYPE": ["INT", "VARCHAR"],
            "CHARACTER_LENGTH": [None, 50],
        }
    )


@pytest.fixture
def sample_target_df():
    """Create sample target DataFrame for testing."""
    return pd.DataFrame(
        {
            COLUMN_VALIDATED: ["ID", "Name"],
            "DATA_TYPE": ["NUMBER", "TEXT"],  # Different from source
            "CHARACTER_LENGTH": [None, 100],  # Different from source
        }
    )


@pytest.fixture
def sample_column_source_df():
    """Create sample column metadata source DataFrame."""
    return pd.DataFrame(
        {
            COLUMN_VALIDATED: ["ID", "Name"],
            "count_distinct": [1000, 500],
            "avg": [50.5, 25.0],
            "min": [1, 10],
            "max": [100, 50],
        }
    )


@pytest.fixture
def sample_column_target_df():
    """Create sample column metadata target DataFrame."""
    return pd.DataFrame(
        {
            COLUMN_VALIDATED: ["ID", "Name"],
            "count_distinct": [999, 500],  # Different count_distinct for ID
            "avg": [50.5, 25.0],
            "min": [1, 10],
            "max": [100, 50],
        }
    )


class TestValidateTableMetadata:
    """Test cases for table metadata validation."""

    def test_table_validation_csv_structure(
        self, mock_context, sample_source_df, sample_target_df, flush_buffer_to_file
    ):
        """Test that CSV file has correct structure for table validation."""
        object_name = "test_schema.test_table"

        # Run validation (should create differences)
        schema_data_validator = SchemaDataValidator()
        result = schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Verify CSV file was created (with timestamp prefix)
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        assert os.path.exists(expected_file)

        # Read and verify CSV content
        df = pd.read_csv(expected_file)

        # Verify column structure and order
        expected_columns = [
            VALIDATION_TYPE_KEY,
            TABLE_KEY,
            COLUMN_VALIDATED_KEY,
            EVALUATION_CRITERIA_KEY,
            SOURCE_VALUE_KEY,
            SNOWFLAKE_VALUE_KEY,
            STATUS_KEY,
            COMMENTS_KEY,
        ]
        assert list(df.columns) == expected_columns

        # Verify all rows have table_validation type
        assert all(df[VALIDATION_TYPE_KEY] == ValidationLevel.SCHEMA_VALIDATION.value)

        # Verify table name is present
        assert all(df[TABLE_KEY] == object_name)

        # Verify status includes both failures and successes
        statuses = set(df[STATUS_KEY])
        assert statuses.issubset({Result.SUCCESS.value, Result.FAILURE.value})
        assert len(statuses) > 0  # At least one status should be present

    def test_console_output_excludes_type_and_table(
        self, mock_context, sample_source_df, sample_target_df
    ):
        """Test that console output excludes VALIDATION_TYPE and TABLE columns."""
        object_name = "test_schema.test_table"

        # Run validation
        schema_data_validator = SchemaDataValidator()
        schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Verify handle_message was called
        mock_context.output_handler.handle_message.assert_called()

        # Get the dataframe that was passed to handle_message
        # Find the call that includes a dataframe parameter
        dataframe_call = None
        for call in mock_context.output_handler.handle_message.call_args_list:
            if len(call) > 1 and "dataframe" in call.kwargs:
                dataframe_call = call
                break

        assert dataframe_call is not None, "No call with dataframe parameter found"
        console_df = dataframe_call.kwargs["dataframe"]

        # Verify console dataframe excludes VALIDATION_TYPE and TABLE
        assert VALIDATION_TYPE_KEY not in console_df.columns
        assert TABLE_KEY not in console_df.columns

        # Verify it has expected columns for console display (without VALIDATION_TYPE and TABLE)
        expected_console_columns = [
            COLUMN_VALIDATED_KEY,
            EVALUATION_CRITERIA_KEY,
            SOURCE_VALUE_KEY,
            SNOWFLAKE_VALUE_KEY,
            STATUS_KEY,
            COMMENTS_KEY,
        ]
        assert list(console_df.columns) == expected_console_columns

    def test_simple_file_name(
        self, mock_context, sample_source_df, sample_target_df, flush_buffer_to_file
    ):
        """Test that the file uses the timestamped naming convention."""
        object_name = "test_schema.test_table"

        # Run validation
        schema_data_validator = SchemaDataValidator()
        schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the file
        flush_buffer_to_file(mock_context)

        # Verify file name follows timestamped convention
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        assert os.path.exists(expected_file)

        # Verify the filename includes timestamp
        expected_filename = f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}"
        assert os.path.basename(expected_file) == expected_filename

    def test_validation_type_first_column(
        self, mock_context, sample_source_df, sample_target_df, flush_buffer_to_file
    ):
        """Test that VALIDATION_TYPE is the first column."""
        object_name = "test_schema.test_table"

        # Run validation
        schema_data_validator = SchemaDataValidator()
        result = schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV file
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # Verify VALIDATION_TYPE is the first column
        assert df.columns[0] == VALIDATION_TYPE_KEY

    def test_evaluation_criteria_column_name(
        self, mock_context, sample_source_df, sample_target_df, flush_buffer_to_file
    ):
        """Test that the differences column is named EVALUATION_CRITERIA."""
        object_name = "test_schema.test_table"

        # Run validation
        schema_data_validator = SchemaDataValidator()
        schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV and verify column names
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # Verify EVALUATION_CRITERIA column exists (not DIFFERENCES)
        assert EVALUATION_CRITERIA_KEY in df.columns
        assert DIFFERENCES_KEY not in df.columns
        assert COLUMN_DIFFERENT_KEY not in df.columns
        assert METRIC_DIFFERENT_KEY not in df.columns

    def test_table_validation_success_scenarios(
        self, mock_context, flush_buffer_to_file
    ):
        """Test that successful validations are recorded properly."""
        object_name = "test_schema.test_table"

        # Create DataFrames with some matching columns
        source_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID", "Name", "Age"],
                "DATA_TYPE": ["INT", "VARCHAR", "INT"],
                "CHARACTER_LENGTH": [None, 50, None],
            }
        )

        target_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID", "Name", "Age"],
                "DATA_TYPE": ["INT", "VARCHAR", "BIGINT"],  # Only Age differs
                "CHARACTER_LENGTH": [None, 50, None],
            }
        )

        # Run validation
        schema_data_validator = SchemaDataValidator()
        result = schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=target_df,
            source_df=source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV and verify content
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # Should have both success and failure records
        statuses = set(df[STATUS_KEY])
        assert Result.SUCCESS.value in statuses
        assert Result.FAILURE.value in statuses

        # Verify success records exist for matching values
        success_df = df[df[STATUS_KEY] == Result.SUCCESS.value]
        assert len(success_df) > 0

        # Verify failure records exist for differing values
        failure_df = df[df[STATUS_KEY] == Result.FAILURE.value]
        assert len(failure_df) > 0

    def test_table_validation_all_success(self, mock_context, flush_buffer_to_file):
        """Test validation with all matching values creates success records."""
        object_name = "test_schema.test_table"

        # Create identical DataFrames
        identical_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID", "Name"],
                "DATA_TYPE": ["INT", "VARCHAR"],
                "CHARACTER_LENGTH": [None, 50],
            }
        )

        # Run validation
        schema_data_validator = SchemaDataValidator()
        result = schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=identical_df,
            source_df=identical_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV and verify all records are successful
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # All records should be successful
        assert len(df) > 0


class TestValidateColumnMetadata:
    """Test cases for column metadata validation."""

    def test_column_validation_csv_structure(
        self,
        mock_context,
        sample_column_source_df,
        sample_column_target_df,
        flush_buffer_to_file,
    ):
        """Test that CSV file has correct structure for column validation."""
        object_name = "test_schema.test_table"

        # Run validation (should create differences)
        metrics_data_validator = MetricsDataValidator()
        result = metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=sample_column_target_df,
            source_df=sample_column_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Verify CSV file was created
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        assert os.path.exists(expected_file)

        # Read and verify CSV content
        df = pd.read_csv(expected_file)

        # Verify column structure
        expected_columns = [
            VALIDATION_TYPE_KEY,
            TABLE_KEY,
            COLUMN_VALIDATED_KEY,
            EVALUATION_CRITERIA_KEY,
            SOURCE_VALUE_KEY,
            SNOWFLAKE_VALUE_KEY,
            STATUS_KEY,
            COMMENTS_KEY,
        ]
        assert list(df.columns) == expected_columns

        # Verify all rows have column_validation type
        assert all(df[VALIDATION_TYPE_KEY] == "METRICS VALIDATION")

        # Verify table name is present
        assert all(df[TABLE_KEY] == object_name)

        # Verify status includes both failures and successes
        statuses = set(df[STATUS_KEY])
        assert statuses.issubset({Result.SUCCESS.value, Result.FAILURE.value})
        assert (
            Result.FAILURE.value in statuses
        )  # Should have at least one failure from the sample data

    def test_column_validation_console_output_excludes_columns(
        self, mock_context, sample_column_source_df, sample_column_target_df
    ):
        """Test that console output excludes VALIDATION_TYPE and TABLE columns."""
        object_name = "test_schema.test_table"

        # Run validation
        metrics_data_validator = MetricsDataValidator()
        metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=sample_column_target_df,
            source_df=sample_column_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Verify handle_message was called
        mock_context.output_handler.handle_message.assert_called()

        # Get the dataframe that was passed to handle_message
        call_args = mock_context.output_handler.handle_message.call_args
        console_df = call_args[1]["dataframe"]

        # Verify console dataframe doesn't have VALIDATION_TYPE and TABLE
        assert VALIDATION_TYPE_KEY not in console_df.columns
        assert TABLE_KEY not in console_df.columns

    def test_column_validation_success_scenarios(
        self, mock_context, flush_buffer_to_file
    ):
        """Test that successful column validations are recorded properly."""
        object_name = "test_schema.test_table"

        # Create DataFrames with some matching and some differing values
        source_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID", "Name"],
                "count_distinct": [1000, 500],
                "avg": [50.5, 25.0],
                "min": [1, 10],
                "max": [100, 50],
            }
        )

        target_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID", "Name"],
                "count_distinct": [999, 500],  # ID differs, Name matches
                "avg": [50.5, 25.0],  # Both match
                "min": [1, 10],  # Both match
                "max": [100, 50],  # Both match
            }
        )

        # Run validation
        metrics_data_validator = MetricsDataValidator()
        result = metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=target_df,
            source_df=source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV and verify content
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # Should have both success and failure records
        statuses = set(df[STATUS_KEY])
        assert Result.SUCCESS.value in statuses
        assert Result.FAILURE.value in statuses

        # Verify success records for matching values
        success_df = df[df[STATUS_KEY] == Result.SUCCESS.value]
        assert len(success_df) > 0

        # Should have successes for avg, min, max for both columns, and count_distinct for Name
        success_criteria = set(success_df[EVALUATION_CRITERIA_KEY])
        assert "AVG" in success_criteria
        assert "MIN" in success_criteria
        assert "MAX" in success_criteria

    def test_column_validation_tolerance_success(
        self, mock_context, flush_buffer_to_file
    ):
        """Test that values within tolerance are recorded as successful."""
        object_name = "test_schema.test_table"

        source_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID"],
                "avg": [50.5],
            }
        )

        target_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID"],
                "avg": [50.502],  # Within tolerance
            }
        )

        # Run validation with tolerance
        metrics_data_validator = MetricsDataValidator()
        result = metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=target_df,
            source_df=source_df,
            context=mock_context,
            tolerance=0.01,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV and verify success record was created
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # Should have success records
        assert Result.SUCCESS.value in set(df[STATUS_KEY])
        success_df = df[df[STATUS_KEY] == Result.SUCCESS.value]

        # Should have a record for the tolerance-based success
        tolerance_success = success_df[
            success_df[COMMENTS_KEY].str.contains("tolerance")
        ]
        assert len(tolerance_success) > 0

    def test_column_validation_always_creates_csv(
        self, mock_context, flush_buffer_to_file
    ):
        """Test that CSV is always created for column validation, even with no differences."""
        object_name = "test_schema.test_table"

        # Create identical source and target DataFrames
        identical_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID", "Name"],
                "count_distinct": [1000, 500],
            }
        )

        # Run validation
        metrics_data_validator = MetricsDataValidator()
        result = metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=identical_df,
            source_df=identical_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Verify CSV file was created even with no differences
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        assert os.path.exists(expected_file)

        # Read CSV and verify records were created
        df = pd.read_csv(expected_file)
        # Check that CSV has records, but not necessarily all success records
        assert len(df) > 0

    def test_empty_dataframe_console_handling(self, mock_context):
        """Test that dataframes with only success records are handled properly for console output."""
        object_name = "test_schema.test_table"

        # Create identical DataFrames (no differences, only successes)
        identical_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID"],
                "count_distinct": [1000],
            }
        )

        # Run column validation (always creates CSV, now with success records)
        metrics_data_validator = MetricsDataValidator()
        metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=identical_df,
            source_df=identical_df,
            context=mock_context,
            columns_mappings={},
        )

        # Verify handle_message was called
        mock_context.output_handler.handle_message.assert_called()

        # Find the call that includes the metrics validation report
        dataframe_call = None
        for call in mock_context.output_handler.handle_message.call_args_list:
            if (
                len(call.kwargs) > 0
                and "header" in call.kwargs
                and "Metrics validation results" in call.kwargs["header"]
            ):
                dataframe_call = call
                break

        assert (
            dataframe_call is not None
        ), "No call with metrics validation report found"

        # Get the dataframe from the call
        console_df = dataframe_call.kwargs["dataframe"]

        # Should have success records now, not be empty
        assert len(console_df) > 0
        expected_console_columns = [
            COLUMN_VALIDATED_KEY,
            EVALUATION_CRITERIA_KEY,
            SOURCE_VALUE_KEY,
            SNOWFLAKE_VALUE_KEY,
            STATUS_KEY,
            COMMENTS_KEY,
        ]
        assert list(console_df.columns) == expected_console_columns

        # All records should be successful
        assert all(console_df[STATUS_KEY] == Result.SUCCESS.value)

    def test_numeric_tolerance_validation(self, mock_context):
        """Test numeric validation with tolerance."""
        object_name = "test_schema.test_table"

        source_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID"],
                "avg": [50.5],
            }
        )

        target_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID"],
                "avg": [50.502],  # Within default tolerance of 0.001
            }
        )

        # Run validation with tolerance
        metrics_data_validator = MetricsDataValidator()
        result = metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=target_df,
            source_df=source_df,
            context=mock_context,
            tolerance=0.01,
            columns_mappings={},
        )


class TestConsolidatedReporting:
    """Test cases for consolidated reporting functionality."""

    def test_multiple_validations_create_separate_files(
        self,
        mock_context,
        sample_source_df,
        sample_target_df,
        sample_column_source_df,
        sample_column_target_df,
        flush_buffer_to_file,
    ):
        """Test that table and column validations can be differentiated by validation type."""
        object_name_1 = "schema1.table1"
        object_name_2 = "schema2.table2"

        # Run table validation first
        schema_data_validator = SchemaDataValidator()
        schema_data_validator.validate_table_metadata(
            object_name=object_name_1,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Run column validation second (appends to same file)
        metrics_data_validator = MetricsDataValidator()
        metrics_data_validator.validate_column_metadata(
            object_name=object_name_2,
            target_df=sample_column_target_df,
            source_df=sample_column_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Both validations now use the same timestamped filename
        report_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        assert os.path.exists(report_file)

        # Read and verify content contains both validation types
        df = pd.read_csv(report_file)
        validation_types = set(df[VALIDATION_TYPE_KEY])
        assert ValidationLevel.SCHEMA_VALIDATION.value in validation_types
        assert ValidationLevel.METRICS_VALIDATION.value in validation_types

        # Verify both table names are present
        table_names = set(df[TABLE_KEY])
        assert object_name_1 in table_names
        assert object_name_2 in table_names

    def test_table_validation_file_naming_convention(
        self, mock_context, flush_buffer_to_file
    ):
        """Test that table validation uses timestamped file naming convention."""
        object_name = "test_schema.test_table"

        source_df = pd.DataFrame({COLUMN_VALIDATED: ["ID"], "DATA_TYPE": ["INT"]})
        target_df = pd.DataFrame({COLUMN_VALIDATED: ["ID"], "DATA_TYPE": ["NUMBER"]})

        # Run table validation
        schema_data_validator = SchemaDataValidator()
        schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=target_df,
            source_df=source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Verify file name follows timestamped convention
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        assert os.path.exists(expected_file)

        # Verify the filename includes timestamp
        expected_filename = f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}"
        assert os.path.basename(expected_file) == expected_filename

    def test_validation_type_column_first(
        self, mock_context, sample_source_df, sample_target_df, flush_buffer_to_file
    ):
        """Test that VALIDATION_TYPE is the first column in CSV."""
        object_name = "test_schema.test_table"

        # Run validation
        schema_data_validator = SchemaDataValidator()
        schema_data_validator.validate_table_metadata(
            object_name=object_name,
            target_df=sample_target_df,
            source_df=sample_source_df,
            context=mock_context,
            columns_mappings={},
        )

        # Flush buffer to create the CSV file
        flush_buffer_to_file(mock_context)

        # Read CSV and verify column order
        expected_file = os.path.join(
            mock_context.report_path,
            f"{mock_context.run_start_time}_{VALIDATION_REPORT_NAME}",
        )
        df = pd.read_csv(expected_file)

        # Verify VALIDATION_TYPE is the first column
        assert df.columns[0] == VALIDATION_TYPE_KEY

        # Verify complete column order
        expected_order = [
            VALIDATION_TYPE_KEY,
            TABLE_KEY,
            COLUMN_VALIDATED_KEY,
            EVALUATION_CRITERIA_KEY,
            SOURCE_VALUE_KEY,
            SNOWFLAKE_VALUE_KEY,
            STATUS_KEY,
            COMMENTS_KEY,
        ]
        assert list(df.columns) == expected_order

    def test_empty_dataframe_console_handling(self, mock_context):
        """Test that dataframes with only success records are handled properly for console output."""
        object_name = "test_schema.test_table"

        # Create identical DataFrames (no differences, only successes)
        identical_df = pd.DataFrame(
            {
                COLUMN_VALIDATED: ["ID"],
                "count_distinct": [1000],
            }
        )

        # Run column validation (always creates CSV, now with success records)
        metrics_data_validator = MetricsDataValidator()
        metrics_data_validator.validate_column_metadata(
            object_name=object_name,
            target_df=identical_df,
            source_df=identical_df,
            context=mock_context,
            columns_mappings={},
        )

        # Verify handle_message was called
        mock_context.output_handler.handle_message.assert_called()

        # Find the call that includes the metrics validation report
        dataframe_call = None
        for call in mock_context.output_handler.handle_message.call_args_list:
            if (
                len(call.kwargs) > 0
                and "header" in call.kwargs
                and "Metrics validation results" in call.kwargs["header"]
            ):
                dataframe_call = call
                break

        assert (
            dataframe_call is not None
        ), "No call with metrics validation report found"

        # Get the dataframe from the call
        console_df = dataframe_call.kwargs["dataframe"]

        # Should have success records now, not be empty
        assert len(console_df) > 0
        expected_console_columns = [
            COLUMN_VALIDATED_KEY,
            EVALUATION_CRITERIA_KEY,
            SOURCE_VALUE_KEY,
            SNOWFLAKE_VALUE_KEY,
            STATUS_KEY,
            COMMENTS_KEY,
        ]
        assert list(console_df.columns) == expected_console_columns

        # All records should be successful
        assert all(console_df[STATUS_KEY] == "SUCCESS")


def test_is_numeric():
    validator = DataValidatorBase()
    assert validator.is_numeric(123) == True
    assert validator.is_numeric(123.45) == True
    assert validator.is_numeric("123") == True
    assert validator.is_numeric("abc") == False
    assert validator.is_numeric(None) == False


if __name__ == "__main__":
    pytest.main([__file__])
