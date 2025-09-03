# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import tempfile
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.executer.async_validation_executor import (
    AsyncValidationExecutor,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_MODE,
    COLUMN_VALIDATED,
    Platform,
    SCHEMA_VALIDATION_KEY,
    METRICS_VALIDATION_KEY,
)


class MockConnector(ConnectorBase):
    """Mock connector for testing purposes."""

    def __init__(self, synthetic_data=None):
        self.synthetic_data = synthetic_data or {}
        super().__init__()

    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        pass

    def execute_query(self, query: str) -> list[tuple]:
        # Return synthetic data based on query type
        if "INFORMATION_SCHEMA.COLUMNS" in query.upper():
            return self._get_schema_metadata()
        elif "COUNT(*)" in query.upper() and "SELECT" in query.upper():
            return self._get_metrics_metadata()
        return []

    def execute_statement(self, statement: str) -> None:
        pass

    def execute_query_no_return(self, query: str) -> None:
        pass

    def close(self) -> None:
        pass

    def _get_schema_metadata(self):
        """Generate synthetic schema metadata."""
        return [
            ("EMPLOYEES", "ID", 1, "INTEGER", None, 10, 0, "NO", 1000),
            ("EMPLOYEES", "FIRST_NAME", 2, "VARCHAR", 50, None, None, "NO", 1000),
            ("EMPLOYEES", "LAST_NAME", 3, "VARCHAR", 50, None, None, "NO", 1000),
            ("EMPLOYEES", "EMAIL", 4, "VARCHAR", 100, None, None, "YES", 1000),
            ("EMPLOYEES", "BIRTH_DATE", 5, "DATE", None, 10, 0, "YES", 1000),
            ("EMPLOYEES", "SALARY", 6, "DECIMAL", None, 10, 2, "YES", 1000),
        ]

    def _get_metrics_metadata(self):
        """Generate synthetic metrics metadata."""
        return [
            ("ID", 1000, 0, 1, 1000, 500.5, 288.675),
            ("FIRST_NAME", 50, 985, 0, 15, None, None),
            ("LAST_NAME", 50, 892, 0, 108, None, None),
            ("EMAIL", 100, 975, 25, 0, None, None),
            ("BIRTH_DATE", 10, 950, 50, 0, None, None),
            ("SALARY", 10, 900, 100, 0, 75000.50, 25000.25),
        ]


class MockOutputHandler(OutputHandlerBase):
    """Mock output handler for testing purposes."""

    def __init__(self):
        self.messages = []
        self.dataframes = []
        super().__init__(enable_console_output=False)

    def handle_message(
        self,
        level: OutputMessageLevel,
        message: str = "",
        header: str = "",
        dataframe: pd.DataFrame = None,
    ) -> None:
        """Store messages for verification in tests."""
        self.messages.append(
            {
                "message": message,
                "header": header,
                "level": level,
                "dataframe": dataframe,
            }
        )
        if dataframe is not None:
            self.dataframes.append(dataframe)


@pytest.fixture
def mock_table_context():
    """Create a mock table configuration for testing."""
    mock_config = MagicMock(spec=TableConfiguration)
    mock_config.fully_qualified_name = "TEST_DB.TEST_SCHEMA.EMPLOYEES"
    mock_config.source_database = "TEST_DB"
    mock_config.source_schema = "TEST_SCHEMA"
    mock_config.source_table = "EMPLOYEES"
    mock_config.column_selection_list = [
        "ID",
        "FIRST_NAME",
        "LAST_NAME",
        "EMAIL",
        "BIRTH_DATE",
        "SALARY",
    ]
    mock_config.where_clause = ""
    mock_config.target_where_clause = ""
    mock_config.has_where_clause = False
    mock_config.use_column_selection_as_exclude_list = False
    mock_config.validation_configuration = None
    mock_config.source_validation_file_name = None
    mock_config.target_validation_file_name = None
    return mock_config


@pytest.fixture
def mock_validation_config():
    """Create a mock validation configuration for testing."""
    mock_config = MagicMock(spec=ValidationConfiguration)
    mock_config.schema_validation = True
    mock_config.metrics_validation = True
    mock_config.row_validation = True
    mock_config.model_dump.return_value = {
        "schema_validation": True,
        "metrics_validation": True,
        "row_validation": True,
    }
    return mock_config


@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    context = MagicMock(spec=Context)
    context.output_handler = MockOutputHandler()
    context.source_platform = Platform.SQLSERVER
    context.target_platform = Platform.SNOWFLAKE
    context.configuration = MagicMock()
    context.configuration.tables = []
    context.configuration.target_platform = Platform.SNOWFLAKE
    context.configuration.source_validation_files_path = "/tmp/source"
    context.configuration.target_validation_files_path = "/tmp/target"
    context.report_path = "/tmp/test_reports"
    context.datatypes_mappings = {
        "INTEGER": "NUMBER",
        "VARCHAR": "VARCHAR",
        "DATE": "DATE",
        "DECIMAL": "NUMBER",
    }
    # Add missing required attributes for Context
    context.run_id = "test_run_12345"
    context.run_start_time = "20250101T120000"
    context.templates_path = "/tmp/templates"
    context.sql_generator = MagicMock()

    return context


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestAsyncValidationIntegration:
    """Integration tests for async validation functionality."""

    def create_test_csv_files(
        self, temp_dir, table_name="TEST_DB.TEST_SCHEMA.EMPLOYEES"
    ):
        """Create test CSV files for validation."""
        schema_dir = os.path.join(temp_dir, "schema_validation")
        metrics_dir = os.path.join(temp_dir, "metrics_validation")
        os.makedirs(schema_dir, exist_ok=True)
        os.makedirs(metrics_dir, exist_ok=True)

        # Create schema validation CSV files
        source_schema_data = {
            COLUMN_VALIDATED: [
                "ID",
                "FIRST_NAME",
                "LAST_NAME",
                "EMAIL",
                "BIRTH_DATE",
                "SALARY",
            ],
            "ORDINAL_POSITION": [1, 2, 3, 4, 5, 6],
            "DATA_TYPE": [
                "INTEGER",
                "VARCHAR",
                "VARCHAR",
                "VARCHAR",
                "DATE",
                "DECIMAL",
            ],
            "CHARACTER_MAXIMUM_LENGTH": [None, 50, 50, 100, None, None],
            "NUMERIC_PRECISION": [10, None, None, None, 10, 10],
            "NUMERIC_SCALE": [0, None, None, None, 0, 2],
            "IS_NULLABLE": ["NO", "NO", "NO", "YES", "YES", "YES"],
            "ROW_COUNT": [1000] * 6,
        }

        target_schema_data = source_schema_data.copy()
        target_schema_data["ROW_COUNT"] = [999] * 6  # Slight difference

        source_schema_df = pd.DataFrame(source_schema_data)
        target_schema_df = pd.DataFrame(target_schema_data)

        source_schema_path = os.path.join(schema_dir, f"{table_name}.csv")
        target_schema_path = os.path.join(schema_dir, f"{table_name}.csv")

        source_schema_df.to_csv(source_schema_path, index=False)
        target_schema_df.to_csv(target_schema_path, index=False)

        # Create metrics validation CSV files
        source_metrics_data = {
            COLUMN_VALIDATED: [
                "ID",
                "FIRST_NAME",
                "LAST_NAME",
                "EMAIL",
                "BIRTH_DATE",
                "SALARY",
            ],
            "MAX_LENGTH": [10, 50, 50, 100, 10, 10],
            "NULL_COUNT": [0, 15, 8, 25, 50, 100],
            "MIN_VALUE": [1, None, None, None, None, 30000.00],
            "MAX_VALUE": [1000, None, None, None, None, 150000.00],
            "AVG_VALUE": [500.5, None, None, None, None, 75000.50],
            "STD_DEV": [288.675, None, None, None, None, 25000.25],
        }

        target_metrics_data = source_metrics_data.copy()
        target_metrics_data["NULL_COUNT"] = [
            0,
            20,
            12,
            30,
            55,
            105,
        ]  # Slight difference

        source_metrics_df = pd.DataFrame(source_metrics_data)
        target_metrics_df = pd.DataFrame(target_metrics_data)

        source_metrics_path = os.path.join(metrics_dir, f"{table_name}.csv")
        target_metrics_path = os.path.join(metrics_dir, f"{table_name}.csv")

        source_metrics_df.to_csv(source_metrics_path, index=False)
        target_metrics_df.to_csv(target_metrics_path, index=False)

        return {
            "source_schema": source_schema_path,
            "target_schema": target_schema_path,
            "source_metrics": source_metrics_path,
            "target_metrics": target_metrics_path,
        }

    def test_async_validation_with_csv_files_success(
        self, mock_table_context, mock_validation_config, mock_context, temp_dir
    ):
        """Test successful async validation with CSV files."""
        # Create test CSV files
        csv_files = self.create_test_csv_files(temp_dir)

        # Update context with proper file paths
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create mock extractors (not used in async validation, but required by executor)
        mock_source_extractor = MagicMock()
        mock_target_extractor = MagicMock()

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=mock_source_extractor,
            target_extractor=mock_target_extractor,
            context=mock_context,
        )

        # Mock the file loading to use our test files
        with patch.object(executor, "_load_validation_files") as mock_load:
            # Load actual test data for schema validation
            source_df = pd.read_csv(csv_files["source_schema"])
            target_df = pd.read_csv(csv_files["target_schema"])
            mock_load.return_value = [source_df, target_df]

            # Execute schema validation
            schema_result = executor.execute_schema_validation(mock_table_context)

            # Verify validation was attempted
            mock_load.assert_called_with(
                validation_type=SCHEMA_VALIDATION_KEY, table_context=mock_table_context
            )

        # Check output messages
        output_handler = mock_context.output_handler
        assert len(output_handler.messages) > 0

        # Look for validation messages
        validation_messages = [
            msg
            for msg in output_handler.messages
            if "validation" in msg.get("header", "").lower()
        ]
        assert len(validation_messages) > 0

    def test_async_validation_with_identical_data(
        self, mock_table_context, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation with identical source and target data."""
        # Create identical data for both source and target
        schema_dir = os.path.join(temp_dir, "schema_validation")
        os.makedirs(schema_dir, exist_ok=True)

        schema_data = {
            COLUMN_VALIDATED: ["ID", "NAME", "EMAIL"],
            "ORDINAL_POSITION": [1, 2, 3],
            "DATA_TYPE": ["INTEGER", "VARCHAR", "VARCHAR"],
            "IS_NULLABLE": ["NO", "NO", "YES"],
            "ROW_COUNT": [1000] * 3,
        }

        df = pd.DataFrame(schema_data)
        source_path = os.path.join(schema_dir, "TEST_DB.TEST_SCHEMA.EMPLOYEES.csv")
        target_path = os.path.join(schema_dir, "TEST_DB.TEST_SCHEMA.EMPLOYEES.csv")

        df.to_csv(source_path, index=False)
        df.to_csv(target_path, index=False)

        # Update context
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=mock_context,
        )

        # Mock file loading with identical data
        with patch.object(executor, "_load_validation_files") as mock_load:
            mock_load.return_value = [df, df]  # Identical data

            # Execute validation
            result = executor.execute_schema_validation(mock_table_context)

            # Should pass with identical data
            assert result is True

    def test_async_validation_with_missing_files(
        self, mock_table_context, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation handling missing CSV files."""
        # Update context with paths to non-existent files
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=mock_context,
        )

        # Mock the file loading to return empty DataFrames
        with patch.object(executor, "_load_validation_files") as mock_load:
            mock_load.return_value = [pd.DataFrame(), pd.DataFrame()]

            # Execute validation (should handle missing files gracefully)
            schema_result = executor.execute_schema_validation(mock_table_context)
            metrics_result = executor.execute_metrics_validation(mock_table_context)

            # Should return False due to missing files
            assert schema_result is False
            assert metrics_result is False

    def test_async_validation_via_orchestrator(
        self, mock_table_context, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation through the orchestrator."""
        # Create test CSV files
        csv_files = self.create_test_csv_files(temp_dir)

        # Create mock connectors
        source_connector = MockConnector()
        target_connector = MockConnector()

        # Update context
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir
        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        # Create orchestrator
        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        # Mock the metadata extractor creation and async validation
        with patch.object(
            orchestrator, "_create_metadata_extractor"
        ) as mock_create_extractor:
            mock_extractor = MagicMock()
            mock_create_extractor.return_value = mock_extractor

            # Mock the executor creation to use our test data
            with patch.object(
                orchestrator.executor_factory, "create_executor"
            ) as mock_create_executor:
                mock_executor = MagicMock()
                mock_create_executor.return_value = mock_executor

                # Execute async validation
                orchestrator.run_async_comparison()

                # Verify extractors were created
                assert mock_create_extractor.call_count >= 2

    def test_async_validation_with_corrupted_csv_files(
        self, mock_table_context, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation handling corrupted CSV files."""
        # Create directory structure
        schema_dir = os.path.join(temp_dir, "schema_validation")
        os.makedirs(schema_dir, exist_ok=True)

        # Create corrupted CSV file
        corrupted_csv_path = os.path.join(
            schema_dir, "TEST_DB.TEST_SCHEMA.EMPLOYEES.csv"
        )
        with open(corrupted_csv_path, "w") as f:
            f.write("corrupted,csv,data\ninvalid,format")

        # Update context
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=mock_context,
        )

        # Mock the file loading to simulate corrupted file handling
        with patch.object(executor, "_load_validation_files") as mock_load:
            mock_load.return_value = [pd.DataFrame(), pd.DataFrame()]

            # Execute validation (should handle corrupted files gracefully)
            result = executor.execute_schema_validation(mock_table_context)

            # Should return False due to corrupted data
            assert result is False

    def test_async_validation_with_custom_file_names(
        self, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation with custom validation file names."""
        # Create table context with custom file names
        mock_table_context = MagicMock(spec=TableConfiguration)
        mock_table_context.fully_qualified_name = "TEST_DB.TEST_SCHEMA.EMPLOYEES"
        mock_table_context.source_validation_file_name = "custom_source_schema.csv"
        mock_table_context.target_validation_file_name = "custom_target_schema.csv"
        mock_table_context.column_selection_list = ["ID", "NAME"]

        # Create custom CSV files
        schema_dir = os.path.join(temp_dir, "schema_validation")
        os.makedirs(schema_dir, exist_ok=True)

        schema_data = {
            COLUMN_VALIDATED: ["ID", "NAME"],
            "DATA_TYPE": ["INTEGER", "VARCHAR"],
            "IS_NULLABLE": ["NO", "NO"],
        }

        df = pd.DataFrame(schema_data)
        source_path = os.path.join(schema_dir, "custom_source_schema.csv")
        target_path = os.path.join(schema_dir, "custom_target_schema.csv")

        df.to_csv(source_path, index=False)
        df.to_csv(target_path, index=False)

        # Update context
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=mock_context,
        )

        # Mock file loading
        with patch.object(executor, "_load_validation_files") as mock_load:
            mock_load.return_value = [df, df]

            # Execute validation
            result = executor.execute_schema_validation(mock_table_context)

            # Should pass
            assert result is True

    def test_async_validation_with_metrics_validation(
        self, mock_table_context, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation specifically for metrics validation."""
        # Create test CSV files
        csv_files = self.create_test_csv_files(temp_dir)

        # Update context with proper file paths
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=mock_context,
        )

        # Mock the file loading to use our test files for metrics validation
        with patch.object(executor, "_load_validation_files") as mock_load:
            # Load actual test data for metrics validation
            source_df = pd.read_csv(csv_files["source_metrics"])
            target_df = pd.read_csv(csv_files["target_metrics"])
            mock_load.return_value = [source_df, target_df]

            # Execute metrics validation
            metrics_result = executor.execute_metrics_validation(mock_table_context)

            # Verify validation was attempted
            mock_load.assert_called_with(
                validation_type=METRICS_VALIDATION_KEY, table_context=mock_table_context
            )

        # Check output messages
        output_handler = mock_context.output_handler
        assert len(output_handler.messages) > 0

    def test_async_validation_with_multiple_table_files(
        self, mock_validation_config, mock_context, temp_dir
    ):
        """Test async validation with multiple table CSV files."""
        # Create multiple table contexts
        table_names = ["EMPLOYEES", "DEPARTMENTS", "CUSTOMERS"]
        table_contexts = []

        for table_name in table_names:
            mock_config = MagicMock(spec=TableConfiguration)
            mock_config.fully_qualified_name = f"TEST_DB.TEST_SCHEMA.{table_name}"
            mock_config.source_table = table_name
            mock_config.column_selection_list = ["ID", "NAME"]
            mock_config.source_validation_file_name = None
            mock_config.target_validation_file_name = None
            table_contexts.append(mock_config)

        # Create CSV files for each table
        schema_dir = os.path.join(temp_dir, "schema_validation")
        os.makedirs(schema_dir, exist_ok=True)

        for table_name in table_names:
            schema_data = {
                COLUMN_VALIDATED: ["ID", "NAME"],
                "DATA_TYPE": ["INTEGER", "VARCHAR"],
                "IS_NULLABLE": ["NO", "NO"],
            }

            df = pd.DataFrame(schema_data)
            csv_path = os.path.join(schema_dir, f"TEST_DB.TEST_SCHEMA.{table_name}.csv")
            df.to_csv(csv_path, index=False)

        # Update context
        mock_context.configuration.source_validation_files_path = temp_dir
        mock_context.configuration.target_validation_files_path = temp_dir

        # Create executor
        executor = AsyncValidationExecutor(
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=mock_context,
        )

        # Test validation for each table
        successful_validations = 0
        for table_context in table_contexts:
            with patch.object(executor, "_load_validation_files") as mock_load:
                # Use the same data for source and target for simplicity
                test_df = pd.DataFrame(
                    {
                        COLUMN_VALIDATED: ["ID", "NAME"],
                        "DATA_TYPE": ["INTEGER", "VARCHAR"],
                        "IS_NULLABLE": ["NO", "NO"],
                    }
                )
                mock_load.return_value = [test_df, test_df]

                result = executor.execute_schema_validation(table_context)
                if result:
                    successful_validations += 1

        # Should have processed all tables
        assert successful_validations == len(table_contexts)
