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

from os import path

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    METRICS_VALIDATION_KEY,
    SCHEMA_VALIDATION_KEY,
)
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.validation.metrics_data_validator import (
    MetricsDataValidator,
)
from snowflake.snowflake_data_validation.validation.schema_data_validator import (
    SchemaDataValidator,
)


LOGGER = logging.getLogger(__name__)


class AsyncValidationExecutor(BaseValidationExecutor):

    """Executor for asynchronous validation operations.

    This executor performs real-time validation by using extracted validation files with metadata from both
    source and target systems and comparing them immediately. Used for run-validation
    commands.
    """

    @log
    def execute_schema_validation(
        self,
        table_context: TableContext,
    ) -> bool:
        """Execute schema validation by comparing table metadata.

        Args:
            table_context: Table context containing all necessary validation parameters

        Returns:
            bool: True if validation passes, False otherwise

        """
        LOGGER.info(
            "Starting async schema validation for table: %s",
            table_context.fully_qualified_name,
        )

        [source_df, target_df] = self._load_validation_files(
            validation_type=SCHEMA_VALIDATION_KEY,
            table_context=table_context,
        )

        # Check if either DataFrame is empty (indicating missing/corrupted files)
        if source_df.empty or target_df.empty:
            LOGGER.warning(
                "Schema validation failed - empty source or target data for table: %s",
                table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Schema validation failed.",
                message="Source or target validation file is missing or empty.",
                level=OutputMessageLevel.FAILURE,
            )
            return False

        try:
            LOGGER.debug(
                "Executing schema validation for table: %s",
                table_context.fully_qualified_name,
            )

            data_validator = SchemaDataValidator()
            validation_result = data_validator.validate_table_metadata(
                object_name=table_context.fully_qualified_name,
                target_df=target_df,
                source_df=source_df,
                context=self.context,
                columns_mappings=table_context.columns_mappings,
            )
            validation_status = "passed" if validation_result else "failed"
            LOGGER.info(
                "Schema validation %s for table: %s",
                validation_status,
                table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header=f"Schema validation {validation_status}.",
                message="",
                level=OutputMessageLevel.SUCCESS
                if validation_result
                else OutputMessageLevel.FAILURE,
            )
            return validation_result
        except Exception as e:
            LOGGER.error(
                "Schema validation failed for table %s: %s",
                table_context.fully_qualified_name,
                str(e),
            )
            self.context.output_handler.handle_message(
                header="Schema validation failed.",
                message=f"Error during schema validation: {str(e)}",
                level=OutputMessageLevel.FAILURE,
            )
            return False

    @log
    def execute_metrics_validation(
        self,
        table_context: TableConfiguration,
    ) -> bool:
        """Execute metrics validation by comparing column metadata.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            bool: True if validation passes, False otherwise

        """
        LOGGER.info(
            "Starting async metrics validation for table: %s",
            table_context.fully_qualified_name,
        )

        [source_df, target_df] = self._load_validation_files(
            validation_type=METRICS_VALIDATION_KEY,
            table_context=table_context,
        )

        # Check if either DataFrame is empty (indicating missing/corrupted files)
        if source_df.empty or target_df.empty:
            LOGGER.warning(
                "Metrics validation failed - empty source or target data for table: %s",
                table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Metrics validation failed.",
                message="Source or target validation file is missing or empty.",
                level=OutputMessageLevel.FAILURE,
            )
            return False

        try:
            LOGGER.debug(
                "Executing metrics validation for table: %s",
                table_context.fully_qualified_name,
            )

            data_validator = MetricsDataValidator()
            validation_result = data_validator.validate_column_metadata(
                object_name=table_context.fully_qualified_name,
                target_df=target_df,
                source_df=source_df,
                context=self.context,
                columns_mappings=table_context.columns_mappings,
            )
            validation_status = "passed" if validation_result else "failed"
            LOGGER.info(
                "Metrics validation %s for table: %s",
                validation_status,
                table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header=f"Metrics validation {validation_status}.",
                message="",
                level=OutputMessageLevel.SUCCESS
                if validation_result
                else OutputMessageLevel.FAILURE,
            )
            return validation_result
        except Exception as e:
            LOGGER.error(
                "Metrics validation failed for table %s: %s",
                table_context.fully_qualified_name,
                str(e),
            )
            self.context.output_handler.handle_message(
                header="Metrics validation failed.",
                message=f"Error during metrics validation: {str(e)}",
                level=OutputMessageLevel.FAILURE,
            )
            return False

    @log
    def execute_row_validation(
        self,
        table_context: TableConfiguration,
    ) -> bool:
        """Execute row validation (placeholder implementation).

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            bool: True (placeholder - row validation not yet implemented)

        """
        LOGGER.info(
            "Starting async row validation for table: %s",
            table_context.fully_qualified_name,
        )
        LOGGER.warning("Row validation not yet implemented - returning False")
        return False

    @log
    def _load_validation_files(
        self,
        validation_type: str,
        table_context: TableContext,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Load validation files for the given table context.

        Args:
            validation_type: Type of validation to load (e.g., schema, metrics)
            table_context: Table context containing all necessary parameters

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: Source and target DataFrames

        """
        LOGGER.debug(
            "Loading validation files for %s validation of table: %s",
            validation_type,
            table_context.fully_qualified_name,
        )

        source_base_path = self.context.configuration.source_validation_files_path
        target_base_path = self.context.configuration.target_validation_files_path
        source_file_path: str
        target_file_path: str
        if table_context.source_validation_file_name:
            source_file_path = path.join(
                source_base_path,
                validation_type,
                table_context.source_validation_file_name,
            )
        else:
            source_file_path = path.join(
                source_base_path,
                validation_type,
                f"{table_context.fully_qualified_name}.csv",
            )
        if table_context.target_validation_file_name:
            target_file_path = path.join(
                target_base_path,
                validation_type,
                table_context.target_validation_file_name,
            )
        else:
            target_file_path = path.join(
                target_base_path, f"{table_context.fully_qualified_name}.csv"
            )

        LOGGER.debug("Loading source file: %s", source_file_path)
        LOGGER.debug("Loading target file: %s", target_file_path)
        if not path.exists(source_file_path):
            LOGGER.error("Source validation file not found: %s", source_file_path)
            self.context.output_handler.handle_message(
                header="Source validation file not found.",
                message=f"Source validation file {source_file_path} does not exist.",
                level=OutputMessageLevel.ERROR,
            )
            return pd.DataFrame(), pd.DataFrame()

        if not path.exists(target_file_path):
            LOGGER.error("Target validation file not found: %s", target_file_path)
            self.context.output_handler.handle_message(
                header="Target validation file not found.",
                message=f"Target validation file {target_file_path} does not exist.",
                level=OutputMessageLevel.ERROR,
            )
            return pd.DataFrame(), pd.DataFrame()
        try:
            # Load source and target validation files from csv or parquet format
            if source_file_path.endswith(".csv"):
                source_df = pd.read_csv(source_file_path)
                LOGGER.debug(
                    "Successfully loaded source CSV file with %d rows", len(source_df)
                )
            elif source_file_path.endswith(".parquet"):
                source_df = pd.read_parquet(source_file_path)
                LOGGER.debug(
                    "Successfully loaded source Parquet file with %d rows",
                    len(source_df),
                )
            else:
                error_msg = "Unsupported file format for source validation file."
                LOGGER.error(error_msg)
                raise ValueError(error_msg)

            if target_file_path.endswith(".csv"):
                target_df = pd.read_csv(target_file_path)
                LOGGER.debug(
                    "Successfully loaded target CSV file with %d rows", len(target_df)
                )
            elif target_file_path.endswith(".parquet"):
                target_df = pd.read_parquet(target_file_path)
                LOGGER.debug(
                    "Successfully loaded target Parquet file with %d rows",
                    len(target_df),
                )
            else:
                error_msg = "Unsupported file format for target validation file."
                LOGGER.error(error_msg)
                raise ValueError(error_msg)

            return source_df, target_df

        except Exception as e:
            LOGGER.error("Error loading validation files: %s", str(e))
            self.context.output_handler.handle_message(
                header="Error loading validation files.",
                message=f"Failed to load validation files: {str(e)}",
                level=OutputMessageLevel.ERROR,
            )
            return pd.DataFrame(), pd.DataFrame()

    def _get_schema_validation_message(self, table_context: TableConfiguration) -> str:
        """Get async validation message for schema validation.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            str: Message for schema validation in async mode

        """
        return (
            f"Validating schema for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )

    def _get_metrics_validation_message(self, table_context: TableConfiguration) -> str:
        """Get async validation message for metrics validation.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            str: Message for metrics validation in async mode

        """
        return (
            f"Validating metrics for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )

    def _get_row_validation_message(self, table_context: TableConfiguration) -> str:
        """Get async validation message for row validation.

        Args:
            table_context: Table configuration containing all necessary validation parameters

        Returns:
            str: Message for row validation in async mode

        """
        return (
            f"Validating rows for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )
