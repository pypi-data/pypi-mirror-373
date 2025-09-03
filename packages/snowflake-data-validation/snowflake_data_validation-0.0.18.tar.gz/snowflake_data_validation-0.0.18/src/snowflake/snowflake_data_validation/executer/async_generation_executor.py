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

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
    validation_handler,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class AsyncGenerationExecutor(BaseValidationExecutor):

    """Executor for asynchronous query generation operations.

    This executor generates async comparison queries and writes them to files
    instead of executing actual validation. Uses script writers to delegate
    the actual file generation and writing operations.
    """

    @validation_handler(
        "Schema validation async generation failed.",
        "Error generating schema validation queries: {error}",
    )
    def execute_schema_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
        columns_mappings: dict[str, str],
    ) -> bool:
        """Generate schema validation queries and write to files.

        Args:
            source_table_context: Source table configuration containing all necessary validation parameters.
            target_table_context: Target table configuration containing all necessary validation parameters.
            columns_mappings: mapping of source to target columns for validation.

        Returns:
            bool: True if queries are successfully generated and written, False if any operation fails

        """
        try:
            # Use script writers' print methods to generate and write queries
            self.source_extractor.print_table_metadata_query(
                table_context=source_table_context,
                context=self.context,
            )
            self.target_extractor.print_table_metadata_query(
                table_context=target_table_context,
                context=self.context,
            )

            self.context.output_handler.handle_message(
                header="Schema validation queries generated.",
                message=f"Queries generated for table: {source_table_context.fully_qualified_name}",
                level=OutputMessageLevel.SUCCESS,
            )
            return True
        except Exception:
            return False

    @validation_handler(
        "Metrics validation async generation failed.",
        "Error generating metrics validation queries: {error}",
    )
    def execute_metrics_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
        columns_mappings: dict[str, str],
    ) -> bool:
        """Generate metrics validation queries and write to files.

        Args:
            source_table_context: Source table configuration containing all necessary validation parameters.
            target_table_context: Target table configuration containing all necessary validation parameters.
            columns_mappings: mapping of source to target columns for validation.

        Returns:
            bool: True if queries are successfully generated and written, False if any operation fails

        """
        try:
            # Use script writers' print methods to generate and write queries
            self.source_extractor.print_column_metadata_query(
                table_context=source_table_context,
                context=self.context,
            )
            self.target_extractor.print_column_metadata_query(
                table_context=target_table_context,
                context=self.context,
            )

            self.context.output_handler.handle_message(
                header="Metrics validation queries generated.",
                message=f"Queries generated for table: {target_table_context.fully_qualified_name}",
                level=OutputMessageLevel.SUCCESS,
            )
            return True
        except Exception:
            return False

    @validation_handler(
        "Row validation async generation failed.",
        "Error in row validation async generation: {error}",
    )
    def execute_row_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
    ) -> bool:
        """Generate row validation queries (placeholder implementation).

        Args:
            table_context: Table configuration containing all necessary validation parameters
            source_table_context: Source table context for validation
            target_table_context: Target table context for validation

        Returns:
            bool: True if no errors are raised during async generation, False if errors occur

        """
        # Placeholder - row validation not implemented yet
        self.context.output_handler.handle_message(
            header="Row validation async generation skipped.",
            message="Row validation async generation is not yet implemented.",
            level=OutputMessageLevel.INFO,
        )
        return True

    def _get_schema_validation_message(self, table_context: TableConfiguration) -> str:
        """Get async generation message for schema validation."""
        return (
            f"Generating async schema validation queries for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )

    def _get_metrics_validation_message(self, table_context: TableConfiguration) -> str:
        """Get async generation message for metrics validation."""
        return (
            f"Generating async metrics validation queries for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )

    def _get_row_validation_message(self, table_context: TableConfiguration) -> str:
        """Get async generation message for row validation."""
        return (
            f"Generating async row validation queries for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )
