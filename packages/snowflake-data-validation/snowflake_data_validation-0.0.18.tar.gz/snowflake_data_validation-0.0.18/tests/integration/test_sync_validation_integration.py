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

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, create_autospec
from datetime import datetime

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
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
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


class MockMetadataExtractor(MetadataExtractorBase):
    """Mock metadata extractor for testing purposes."""

    def __init__(
        self, connector: ConnectorBase, platform: Platform, is_source: bool = True
    ):
        self.connector = connector
        self.platform = platform
        self.is_source = is_source
        self.query_generator = MagicMock()
        self.report_path = ""
        self.columns_metrics = {}

    def extract_schema_metadata(
        self,
        table_context: TableConfiguration,
        context: Context,
    ) -> pd.DataFrame:
        """Extract synthetic schema metadata."""
        # Generate slightly different data for source vs target to test validation
        base_data = {
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

        # Introduce slight differences for validation testing
        if not self.is_source:
            # Target has different row count to test validation
            base_data["ROW_COUNT"] = [999] * 6
            # Target has different nullable setting for EMAIL
            base_data["IS_NULLABLE"][3] = "NO"

        return pd.DataFrame(base_data)

    def extract_metrics_metadata(
        self,
        table_context: TableConfiguration,
        context: Context,
    ) -> pd.DataFrame:
        """Extract synthetic metrics metadata."""
        base_data = {
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

        # Introduce slight differences for validation testing
        if not self.is_source:
            # Target has slightly different statistics
            base_data["NULL_COUNT"] = [0, 20, 12, 30, 55, 105]
            base_data["AVG_VALUE"][0] = 499.5  # Slightly different average
            base_data["STD_DEV"][5] = 25100.30  # Slightly different std dev

        return pd.DataFrame(base_data)

    def extract_md5_checksum(
        self, fully_qualified_name: str, context: Context
    ) -> pd.DataFrame:
        """Extract synthetic MD5 checksum."""
        return pd.DataFrame(
            {
                "TABLE_NAME": [fully_qualified_name.split(".")[-1]],
                "MD5_CHECKSUM": ["abc123def456"]
                if self.is_source
                else ["abc123def457"],
            }
        )

    def extract_table_column_metadata(
        self, fully_qualified_name: str, context: Context
    ) -> pd.DataFrame:
        """Extract synthetic table column metadata."""
        return pd.DataFrame(
            {
                "DATABASE_NAME": ["TEST_DB"] * 6,
                "SCHEMA_NAME": ["TEST_SCHEMA"] * 6,
                "TABLE_NAME": ["EMPLOYEES"] * 6,
                "COLUMN_NAME": [
                    "ID",
                    "FIRST_NAME",
                    "LAST_NAME",
                    "EMAIL",
                    "BIRTH_DATE",
                    "SALARY",
                ],
                "NULLABLE": [False, False, False, True, True, True],
                "DATA_TYPE": [
                    "INTEGER",
                    "VARCHAR",
                    "VARCHAR",
                    "VARCHAR",
                    "DATE",
                    "DECIMAL",
                ],
                "IS_PRIMARY_KEY": [True, False, False, False, False, False],
                "CHARACTER_LENGTH": [None, 50, 50, 100, None, None],
                "PRECISION": [10, None, None, None, 10, 10],
                "SCALE": [0, None, None, None, 0, 2],
                "CALCULATED_COLUMN_SIZE_IN_BYTES": [4, 200, 200, 400, 3, 9],
            }
        )


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


class TestSyncValidationIntegration:
    """Integration tests for run_sync_validation functionality."""

    def test_run_sync_validation_with_mocked_connectors_success(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test successful sync validation with mocked connectors and synthetic data."""
        # Create mock connectors with synthetic data
        source_connector = MockConnector()
        target_connector = MockConnector()

        # Create mock extractors
        source_extractor = MockMetadataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = MockMetadataExtractor(
            target_connector, Platform.SNOWFLAKE, is_source=False
        )

        # Mock the tables configuration
        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        # Create orchestrator
        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        # Mock the metadata extractor creation
        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            # Execute the sync validation
            orchestrator.run_sync_comparison()

        # Verify that messages were generated
        output_handler = mock_context.output_handler
        assert len(output_handler.messages) > 0

        # Check that schema validation messages are present
        schema_messages = [
            msg
            for msg in output_handler.messages
            if "schema" in msg.get("message", "").lower()
            or "schema" in msg.get("header", "").lower()
        ]
        assert len(schema_messages) > 0

        # Check that metrics validation messages are present
        metrics_messages = [
            msg
            for msg in output_handler.messages
            if "metrics" in msg.get("message", "").lower()
            or "metrics" in msg.get("header", "").lower()
        ]
        assert len(metrics_messages) > 0

    def test_run_sync_validation_with_matching_data(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test sync validation with perfectly matching source and target data."""
        # Create identical extractors for both source and target
        source_connector = MockConnector()
        target_connector = MockConnector()

        source_extractor = MockMetadataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = MockMetadataExtractor(
            target_connector,
            Platform.SNOWFLAKE,
            is_source=True,  # Same as source for perfect match
        )

        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            orchestrator.run_sync_comparison()

        # Verify validation completed without critical errors
        output_handler = mock_context.output_handler
        error_messages = [
            msg
            for msg in output_handler.messages
            if msg.get("level") == OutputMessageLevel.FAILURE
        ]

        # There should be fewer error messages with matching data
        assert len(error_messages) <= len(output_handler.messages) / 2

    def test_run_sync_validation_with_schema_differences(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test sync validation detecting schema differences."""
        source_connector = MockConnector()
        target_connector = MockConnector()

        # Create extractors with different schema data
        source_extractor = MockMetadataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = MockMetadataExtractor(
            target_connector, Platform.SNOWFLAKE, is_source=False
        )

        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            orchestrator.run_sync_comparison()

        # Verify validation detected differences
        output_handler = mock_context.output_handler
        validation_messages = [
            msg
            for msg in output_handler.messages
            if "validation" in msg.get("header", "").lower()
        ]
        assert len(validation_messages) > 0

    def test_run_sync_validation_with_metrics_differences(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test sync validation detecting metrics differences."""
        source_connector = MockConnector()
        target_connector = MockConnector()

        source_extractor = MockMetadataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = MockMetadataExtractor(
            target_connector, Platform.SNOWFLAKE, is_source=False
        )

        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            orchestrator.run_sync_comparison()

        # Verify metrics validation was executed
        output_handler = mock_context.output_handler
        metrics_messages = [
            msg
            for msg in output_handler.messages
            if "metrics" in msg.get("message", "").lower()
            or "metrics" in msg.get("header", "").lower()
        ]
        assert len(metrics_messages) > 0

    def test_run_sync_validation_with_query_execution_errors(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test sync validation handling query execution errors gracefully."""
        # Create a connector that raises exceptions
        class ErrorConnector(MockConnector):
            def execute_query(self, query: str) -> list[tuple]:
                raise Exception("Database connection error")

        source_connector = ErrorConnector()
        target_connector = MockConnector()

        source_extractor = MockMetadataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = MockMetadataExtractor(
            target_connector, Platform.SNOWFLAKE, is_source=False
        )

        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            # Should handle errors gracefully without crashing
            orchestrator.run_sync_comparison()

        # Verify error handling
        output_handler = mock_context.output_handler
        error_messages = [
            msg
            for msg in output_handler.messages
            if msg.get("level") == OutputMessageLevel.FAILURE
        ]
        assert len(error_messages) > 0

    def test_run_sync_validation_with_empty_datasets(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test sync validation with empty datasets."""

        class EmptyDataConnector(MockConnector):
            def execute_query(self, query: str) -> list[tuple]:
                return []

        source_connector = EmptyDataConnector()
        target_connector = EmptyDataConnector()

        class EmptyDataExtractor(MockMetadataExtractor):
            def extract_schema_metadata(self, table_context, context):
                return pd.DataFrame()

            def extract_metrics_metadata(self, table_context, context):
                return pd.DataFrame()

        source_extractor = EmptyDataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = EmptyDataExtractor(
            target_connector, Platform.SNOWFLAKE, is_source=False
        )

        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            orchestrator.run_sync_comparison()

        # Verify that validation handles empty datasets
        output_handler = mock_context.output_handler
        assert len(output_handler.messages) > 0

    def test_run_sync_validation_with_multiple_tables(
        self, mock_validation_config, mock_context
    ):
        """Test sync validation with multiple tables."""
        # Create multiple table configurations
        table_contexts = []
        for i, table_name in enumerate(["EMPLOYEES", "DEPARTMENTS", "PROJECTS"]):
            mock_config = MagicMock(spec=TableConfiguration)
            mock_config.fully_qualified_name = f"TEST_DB.TEST_SCHEMA.{table_name}"
            mock_config.column_selection_list = [f"ID", f"NAME", f"DESCRIPTION"]
            mock_config.where_clause = ""
            mock_config.target_where_clause = ""
            mock_config.has_where_clause = False
            mock_config.use_column_selection_as_exclude_list = False
            mock_config.validation_configuration = None
            table_contexts.append(mock_config)

        source_connector = MockConnector()
        target_connector = MockConnector()

        source_extractor = MockMetadataExtractor(
            source_connector, Platform.SQLSERVER, is_source=True
        )
        target_extractor = MockMetadataExtractor(
            target_connector, Platform.SNOWFLAKE, is_source=False
        )

        mock_context.configuration.tables = table_contexts
        mock_context.configuration.validation = mock_validation_config

        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        with patch.object(
            orchestrator,
            "_create_metadata_extractor",
            side_effect=[source_extractor, target_extractor],
        ):
            orchestrator.run_sync_comparison()

        # Verify that all tables were processed
        output_handler = mock_context.output_handler
        table_messages = [
            msg
            for msg in output_handler.messages
            if any(
                table in msg.get("message", "")
                for table in ["EMPLOYEES", "DEPARTMENTS", "PROJECTS"]
            )
        ]
        # Should have messages for multiple tables
        assert len(table_messages) > len(table_contexts)
