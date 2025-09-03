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

"""Tests for ScriptWriterRedshift."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.redshift.script_writer.script_writer_redshift import (
    ScriptWriterRedshift,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALIDATED,
    Platform,
)
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)


class TestScriptWriterRedshift:
    def setup_method(self):
        self.mock_connector = Mock(spec=ConnectorBase)
        self.mock_query_generator = Mock(spec=QueryGeneratorBase)
        self.report_path = "/test/reports"

        self.script_writer = ScriptWriterRedshift(
            connector=self.mock_connector,
            query_generator=self.mock_query_generator,
            report_path=self.report_path,
        )

    def test_init_with_all_parameters(self):
        assert self.script_writer is not None
        assert self.script_writer.connector == self.mock_connector
        assert self.script_writer.query_generator == self.mock_query_generator
        assert self.script_writer.report_path == self.report_path

    def _create_mock_table_configuration(self):
        mock_config = Mock(spec=TableConfiguration)
        mock_config.source_database = "test_db"
        mock_config.source_schema = "test_schema"
        mock_config.source_table = "test_table"
        mock_config.fully_qualified_name = "test_db.test_schema.test_table"
        return mock_config

    def _create_mock_context(self):
        mock_context = Mock(spec=Context)
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        mock_sql_generator.extract_table_column_metadata.return_value = (
            "SELECT * FROM metadata"
        )

        mock_output_handler = Mock(spec=OutputHandlerBase)
        mock_output_handler.console_output_enabled = True

        mock_context.sql_generator = mock_sql_generator
        mock_context.output_handler = mock_output_handler
        mock_context.run_id = "test_run_123"
        mock_context.run_start_time = "2025-01-01T00:00:00"

        return mock_context

    def test_extract_table_column_metadata_success(self):
        mock_config = self._create_mock_table_configuration()
        mock_context = self._create_mock_context()

        result_columns = ["COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE"]
        result_data = [
            ("col1", "VARCHAR", "YES"),
            ("col2", "INTEGER", "NO"),
        ]
        self.mock_connector.execute_query.return_value = (result_columns, result_data)

        result = self.script_writer.extract_table_column_metadata(
            mock_config, mock_context
        )

        actual_dict = result.to_dict("records")
        expected_dict = [
            {"COLUMN_NAME": "col1", "DATA_TYPE": "VARCHAR", "IS_NULLABLE": "YES"},
            {"COLUMN_NAME": "col2", "DATA_TYPE": "INTEGER", "IS_NULLABLE": "NO"},
        ]
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True)
        assert not diff, f"DataFrames differ: {diff}"

    def test_extract_table_column_metadata_logs_critical_error_on_failure(self):
        mock_config = self._create_mock_table_configuration()
        mock_context = self._create_mock_context()

        with patch(
            "snowflake.snowflake_data_validation.redshift.script_writer.script_writer_redshift.LOGGER"
        ) as mock_logger:
            self.mock_connector.execute_query.side_effect = Exception(
                "Connection timeout"
            )

            with pytest.raises(Exception, match="Connection timeout"):
                self.script_writer.extract_table_column_metadata(
                    mock_config, mock_context
                )

            mock_logger.critical.assert_called_once()
            log_args = mock_logger.critical.call_args[0]
            assert "Metadata extraction query failed for table" in str(log_args)
            assert "test_db.test_schema.test_table" in str(log_args)
