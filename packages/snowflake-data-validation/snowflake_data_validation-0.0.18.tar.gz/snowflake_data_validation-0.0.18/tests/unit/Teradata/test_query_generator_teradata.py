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

"""Tests for QueryGeneratorTeradata."""

import pytest
from unittest.mock import Mock, call

from snowflake.snowflake_data_validation.teradata.query.query_generator_teradata import (
    QueryGeneratorTeradata,
)
from snowflake.snowflake_data_validation.utils.model.chunk import Chunk
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.utils.constants import (
    Platform,
    COL_NAME_NO_QUOTES_PLACEHOLDER,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.context import Context


class TestQueryGeneratorTeradata:
    """Test cases for QueryGeneratorTeradata."""

    def setup_method(self):
        """Set up test fixtures."""
        self.query_generator = QueryGeneratorTeradata()

    def test_init(self):
        """Test QueryGeneratorTeradata initialization."""
        assert self.query_generator is not None
        assert self.query_generator.platform == Platform.TERADATA

    def test_cte_query_generator_error_handling(self):
        """Test that CTE query generation handles errors when sql_generator is None."""
        with pytest.raises(AttributeError):
            self.query_generator.cte_query_generator(
                metrics_templates=None,
                col_name="test_col",
                col_type="INTEGER",
                fully_qualified_name="test_db.test_table",
                where_clause="",
                has_where_clause=False,
                sql_generator=None,
                exclude_metrics=False,
            )

    def test_outer_query_generator_basic(self):
        """Test that outer query generation works with basic inputs."""
        cte_names = ["test_cte"]
        metrics = [["min", "max"]]
        result = self.query_generator.outer_query_generator(cte_names, metrics)
        assert "SELECT" in result
        assert "test_cte" in result
        assert "min" in result
        assert "max" in result

    def test_generate_metrics_query_error_handling(self):
        """Test that metrics query generation handles errors properly."""
        # Create mock table context with all required attributes
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.columns_to_validate = []  # Empty list should cause exception
        mock_table_context.fully_qualified_name = "test_db.test_schema.test_table"
        mock_table_context.templates_loader_manager = Mock()
        mock_table_context.templates_loader_manager.metrics_templates = Mock()
        mock_table_context.where_clause = ""
        mock_table_context.has_where_clause = False
        mock_table_context.sql_generator = Mock()
        mock_table_context.id = "test_table_id"

        mock_connector = Mock(spec=ConnectorBase)

        with pytest.raises(
            Exception, match="Metrics templates are missing for the column data types"
        ):
            self.query_generator.generate_metrics_query(
                table_context=mock_table_context, connector=mock_connector
            )

    def test_generate_compute_md5_query(self):
        """Test MD5 computation query generation."""
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.templates_loader_manager = Mock()
        mock_table_context.templates_loader_manager.datatypes_normalization_templates = {
            "VARCHAR": 'TRIM("{{ col_name }}")'
        }

        # Create a mock column with proper string attributes
        mock_column = Mock()
        mock_column.data_type = "VARCHAR"
        mock_column.name = "col1"  # Use string instead of Mock
        mock_table_context.columns_to_validate = [mock_column]

        # Mock SQL generator and its methods with actual return values
        mock_sql_generator = Mock()
        mock_env = Mock()
        mock_template = Mock()

        # Mock the template rendering for each template
        mock_template.render.side_effect = [
            "CREATE VOLATILE TABLE ROW_CONCATENATED_test_chunk_id...",
            "CREATE VOLATILE TABLE ROW_MD5_test_chunk_id...",
            "INSERT INTO CHUNKS_MD5_test_db_test_schema_test_table...",
        ]
        mock_env.get_template = Mock(return_value=mock_template)
        mock_sql_generator.env = mock_env
        mock_table_context.sql_generator = mock_sql_generator

        # Set all required attributes
        mock_table_context.index_column_collection = []
        mock_table_context.join_column_names_with_commas.return_value = "col1"
        mock_table_context.fully_qualified_name = "test_db.test_schema.test_table"
        mock_table_context.has_where_clause = False
        mock_table_context.where_clause = ""
        mock_table_context.database_name = "test_db"
        mock_table_context.schema_name = "test_schema"
        mock_table_context.table_name = "test_table"
        mock_table_context.normalized_fully_qualified_name = (
            "test_db_test_schema_test_table"
        )
        mock_table_context.platform = Platform.TERADATA
        mock_table_context.id = "test_table_id"

        # Call the method we're testing
        result = self.query_generator._generate_compute_md5_chunk_query(
            table_context=mock_table_context,
            chunk_id="test_chunk_id",
            fetch=1,
            offset=0,
        )

        # Verify the result is a list of strings
        assert isinstance(result, list)
        assert (
            len(result) == 3
        )  # Should have 3 queries: create concatenated, create md5, insert
        assert all(isinstance(query, str) for query in result)

        # Verify that each template was loaded
        expected_template_calls = [
            call("teradata_create_row_concatenated.sql.j2"),
            call("teradata_create_row_md5.sql.j2"),
            call("teradata_compute_md5_sql.j2"),
        ]
        assert mock_env.get_template.call_args_list == expected_template_calls

        # Verify template render calls with correct parameters
        expected_render_calls = [
            # First template - create row concatenated
            call(
                chunk_id="test_chunk_id",
                index_column_collection=[],
                table_id="test_table_id",
            ),
            # Second template - create row md5
            call(
                chunk_id="test_chunk_id",
                index_column_collection=[],
                table_id="test_table_id",
            ),
            # Third template - compute md5
            call(
                chunk_id="test_chunk_id",
                column_names_separate_by_comma="col1",
                index_column_collection=[],
                column_collection=[mock_column],
                datatypes_normalization_renderer_templates={"col1": 'TRIM("col1")'},
                fully_qualified_name="test_db.test_schema.test_table",
                has_where_clause=False,
                where_clause="",
                source_table_name="test_table",
                normalized_fully_qualified_name="test_db_test_schema_test_table",
                offset=0,
                fetch=1,
                database_name="test_db",
                schema_name="test_schema",
                table_id="test_table_id",
            ),
        ]
        assert mock_template.render.call_args_list == expected_render_calls

    def test_generate_statement_table_chunks_md5(self):
        """Test MD5 table creation query generation."""
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.sql_generator = Mock()
        mock_table_context.normalized_fully_qualified_name = (
            "test_db_test_schema_test_table"
        )
        mock_table_context.platform = Platform.TERADATA
        mock_table_context.database_name = "test_db"
        mock_table_context.schema_name = "test_schema"
        mock_table_context.id = "test_table_id"

        self.query_generator.generate_statement_table_chunks_md5(
            table_context=mock_table_context
        )

        mock_table_context.sql_generator.generate_statement_table_chunks_md5.assert_called_once_with(
            normalized_fully_qualified_name=mock_table_context.normalized_fully_qualified_name,
            platform=Platform.TERADATA.value,
            database_name=mock_table_context.database_name,
            schema_name=mock_table_context.schema_name,
            table_id=mock_table_context.id,
        )

    def test_generate_extract_chunks_md5_query(self):
        """Test MD5 chunk extraction query generation."""
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.sql_generator = Mock()
        mock_table_context.normalized_fully_qualified_name = (
            "test_db_test_schema_test_table"
        )
        mock_table_context.platform = Platform.TERADATA
        mock_table_context.database_name = "test_db"
        mock_table_context.schema_name = "test_schema"
        mock_table_context.id = "test_table_id"

        self.query_generator.generate_extract_chunks_md5_query(
            table_context=mock_table_context
        )

        mock_table_context.sql_generator.generate_extract_chunks_md5_query.assert_called_once_with(
            platform=Platform.TERADATA.value,
            normalized_fully_qualified_name=mock_table_context.normalized_fully_qualified_name,
            database_name=mock_table_context.database_name,
            schema_name=mock_table_context.schema_name,
            table_id=mock_table_context.id,
        )

    def test_generate_extract_md5_rows_chunk_query(self):
        """Test MD5 chunk row extraction query generation."""
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.sql_generator = Mock()
        mock_table_context.index_column_collection = []
        mock_table_context.platform = Platform.TERADATA
        mock_table_context.database_name = "test_db"
        mock_table_context.schema_name = "test_schema"
        mock_table_context.id = "test_table_id"

        self.query_generator.generate_extract_md5_rows_chunk_query(
            chunk_id="test_chunk_id", table_context=mock_table_context
        )

        mock_table_context.sql_generator.generate_extract_md5_rows_chunk_query.assert_called_once_with(
            platform=Platform.TERADATA.value,
            chunk_id="test_chunk_id",
            index_column_collection=mock_table_context.index_column_collection,
            database_name=mock_table_context.database_name,
            schema_name=mock_table_context.schema_name,
            table_id=mock_table_context.id,
        )
