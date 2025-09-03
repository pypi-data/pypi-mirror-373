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

from abc import ABC, abstractmethod

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    ERROR_MESSAGE_TEMPLATE,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class MetadataExtractorBase(ABC):

    """Provide interface for extracting metadata from various database sources.

    This class gets SQL queries from QueryGenerator and executes them to return DataFrames.
    """

    @log
    def __init__(
        self,
        platform: Platform,
        query_generator: QueryGeneratorBase,
        connector: ConnectorBase,
        report_path: str = "",
    ):
        """Initialize the metadata extractor with a database connector and query generator.

        Args:
            platform (Platform): The platform enum value.
            query_generator (QueryGeneratorBase): Query generator instance.
            connector (ConnectorBase): Database connector instance.
            report_path: Optional path for output reports.

        """
        LOGGER.debug("Initializing MetadataExtractorBase")
        self.platform = platform
        self.query_generator = query_generator
        self.connector = connector
        self.report_path = report_path
        self.columns_metrics = {}
        LOGGER.debug(
            "MetadataExtractorBase initialized with connector and query generator"
        )

    @log
    def extract_schema_metadata(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
    ) -> pd.DataFrame:
        """Extract table-level metadata for the specified table.

        This template method provides the common workflow for extracting schema metadata.
        Platform-specific implementations override the hook methods.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            output_handler (OutputHandlerBase): Output handler for logging and reporting.

        Returns:
            pd.DataFrame: A DataFrame containing table metadata including row count, column count, etc.

        """
        LOGGER.info(
            "Extracting schema metadata for table: %s",
            table_context.fully_qualified_name,
        )

        sql_query = self.query_generator.generate_schema_query(table_context)

        try:
            result = self.connector.execute_query(sql_query)
        except Exception:
            error_message = self._get_error_message(
                "Schema validation query failed", table_context.fully_qualified_name
            )
            LOGGER.critical(error_message)
            raise

        if not result:
            output_handler.handle_message(
                message=f"No metadata found for table: {table_context.fully_qualified_name}",
                level=OutputMessageLevel.WARNING,
            )
            return pd.DataFrame()

        return self.process_schema_query_result(result, output_handler)

    @log
    def extract_metrics_metadata(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
    ) -> pd.DataFrame:
        """Extract column-level metadata for the specified columns in a table.

        This template method provides the common workflow for extracting metrics metadata.
        Platform-specific implementations override the hook methods.

        Args:
            table_context (TableContext): Configuration object containing table properties and columns.
            output_handler (OutputHandlerBase): Output handler for logging and reporting.

        Returns:
            pd.DataFrame: A DataFrame containing column metadata including:
                          - data types
                          - nullability
                          - descriptive statistics (min, max, avg, etc.)
                          - distinct values count
                          - other column-specific attributes

        Raises:
            ValueError: If the table or specified columns don't exist.

        """
        LOGGER.info(
            "Extracting metrics metadata for table: %s",
            table_context.fully_qualified_name,
        )

        query = self.query_generator.generate_metrics_query(
            table_context=table_context,
            connector=self.connector,
        )

        try:
            result = self.connector.execute_query(query)
        except Exception:
            error_message = self._get_error_message(
                "Metrics validation query failed", table_context.fully_qualified_name
            )
            LOGGER.critical(error_message)
            raise

        if not result:
            LOGGER.warning(
                "No metrics metadata found for table: %s",
                table_context.fully_qualified_name,
            )
            output_handler.handle_message(
                message=f"No metadata found for table: {table_context.fully_qualified_name}",
                level=OutputMessageLevel.WARNING,
            )
            return pd.DataFrame()

        return self.process_metrics_query_result(result, output_handler)

    @log
    def extract_table_column_metadata(
        self, table_configuration: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        """Extract column information metadata for a given table.

        This template method provides the common workflow for extracting table column metadata.
        Platform-specific implementations override the hook methods.

        Args:
            table_configuration (TableConfiguration): The table configuration containing all necessary metadata.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            pd.DataFrame: A DataFrame containing column information metadata.

        """
        LOGGER.info(
            "Extracting table column metadata for table: %s",
            table_configuration.fully_qualified_name,
        )

        sql_query = self.query_generator.generate_table_column_metadata_query(
            table_configuration=table_configuration,
            context=context,
        )

        try:
            result = self.connector.execute_query(sql_query)
        except Exception:
            error_message = self._get_error_message(
                "Metadata extraction query failed",
                table_configuration.fully_qualified_name,
            )
            LOGGER.critical(error_message)
            raise

        if not result:
            return pd.DataFrame()

        return self.process_table_column_metadata_result(result, context.output_handler)

    @abstractmethod
    def create_table_chunks_md5(self, table_context: TableContext) -> None:
        """Create table chunks for MD5 calculation.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        """
        pass

    @abstractmethod
    def compute_md5(self, table_context: TableContext, other_table_name: str) -> None:
        """Compute MD5 for a specified table.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            other_table_name (str): the name of the equivalent table in other platform.

        Raises:
            ValueError: If the table or specified columns don't exist.
            DatabaseError: If there is an error executing the SQL query.

        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def process_schema_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process schema query results into a DataFrame.

        Args:
            result: Query result list containing columns and data.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with schema metadata.

        """
        pass

    @abstractmethod
    def process_metrics_query_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process metrics query results into a DataFrame.

        Args:
            result: Query result list containing columns and data.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with metrics metadata.

        """
        pass

    @abstractmethod
    def process_table_column_metadata_result(
        self, result: list, output_handler: OutputHandlerBase
    ) -> pd.DataFrame:
        """Process table column metadata query results into a DataFrame.

        Args:
            result: List of data rows from the query result.
            output_handler: Output handler for logging and reporting.

        Returns:
            pd.DataFrame: Processed DataFrame with table column metadata.

        """
        pass

    @abstractmethod
    def extract_table_row_count(
        self,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        platform: Platform,
        context: Context,
    ) -> pd.DataFrame:
        """Extract the row count for a specified table.

        Args:
            fully_qualified_name (str): The fully qualified name of the table.
            where_clause (str): Optional WHERE clause to filter the row count.
            has_where_clause (bool): Whether the WHERE clause is present.
            platform (Platform): The platform enum value.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            pd.DataFrame: A DataFrame containing the row count for the specified table.

        """
        pass

    def _get_error_message(self, operation: str, table_name: str) -> str:
        """Generate platform-specific error message.

        Args:
            operation: The operation that failed.
            table_name: The table name involved in the operation.

        Returns:
            str: Formatted error message.

        """
        return ERROR_MESSAGE_TEMPLATE.format(
            platform=self.platform.value,
            operation=operation,
            table_name=table_name,
        )
