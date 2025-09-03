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
import math
import re

from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CHUNK_ID_FORMAT,
    ROW_NUMBER_DEFAULT_CHUNK,
    Origin,
    Platform,
)
from snowflake.snowflake_data_validation.utils.model.chunk import Chunk
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)


LOGGER = logging.getLogger(__name__)


class TableContext:

    """Context for a table in the data validation process.

    Attributes:
        chunk_number (int): The number of chunks for the table.
        column_selection_list (list[str]): List of columns to include or exclude.
        columns (list[ColumnMetadata]): List of column metadata for the table.
        database_name (str): Name of the database containing the table.
        fully_qualified_name (str): Fully qualified name of the table.
        has_where_clause (bool): Indicates if the table has a WHERE clause.
        is_case_sensitive (bool): Indicates if the table is case-sensitive.
        is_exclusion_mode (bool): Indicates if the column selection is in exclusion mode.
        origin (Origin): The origin of the table (SOURCE or TARGET).
        platform (Platform): The platform of the table (e.g., Snowflake).
        row_count (int): Number of rows in the table.
        run_id (str): Unique identifier for the validation run.
        run_start_time (str): Start time of the validation run.
        schema_name (str): Name of the schema containing the table.
        sql_generator (SQLQueriesTemplateGenerator): SQL query generator for the table.
        templates_loader_manager (TemplatesLoaderManager): Manager for loading templates.
        table_name (str): Name of the table.
        chunk_id_index (int): Index for generating unique chunk IDs.
        columns_to_validate (list[ColumnMetadata]): List of columns to validate based on inclusion/exclusion mode.
        normalized_fully_qualified_name (str): Normalized fully qualified name of the table.
        index_column_collection (list[ColumnMetadata]): List of index columns for the table.

    """

    def __init__(
        self,
        chunk_number: int,
        column_selection_list: list[str],
        columns: list[ColumnMetadata],
        database_name: str,
        exclude_metrics: bool,
        fully_qualified_name: str,
        has_where_clause: bool,
        id: int,
        is_case_sensitive: bool,
        is_exclusion_mode: bool,
        max_failed_rows_number: int,
        origin: Origin,
        platform: Platform,
        row_count: int,
        run_id: str,
        run_start_time: str,
        schema_name: str,
        sql_generator: SQLQueriesTemplateGenerator,
        table_name: str,
        templates_loader_manager: TemplatesLoaderManager,
        user_index_column_collection: list[str],
        where_clause: str,
    ):
        self.chunk_number = chunk_number
        self.id = id
        self.is_case_sensitive = is_case_sensitive
        self.exclude_metrics = exclude_metrics
        self.max_failed_rows_number = max_failed_rows_number
        self.platform = platform
        self.origin = origin
        self.fully_qualified_name = fully_qualified_name
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_name = table_name
        self.columns = columns
        self.where_clause = where_clause
        self.has_where_clause = has_where_clause
        self.is_exclusion_mode = is_exclusion_mode
        self.column_selection_list = column_selection_list
        self.row_count = row_count
        self.run_id = run_id
        self.run_start_time = run_start_time
        self.templates_loader_manager = templates_loader_manager
        self.sql_generator = sql_generator

        self.chunk_id_index = 0
        self.columns_to_validate = self._get_columns_to_validate()
        self.normalized_fully_qualified_name = (
            self._get_normalized_fully_qualified_name()
        )
        self.index_column_collection = self._get_index_column_collection(
            user_index_column_collection
        )

    def get_chunk_id(self, other_table_name: str) -> str:
        """Generate a unique chunk ID for the table context."""
        self.chunk_id_index = self.chunk_id_index + 1
        if self.origin == Origin.SOURCE:
            chunk_id = CHUNK_ID_FORMAT.format(
                source_name=self.table_name,
                other_table_name=other_table_name,
                id=self.chunk_id_index,
            )
        else:
            chunk_id = CHUNK_ID_FORMAT.format(
                source_name=other_table_name,
                other_table_name=self.table_name,
                id=self.chunk_id_index,
            )

        return chunk_id

    def join_column_names_with_commas(self) -> str:
        """Join column names with commas and convert them to uppercase with quotes.

        Returns:
            str: A string of column names joined by commas, each in uppercase and quoted.

        """
        column_names_upper_and_quote = [
            f'"{col.name}"' for col in self.columns_to_validate
        ]
        return (
            ", ".join(column_names_upper_and_quote)
            if column_names_upper_and_quote
            else ""
        )

    def get_chunk_collection(self) -> list[Chunk]:
        """Get a collection of chunks for the table context."""
        local_chunk_number = self.chunk_number

        if local_chunk_number == 0:
            local_chunk_number = math.ceil(self.row_count / ROW_NUMBER_DEFAULT_CHUNK)
            fetch = ROW_NUMBER_DEFAULT_CHUNK
        else:
            fetch = self.row_count // local_chunk_number

        offset = 0
        chunk_counter = 1
        last_chunk = chunk_counter == local_chunk_number
        has_next_chunk = chunk_counter <= local_chunk_number
        chunk_collection = []

        while has_next_chunk:

            if last_chunk:
                fetch = self.row_count - offset

            chunk = Chunk(fetch=fetch, offset=offset)
            chunk_collection.append(chunk)

            chunk_counter += 1
            offset += fetch
            last_chunk = chunk_counter == local_chunk_number
            has_next_chunk = chunk_counter <= local_chunk_number

        return chunk_collection

    def _get_columns_to_validate(self) -> list[ColumnMetadata]:
        """Return the list of columns to validate based on inclusion or exclusion mode.

        Returns:
            list[str]: The list of columns to validate.

        """
        if (
            not self.column_selection_list or len(self.column_selection_list) == 0
        ):  # If no columns are specified, return all columns
            columns_to_validate = self.columns
        else:
            if not self.is_exclusion_mode:
                columns_to_validate = [
                    col for col in self.columns if self._is_column_present(col.name)
                ]

            else:
                columns_to_validate = [
                    col for col in self.columns if not self._is_column_present(col.name)
                ]

        return columns_to_validate

    def _is_column_present(self, column_name: str) -> bool:
        """Check if a column exists in a list of columns.

        If the column list contains regular expressions,
        it checks if the column name matches any of the regular expressions.
        regular expressions are expected to start with 'r' and be wrapped between quotes e.g: r".*".

        Args:
            column_name (str): The name of the column to check.

        Returns:
            bool: True if the column exists in the list, False otherwise.

        """
        for col in self.column_selection_list:
            if col.lower().startswith('r"') and col.endswith('"'):
                # If the column is a regex, check if it matches the column name
                regex_pattern = col[2:-1]  # Remove the 'r' and quotes

                # For regex, we should use case-insensitive flag rather than uppercasing both pattern and name
                if self.is_case_sensitive:
                    if re.match(regex_pattern, column_name):
                        return True
                else:
                    # Use re.IGNORECASE flag for case-insensitive matching with regex
                    if re.match(regex_pattern, column_name, re.IGNORECASE):
                        return True
            elif col == column_name:
                return True
        return False

    def _get_index_column_collection(
        self, index_column_collection: list[str]
    ) -> list[ColumnMetadata]:
        """Get a list of index columns for the table.

        Returns:
            list[str]: A list of index column names.

        """
        index_column_metadata_collection = []
        columns_dict = {col.name: col for col in self.columns}
        for index_column in index_column_collection:
            index_column_key = (
                index_column.upper() if not self.is_case_sensitive else index_column
            )
            if index_column_key not in columns_dict:
                LOGGER.warning(
                    "Index column %s not found in table %s on %s.",
                    index_column,
                    self.fully_qualified_name,
                    self.platform.value,
                )
                continue

            index_column = columns_dict[index_column_key]
            index_column_metadata_collection.append(index_column)

        if not index_column_metadata_collection:
            index_column_metadata_collection = (
                self._get_index_column_collection_default()
            )
            LOGGER.warning(
                "No user-specified index columns found for table %s on %s. "
                "Using automatically detected index columns: %s. "
                "To override, set 'column_index_list' in your configuration file.",
                self.fully_qualified_name,
                self.platform.value,
                [col.name for col in index_column_metadata_collection],
            )

        return index_column_metadata_collection

    def _get_normalized_fully_qualified_name(self) -> str:
        """Normalize a fully qualified name by replacing dots and spaces with underscores.

        Returns:
            str: The normalized fully qualified name.

        """
        normalized_fully_qualified_name = self.fully_qualified_name.replace(
            ".", "_"
        ).replace(" ", "_")

        return normalized_fully_qualified_name

    def _get_index_column_collection_default(self) -> list[ColumnMetadata]:
        """Get a list of index columns for the table.

        Returns:
            list[str]: A list of index column names.

        """
        return [column for column in self.columns if column.is_primary_key]
