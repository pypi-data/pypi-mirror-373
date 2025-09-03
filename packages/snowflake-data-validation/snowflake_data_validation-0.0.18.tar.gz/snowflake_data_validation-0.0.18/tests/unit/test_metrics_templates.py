import pytest
import pandas as pd
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import jinja2
from typing import Set
from deepdiff import DeepDiff
from snowflake.snowflake_data_validation.sqlserver.extractor.sqlserver_cte_generator import (
    generate_cte_query as generate_sqlserver_cte,
)
from snowflake.snowflake_data_validation.snowflake.extractor.snowflake_cte_generator import (
    generate_cte_query as generate_snowflake_cte,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
import tempfile
from snowflake.snowflake_data_validation.utils.constants import Platform, ExecutionMode
from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)


def load_both_templates():
    """Helper function to load both SQL Server and Snowflake templates"""
    base_path = (
        Path(__file__).parent.parent.parent / "src/snowflake/snowflake_data_validation"
    )

    sqlserver_datatypes_normalization_path = (
        base_path
        / "sqlserver/extractor/templates/sqlserver_datatypes_normalization_templates.yaml"
    )
    snowflake_datatypes_normalization_path = (
        base_path
        / "snowflake/extractor/templates/snowflake_datatypes_normalization_templates.yaml"
    )

    sqlserver_datatypes_normalization_templates = (
        Helper.load_datatypes_normalization_templates_from_yaml(
            sqlserver_datatypes_normalization_path
        )
    )
    snowflake_datatypes_normalization_templates = (
        Helper.load_datatypes_normalization_templates_from_yaml(
            snowflake_datatypes_normalization_path
        )
    )

    sqlserver_path = (
        base_path
        / "sqlserver/extractor/templates/sqlserver_column_metrics_templates.yaml"
    )
    snowflake_path = (
        base_path
        / "snowflake/extractor/templates/snowflake_column_metrics_templates.yaml"
    )

    sqlserver_df = Helper.load_metrics_templates_from_yaml(
        sqlserver_path, sqlserver_datatypes_normalization_templates
    )
    snowflake_df = Helper.load_metrics_templates_from_yaml(
        snowflake_path, snowflake_datatypes_normalization_templates
    )

    return sqlserver_df, snowflake_df


def test_type_mappings():
    """Test that SQL Server types map correctly to Snowflake types for metrics"""
    sqlserver_df, snowflake_df = load_both_templates()

    # Expected type mappings
    type_mappings = {
        "BIGINT": "NUMBER",
        "INT": "NUMBER",
        "SMALLINT": "NUMBER",
        "TINYINT": "NUMBER",
        "DECIMAL": "NUMBER",
        "NUMERIC": "NUMBER",
        "FLOAT": "FLOAT",
        "REAL": "FLOAT",
        "CHAR": "VARCHAR",
        "VARCHAR": "VARCHAR",
        "TEXT": "VARCHAR",
        "NCHAR": "VARCHAR",
        "NVARCHAR": "VARCHAR",
        "NTEXT": "VARCHAR",
        "DATE": "DATE",
        "BIT": "BOOLEAN",
        "BINARY": "BINARY",
        "VARBINARY": "BINARY",
    }

    for sql_type, snow_type in type_mappings.items():
        # Get metrics for SQL Server type
        sql_metrics = set(sqlserver_df[sqlserver_df["type"] == sql_type]["metric"])

        # Get metrics for corresponding Snowflake type
        snow_metrics = set(snowflake_df[snowflake_df["type"] == snow_type]["metric"])

        # SQL Server metrics should exist in Snowflake
        assert sql_metrics.issubset(
            snow_metrics
        ), f"Type mapping {sql_type} -> {snow_type} has incompatible metrics: {sql_metrics - snow_metrics}"


@pytest.fixture
def mock_context(tmp_path):
    """Create a mock context for testing using a temporary directory

    Args:
        tmp_path: pytest fixture that provides a temporary directory unique to each test function
    """
    temp_dir = None
    context = None
    output_handler = None

    try:
        # Create a mock output handler
        output_handler = MagicMock(spec=OutputHandlerBase)
        output_handler.console_output_enabled = True

        # Create a mock configuration
        configuration = ConfigurationModel(
            source_platform="SQL server",
            target_platform="Snowflake",
            output_directory_path="",
        )

        # Set up paths
        base_path = (
            Path(__file__).parent.parent.parent
            / "src/snowflake/snowflake_data_validation"
        )
        sqlserver_templates = str(base_path / "sqlserver/extractor/templates")
        snowflake_templates = str(base_path / "snowflake/extractor/templates")

        # Create a temporary directory for test reports
        temp_dir = tempfile.mkdtemp(prefix="test_metrics_")
        report_path = str(Path(temp_dir) / "test_reports")
        os.makedirs(report_path, exist_ok=True)

        # Create a custom SQL generator that uses both template directories
        sql_generator = SQLQueriesTemplateGenerator(sqlserver_templates)
        # Override the Jinja environment to include both template directories
        sql_generator.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([sqlserver_templates, snowflake_templates])
        )

        source_templates = TemplatesLoaderManager(
            Path(sqlserver_templates), Platform.SQLSERVER
        )
        target_templates = TemplatesLoaderManager(
            Path(snowflake_templates), Platform.SNOWFLAKE
        )

        # Create the context with all required parameters
        context = Context(
            configuration=configuration,
            report_path=report_path,
            templates_dir_path=sqlserver_templates,  # Use SQL Server templates as primary
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            custom_output_handler=output_handler,
            run_id="test_run",
            run_start_time="20250101T000000",
            source_templates=source_templates,
            target_templates=target_templates,
            execution_mode=ExecutionMode.SYNC_VALIDATION,
        )

        # Set the SQL generator
        context.sql_generator = sql_generator

        yield context

    finally:
        # Clean up resources
        if context is not None:
            # Close any open files in the context
            if hasattr(context, "close"):
                context.close()

        if output_handler is not None:
            # Close the output handler
            if hasattr(output_handler, "close"):
                output_handler.close()

        # Clean up the temporary directory
        if temp_dir is not None and os.path.exists(temp_dir):
            try:
                # On Windows, we need to handle files that might still be open
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for name in files:
                        try:
                            os.chmod(os.path.join(root, name), 0o777)
                            os.unlink(os.path.join(root, name))
                        except (OSError, PermissionError):
                            pass  # Skip files that can't be deleted
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except (OSError, PermissionError):
                            pass  # Skip directories that can't be deleted
                os.rmdir(temp_dir)
            except (OSError, PermissionError):
                pass  # Ignore errors during cleanup


def verify_column_query_generation(
    mock_context,
    sql_type: str,
    snow_type: str,
    col_name: str,
    table_name: str,
    expected_metrics: Set[str],
):
    """Helper function to verify query generation for a specific column type in both SQL Server and Snowflake

    Args:
        mock_context: The mock context fixture
        sql_type: SQL Server data type
        snow_type: Snowflake data type
        col_name: Name of the column to test
        table_name: Name of the table containing the column
        expected_metrics: Set of metric names expected for this data type
    """
    sqlserver_df, snowflake_df = load_both_templates()

    # Generate SQL Server query
    sqlserver_query, sqlserver_cte, sqlserver_metrics = generate_sqlserver_cte(
        metrics_templates=sqlserver_df,
        col_name=col_name,
        col_type=sql_type,
        fully_qualified_name=table_name,
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_context.sql_generator,
        exclude_metrics=False,
    )

    # Generate Snowflake query
    snowflake_query, snowflake_cte, snowflake_metrics = generate_snowflake_cte(
        metrics_templates=snowflake_df,
        col_name=col_name,
        col_type=snow_type,
        fully_qualified_name=table_name,
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_context.sql_generator,
        exclude_metrics=False,
    )

    # Verify queries are not None
    assert sqlserver_query is not None, "SQL Server query should not be None"
    assert snowflake_query is not None, "Snowflake query should not be None"

    # Verify CTEs are named correctly
    assert sqlserver_cte == f"{col_name}"
    assert snowflake_cte == f"{col_name}"

    # Verify metrics are present
    assert set(sqlserver_metrics) == expected_metrics
    assert set(snowflake_metrics) == expected_metrics

    # Verify query structure
    assert "SELECT" in sqlserver_query
    assert f"FROM {table_name}" in sqlserver_query
    assert "SELECT" in snowflake_query
    assert f"FROM {table_name}" in snowflake_query


def test_numeric_column_query_generation(mock_context):
    """Test query generation for a numeric column in both SQL Server and Snowflake"""
    verify_column_query_generation(
        mock_context=mock_context,
        sql_type="int",
        snow_type="NUMBER",
        col_name="revenue",
        table_name="sales.transactions",
        expected_metrics={
            "min",
            "max",
            "avg",
            "sum",
            "count_distinct",
            "count_null",
            "count_zero",
            "stddev",
            "variance",
        },
    )


def test_string_column_query_generation(mock_context):
    """Test query generation for a string column in both SQL Server and Snowflake"""
    verify_column_query_generation(
        mock_context=mock_context,
        sql_type="varchar",
        snow_type="VARCHAR",
        col_name="customer_name",
        table_name="sales.customers",
        expected_metrics={
            "min",
            "max",
            "avg",
            "count_empty",
            "count_distinct",
            "count_null",
        },
    )


def test_date_column_query_generation(mock_context):
    """Test query generation for a date column in both SQL Server and Snowflake"""
    verify_column_query_generation(
        mock_context=mock_context,
        sql_type="date",
        snow_type="DATE",
        col_name="transaction_date",
        table_name="sales.transactions",
        expected_metrics={"min", "max", "count_null"},
    )


def test_boolean_column_query_generation(mock_context):
    """Test query generation for a boolean column in both SQL Server and Snowflake"""
    verify_column_query_generation(
        mock_context=mock_context,
        sql_type="bit",
        snow_type="BOOLEAN",
        col_name="is_active",
        table_name="sales.customers",
        expected_metrics={"count_true", "count_false", "count_null"},
    )


def test_metrics_not_found_in_snowflake():
    """Test behavior when SQL Server metrics are not found in Snowflake"""
    sqlserver_df, snowflake_df = load_both_templates()

    # Create a copy of the dataframe and add a custom metric that doesn't exist in Snowflake
    custom_sqlserver_df = sqlserver_df.copy()
    custom_metric_row = {
        "type": "int",
        "category": "numeric",
        "metric": "custom_metric_not_in_snowflake",
        "template": 'CUSTOM("{{ col_name }}")',
        "normalization": 'TO CHAR("{{ metric_query }}")',
    }
    custom_sqlserver_df = pd.concat(
        [custom_sqlserver_df, pd.DataFrame([custom_metric_row])], ignore_index=True
    )

    # Get unique metrics for each
    sqlserver_metrics = set(custom_sqlserver_df["metric"])
    snowflake_metrics = set(snowflake_df["metric"])

    # Compare using DeepDiff to find the differences
    diff = DeepDiff(snowflake_metrics, sqlserver_metrics, ignore_order=True)

    # Verify the custom metric appears in the set_item_added section of the diff
    assert any(
        "custom_metric_not_in_snowflake" in item
        for item in diff.get("set_item_added", [])
    )
    # Verify there are no unexpected differences
    assert "set_item_removed" not in diff


def test_metrics_not_found_in_sqlserver():
    """Test behavior when Snowflake metrics are not found in SQL Server"""
    sqlserver_df, snowflake_df = load_both_templates()

    # Create a copy of the dataframe and add a custom metric that doesn't exist in SQL Server
    custom_snowflake_df = snowflake_df.copy()
    custom_metric_row = {
        "type": "NUMBER",
        "category": "numeric",
        "metric": "custom_metric_not_in_sqlserver",
        "template": 'CUSTOM("{{ col_name }}")',
    }
    custom_snowflake_df = pd.concat(
        [custom_snowflake_df, pd.DataFrame([custom_metric_row])], ignore_index=True
    )

    # Get unique metrics for each
    sqlserver_metrics = set(sqlserver_df["metric"])
    snowflake_metrics = set(custom_snowflake_df["metric"])

    # Compare using DeepDiff to find the differences
    diff = DeepDiff(sqlserver_metrics, snowflake_metrics, ignore_order=True)

    # Verify the custom metric appears in the set_item_added section of the diff
    assert any(
        "custom_metric_not_in_sqlserver" in item
        for item in diff.get("set_item_added", [])
    )
    # Verify there are no unexpected differences
    assert "set_item_removed" not in diff


def test_incompatible_metric_templates():
    """Test behavior when metric templates are incompatible between SQL Server and Snowflake"""
    sqlserver_df, snowflake_df = load_both_templates()

    # Create copies of the dataframes
    custom_sqlserver_df = sqlserver_df.copy()
    custom_snowflake_df = snowflake_df.copy()

    # Add same metric name but with different templates
    metric_name = "same_metric_different_template"
    sqlserver_row = {
        "type": "int",
        "category": "numeric",
        "metric": metric_name,
        "template": 'SQLSERVER_SPECIFIC("{{ col_name }}")',
    }
    snowflake_row = {
        "type": "NUMBER",
        "category": "numeric",
        "metric": metric_name,
        "template": 'SNOWFLAKE_SPECIFIC("{{ col_name }}")',
    }

    custom_sqlserver_df = pd.concat(
        [custom_sqlserver_df, pd.DataFrame([sqlserver_row])], ignore_index=True
    )
    custom_snowflake_df = pd.concat(
        [custom_snowflake_df, pd.DataFrame([snowflake_row])], ignore_index=True
    )

    # Get the templates for the metric
    sqlserver_template = (
        custom_sqlserver_df[custom_sqlserver_df["metric"] == metric_name][
            ["metric", "template"]
        ]
        .iloc[0]
        .to_dict()
    )
    snowflake_template = (
        custom_snowflake_df[custom_snowflake_df["metric"] == metric_name][
            ["metric", "template"]
        ]
        .iloc[0]
        .to_dict()
    )

    # Compare using DeepDiff
    diff = DeepDiff(sqlserver_template, snowflake_template, ignore_order=True)

    # Verify the templates are different
    assert "values_changed" in diff
    assert "root['template']" in diff["values_changed"]
    assert (
        "SQLSERVER_SPECIFIC" in diff["values_changed"]["root['template']"]["old_value"]
    )
    assert (
        "SNOWFLAKE_SPECIFIC" in diff["values_changed"]["root['template']"]["new_value"]
    )
    # Verify metric name remains the same
    assert "metric" not in diff  # metric name should not be in diff since it's the same


def test_query_generation_with_missing_metric(mock_context):
    """Test query generation behavior when a metric is missing in one platform"""
    sqlserver_df, snowflake_df = load_both_templates()

    # Add a custom metric only to SQL Server
    custom_sqlserver_df = sqlserver_df.copy()
    custom_metric_row = {
        "type": "INT",
        "category": "numeric",
        "metric": "custom_metric_not_in_snowflake",
        "template": 'CUSTOM("{{ col_name }}")',
        "normalization": 'TO CHAR("{{ metric_query }}")',
    }
    custom_sqlserver_df = pd.concat(
        [custom_sqlserver_df, pd.DataFrame([custom_metric_row])], ignore_index=True
    )

    # Generate SQL Server query with custom metric
    sqlserver_query, sqlserver_cte, sqlserver_metrics = generate_sqlserver_cte(
        metrics_templates=custom_sqlserver_df,  # Use the modified dataframe
        col_name="test_column",
        col_type="int",
        fully_qualified_name="test_table",
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_context.sql_generator,
        exclude_metrics=False,
    )

    # Generate Snowflake query
    snowflake_query, snowflake_cte, snowflake_metrics = generate_snowflake_cte(
        metrics_templates=snowflake_df,
        col_name="test_column",
        col_type="NUMBER",  # Snowflake equivalent of int
        fully_qualified_name="test_table",
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_context.sql_generator,
        exclude_metrics=False,
    )

    # Verify the custom metric is included in SQL Server metrics but not in Snowflake
    assert "custom_metric_not_in_snowflake" in sqlserver_metrics
    assert "custom_metric_not_in_snowflake" not in snowflake_metrics

    # Verify both queries were generated (not None)
    assert sqlserver_query is not None
    assert snowflake_query is not None

    # Verify both CTEs follow the expected naming pattern
    assert sqlserver_cte == "test_column"
    assert snowflake_cte == "test_column"

    # Verify the custom metric appears in the SQL Server query but not in the Snowflake query
    assert 'CUSTOM("test_column")' in sqlserver_query
    assert 'CUSTOM("test_column")' not in snowflake_query
