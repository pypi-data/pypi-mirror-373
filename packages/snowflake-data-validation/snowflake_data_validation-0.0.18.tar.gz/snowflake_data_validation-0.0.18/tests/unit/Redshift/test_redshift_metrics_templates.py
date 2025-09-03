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
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import jinja2
from typing import Set
from deepdiff import DeepDiff
from snowflake.snowflake_data_validation.redshift.extractor.redshift_cte_generator import (
    generate_cte_query as generate_redshift_cte,
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


def load_redshift_and_snowflake_templates():
    """Helper function to load both Redshift and Snowflake templates"""
    base_path = (
        Path(__file__).parent.parent.parent.parent
        / "src/snowflake/snowflake_data_validation"
    )

    redshift_datatypes_normalization_path = (
        base_path
        / "redshift/extractor/templates/redshift_datatypes_normalization_templates.yaml"
    )
    snowflake_datatypes_normalization_path = (
        base_path
        / "snowflake/extractor/templates/snowflake_datatypes_normalization_templates.yaml"
    )

    redshift_datatypes_normalization_templates = (
        Helper.load_datatypes_normalization_templates_from_yaml(
            redshift_datatypes_normalization_path
        )
    )
    snowflake_datatypes_normalization_templates = (
        Helper.load_datatypes_normalization_templates_from_yaml(
            snowflake_datatypes_normalization_path
        )
    )

    redshift_path = (
        base_path
        / "redshift/extractor/templates/redshift_column_metrics_templates.yaml"
    )
    snowflake_path = (
        base_path
        / "snowflake/extractor/templates/snowflake_column_metrics_templates.yaml"
    )

    redshift_df = Helper.load_metrics_templates_from_yaml(
        redshift_path, redshift_datatypes_normalization_templates
    )
    snowflake_df = Helper.load_metrics_templates_from_yaml(
        snowflake_path, snowflake_datatypes_normalization_templates
    )

    return redshift_df, snowflake_df


def test_redshift_type_mappings():
    """Test that Redshift types map correctly to Snowflake types for metrics"""
    redshift_df, snowflake_df = load_redshift_and_snowflake_templates()

    type_mappings = {
        "SMALLINT": "NUMBER",
        "INT2": "NUMBER",
        "INT": "NUMBER",
        "INTEGER": "NUMBER",
        "INT4": "NUMBER",
        "BIGINT": "NUMBER",
        "INT8": "NUMBER",
        "DECIMAL": "NUMBER",
        "NUMERIC": "NUMBER",
        "REAL": "FLOAT",
        "FLOAT4": "FLOAT",
        "FLOAT": "FLOAT",
        "DOUBLE PRECISION": "FLOAT",
        "FLOAT8": "FLOAT",
        "VARCHAR": "VARCHAR",
        "CHARACTER VARYING": "VARCHAR",
        "CHAR": "VARCHAR",
        "CHARACTER": "VARCHAR",
        "TEXT": "VARCHAR",
        "BOOLEAN": "BOOLEAN",
        "BOOL": "BOOLEAN",
        "DATE": "DATE",
        "TIMESTAMP": "TIMESTAMP_NTZ",
        "TIMESTAMP WITHOUT TIME ZONE": "TIMESTAMP_NTZ",
        "TIMESTAMPTZ": "TIMESTAMP_TZ",
        "TIMESTAMP WITH TIME ZONE": "TIMESTAMP_TZ",
        "TIME": "TIME",
        "TIME WITHOUT TIME ZONE": "TIME",
        "TIMETZ": "TIME",
        "TIME WITH TIME ZONE": "TIME",
        "SUPER": "VARIANT",
    }

    for redshift_type, snowflake_type in type_mappings.items():
        redshift_metrics = set(
            redshift_df[redshift_df["type"] == redshift_type]["metric"]
        )

        snowflake_metrics = set(
            snowflake_df[snowflake_df["type"] == snowflake_type]["metric"]
        )

        if len(redshift_metrics) > 0 and len(snowflake_metrics) > 0:
            compatible_metrics = redshift_metrics.intersection(snowflake_metrics)
            assert (
                len(compatible_metrics) > 0
            ), f"Type mapping {redshift_type} -> {snowflake_type} has no compatible metrics"


@pytest.fixture
def mock_redshift_context(tmp_path):
    """Create a mock context for Redshift testing using a temporary directory

    Args:
        tmp_path: pytest fixture that provides a temporary directory unique to each test function
    """
    temp_dir = None
    context = None
    output_handler = None

    try:
        output_handler = MagicMock(spec=OutputHandlerBase)
        output_handler.console_output_enabled = True

        configuration = ConfigurationModel(
            source_platform="Redshift",
            target_platform="Snowflake",
            output_directory_path="",
        )

        base_path = (
            Path(__file__).parent.parent.parent.parent
            / "src/snowflake/snowflake_data_validation"
        )
        redshift_templates = str(base_path / "redshift/extractor/templates")
        snowflake_templates = str(base_path / "snowflake/extractor/templates")

        temp_dir = tempfile.mkdtemp(prefix="test_redshift_metrics_")
        report_path = str(Path(temp_dir) / "test_reports")
        os.makedirs(report_path, exist_ok=True)

        sql_generator = SQLQueriesTemplateGenerator(redshift_templates)
        sql_generator.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader([redshift_templates, snowflake_templates])
        )

        source_templates = TemplatesLoaderManager(
            Path(redshift_templates), Platform.REDSHIFT
        )
        target_templates = TemplatesLoaderManager(
            Path(snowflake_templates), Platform.SNOWFLAKE
        )

        context = Context(
            configuration=configuration,
            report_path=report_path,
            templates_dir_path=redshift_templates,
            source_platform=Platform.REDSHIFT,
            target_platform=Platform.SNOWFLAKE,
            custom_output_handler=output_handler,
            run_id="test_redshift_run",
            run_start_time="20250101T000000",
            source_templates=source_templates,
            target_templates=target_templates,
            execution_mode=ExecutionMode.SYNC_VALIDATION,
        )

        context.sql_generator = sql_generator

        yield context

    finally:
        if context is not None:
            if hasattr(context, "close"):
                context.close()

        if output_handler is not None:
            if hasattr(output_handler, "close"):
                output_handler.close()

        if temp_dir is not None and os.path.exists(temp_dir):
            try:
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for name in files:
                        try:
                            os.chmod(os.path.join(root, name), 0o777)
                            os.unlink(os.path.join(root, name))
                        except (OSError, PermissionError):
                            pass
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except (OSError, PermissionError):
                            pass
                os.rmdir(temp_dir)
            except (OSError, PermissionError):
                pass


def verify_redshift_column_query_generation(
    mock_context,
    redshift_type: str,
    snowflake_type: str,
    col_name: str,
    table_name: str,
    expected_metrics: Set[str],
):
    """Helper function to verify query generation for a specific column type in both Redshift and Snowflake

    Args:
        mock_context: The mock context fixture
        redshift_type: Redshift data type
        snowflake_type: Snowflake data type
        col_name: Name of the column to test
        table_name: Name of the table containing the column
        expected_metrics: Set of metric names expected for this data type
    """
    redshift_df, snowflake_df = load_redshift_and_snowflake_templates()

    redshift_query, redshift_cte, redshift_metrics = generate_redshift_cte(
        metrics_templates=redshift_df,
        col_name=col_name,
        col_type=redshift_type,
        fully_qualified_name=table_name,
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_context.sql_generator,
        exclude_metrics=False,
    )

    snowflake_query, snowflake_cte, snowflake_metrics = generate_snowflake_cte(
        metrics_templates=snowflake_df,
        col_name=col_name,
        col_type=snowflake_type,
        fully_qualified_name=table_name,
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_context.sql_generator,
        exclude_metrics=False,
    )

    assert redshift_query is not None, "Redshift query should not be None"
    assert snowflake_query is not None, "Snowflake query should not be None"

    assert redshift_cte == f"{col_name}"
    assert snowflake_cte == f"{col_name}"

    assert set(redshift_metrics) == expected_metrics
    assert set(snowflake_metrics) == expected_metrics

    assert "SELECT" in redshift_query
    assert f"FROM {table_name}" in redshift_query
    assert "SELECT" in snowflake_query
    assert f"FROM {table_name}" in snowflake_query


def test_redshift_integer_column_query_generation(mock_redshift_context):
    """Test query generation for an integer column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="INTEGER",
        snowflake_type="NUMBER",
        col_name="customer_id",
        table_name="sales.customers",
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


def test_redshift_bigint_column_query_generation(mock_redshift_context):
    """Test query generation for a BIGINT column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="BIGINT",
        snowflake_type="NUMBER",
        col_name="transaction_id",
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


def test_redshift_varchar_column_query_generation(mock_redshift_context):
    """Test query generation for a VARCHAR column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="VARCHAR",
        snowflake_type="VARCHAR",
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


def test_redshift_decimal_column_query_generation(mock_redshift_context):
    """Test query generation for a DECIMAL column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="DECIMAL",
        snowflake_type="NUMBER",
        col_name="price",
        table_name="products.catalog",
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


def test_redshift_double_precision_column_query_generation(mock_redshift_context):
    """Test query generation for a DOUBLE PRECISION column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="DOUBLE PRECISION",
        snowflake_type="FLOAT",
        col_name="latitude",
        table_name="locations.coordinates",
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


def test_redshift_date_column_query_generation(mock_redshift_context):
    """Test query generation for a DATE column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="DATE",
        snowflake_type="DATE",
        col_name="created_date",
        table_name="sales.orders",
        expected_metrics={"min", "max", "count_null"},
    )


def test_redshift_timestamp_column_query_generation(mock_redshift_context):
    """Test query generation for a TIMESTAMP column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="TIMESTAMP",
        snowflake_type="TIMESTAMP_NTZ",
        col_name="updated_at",
        table_name="sales.orders",
        expected_metrics={"min", "max", "count_null"},
    )


def test_redshift_boolean_column_query_generation(mock_redshift_context):
    """Test query generation for a BOOLEAN column in both Redshift and Snowflake"""
    verify_redshift_column_query_generation(
        mock_context=mock_redshift_context,
        redshift_type="BOOLEAN",
        snowflake_type="BOOLEAN",
        col_name="is_active",
        table_name="users.accounts",
        expected_metrics={"count_true", "count_false", "count_null"},
    )


def test_redshift_metrics_not_found_in_snowflake():
    """Test behavior when Redshift metrics are not found in Snowflake"""
    redshift_df, snowflake_df = load_redshift_and_snowflake_templates()

    custom_redshift_df = redshift_df.copy()
    custom_metric_row = {
        "type": "INTEGER",
        "category": "numeric",
        "metric": "custom_redshift_metric_not_in_snowflake",
        "metric_query": 'CUSTOM_REDSHIFT_FUNCTION("{{ col_name }}")',
        "metric_return_datatype": "BIGINT",
        "normalization": 'CAST("{{ metric_query }}" AS VARCHAR)',
    }
    custom_redshift_df = pd.concat(
        [custom_redshift_df, pd.DataFrame([custom_metric_row])], ignore_index=True
    )

    redshift_metrics = set(custom_redshift_df["metric"])
    snowflake_metrics = set(snowflake_df["metric"])

    diff = DeepDiff(snowflake_metrics, redshift_metrics, ignore_order=True)

    assert any(
        "custom_redshift_metric_not_in_snowflake" in item
        for item in diff.get("set_item_added", [])
    )
    assert "set_item_removed" not in diff


def test_redshift_metrics_not_found_in_redshift():
    """Test behavior when Snowflake metrics are not found in Redshift"""
    redshift_df, snowflake_df = load_redshift_and_snowflake_templates()

    custom_snowflake_df = snowflake_df.copy()
    custom_metric_row = {
        "type": "NUMBER",
        "category": "numeric",
        "metric": "custom_snowflake_metric_not_in_redshift",
        "metric_query": 'CUSTOM_SNOWFLAKE_FUNCTION("{{ col_name }}")',
        "metric_return_datatype": "NUMBER",
        "normalization": 'TO_CHAR("{{ metric_query }}")',
    }
    custom_snowflake_df = pd.concat(
        [custom_snowflake_df, pd.DataFrame([custom_metric_row])], ignore_index=True
    )

    redshift_metrics = set(redshift_df["metric"])
    snowflake_metrics = set(custom_snowflake_df["metric"])

    diff = DeepDiff(redshift_metrics, snowflake_metrics, ignore_order=True)

    assert any(
        "custom_snowflake_metric_not_in_redshift" in item
        for item in diff.get("set_item_added", [])
    )
    assert "set_item_removed" not in diff


def test_redshift_incompatible_metric_templates():
    """Test behavior when metric templates are incompatible between Redshift and Snowflake"""
    redshift_df, snowflake_df = load_redshift_and_snowflake_templates()

    custom_redshift_df = redshift_df.copy()
    custom_snowflake_df = snowflake_df.copy()

    metric_name = "same_metric_different_template"
    redshift_row = {
        "type": "INTEGER",
        "category": "numeric",
        "metric": metric_name,
        "metric_query": 'REDSHIFT_SPECIFIC("{{ col_name }}")',
        "metric_return_datatype": "BIGINT",
        "normalization": 'CAST("{{ metric_query }}" AS VARCHAR)',
    }
    snowflake_row = {
        "type": "NUMBER",
        "category": "numeric",
        "metric": metric_name,
        "metric_query": 'SNOWFLAKE_SPECIFIC("{{ col_name }}")',
        "metric_return_datatype": "NUMBER",
        "normalization": 'TO_CHAR("{{ metric_query }}")',
    }

    custom_redshift_df = pd.concat(
        [custom_redshift_df, pd.DataFrame([redshift_row])], ignore_index=True
    )
    custom_snowflake_df = pd.concat(
        [custom_snowflake_df, pd.DataFrame([snowflake_row])], ignore_index=True
    )

    redshift_template = (
        custom_redshift_df[custom_redshift_df["metric"] == metric_name][
            ["metric", "metric_query"]
        ]
        .iloc[0]
        .to_dict()
    )
    snowflake_template = (
        custom_snowflake_df[custom_snowflake_df["metric"] == metric_name][
            ["metric", "metric_query"]
        ]
        .iloc[0]
        .to_dict()
    )

    diff = DeepDiff(redshift_template, snowflake_template, ignore_order=True)

    assert "values_changed" in diff
    assert "root['metric_query']" in diff["values_changed"]
    assert (
        "REDSHIFT_SPECIFIC"
        in diff["values_changed"]["root['metric_query']"]["old_value"]
    )
    assert (
        "SNOWFLAKE_SPECIFIC"
        in diff["values_changed"]["root['metric_query']"]["new_value"]
    )
    assert "metric" not in diff


def test_redshift_query_generation_with_missing_metric(mock_redshift_context):
    """Test query generation behavior when a metric is missing in one platform"""
    redshift_df, snowflake_df = load_redshift_and_snowflake_templates()

    custom_redshift_df = redshift_df.copy()
    custom_metric_row = {
        "type": "INTEGER",
        "metric": "missing_metric",
        "template": 'SOME_AGG_FUNCTION(CAST("{{ col_name }}" AS DOUBLE PRECISION))',
        "normalization": 'CAST("{{ metric_query }}" AS VARCHAR)',
    }
    custom_redshift_df = pd.concat(
        [custom_redshift_df, pd.DataFrame([custom_metric_row])], ignore_index=True
    )

    redshift_query, redshift_cte, redshift_metrics = generate_redshift_cte(
        metrics_templates=custom_redshift_df,
        col_name="test_column",
        col_type="INTEGER",
        fully_qualified_name="test_table",
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_redshift_context.sql_generator,
        exclude_metrics=False,
    )

    snowflake_query, snowflake_cte, snowflake_metrics = generate_snowflake_cte(
        metrics_templates=snowflake_df,
        col_name="test_column",
        col_type="NUMBER",
        fully_qualified_name="test_table",
        where_clause="",
        has_where_clause=False,
        sql_generator=mock_redshift_context.sql_generator,
        exclude_metrics=False,
    )

    assert "missing_metric" in redshift_metrics
    assert "missing_metric" not in snowflake_metrics

    assert redshift_query is not None
    assert snowflake_query is not None

    assert redshift_cte == "test_column"
    assert snowflake_cte == "test_column"

    assert (
        'SOME_AGG_FUNCTION(CAST("test_column" AS DOUBLE PRECISION))' in redshift_query
    )
    assert (
        'SOME_AGG_FUNCTION(CAST("test_column" AS DOUBLE PRECISION))'
        not in snowflake_query
    )


def test_redshift_query_generation_with_where_clause(mock_redshift_context):
    """Test Redshift query generation with WHERE clause"""
    redshift_df, _ = load_redshift_and_snowflake_templates()

    query, cte_name, metrics = generate_redshift_cte(
        metrics_templates=redshift_df,
        col_name="amount",
        col_type="DECIMAL",
        fully_qualified_name="sales.transactions",
        where_clause="status = 'completed'",
        has_where_clause=True,
        sql_generator=mock_redshift_context.sql_generator,
        exclude_metrics=False,
    )

    assert query is not None, "Query with WHERE clause should not be None"
    assert (
        "WHERE status = 'completed'" in query
    ), "Query should contain the WHERE clause"
    assert cte_name == "amount", "CTE name should match column name"
    assert len(metrics) > 0, "Should have metrics for DECIMAL type"


def test_redshift_template_file_existence():
    """Test that all required Redshift template files exist"""
    base_path = (
        Path(__file__).parent.parent.parent.parent
        / "src/snowflake/snowflake_data_validation/redshift/extractor/templates"
    )

    required_files = [
        "redshift_column_metrics_templates.yaml",
        "redshift_datatypes_normalization_templates.yaml",
        "redshift_to_snowflake_datatypes_mapping_template.yaml",
        "redshift_columns_cte_template.sql.j2",
        "redshift_get_columns_metadata.sql.j2",
        "redshift_table_metadata_query.sql.j2",
        "redshift_row_count_query.sql.j2",
    ]

    for file_name in required_files:
        file_path = base_path / file_name
        assert (
            file_path.exists()
        ), f"Required Redshift template file {file_name} should exist"
        assert (
            file_path.stat().st_size > 0
        ), f"Template file {file_name} should not be empty"
