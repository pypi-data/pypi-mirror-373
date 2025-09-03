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

"""Unit tests for MetadataExtractorTeradata class."""

import unittest
from unittest.mock import Mock, patch

import pandas as pd

from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.teradata.extractor.metadata_extractor_teradata import (
    MetadataExtractorTeradata,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import COLUMN_VALIDATED
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class TestMetadataExtractorTeradata(unittest.TestCase):
    """Test cases for MetadataExtractorTeradata."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects
        self.mock_connector = Mock(spec=ConnectorBase)
        self.mock_query_generator = Mock(spec=QueryGeneratorBase)

        # Create a mock DataFrame for test results
        self.mock_df = pd.DataFrame(
            {
                "COLUMN_NAME": ["COL1", "COL2"],
                "DATA_TYPE": ["INTEGER", "VARCHAR"],
                "IS_NULLABLE": ["Y", "N"],
            }
        )

        # Create the extractor instance with mocked HelperDataFrame
        with patch(
            "snowflake.snowflake_data_validation.teradata.extractor.metadata_extractor_teradata.HelperDataFrame"
        ) as mock_helper_df_class:
            # Configure the mock to return our DataFrame
            mock_helper_df_instance = Mock()
            mock_helper_df_instance.process_query_result_to_dataframe.return_value = (
                self.mock_df
            )
            mock_helper_df_class.return_value = mock_helper_df_instance

            self.extractor = MetadataExtractorTeradata(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path="",
            )

    def _create_mock_table_context(self, fully_qualified_name="TEST_DB.TEST_TABLE"):
        """Create a mock TableContext with required attributes."""
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.fully_qualified_name = fully_qualified_name
        mock_table_context.column_selection_list = ["COL1", "COL2"]
        mock_table_context.run_id = "test_run"
        mock_table_context.run_start_time = "2025-01-01"
        return mock_table_context

    def test_extract_schema_metadata_success(self):
        """Test successful schema metadata extraction."""
        # Setup
        mock_table_context = self._create_mock_table_context()
        mock_output_handler = Mock(spec=OutputHandlerBase)
        mock_output_handler.console_output_enabled = True

        # Mock query generation and execution
        test_query = "SELECT * FROM TEST_TABLE"
        self.mock_query_generator.generate_schema_query.return_value = test_query

        mock_columns = ["COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE"]
        mock_data = [("COL1", "INTEGER", "Y"), ("COL2", "VARCHAR", "N")]
        self.mock_connector.execute_query.return_value = (mock_columns, mock_data)

        # Execute
        result = self.extractor.extract_schema_metadata(
            table_context=mock_table_context, output_handler=mock_output_handler
        )

        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.mock_query_generator.generate_schema_query.assert_called_once_with(
            mock_table_context
        )
        self.mock_connector.execute_query.assert_called_once_with(test_query)

    def test_extract_metrics_metadata_success(self):
        """Test successful metrics metadata extraction."""
        # Setup
        mock_table_context = self._create_mock_table_context()
        mock_output_handler = Mock(spec=OutputHandlerBase)
        mock_output_handler.console_output_enabled = True

        # Mock query generation and execution
        test_query = f"SELECT * FROM TEST_TABLE"
        self.mock_query_generator.generate_metrics_query.return_value = test_query

        mock_columns = [COLUMN_VALIDATED, "METRIC_VALUE"]
        mock_data = [("COL1", 100), ("COL2", 200)]
        self.mock_connector.execute_query.return_value = (mock_columns, mock_data)

        # Execute
        result = self.extractor.extract_metrics_metadata(
            table_context=mock_table_context,
            output_handler=mock_output_handler,
        )

        # Assert
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.mock_query_generator.generate_metrics_query.assert_called_once_with(
            table_context=mock_table_context,
            connector=self.mock_connector,
        )
        self.mock_connector.execute_query.assert_called_once_with(test_query)

    def test_extract_schema_metadata_no_results(self):
        """Test schema metadata extraction with no results."""
        # Setup
        mock_table_context = self._create_mock_table_context()
        mock_output_handler = Mock(spec=OutputHandlerBase)
        mock_output_handler.console_output_enabled = True

        # Mock empty results
        self.mock_connector.execute_query.return_value = None

        # Execute
        result = self.extractor.extract_schema_metadata(
            table_context=mock_table_context, output_handler=mock_output_handler
        )

        # Assert
        self.assertTrue(result.empty)
        mock_output_handler.handle_message.assert_called_once()

    def test_extract_metrics_metadata_query_failure(self):
        """Test metrics metadata extraction when query fails."""
        # Setup
        mock_table_context = self._create_mock_table_context()
        mock_output_handler = Mock(spec=OutputHandlerBase)
        mock_output_handler.console_output_enabled = True

        # Mock query failure
        self.mock_connector.execute_query.side_effect = Exception("Query failed")

        # Execute and assert
        with self.assertRaises(Exception):
            self.extractor.extract_metrics_metadata(
                table_context=mock_table_context, output_handler=mock_output_handler
            )

    def test_md5_methods_implementation(self):
        """Test that MD5-related methods are properly implemented."""
        mock_table_context = self._create_mock_table_context()
        
        # Mock query generation
        test_statement = "CREATE TABLE chunks_md5..."
        test_query = "SELECT * FROM chunks_md5..."
        self.mock_query_generator.generate_statement_table_chunks_md5.return_value = test_statement
        self.mock_query_generator.generate_compute_md5_query.return_value = [test_query]
        self.mock_query_generator.generate_extract_chunks_md5_query.return_value = test_query
        self.mock_query_generator.generate_extract_md5_rows_chunk_query.return_value = test_query

        # Mock query execution results
        mock_columns = ["CHUNK_ID", "MD5_VALUE"]
        mock_data = [("chunk1", "abc123"), ("chunk2", "def456")]
        self.mock_connector.execute_query.return_value = (mock_columns, mock_data)

        # Test create_table_chunks_md5
        self.extractor.create_table_chunks_md5(table_context=mock_table_context)
        self.mock_query_generator.generate_statement_table_chunks_md5.assert_called_once_with(
            table_context=mock_table_context
        )
        self.mock_connector.execute_statement.assert_called_with(test_statement)

        # Test compute_md5
        self.extractor.compute_md5(
            table_context=mock_table_context, other_table_name="OTHER_TABLE"
        )
        self.mock_query_generator.generate_compute_md5_query.assert_called_once_with(
            table_context=mock_table_context, other_table_name="OTHER_TABLE"
        )
        self.mock_connector.execute_query_no_return.assert_called_with(test_query)

        # Test extract_chunks_md5
        result_df = self.extractor.extract_chunks_md5(table_context=mock_table_context)
        self.mock_query_generator.generate_extract_chunks_md5_query.assert_called_once_with(
            table_context=mock_table_context
        )
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)

        # Test extract_md5_rows_chunk
        result_df = self.extractor.extract_md5_rows_chunk(
            chunk_id="chunk1", table_context=mock_table_context
        )
        self.mock_query_generator.generate_extract_md5_rows_chunk_query.assert_called_once_with(
            chunk_id="chunk1", table_context=mock_table_context
        )
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), 2)
