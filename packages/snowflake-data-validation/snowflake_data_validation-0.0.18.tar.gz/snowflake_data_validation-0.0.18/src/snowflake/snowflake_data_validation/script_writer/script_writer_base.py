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

import os

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
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_METADATA_QUERIES_FILENAME,
    NEWLINE,
    TABLE_METADATA_QUERIES_FILENAME,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class ScriptWriterBase(ABC):

    """Base class for printing database queries to files.

    This class provides the same interface as MetadataExtractorBase but instead of
    returning pandas DataFrames, it writes the generated SQL queries to files.

    All methods have concrete implementations since the logic is identical across
    all database platforms - they create TableConfiguration objects and delegate
    to the platform-specific query generators.
    """

    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the script printer with a database connector and query generator.

        Args:
            connector: Database connector instance for the specific database type.
            query_generator: Query generator instance for generating SQL queries.
            report_path: Path where the script files should be written.

        """
        self.connector = connector
        self.query_generator = query_generator
        self.report_path = report_path or "."

    def _get_filename(self, filename_template: str, context: Context) -> str:
        """Get the filename with timestamp from context.

        Args:
            filename_template (str): The filename template with {timestamp} placeholder.
            context (Context): The execution context containing run_start_time.

        Returns:
            str: Full file path with timestamp.

        """
        timestamp = context.run_start_time
        filename = filename_template.format(timestamp=timestamp)
        return os.path.join(self.report_path, filename)

    def print_table_metadata_query(
        self,
        table_context: TableContext,
        context: Context,
    ) -> None:
        """Write the table-level metadata query for the specified table to file.

        Args:
            table_context (TableContext): The table context containing all necessary parameters for the table.
            context (Context): The execution context containing relevant configuration and runtime information.

        """
        query = self.query_generator.generate_schema_query(table_context=table_context)
        file_path = self._get_filename(TABLE_METADATA_QUERIES_FILENAME, context)
        self.write_to_file(file_path, query)

    def print_column_metadata_query(
        self,
        table_context: TableContext,
        context: Context,
    ) -> None:
        """Write the column-level metadata query for the specified columns in a table to file.

        Args:
            table_context (TableContext): The table context containing all necessary parameters for the table.
            context (Context): The execution context containing relevant configuration and runtime information.

        """
        query = self.query_generator.generate_metrics_query(
            table_context=table_context,
            connector=self.connector,
        )
        file_path = self._get_filename(COLUMN_METADATA_QUERIES_FILENAME, context)
        self.write_to_file(file_path, query)

    @abstractmethod
    def extract_table_column_metadata(
        self, table_configuration: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        """Extract table and column metadata for the specified table configuration.

        Args:
            table_configuration (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted metadata.

        """
        pass

    def write_to_file(self, file_path: str, content: str) -> None:
        """Write content to a file with UTF-8 encoding.

        Creates the directory if it doesn't exist.

        Args:
            file_path (str): The full path to the file including directory and filename.
            content (str): The content to write to the file.

        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
            f.write(NEWLINE)
