import unittest
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from snowflake.snowflake_data_validation.teradata.extractor.teradata_cte_generator import (
    generate_cte_query,
    generate_outer_query,
)
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.constants import (
    TYPE_COLUMN_KEY,
    METRIC_COLUMN_KEY,
    TEMPLATE_COLUMN_KEY,
    NORMALIZATION_COLUMN_KEY,
)


class TestTeradataMetricsValidation(unittest.TestCase):
    """Test cases for Teradata metrics validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_sql_generator = Mock(spec=SQLQueriesTemplateGenerator)
        self.mock_template = Mock()
        self.mock_env = Mock()
        self.mock_env.get_template.return_value = self.mock_template
        self.mock_sql_generator.env = self.mock_env

    def _create_metrics_templates_df(self, data):
        """Create a DataFrame with metrics templates."""
        return pd.DataFrame(data)

    def test_generate_cte_query_numeric_metrics(self):
        """Test CTE query generation for numeric data types."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "INTEGER",
                METRIC_COLUMN_KEY: "min",
                TEMPLATE_COLUMN_KEY: 'MIN("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
            {
                TYPE_COLUMN_KEY: "INTEGER",
                METRIC_COLUMN_KEY: "max",
                TEMPLATE_COLUMN_KEY: 'MAX("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
            {
                TYPE_COLUMN_KEY: "INTEGER",
                METRIC_COLUMN_KEY: "avg",
                TEMPLATE_COLUMN_KEY: 'AVG("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        expected_query = "WITH test_col AS (SELECT metrics FROM test_table)"
        self.mock_template.render.return_value = expected_query

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="INTEGER",
            fully_qualified_name="test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query == expected_query
        assert result_type == "test_col"
        assert set(result_metrics or []) == {"min", "max", "avg"}

        self.mock_env.get_template.assert_called_once_with(
            "teradata_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_called_once()

    def test_generate_cte_query_string_metrics(self):
        """Test CTE query generation for string data types."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "VARCHAR",
                METRIC_COLUMN_KEY: "count_distinct",
                TEMPLATE_COLUMN_KEY: 'COUNT(DISTINCT "{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
            {
                TYPE_COLUMN_KEY: "VARCHAR",
                METRIC_COLUMN_KEY: "count_null",
                TEMPLATE_COLUMN_KEY: 'SUM(CASE WHEN "{{ col_name }}" IS NULL THEN 1 ELSE 0 END)',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        expected_query = (
            "WITH test_col AS (SELECT metrics FROM test_table WHERE condition)"
        )
        self.mock_template.render.return_value = expected_query

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="VARCHAR",
            fully_qualified_name="test_table",
            where_clause="condition",
            has_where_clause=True,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query == expected_query
        assert result_type == "test_col"
        assert set(result_metrics or []) == {"count_distinct", "count_null"}

        self.mock_env.get_template.assert_called_once_with(
            "teradata_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_called_once()

    def test_generate_cte_query_date_metrics(self):
        """Test CTE query generation for date data types."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "DATE",
                METRIC_COLUMN_KEY: "min",
                TEMPLATE_COLUMN_KEY: 'MIN("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
            {
                TYPE_COLUMN_KEY: "DATE",
                METRIC_COLUMN_KEY: "max",
                TEMPLATE_COLUMN_KEY: 'MAX("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            },
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        expected_query = "WITH test_col AS (SELECT metrics FROM test_table)"
        self.mock_template.render.return_value = expected_query

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="DATE",
            fully_qualified_name="test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query == expected_query
        assert result_type == "test_col"
        assert set(result_metrics or []) == {"min", "max"}

        self.mock_env.get_template.assert_called_once_with(
            "teradata_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_called_once()

    def test_generate_cte_query_no_metrics(self):
        """Test CTE query generation when no metrics are found for a data type."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "INTEGER",
                METRIC_COLUMN_KEY: "min",
                TEMPLATE_COLUMN_KEY: 'MIN("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            }
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="UNKNOWN_TYPE",  # Type not in templates
            fully_qualified_name="test_table",
            where_clause="",
            has_where_clause=False,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query is None
        assert result_type is None
        assert result_metrics is None

        # The template is still fetched, but no rendering happens because no metrics were found
        self.mock_env.get_template.assert_called_once_with(
            "teradata_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_not_called()

    def test_generate_cte_query_with_where_clause(self):
        """Test CTE query generation with a WHERE clause."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "INTEGER",
                METRIC_COLUMN_KEY: "count",
                TEMPLATE_COLUMN_KEY: 'COUNT("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            }
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        expected_query = (
            "WITH test_col AS (SELECT metrics FROM test_table WHERE id > 100)"
        )
        self.mock_template.render.return_value = expected_query

        result_query, result_type, result_metrics = generate_cte_query(
            metrics_templates=metrics_templates,
            col_name="test_col",
            col_type="INTEGER",
            fully_qualified_name="test_table",
            where_clause="id > 100",
            has_where_clause=True,
            sql_generator=self.mock_sql_generator,
            exclude_metrics=False,
        )

        assert result_query == expected_query
        assert result_type == "test_col"
        assert result_metrics == ["count"]

        self.mock_env.get_template.assert_called_once_with(
            "teradata_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_called_once()

    def test_generate_cte_query_template_error(self):
        """Test CTE query generation when template rendering fails."""
        metrics_data = [
            {
                TYPE_COLUMN_KEY: "INTEGER",
                METRIC_COLUMN_KEY: "count",
                TEMPLATE_COLUMN_KEY: 'COUNT("{{ col_name }}")',
                NORMALIZATION_COLUMN_KEY: "{{ metric_query }}",
            }
        ]
        metrics_templates = self._create_metrics_templates_df(metrics_data)

        # Mock template rendering error
        self.mock_template.render.side_effect = Exception("Template error")

        with self.assertRaises(Exception):
            generate_cte_query(
                metrics_templates=metrics_templates,
                col_name="test_col",
                col_type="INTEGER",
                fully_qualified_name="test_table",
                where_clause="",
                has_where_clause=False,
                sql_generator=self.mock_sql_generator,
                exclude_metrics=False,
            )

        self.mock_env.get_template.assert_called_once_with(
            "teradata_columns_cte_template.sql.j2"
        )
        self.mock_template.render.assert_called_once()

    def test_generate_outer_query_single_column(self):
        """Test outer query generation for a single column."""
        cte_names = ["test_col"]
        metrics = [["min", "max", "avg"]]

        outer_query = generate_outer_query(cte_names, metrics)

        # Verify the basic structure
        assert "SELECT" in outer_query
        assert "FROM test_col" in outer_query
        assert "CAST('test_col' AS VARCHAR(30)) AS COLUMN_VALIDATED" in outer_query

        # Verify all metrics are present, regardless of order
        for metric in ["min", "max", "avg"]:
            assert f'TRIM(CAST("{metric}" AS VARCHAR(25))) AS "{metric}"' in outer_query

    def test_generate_outer_query_multiple_columns(self):
        """Test outer query generation for multiple columns with different metrics."""
        cte_names = ["numeric_col", "string_col"]
        metrics = [
            ["min", "max", "avg"],  # numeric column metrics
            ["count_distinct", "count_null"],  # string column metrics
        ]

        outer_query = generate_outer_query(cte_names, metrics)

        # First query should have numeric metrics present and string metrics as NULL
        first_query = outer_query.split("UNION ALL")[0].strip()
        assert first_query.startswith("SELECT")
        assert first_query.endswith("FROM numeric_col")
        assert "CAST('numeric_col' AS VARCHAR(30)) AS COLUMN_VALIDATED" in first_query
        # Check numeric metrics are present
        for metric in ["min", "max", "avg"]:
            assert f'TRIM(CAST("{metric}" AS VARCHAR(25))) AS "{metric}"' in first_query
        # Check string metrics are NULL
        for metric in ["count_distinct", "count_null"]:
            assert f'CAST(NULL AS VARCHAR(25)) AS "{metric}"' in first_query

        # Second query should have string metrics present and numeric metrics as NULL
        second_query = outer_query.split("UNION ALL")[1].strip()
        assert second_query.startswith("SELECT")
        assert second_query.endswith("FROM string_col")
        assert "CAST('string_col' AS VARCHAR(30)) AS COLUMN_VALIDATED" in second_query
        # Check numeric metrics are NULL
        for metric in ["min", "max", "avg"]:
            assert f'CAST(NULL AS VARCHAR(25)) AS "{metric}"' in second_query
        # Check string metrics are present
        for metric in ["count_distinct", "count_null"]:
            assert (
                f'TRIM(CAST("{metric}" AS VARCHAR(25))) AS "{metric}"' in second_query
            )

    def test_generate_outer_query_empty_metrics(self):
        """Test outer query generation with empty metrics."""
        cte_names = ["test_col"]
        metrics = [[]]  # No metrics

        outer_query = generate_outer_query(cte_names, metrics)

        # Should generate a minimal query with just the COLUMN_VALIDATED
        expected_parts = [
            "SELECT",
            "CAST('test_col' AS VARCHAR(30)) AS COLUMN_VALIDATED",
            "FROM test_col",
        ]
        for part in expected_parts:
            assert part in outer_query

    def test_generate_outer_query_edge_cases(self):
        """Test outer query generation with edge cases."""
        # Test with empty inputs
        cte_names = []
        metrics = []
        result = generate_outer_query(cte_names, metrics)
        assert result == "", "Empty inputs should produce empty output"

        # Test with mismatched lengths
        cte_names = ["col1", "col2"]
        metrics = [["min", "max"]]  # Only one set of metrics
        result = generate_outer_query(cte_names, metrics)
        assert "col1" in result, "First CTE should be in output"
        assert "col2" not in result, "Second CTE should be truncated"

        # Test with no metrics
        cte_names = ["col1"]
        metrics = [[]]
        result = generate_outer_query(cte_names, metrics)
        assert (
            "COLUMN_VALIDATED" in result
        ), "Should include column name even with no metrics"
