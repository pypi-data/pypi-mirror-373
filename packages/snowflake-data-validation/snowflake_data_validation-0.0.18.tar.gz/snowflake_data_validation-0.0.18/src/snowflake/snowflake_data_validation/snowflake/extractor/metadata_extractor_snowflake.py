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

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)

# WIP check what needs to be generalized and what not in the template generator
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    Platform,
)

# WIP check what needs to be generalized and what not in the template generator
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class MetadataExtractorSnowflake(MetadataExtractorBase):

    """Implement methods to extract metadata from Snowflake database tables."""

    @log
    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the Snowflake metadata extractor.

        Args:
            connector (ConnectorBase): Database connector instance.
            query_generator (QueryGeneratorBase): Query generator instance.
            report_path (str): Optional path for output reports.

        """
        LOGGER.debug("Initializing MetadataExtractorSnowflake")
        super().__init__(
            platform=Platform.SNOWFLAKE,
            connector=connector,
            query_generator=query_generator,
            report_path=report_path,
        )
        LOGGER.debug("MetadataExtractorSnowflake initialized successfully")

    @log
    def extract_case_sensitive_columns(
        self, table_configuration: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        """Extract case sensitive column information from Snowflake.

        Args:
            table_configuration (TableConfiguration): Table configuration instance.
            context (Context): Context instance.

        Returns:
            pd.DataFrame: DataFrame containing case-sensitive columns information.

        Raises:
            Exception: If query execution fails.

        """
        LOGGER.info(
            "Extracting case-sensitive column information for: %s",
            table_configuration.fully_qualified_name,
        )

        database_name = table_configuration.target_database
        schema_name = table_configuration.target_schema
        table_name = table_configuration.target_name

        try:
            sql_query = context.sql_generator.get_case_sensitive_columns(
                database_name=database_name,
                schema_name=schema_name,
                table_name=table_name,
                platform=self.platform.value,
            )

            LOGGER.debug(
                "Generated query to extract case-sensitive columns: %s", sql_query
            )

            result = self.connector.execute_query(sql_query)

            if result is None or len(result) == 0:
                LOGGER.warning("No case-sensitive column information found")
                return pd.DataFrame(columns=["COLUMN_NAME", "IS_CASE_SENSITIVE"])

            result_df = pd.DataFrame(result)

            LOGGER.info(
                "Successfully extracted case-sensitive column information for: %s",
                table_configuration.fully_qualified_name,
            )

            return result_df

        except Exception as e:
            LOGGER.critical(
                "Failed to extract case-sensitive column information for %s: %s",
                table_configuration.fully_qualified_name,
                str(e),
            )
            raise

    def process_schema_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process schema query results into a DataFrame for Snowflake.

        Args:
            result: Query result list containing data rows.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with schema metadata.

        """
        df = pd.DataFrame(result)

        LOGGER.info(
            "Successfully extracted metrics metadata (%d rows)",
            len(df),
        )
        output_handler.handle_message(
            header="Snowflake metadata info:",
            dataframe=df,
            level=OutputMessageLevel.TARGET_RESULT,
        )
        return df

    def process_metrics_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process metrics query results into a DataFrame for Snowflake.

        Args:
            result: Query result list containing columns and data.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with metrics metadata.

        """
        df = pd.DataFrame(result)

        LOGGER.info(
            "Successfully extracted metrics metadata (%d rows)",
            len(df),
        )
        output_handler.handle_message(
            header="Snowflake metadata info:",
            dataframe=df,
            level=OutputMessageLevel.TARGET_RESULT,
        )
        return df

    @log
    def extract_md5_checksum(
        self, fully_qualified_name: str, context: Context
    ) -> pd.DataFrame:
        """Extract MD5 checksum for a specified table from a Snowflake database.

        Args:
            fully_qualified_name (str): Fully qualified table name in format 'database.schema.table'.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            pd.DataFrame: A DataFrame containing the MD5 checksum of the specified table.

        Raises:
            ValueError: If the fully qualified name is not in the correct format.
            DatabaseError: If there is an error executing the SQL query.

        """
        LOGGER.info("Extracting MD5 checksum for table: %s", fully_qualified_name)
        context.output_handler.handle_message(
            message=f"Extracting MD5 checksum for: {fully_qualified_name} on {Platform.SNOWFLAKE.value}",
            level=OutputMessageLevel.INFO,
        )

        # Create a TableConfiguration for the MD5 checksum query
        table_context = TableConfiguration(
            fully_qualified_name=fully_qualified_name,
            column_selection_list=[],
            use_column_selection_as_exclude_list=False,
            where_clause="",
            target_where_clause="",
            has_where_clause=False,
        )

        query = self.query_generator.generate_row_md5_query(table_context, context)
        LOGGER.debug("Generated MD5 checksum query for table: %s", fully_qualified_name)
        try:
            result = self.connector.execute_query(query)
        except Exception:
            error_message = f"[Snowflake] Row validation query failed for table: {table_context.fully_qualified_name}"
            LOGGER.critical(error_message)
            raise

        if not result:
            LOGGER.warning(
                "No MD5 checksum data found for table: %s", fully_qualified_name
            )
            context.output_handler.handle_message(
                message=f"No metadata found for table: {fully_qualified_name}",
                level=OutputMessageLevel.WARNING,
            )
            return pd.DataFrame()

        df = pd.DataFrame(result)
        LOGGER.info(
            "Successfully extracted MD5 checksum for table: %s", fully_qualified_name
        )
        context.output_handler.handle_message(
            header="Snowflake metadata info:",
            dataframe=df,
            level=OutputMessageLevel.TARGET_RESULT,
        )
        return df

    def process_table_column_metadata_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process table column metadata query results into a DataFrame for Snowflake.

        Args:
            result: List of data rows from the query result.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with table column metadata.

        """
        # Snowflake intentionally returns empty DataFrame for table column metadata
        LOGGER.debug(
            "Returning empty DataFrame for table column metadata (intentional)"
        )
        return pd.DataFrame()

    def create_table_chunks_md5(self, table_context: TableContext) -> None:

        statement = self.query_generator.generate_statement_table_chunks_md5(
            table_context=table_context
        )

        self.connector.execute_statement(statement)

    def compute_md5(self, table_context: TableContext, other_table_name: str) -> None:

        queries = self.query_generator.generate_compute_md5_query(
            table_context=table_context, other_table_name=other_table_name
        )

        for query in queries:
            self.connector.execute_query_no_return(query)

    def extract_chunks_md5(
        self,
        table_context: TableContext,
    ) -> pd.DataFrame:

        query = self.query_generator.generate_extract_chunks_md5_query(
            table_context=table_context
        )

        result = self.connector.execute_query(query)

        df = pd.DataFrame(result)
        return df

    def extract_md5_rows_chunk(
        self, chunk_id: str, table_context: TableContext
    ) -> pd.DataFrame:

        query = self.query_generator.generate_extract_md5_rows_chunk_query(
            chunk_id=chunk_id, table_context=table_context
        )

        result = self.connector.execute_query(query)

        df = pd.DataFrame(result)
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

        result = self.connector.execute_query(query)

        df = pd.DataFrame(result)
        return df
