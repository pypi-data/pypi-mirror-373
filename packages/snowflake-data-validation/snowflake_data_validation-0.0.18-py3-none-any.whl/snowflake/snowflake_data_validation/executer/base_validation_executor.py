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
from functools import wraps
from typing import Callable, TypeVar, Union

from typing_extensions import ParamSpec

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    METRICS_TO_EXCLUDE,
    METRICS_VALIDATION_KEY,
    ROW_VALIDATION_KEY,
    SCHEMA_VALIDATION_KEY,
    Origin,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_column_metadata import (
    TableColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)
P = ParamSpec("P")
R = TypeVar("R")


def validation_handler(
    failure_header: str,
    failure_message_template: str = "Error during {operation}: {error}",
):
    """Provide consistent error handling for validation methods.

    This decorator provides consistent error handling for validation methods by:
    1. Wrapping method execution in try/catch block
    2. Handling success/failure message reporting
    3. Returning appropriate boolean results
    4. Providing consistent error message formatting

    Args:
        failure_header: Header message to use when validation fails
        failure_message_template: Template for failure message. Can use {operation} and {error} placeholders.

    Returns:
        Decorated method that handles errors and messaging consistently

    """

    def decorator(method: Callable[P, R]) -> Callable[P, R]:
        @wraps(method)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
            try:
                result = method(self, *args, **kwargs)
                return result

            except Exception as e:
                operation = method.__name__.replace("execute_", "").replace("_", " ")

                formatted_message = failure_message_template.format(
                    operation=operation, error=str(e)
                )

                self.context.output_handler.handle_message(
                    header=failure_header,
                    message=formatted_message,
                    level=OutputMessageLevel.FAILURE,
                )
                return False

        return wrapper

    return decorator


class BaseValidationExecutor(ABC):

    """Base class for all validation executors.

    Implements the Template Method Pattern for table validation workflows.
    Defines the common interface and shared functionality for different
    validation execution strategies (sync validation, async generation, etc.).

    Subclasses must implement:
    - Individual validation methods (execute_schema_validation, etc.)
    - Message generation methods (_get_*_validation_message)
    """

    @log
    def __init__(
        self,
        source_extractor: Union[MetadataExtractorBase, ScriptWriterBase],
        target_extractor: Union[MetadataExtractorBase, ScriptWriterBase],
        context: Context,
    ):
        """Initialize the base validation executor.

        Args:
            source_extractor: Extractor for source metadata
            target_extractor: Extractor for target metadata
            context: Validation context containing configuration and runtime info

        """
        LOGGER.debug("Initializing BaseValidationExecutor")
        self.source_extractor = source_extractor
        self.target_extractor = target_extractor
        self.context = context
        LOGGER.debug(
            "BaseValidationExecutor initialized with source and target extractors"
        )

    @log
    def execute_validation_levels(
        self,
        validation_config: ValidationConfiguration,
        table_configuration: TableConfiguration,
        source_table_column_metadata: TableColumnMetadata,
        target_table_column_metadata: TableColumnMetadata,
    ) -> None:
        """Execute validation for all configured validations of a single table.

        Template Method: Defines the validation workflow while allowing subclasses
        to customize validation messages through abstract message methods.

        Args:
            validation_config: Configuration specifying which validations to run
            table_configuration: Configuration for the table being validated
            source_table_column_metadata: Metadata for source table columns
            target_table_column_metadata: Metadata for target table columns

        """
        validations = validation_config.model_dump()
        LOGGER.info(
            "Executing validation levels for table: %s",
            table_configuration.fully_qualified_name,
        )

        if not validations:
            LOGGER.warning(
                "No validations configured for table: %s",
                table_configuration.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="No validations configured.",
                message="No validation configuration found for the object.",
                level=OutputMessageLevel.WARNING,
            )
            return

        source_table_context = self._generate_source_table_context(
            table_configuration, source_table_column_metadata
        )
        target_table_context = self._generate_target_table_context(
            table_configuration, target_table_column_metadata
        )

        if validations[SCHEMA_VALIDATION_KEY]:
            LOGGER.info(
                "Starting schema validation for table: %s",
                source_table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Schema validation started.",
                message=self._get_schema_validation_message(table_configuration),
                level=OutputMessageLevel.INFO,
            )
            self.execute_schema_validation(
                source_table_context=source_table_context,
                target_table_context=target_table_context,
                columns_mappings=table_configuration.column_mappings,
            )

        if validations[METRICS_VALIDATION_KEY]:
            LOGGER.info(
                "Starting metrics validation for table: %s",
                table_configuration.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Metrics validation started.",
                message=self._get_metrics_validation_message(table_configuration),
                level=OutputMessageLevel.INFO,
            )
            if source_table_context.exclude_metrics:
                LOGGER.warning(
                    "Excluding metrics %s for tables %s (%s) and %s (%s) due to 'metrics_exclude' setting. "
                    "To include these metrics, disable 'metrics_exclude' in your configuration file.",
                    METRICS_TO_EXCLUDE,
                    source_table_context.fully_qualified_name,
                    source_table_context.platform.value,
                    target_table_context.fully_qualified_name,
                    target_table_context.platform.value,
                )
                self.context.output_handler.handle_message(
                    message=(
                        f"Excluding metrics {METRICS_TO_EXCLUDE} for tables "
                        f"{source_table_context.fully_qualified_name} "
                        f"({source_table_context.platform.value}) and "
                        f"{target_table_context.fully_qualified_name} "
                        f"({target_table_context.platform.value}) due to "
                        "'metrics_exclude' setting. To include these metrics, "
                        "disable 'metrics_exclude' in your configuration file."
                    ),
                    level=OutputMessageLevel.WARNING,
                )

            self.execute_metrics_validation(
                source_table_context=source_table_context,
                target_table_context=target_table_context,
                columns_mappings=table_configuration.column_mappings,
            )

        if validations[ROW_VALIDATION_KEY]:
            LOGGER.info(
                "Starting row validation for table: %s",
                table_configuration.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Row validation started.",
                message=self._get_row_validation_message(table_configuration),
                level=OutputMessageLevel.INFO,
            )
            self.execute_row_validation(
                source_table_context=source_table_context,
                target_table_context=target_table_context,
            )

        LOGGER.info(
            "Completed all validation levels for table: %s",
            table_configuration.fully_qualified_name,
        )

    @abstractmethod
    def execute_schema_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
        columns_mappings: dict[str, str],
    ) -> bool:
        """Execute schema validation for a table.

        Args:
            source_table_context: source table configuration containing all necessary validation parameters.
            target_table_context: target table configuration containing all necessary validation parameters.
            columns_mappings: A dictionary mapping source column names to target column names.

        Returns:
            bool: True if validation passes, False otherwise

        """
        pass

    @abstractmethod
    def execute_metrics_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
        columns_mappings: dict[str, str],
    ) -> bool:
        """Execute metrics validation for a table.

        Args:
            source_table_context: source table configuration containing all necessary validation parameters.
            target_table_context: target table configuration containing all necessary validation parameters.
            columns_mappings: A dictionary mapping source column names to target column names.

        Returns:
            bool: True if validation passes, False otherwise

        """
        pass

    @abstractmethod
    def execute_row_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
    ) -> bool:
        """Execute row validation for a table.

        Args:
            table_context: Table configuration containing all necessary validation parameters
            source_table_context: Source table context for validation
            target_table_context: Target table context for validation

        Returns:
            bool: True if validation passes, False otherwise

        """
        pass

    @abstractmethod
    def _get_schema_validation_message(self, table_context: TableConfiguration) -> str:
        """Get operation-specific message for schema validation.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            str: Operation-specific message for schema validation

        """
        pass

    @abstractmethod
    def _get_metrics_validation_message(self, table_context: TableConfiguration) -> str:
        """Get operation-specific message for metrics validation.

        Template Method Hook: Subclasses customize messaging for their operation type.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            str: Operation-specific message for metrics validation

        """
        pass

    @abstractmethod
    def _get_row_validation_message(self, table_context: TableConfiguration) -> str:
        """Get operation-specific message for row validation.

        Template Method Hook: Subclasses customize messaging for their operation type.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            str: Operation-specific message for row validation

        """
        pass

    def _generate_source_table_context(
        self,
        table_configuration: TableConfiguration,
        source_table_column_metadata: TableColumnMetadata,
    ) -> TableContext:
        source_table_context = TableContext(
            chunk_number=table_configuration.chunk_number,
            column_selection_list=source_table_column_metadata.column_selection_list,
            columns=source_table_column_metadata.columns,
            database_name=table_configuration.source_database,
            exclude_metrics=table_configuration.exclude_metrics,
            fully_qualified_name=table_configuration.fully_qualified_name,
            has_where_clause=table_configuration.has_where_clause,
            max_failed_rows_number=table_configuration.max_failed_rows_number,
            user_index_column_collection=table_configuration.index_column_list,
            id=table_configuration.id,
            is_case_sensitive=table_configuration.is_case_sensitive,
            is_exclusion_mode=table_configuration.use_column_selection_as_exclude_list,
            origin=Origin.SOURCE,
            platform=self.context.source_platform,
            row_count=source_table_column_metadata.row_count,
            run_id=self.context.run_id,
            run_start_time=self.context.run_start_time,
            schema_name=table_configuration.source_schema,
            sql_generator=self.context.sql_generator,
            table_name=table_configuration.source_table,
            templates_loader_manager=self.context.source_templates,
            where_clause=table_configuration.where_clause,
        )

        return source_table_context

    def _generate_target_table_context(
        self,
        table_configuration: TableConfiguration,
        target_table_column_metadata: TableColumnMetadata,
    ) -> TableContext:
        target_table_context = TableContext(
            chunk_number=table_configuration.chunk_number,
            column_selection_list=target_table_column_metadata.column_selection_list,
            columns=target_table_column_metadata.columns,
            database_name=table_configuration.target_database,
            exclude_metrics=table_configuration.exclude_metrics,
            fully_qualified_name=table_configuration.target_fully_qualified_name,
            has_where_clause=table_configuration.has_target_where_clause,
            max_failed_rows_number=table_configuration.max_failed_rows_number,
            user_index_column_collection=table_configuration.target_index_column_list,
            id=table_configuration.id,
            is_case_sensitive=table_configuration.is_case_sensitive,
            is_exclusion_mode=table_configuration.use_column_selection_as_exclude_list,
            origin=Origin.TARGET,
            platform=self.context.target_platform,
            row_count=target_table_column_metadata.row_count,
            run_id=self.context.run_id,
            run_start_time=self.context.run_start_time,
            schema_name=table_configuration.target_schema,
            sql_generator=self.context.sql_generator,
            table_name=table_configuration.target_name,
            templates_loader_manager=self.context.target_templates,
            where_clause=table_configuration.target_where_clause,
        )

        return target_table_context
