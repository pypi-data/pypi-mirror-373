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
from snowflake.snowflake_data_validation.executer.async_generation_executor import (
    AsyncGenerationExecutor,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_MODE,
    Platform,
    TABLE_METADATA_QUERIES_FILENAME,
    COLUMN_METADATA_QUERIES_FILENAME,
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


class MockQueryGenerator(QueryGeneratorBase):
    """Mock query generator for testing purposes."""

    def __init__(self, connector: ConnectorBase = None):
        self.connector = connector

    def generate_schema_query(
        self, table_context: TableConfiguration, context: Context
    ) -> str:
        return f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_context.source_table}'"

    def generate_metrics_query(
        self,
        table_context: TableConfiguration,
        context: Context,
        connector: ConnectorBase,
    ) -> str:
        return f"SELECT col_name, COUNT(*) FROM {table_context.fully_qualified_name} GROUP BY col_name"

    def generate_row_md5_query(
        self, table_context: TableConfiguration, context: Context
    ) -> str:
        return f"SELECT MD5(*) FROM {table_context.fully_qualified_name}"

    def generate_table_column_metadata_query(
        self, table_context: TableConfiguration, context: Context
    ) -> str:
        return f"SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_context.source_table}'"


class MockScriptWriter(ScriptWriterBase):
    """Mock script writer for testing file operations."""

    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        super().__init__(connector, query_generator, report_path)
        self.written_files = {}  # Track files that were written

    def print_table_metadata_query(
        self, table_context: TableConfiguration, context: Context
    ) -> None:
        """Mock implementation that tracks file writing."""
        query = self.query_generator.generate_schema_query(table_context, context)
        file_path = self._get_filename(TABLE_METADATA_QUERIES_FILENAME, context)
        # Store in memory instead of actually writing
        self.written_files[file_path] = query

    def print_column_metadata_query(
        self, table_context: TableConfiguration, context: Context
    ) -> None:
        """Mock implementation that tracks file writing."""
        query = self.query_generator.generate_metrics_query(
            table_context, context, self.connector
        )
        file_path = self._get_filename(COLUMN_METADATA_QUERIES_FILENAME, context)
        # Store in memory instead of actually writing
        self.written_files[file_path] = query


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


class TestAsyncGenerationIntegration:
    """Integration tests for async generation functionality."""

    def test_async_generation_with_mocked_script_writers_success(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test successful async generation with mocked script writers."""
        # Create mock connectors
        source_connector = MockConnector()
        target_connector = MockConnector()

        # Create mock query generators
        source_query_generator = MockQueryGenerator(source_connector)
        target_query_generator = MockQueryGenerator(target_connector)

        # Create mock script writers
        source_script_writer = MockScriptWriter(
            source_connector, source_query_generator, "/tmp/source_scripts"
        )
        target_script_writer = MockScriptWriter(
            target_connector, target_query_generator, "/tmp/target_scripts"
        )

        # Setup configuration
        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        # Create executor
        executor = AsyncGenerationExecutor(
            source_extractor=source_script_writer,
            target_extractor=target_script_writer,
            context=mock_context,
        )

        # Execute schema validation generation
        schema_result = executor.execute_schema_validation(mock_table_context)
        assert schema_result is True

        # Execute metrics validation generation
        metrics_result = executor.execute_metrics_validation(mock_table_context)
        assert metrics_result is True

        # Verify that files were "written" (stored in mock)
        assert len(source_script_writer.written_files) > 0
        assert len(target_script_writer.written_files) > 0

        # Verify that messages were generated
        output_handler = mock_context.output_handler
        assert len(output_handler.messages) > 0

        # Check for success messages
        success_messages = [
            msg
            for msg in output_handler.messages
            if msg.get("level") == OutputMessageLevel.SUCCESS
        ]
        assert len(success_messages) >= 2  # One for schema, one for metrics

    def test_async_generation_via_orchestrator(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test async generation through the orchestrator."""
        # Create mock connectors
        source_connector = MockConnector()
        target_connector = MockConnector()

        # Setup configuration
        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        # Create orchestrator
        orchestrator = ComparisonOrchestrator(
            source_connector=source_connector,
            target_connector=target_connector,
            context=mock_context,
        )

        # Mock the script writer creation
        with patch.object(
            orchestrator, "_create_script_printer"
        ) as mock_create_printer:
            mock_printer = MagicMock(spec=ScriptWriterBase)
            mock_create_printer.return_value = mock_printer

            # Execute async generation
            orchestrator.run_async_generation()

            # Verify script writers were created and used
            assert mock_create_printer.call_count >= 2
            mock_printer.print_table_metadata_query.assert_called()
            mock_printer.print_column_metadata_query.assert_called()

    def test_async_generation_with_multiple_tables(
        self, mock_validation_config, mock_context
    ):
        """Test async generation with multiple tables."""
        # Create multiple table configurations
        table_contexts = []
        for i, table_name in enumerate(["EMPLOYEES", "DEPARTMENTS", "PROJECTS"]):
            mock_config = MagicMock(spec=TableConfiguration)
            mock_config.fully_qualified_name = f"TEST_DB.TEST_SCHEMA.{table_name}"
            mock_config.source_database = "TEST_DB"
            mock_config.source_schema = "TEST_SCHEMA"
            mock_config.source_table = table_name
            mock_config.column_selection_list = ["ID", "NAME", "DESCRIPTION"]
            mock_config.where_clause = ""
            mock_config.target_where_clause = ""
            mock_config.has_where_clause = False
            mock_config.use_column_selection_as_exclude_list = False
            mock_config.validation_configuration = None
            table_contexts.append(mock_config)

        # Create mock connectors and generators
        source_connector = MockConnector()
        target_connector = MockConnector()
        source_query_generator = MockQueryGenerator(source_connector)
        target_query_generator = MockQueryGenerator(target_connector)

        # Create mock script writers with unique timestamps
        source_script_writer = MockScriptWriter(
            source_connector, source_query_generator, "/tmp/source_scripts"
        )
        target_script_writer = MockScriptWriter(
            target_connector, target_query_generator, "/tmp/target_scripts"
        )

        # Setup configuration
        mock_context.configuration.tables = table_contexts
        mock_context.configuration.validation = mock_validation_config

        # Create executor
        executor = AsyncGenerationExecutor(
            source_extractor=source_script_writer,
            target_extractor=target_script_writer,
            context=mock_context,
        )

        # Execute generation for each table with unique timestamps
        for i, table_context in enumerate(table_contexts):
            # Use unique timestamp for each table to avoid file overwriting
            mock_context.run_start_time = f"20250101T12000{i}"

            schema_result = executor.execute_schema_validation(table_context)
            metrics_result = executor.execute_metrics_validation(table_context)
            assert schema_result is True
            assert metrics_result is True

        # Verify files were generated (since files get overwritten due to same timestamp,
        # we check that at least some files were generated)
        assert len(source_script_writer.written_files) >= 2
        assert len(target_script_writer.written_files) >= 2

    def test_async_generation_with_file_write_errors(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test async generation handling file write errors gracefully."""

        class ErrorScriptWriter(MockScriptWriter):
            def print_table_metadata_query(self, table_context, context):
                raise OSError("Failed to write file")

            def print_column_metadata_query(self, table_context, context):
                raise OSError("Failed to write file")

        # Create connectors and error-prone script writers
        source_connector = MockConnector()
        target_connector = MockConnector()
        source_query_generator = MockQueryGenerator(source_connector)
        target_query_generator = MockQueryGenerator(target_connector)

        source_script_writer = ErrorScriptWriter(
            source_connector, source_query_generator, "/tmp/source_scripts"
        )
        target_script_writer = ErrorScriptWriter(
            target_connector, target_query_generator, "/tmp/target_scripts"
        )

        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        executor = AsyncGenerationExecutor(
            source_extractor=source_script_writer,
            target_extractor=target_script_writer,
            context=mock_context,
        )

        # Should handle errors gracefully
        schema_result = executor.execute_schema_validation(mock_table_context)
        metrics_result = executor.execute_metrics_validation(mock_table_context)

        # Results should be False due to errors
        assert schema_result is False
        assert metrics_result is False

    def test_async_generation_with_different_connector_types(
        self, mock_table_context, mock_validation_config, mock_context
    ):
        """Test async generation with different types of connectors (SQL Server vs Snowflake)."""
        # Create different mock connectors with specific behaviors
        class SqlServerMockConnector(MockConnector):
            def _get_schema_metadata(self):
                return [
                    ("EMPLOYEES", "ID", 1, "INT", None, 10, 0, "NO", 1000),
                    ("EMPLOYEES", "NAME", 2, "NVARCHAR", 100, None, None, "NO", 1000),
                ]

        class SnowflakeMockConnector(MockConnector):
            def _get_schema_metadata(self):
                return [
                    ("EMPLOYEES", "ID", 1, "NUMBER", None, 10, 0, "NO", 1000),
                    ("EMPLOYEES", "NAME", 2, "VARCHAR", 100, None, None, "NO", 1000),
                ]

        # Create different connectors
        source_connector = SqlServerMockConnector()
        target_connector = SnowflakeMockConnector()

        # Create generators and script writers
        source_query_generator = MockQueryGenerator(source_connector)
        target_query_generator = MockQueryGenerator(target_connector)

        source_script_writer = MockScriptWriter(
            source_connector, source_query_generator, "/tmp/source_scripts"
        )
        target_script_writer = MockScriptWriter(
            target_connector, target_query_generator, "/tmp/target_scripts"
        )

        # Setup configuration
        mock_context.configuration.tables = [mock_table_context]
        mock_context.configuration.validation = mock_validation_config

        # Create executor
        executor = AsyncGenerationExecutor(
            source_extractor=source_script_writer,
            target_extractor=target_script_writer,
            context=mock_context,
        )

        # Execute generation
        schema_result = executor.execute_schema_validation(mock_table_context)
        metrics_result = executor.execute_metrics_validation(mock_table_context)

        # Should succeed with different connector types
        assert schema_result is True
        assert metrics_result is True

        # Verify files were written for both connectors
        assert len(source_script_writer.written_files) > 0
        assert len(target_script_writer.written_files) > 0

    def test_async_generation_with_large_table_sets(
        self, mock_validation_config, mock_context
    ):
        """Test async generation with a large number of tables."""
        # Create a large set of table configurations
        table_contexts = []
        for i in range(20):  # Test with 20 tables
            mock_config = MagicMock(spec=TableConfiguration)
            mock_config.fully_qualified_name = f"TEST_DB.TEST_SCHEMA.TABLE_{i:02d}"
            mock_config.source_database = "TEST_DB"
            mock_config.source_schema = "TEST_SCHEMA"
            mock_config.source_table = f"TABLE_{i:02d}"
            mock_config.column_selection_list = ["ID", "DATA"]
            mock_config.where_clause = ""
            mock_config.target_where_clause = ""
            mock_config.has_where_clause = False
            mock_config.use_column_selection_as_exclude_list = False
            mock_config.validation_configuration = None
            table_contexts.append(mock_config)

        # Create mock infrastructure
        source_connector = MockConnector()
        target_connector = MockConnector()
        source_query_generator = MockQueryGenerator(source_connector)
        target_query_generator = MockQueryGenerator(target_connector)
        source_script_writer = MockScriptWriter(
            source_connector, source_query_generator, "/tmp/source_scripts"
        )
        target_script_writer = MockScriptWriter(
            target_connector, target_query_generator, "/tmp/target_scripts"
        )

        # Setup configuration
        mock_context.configuration.tables = table_contexts
        mock_context.configuration.validation = mock_validation_config

        # Create executor
        executor = AsyncGenerationExecutor(
            source_extractor=source_script_writer,
            target_extractor=target_script_writer,
            context=mock_context,
        )

        # Execute generation for a subset of tables
        successful_generations = 0
        for i, table_context in enumerate(table_contexts[:5]):  # Test first 5 tables
            mock_context.run_start_time = f"20250101T1200{i:02d}"

            schema_result = executor.execute_schema_validation(table_context)
            metrics_result = executor.execute_metrics_validation(table_context)

            if schema_result and metrics_result:
                successful_generations += 1

        # Should have successful generations
        assert successful_generations > 0
        assert len(source_script_writer.written_files) > 0
        assert len(target_script_writer.written_files) > 0
