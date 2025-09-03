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

import pandas as pd

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import ROW_COUNT_KEY, Platform
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.helpers.helper_dataframe import (
    HelperDataFrame,
)
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class MetadataExtractorRedshift(MetadataExtractorBase):

    """Implement methods to extract metadata from Redshift database tables."""

    @log
    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the Redshift metadata extractor with a Redshift connector.

        Args:
            connector (ConnectorBase): Redshift database connector instance.
            query_generator (QueryGeneratorBase): Query generator instance for generating SQL queries.
            report_path (str): Path to save the metadata extraction report.

        """
        LOGGER.debug("Initializing MetadataExtractorRedshift")
        super().__init__(
            platform=Platform.REDSHIFT,
            query_generator=query_generator,
            connector=connector,
            report_path=report_path,
        )
        self.helper_dataframe = HelperDataFrame()
        LOGGER.debug("MetadataExtractorRedshift initialized successfully")

    def process_schema_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process schema query results into a DataFrame for Redshift.

        Args:
            result: Query result containing (columns_names, data_rows).
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with schema metadata.

        """
        columns_names, metadata_info = result
        return self.helper_dataframe.process_query_result_to_dataframe(
            columns_names=list(columns_names),
            data_rows=list(metadata_info),
            output_handler=output_handler,
            header="Redshift metadata info:",
            output_level=OutputMessageLevel.SOURCE_RESULT,
            apply_column_validated_uppercase=True,
            sort_and_reset_index=True,
        )

    def process_metrics_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process metrics query results into a DataFrame for Redshift.

        Args:
            result: Query result list containing columns and data.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with metrics metadata.

        """
        result_columns, result_data = result
        return self.helper_dataframe.process_query_result_to_dataframe(
            columns_names=list(result_columns),
            data_rows=list(result_data),
            output_handler=output_handler,
            header="Redshift column metrics info:",
            output_level=OutputMessageLevel.SOURCE_RESULT,
            apply_column_validated_uppercase=True,
            sort_and_reset_index=True,
        )

    def process_table_column_metadata_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process table column metadata query results into a DataFrame for Redshift.

        Args:
            result: List of data rows from the query result.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with table column metadata.

        """
        result_columns, result_data = result
        return self.helper_dataframe.process_query_result_to_dataframe(
            columns_names=list(result_columns),
            data_rows=list(result_data),
            output_handler=output_handler,
            header=None,
            output_level=None,
            apply_column_validated_uppercase=False,
            sort_and_reset_index=False,
        )

    def create_table_chunks_md5(self, table_context: TableContext) -> None:
        """Create table chunks for MD5 calculation.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        """
        statement = self.query_generator.generate_statement_table_chunks_md5(
            table_context=table_context
        )

        self.connector.execute_statement(statement)

    def compute_md5(self, table_context: TableContext, other_table_name: str) -> None:
        """Compute MD5 for a specified table.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            other_table_name (str): the name of the equivalent table in other platform.

        """
        queries = self.query_generator.generate_compute_md5_query(
            table_context=table_context, other_table_name=other_table_name
        )

        for query in queries:
            self.connector.execute_query_no_return(query)

    def extract_chunks_md5(
        self,
        table_context: TableContext,
    ) -> pd.DataFrame:
        """Extract MD5 for all chunks of a specified table.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            pd.DataFrame: A DataFrame containing the MD5 checksums for each chunk of the specified table.

        """
        query = self.query_generator.generate_extract_chunks_md5_query(
            table_context=table_context
        )
        result_columns, result = self.connector.execute_query(query)
        df = self.helper_dataframe.process_query_result_to_dataframe(
            columns_names=list(result_columns),
            data_rows=list(result),
            output_handler=None,
            header=None,
            output_level=None,
            apply_column_validated_uppercase=False,
            sort_and_reset_index=False,
        )
        return df

    def extract_md5_rows_chunk(
        self, chunk_id: str, table_context: TableContext
    ) -> pd.DataFrame:
        """Extract MD5 rows for a specific chunk of a table.

        Args:
            chunk_id (str): The ID of the chunk for which to extract the MD5.
            table_context (TableContext): table column metadata containing column definitions and types.

        Returns:
            pd.DataFrame: A DataFrame containing the MD5 rows for the specified chunk.

        """
        query = self.query_generator.generate_extract_md5_rows_chunk_query(
            chunk_id=chunk_id, table_context=table_context
        )

        result_columns, result = self.connector.execute_query(query)

        df = self.helper_dataframe.process_query_result_to_dataframe(
            columns_names=list(result_columns),
            data_rows=list(result),
            output_handler=None,
            header=None,
            output_level=None,
            apply_column_validated_uppercase=False,
            sort_and_reset_index=False,
        )

        return df

    def extract_table_row_count(
        self,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        platform: Platform,
        context: Context,
    ) -> pd.DataFrame:
        query = self.query_generator.generate_table_row_count_query(
            fully_qualified_name=fully_qualified_name,
            where_clause=where_clause,
            has_where_clause=has_where_clause,
            platform=platform,
            context=context,
        )

        _ , data = self.connector.execute_query(query)

        df = pd.DataFrame(data)
        df.columns = [ROW_COUNT_KEY]
        return df
