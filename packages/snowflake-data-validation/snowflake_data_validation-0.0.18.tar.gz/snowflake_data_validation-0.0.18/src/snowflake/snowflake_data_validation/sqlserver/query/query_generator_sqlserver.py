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

from typing import Union

from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.sqlserver.extractor.sqlserver_cte_generator import (
    generate_cte_query,
    generate_outer_query,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COL_NAME_NO_QUOTES_PLACEHOLDER,
    Platform,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class QueryGeneratorSqlServer(QueryGeneratorBase):

    """SQL Server-specific implementation of query generator."""

    def __init__(self):
        """Initialize the SQL Server query generator."""
        super().__init__(platform=Platform.SQLSERVER)

    def cte_query_generator(
        self,
        metrics_templates,
        col_name: str,
        col_type: str,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        sql_generator,
        exclude_metrics: bool,
    ) -> Union[tuple[str, str, list[str]], tuple[None, None, None]]:
        """Generate a CTE query for a specific column using SQL Server CTE generator.

        Args:
            metrics_templates: DataFrame containing metrics templates.
            col_name (str): Column name.
            col_type (str): Column data type.
            fully_qualified_name (str): Fully qualified table name.
            where_clause (str): WHERE clause.
            has_where_clause (bool): Whether WHERE clause is present.
            sql_generator: SQL template generator instance.
            exclude_metrics (bool): If True, excludes certain metrics from the CTE query.

        Returns:
            Tuple containing CTE query, CTE name, and metrics list, or (None, None, None) if no query generated.

        """
        return generate_cte_query(
            metrics_templates=metrics_templates,
            col_name=col_name,
            col_type=col_type,
            fully_qualified_name=fully_qualified_name,
            where_clause=where_clause,
            has_where_clause=has_where_clause,
            sql_generator=sql_generator,
            exclude_metrics=exclude_metrics,
        )

    def outer_query_generator(self, cte_names, metrics) -> str:
        """Generate an outer query combining CTEs using SQL Server outer query generator.

        Args:
            cte_names: List of CTE names.
            metrics: List of metrics for each CTE.

        Returns:
            str: Generated outer query.

        """
        return generate_outer_query(cte_names, metrics)

    def _generate_compute_md5_chunk_query(
        self, table_context: TableContext, chunk_id: str, fetch: int, offset: int
    ) -> Union[str, list[str]]:

        datatypes_normalization_templates = (
            table_context.templates_loader_manager.datatypes_normalization_templates
        )
        datatypes_normalization_renderer_templates = {}
        for column in table_context.columns_to_validate:
            normalization_template = datatypes_normalization_templates[column.data_type]
            normalization_template_rendered = normalization_template.replace(
                COL_NAME_NO_QUOTES_PLACEHOLDER, column.name
            )
            datatypes_normalization_renderer_templates[
                column.name
            ] = normalization_template_rendered

        query = table_context.sql_generator.generate_compute_md5_query(
            platform=self.platform.value,
            chunk_id=chunk_id,
            column_names_separate_by_comma=table_context.join_column_names_with_commas(),
            index_column_collection=table_context.index_column_collection,
            column_collection=table_context.columns_to_validate,
            datatypes_normalization_renderer_templates=datatypes_normalization_renderer_templates,
            fully_qualified_name=table_context.fully_qualified_name,
            has_where_clause=table_context.has_where_clause,
            where_clause=table_context.where_clause,
            source_table_name=table_context.table_name,
            normalized_fully_qualified_name=table_context.normalized_fully_qualified_name,
            offset=offset,
            fetch=fetch,
            database_name=table_context.database_name,
            schema_name=table_context.schema_name,
            table_id=table_context.id,
        )

        return query

    def generate_statement_table_chunks_md5(self, table_context: TableContext) -> str:
        """Generate the DDL statement to create a table for storing MD5 checksums of data chunks.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to create a table for storing MD5 checksums of data chunks.

        """
        statement = table_context.sql_generator.generate_statement_table_chunks_md5(
            normalized_fully_qualified_name=table_context.normalized_fully_qualified_name,
            platform=table_context.platform.value,
            database_name=table_context.database_name,
            schema_name=table_context.schema_name,
            table_id=table_context.id,
        )

        return statement

    def generate_extract_chunks_md5_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract MD5 for all chunks of a table.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract MD5 for all chunks of a table.

        """
        query = table_context.sql_generator.generate_extract_chunks_md5_query(
            platform=table_context.platform.value,
            normalized_fully_qualified_name=table_context.normalized_fully_qualified_name,
            database_name=table_context.database_name,
            schema_name=table_context.schema_name,
            table_id=table_context.id,
        )

        return query

    def generate_extract_md5_rows_chunk_query(
        self, chunk_id: str, table_context: TableContext
    ) -> str:
        """Generate the SQL query to extract the MD5 rows for a specific chunk of a table.

        Args:
            chunk_id (str): The unique identifier for the chunk.
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract the MD5 rows for the specified chunk.

        """
        query = table_context.sql_generator.generate_extract_md5_rows_chunk_query(
            platform=Platform.SQLSERVER.value,
            chunk_id=chunk_id,
            index_column_collection=table_context.index_column_collection,
            database_name=table_context.database_name,
            schema_name=table_context.schema_name,
            table_id=table_context.id,
        )

        return query
