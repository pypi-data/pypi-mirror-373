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

from typing import Optional

from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COL_NAME_NO_QUOTES_PLACEHOLDER,
    METRIC_COLUMN_KEY,
    METRIC_QUERY_PLACEHOLDER,
    METRICS_TO_EXCLUDE,
    NORMALIZATION_COLUMN_KEY,
    TEMPLATE_COLUMN_KEY,
    TYPE_COLUMN_KEY,
)


LOGGER = logging.getLogger(__name__)


def generate_cte_query(
    metrics_templates,
    col_name: str,
    col_type: str,
    fully_qualified_name: str,
    where_clause: str,
    has_where_clause: bool,
    sql_generator: SQLQueriesTemplateGenerator,
    exclude_metrics: bool,
) -> tuple[Optional[str], Optional[str], Optional[list[str]]]:
    """Generate a CTE-based SELECT query for Teradata based on the provided data.

    Args:
        metrics_templates (pd.DataFrame): DataFrame containing metrics templates to be applied.
        col_name (str): The name of the column for which the query is being generated.
        col_type (str): The type of the column (e.g., "int", "varchar") used to filter templates.
        fully_qualified_name (str): The fully qualified name of the table.
        where_clause (str): A WHERE clause to filter the data.
        has_where_clause (bool): A boolean indicating whether the WHERE clause is present.
        sql_generator (SQLQueriesTemplateGenerator): An instance of SQLQueriesTemplateGenerator
                                                    used to render the SQL templates.
        exclude_metrics (bool): If True, excludes certain metrics from the CTE query.

    Returns:
        tuple: A tuple containing:
            - query (str or None): The rendered SQL query as a string, or None if no templates
                                  are found for the given column type.
            - col_name (str or None): The column name, or None if no templates are found.
            - metrics (list or None): A list of metric names used in the query, or None if no templates
                                    are found.

    Notes:
        - The function uses Teradata's CTE syntax to generate the query
        - Each metric is calculated in a single CTE and then selected in the final query
        - Error handling includes logging for missing templates and invalid column types

    """
    try:
        template = sql_generator.env.get_template(
            "teradata_columns_cte_template.sql.j2"
        )

        type_category = f"{col_name}"
        metrics_templates_df = metrics_templates[
            (metrics_templates[TYPE_COLUMN_KEY] == col_type.upper())
        ]

        # Build metrics dictionary
        metrics: dict[str, str] = {}
        for _, row in metrics_templates_df.iterrows():
            metric_name = row[METRIC_COLUMN_KEY]
            if exclude_metrics and metric_name in METRICS_TO_EXCLUDE:
                continue

            metric_query = row[TEMPLATE_COLUMN_KEY].replace(
                COL_NAME_NO_QUOTES_PLACEHOLDER, col_name
            )
            metric_query_normalized = row[NORMALIZATION_COLUMN_KEY].replace(
                METRIC_QUERY_PLACEHOLDER, metric_query
            )
            metrics[metric_name] = metric_query_normalized

        if not metrics:
            LOGGER.warning(
                "No metrics templates found for column type %s in table %s.",
                col_type,
                fully_qualified_name,
            )
            return None, None, None

        # Render the template with the metrics
        query = template.render(
            type_category=type_category,
            metrics=metrics,
            table_name=fully_qualified_name,
            where_clause=where_clause,
            has_where_clause=has_where_clause,
        )

        LOGGER.debug(
            "Generated Teradata CTE query for column %s of type %s",
            col_name,
            col_type,
        )
        return query.strip(), col_name, list(metrics.keys())

    except Exception as e:
        LOGGER.error(
            "Failed to generate Teradata CTE query for column %s: %s",
            col_name,
            str(e),
        )
        raise


def generate_outer_query(cte_names: list[str], metrics: list[list[str]]) -> str:
    """Generate a single SELECT query that combines all metrics.

    Args:
        cte_names (list): List of column names
        metrics (list): List of available metrics for each column

    Returns:
        str: The combined SELECT query string

    Notes:
        - The function creates a UNION ALL query combining results from all columns
        - All metrics are cast to VARCHAR for consistent output
        - NULL values are used for metrics not available for specific columns

    """
    try:
        all_metrics = set()
        for metric_list in metrics:
            all_metrics.update(metric_list)

        union_queries = []

        for cte_name, available_metrics in zip(cte_names, metrics):
            metric_clauses = []
            for metric in all_metrics:
                if metric in available_metrics:
                    metric_clauses.append(
                        f'TRIM(CAST("{metric}" AS VARCHAR(25))) AS "{metric}"'
                    )
                else:
                    metric_clauses.append(f'CAST(NULL AS VARCHAR(25)) AS "{metric}"')

            select_query = f"""SELECT
    CAST('{cte_name}' AS VARCHAR(30)) AS COLUMN_VALIDATED,
    {', '.join(metric_clauses)}
FROM {cte_name}"""

            union_queries.append(select_query)

        outer_query = "\n\nUNION ALL\n\n".join(union_queries)
        return outer_query

    except Exception as e:
        LOGGER.error("Failed to generate outer query: %s", str(e))
        raise
