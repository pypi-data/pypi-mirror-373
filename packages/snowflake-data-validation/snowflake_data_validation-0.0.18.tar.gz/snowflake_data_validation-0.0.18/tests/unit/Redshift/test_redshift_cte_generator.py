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

import logging
import pytest
import pandas as pd
from unittest.mock import Mock, patch

from snowflake.snowflake_data_validation.redshift.extractor.redshift_cte_generator import (
    generate_cte_query,
    generate_outer_query,
)
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.constants import (
    METRIC_COLUMN_KEY,
    NORMALIZATION_COLUMN_KEY,
    TEMPLATE_COLUMN_KEY,
    TYPE_COLUMN_KEY,
)


class TestGenerateCteQuery:
    """Test cases for generate_cte_query function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        self.mock_template = Mock()
        self.mock_env = Mock()
        self.mock_env.get_template.return_value = self.mock_template
        self.mock_sql_generator.env = self.mock_env

    def _create_metrics_templates_df(self, data):
        """Create a DataFrame with metrics templates."""
        return pd.DataFrame(data)

    def test_generate_cte_query_success(self):
        """Test successful CTE query generation."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "VARCHAR",
                METRIC_COLUMN_KEY: "count_metric",
                TEMPLATE_COLUMN_KEY: "COUNT({col_name})",
                NORMALIZATION_COLUMN_KEY: "CAST({metric_query} AS BIGINT)",
            }
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        expected_query = "WITH test_col AS (SELECT CAST(COUNT(test_col) AS BIGINT) AS count_metric FROM test_table WHERE condition)"
        self.mock_template.render.return_value = expected_query

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="varchar",
            fully_qualified_name="test_table",
            where_clause="condition",
            has_where_clause=True,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query == expected_query
        assert result_type == "test_col"
        assert result_metrics == ["count_metric"]

        self.mock_env.get_template.assert_called_once_with(
            "redshift_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_called_once()

    def test_generate_cte_query_no_matching_templates(self, caplog):
        """Test CTE query generation when no templates match the column type."""
        caplog.set_level(logging.WARNING)
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "VARCHAR",
                METRIC_COLUMN_KEY: "count_metric",
                TEMPLATE_COLUMN_KEY: "COUNT({col_name})",
                NORMALIZATION_COLUMN_KEY: "CAST({metric_query} AS BIGINT)",
            }
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="BOOLEAN",
            fully_qualified_name="test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query is None
        assert result_type is None
        assert result_metrics is None

        assert "No metrics templates found for column type BOOLEAN" in caplog.text


class TestGenerateOuterQuery:
    """Test cases for generate_outer_query function."""

    def test_generate_outer_query(self):
        """Test outer query generation."""
        cte_names = ["col1"]
        metrics = [["count_metric"]]

        result = generate_outer_query(cte_names, metrics)

        expected_query = """SELECT
    'col1' AS COLUMN_VALIDATED,
    CAST(count_metric AS VARCHAR) AS count_metric
FROM col1"""

        assert result.strip() == expected_query.strip()

    def test_generate_outer_query_empty_lists(self):
        """Test outer query generation with empty lists."""
        cte_names = []
        metrics = []

        result = generate_outer_query(cte_names, metrics)

        assert result == ""
