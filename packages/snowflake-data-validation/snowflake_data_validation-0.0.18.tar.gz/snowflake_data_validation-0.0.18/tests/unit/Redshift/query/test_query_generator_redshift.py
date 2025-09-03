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

from typing import Literal
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch

from snowflake.snowflake_data_validation.redshift.query.query_generator_redshift import (
    QueryGeneratorRedshift,
)
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)


EXPECTED_ROW_CONCATENATED_QUERY: Literal = """CREATE TEMPORARY TABLE IF NOT EXISTS ROW_CONCATENATED_datatypes_test_123 (

        "pk_IDX" BIGINT,

    ROW_CONCAT_VALUES VARCHAR(MAX)
);"""

EXPECTED_ROW_CONCATENATED_INSERTION_QUERY: Literal = """INSERT INTO ROW_CONCATENATED_datatypes_test_123
SELECT

        "pk_IDX",


        CAST("text_col" AS VARCHAR(MAX))

     FROM
    (SELECT

            "pk" AS "pk_IDX",



                "text_col" AS "text_col"


     FROM test.data_types_table

     ORDER BY  "pk_IDX"
     LIMIT 500
     OFFSET 1000
    ) AS RW;"""

EXPECTED_ROW_MD5_QUERY: Literal = """CREATE TEMPORARY TABLE IF NOT EXISTS ROW_MD5_datatypes_test_123(

        "pk" BIGINT,

    ROW_MD5 VARCHAR(MAX)
);"""

EXPECTED_ROW_MD5_INSERTION_QUERY: Literal = """INSERT INTO ROW_MD5_datatypes_test_123
SELECT

        "pk_IDX",

    UPPER(MD5(ROW_CONCAT_VALUES))
FROM ROW_CONCATENATED_datatypes_test_123
ORDER BY "pk_IDX";"""

EXPECTED_NUMBER_OF_STATEMENTS_TO_COMPUTE_MD5: int = 5


class TestQueryGeneratorRedshift:
    def setup_method(self):
        self.query_generator = QueryGeneratorRedshift()

    def test_init(self):
        assert self.query_generator is not None
        assert self.query_generator.platform == Platform.REDSHIFT

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query"
    )
    def test_cte_query_generator_success(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        expected_result = ("SELECT * FROM test", "test_cte", ["metric1", "metric2"])
        mock_generate_cte.return_value = expected_result

        result = self.query_generator.cte_query_generator(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="VARCHAR",
            fully_qualified_name="test_db.test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=mock_sql_generator,
            exclude_metrics=False,
        )

        assert result == expected_result
        mock_generate_cte.assert_called_once_with(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="VARCHAR",
            fully_qualified_name="test_db.test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=mock_sql_generator,
            exclude_metrics=False,
        )

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query"
    )
    def test_cte_query_generator_with_where_clause(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        expected_result = ("SELECT * FROM test WHERE id > 0", "test_cte", ["metric1"])
        mock_generate_cte.return_value = expected_result

        result = self.query_generator.cte_query_generator(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="INTEGER",
            fully_qualified_name="test_db.test_table",
            where_clause="WHERE id > 0",
            has_where_clause=True,
            sql_generator=mock_sql_generator,
            exclude_metrics=False,
        )

        assert result == expected_result
        mock_generate_cte.assert_called_once_with(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="INTEGER",
            fully_qualified_name="test_db.test_table",
            where_clause="WHERE id > 0",
            has_where_clause=True,
            sql_generator=mock_sql_generator,
            exclude_metrics=False,
        )

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query"
    )
    def test_cte_query_generator_no_query_generated(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        mock_generate_cte.return_value = (None, None, None)

        result = self.query_generator.cte_query_generator(
            metrics_templates=mock_metrics_templates,
            col_name="test_col",
            col_type="UNKNOWN_TYPE",
            fully_qualified_name="test_db.test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=mock_sql_generator,
            exclude_metrics=False,
        )

        assert result == (None, None, None)

    def test_generate_compute_md5_chunk_query_without_index_columns(self):
        mock_table_context = Mock()
        mock_table_context.index_column_collection = []
        mock_table_context.fully_qualified_name = "test_db.test_table"

        with pytest.raises(Exception) as exc_info:
            self.query_generator._generate_compute_md5_chunk_query(
                table_context=mock_table_context, chunk_id="123", fetch=1000, offset=0
            )

        assert "Index column collection is required" in str(exc_info.value)
        assert "test_db.test_table" in str(exc_info.value)

    def test_generate_compute_md5_chunk_query(self):
        mock_table_context = Mock()
        mock_table_context.index_column_collection = [
            ColumnMetadata(
                name="pk",
                data_type="BIGINT",
                is_primary_key=True,
                nullable=False,
                calculated_column_size_in_bytes=256,
                properties={},
            )
        ]
        mock_table_context.columns_to_validate = [
            ColumnMetadata(
                name="text_col",
                data_type="TEXT",
                is_primary_key=False,
                nullable=False,
                calculated_column_size_in_bytes=256,
                properties={},
            ),
        ]

        mock_table_context.templates_loader_manager.datatypes_normalization_templates = {
            "TEXT": '"{{ col_name }}"',
            "BOOLEAN": "CASE WHEN \"{{ col_name }}\" = true THEN 'true' ELSE 'false' END",
            "TIME": "TO_CHAR(\"{{ col_name }}\", 'HH24:MI:SS')",
            "NUMERIC": "TO_CHAR(\"{{ col_name }}\", 'FM99999990.0000')",
        }

        mock_table_context.join_column_names_with_commas.return_value = '"text_col"'
        mock_table_context.fully_qualified_name = "test.data_types_table"
        mock_table_context.has_where_clause = False
        mock_table_context.where_clause = ""
        mock_table_context.table_name = "data_types_table"
        mock_table_context.normalized_fully_qualified_name = "test_data_types_table"
        mock_table_context.database_name = "test"
        mock_table_context.schema_name = "public"
        mock_table_context.id = "123"

        templates_dir_path = str(
            Path(__file__).parent.parent.parent.parent.parent
            / "src/snowflake/snowflake_data_validation/redshift/extractor/templates"
        )
        mock_table_context.sql_generator = SQLQueriesTemplateGenerator(
            templates_dir_path
        )

        results = self.query_generator._generate_compute_md5_chunk_query(
            table_context=mock_table_context,
            chunk_id="datatypes_test",
            fetch=500,
            offset=1000,
        )

        assert results is not None
        assert isinstance(results, list)
        assert len(results) == EXPECTED_NUMBER_OF_STATEMENTS_TO_COMPUTE_MD5

        # Normalize whitespace for robust string comparison
        def normalize(s):
            return " ".join(s.split())

        normalized_results = [normalize(stmt) for stmt in results]

        assert any(
            normalize(EXPECTED_ROW_CONCATENATED_QUERY) == stmt
            for stmt in normalized_results
        )
        assert any(
            normalize(EXPECTED_ROW_CONCATENATED_INSERTION_QUERY) == stmt
            for stmt in normalized_results
        )
        assert any(
            normalize(EXPECTED_ROW_MD5_QUERY) == stmt for stmt in normalized_results
        )
        assert any(
            normalize(EXPECTED_ROW_MD5_INSERTION_QUERY) == stmt
            for stmt in normalized_results
        )
        # Check that final INSERT statement includes table_id
        expected_final_insert = "INSERT INTO CHUNKS_MD5_test_data_types_table_123"
        assert any(
            expected_final_insert in stmt for stmt in results
        ), f"Expected final insert statement not found in: {results}"

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_outer_query"
    )
    def test_outer_query_generator_success(self, mock_generate_outer):
        expected_result = "SELECT * FROM cte1 UNION ALL SELECT * FROM cte2"
        mock_generate_outer.return_value = expected_result
        cte_names = ["cte1", "cte2"]
        metrics = [["metric1"], ["metric2"]]

        result = self.query_generator.outer_query_generator(cte_names, metrics)

        assert result == expected_result
        mock_generate_outer.assert_called_once_with(cte_names, metrics)

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query"
    )
    def test_cte_query_generator_error_handling(self, mock_generate_cte):
        mock_metrics_templates = Mock()
        mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        mock_generate_cte.side_effect = Exception("CTE generation failed")

        with pytest.raises(Exception, match="CTE generation failed"):
            self.query_generator.cte_query_generator(
                metrics_templates=mock_metrics_templates,
                col_name="test_col",
                col_type="VARCHAR",
                fully_qualified_name="test_db.test_table",
                where_clause="",
                has_where_clause=False,
                sql_generator=mock_sql_generator,
                exclude_metrics=False,
            )

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_outer_query"
    )
    def test_outer_query_generator_error_handling(self, mock_generate_outer):
        mock_generate_outer.side_effect = Exception("Outer query generation failed")
        cte_names = ["cte1", "cte2"]
        metrics = [["metric1"], ["metric2"]]

        with pytest.raises(Exception, match="Outer query generation failed"):
            self.query_generator.outer_query_generator(cte_names, metrics)

    @patch(
        "snowflake.snowflake_data_validation.redshift.query.query_generator_redshift.generate_cte_query"
    )
    def test_cte_query_generator_with_none_parameters(self, mock_generate_cte):
        mock_generate_cte.return_value = (None, None, None)

        result = self.query_generator.cte_query_generator(
            metrics_templates=None,
            col_name=None,
            col_type=None,
            fully_qualified_name=None,
            where_clause=None,
            has_where_clause=False,
            sql_generator=None,
            exclude_metrics=False,
        )

        assert result == (None, None, None)
