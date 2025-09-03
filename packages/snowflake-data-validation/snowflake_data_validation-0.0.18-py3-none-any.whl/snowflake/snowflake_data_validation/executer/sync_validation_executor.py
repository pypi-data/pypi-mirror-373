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
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
    validation_handler,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import CHUNK_ID_COLUMN_KEY
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.telemetry import (
    report_telemetry,
)
from snowflake.snowflake_data_validation.validation.metrics_data_validator import (
    MetricsDataValidator,
)
from snowflake.snowflake_data_validation.validation.row_data_validator import (
    SOURCE_SUFFIX,
    TARGET_SUFFIX,
    RowDataValidator,
)
from snowflake.snowflake_data_validation.validation.schema_data_validator import (
    SchemaDataValidator,
)


LOGGER = logging.getLogger(__name__)


class SyncValidationExecutor(BaseValidationExecutor):

    """Executor for synchronous validation operations.

    This executor performs real-time validation by extracting metadata from both
    source and target systems and comparing them immediately. Used for run-validation
    and run-validation-ipc commands.
    """

    @validation_handler("Schema validation failed.")
    @log
    @report_telemetry(params_list=["source_table_context", "target_table_context"])
    def execute_schema_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
        columns_mappings: dict[str, str],
    ) -> bool:
        LOGGER.info(
            "Starting schema validation for table: %s",
            source_table_context.fully_qualified_name,
        )

        extraction_message = (
            "Extracting schema validations for: {fully_qualified_name} on {platform}"
        )

        self.context.output_handler.handle_message(
            message=extraction_message.format(
                fully_qualified_name=source_table_context.fully_qualified_name,
                platform=self.context.source_platform.value,
            ),
            level=OutputMessageLevel.INFO,
        )

        LOGGER.debug("Extracting source schema metadata")
        source_metadata = self.source_extractor.extract_schema_metadata(
            table_context=source_table_context,
            output_handler=self.context.output_handler,
        )

        self.context.output_handler.handle_message(
            message=extraction_message.format(
                fully_qualified_name=target_table_context.fully_qualified_name,
                platform=target_table_context.platform.value,
            ),
            level=OutputMessageLevel.INFO,
        )
        LOGGER.debug("Extracting target schema metadata")
        target_metadata = self.target_extractor.extract_schema_metadata(
            table_context=target_table_context,
            output_handler=self.context.output_handler,
        )

        LOGGER.debug("Validating schema metadata")
        data_validator = SchemaDataValidator()
        validation_result = data_validator.validate_table_metadata(
            object_name=source_table_context.fully_qualified_name,
            target_df=target_metadata,
            source_df=source_metadata,
            context=self.context,
            columns_mappings=columns_mappings,
        )

        validation_status = "passed" if validation_result else "failed"
        LOGGER.info(
            "Schema validation %s for table: %s",
            validation_status,
            source_table_context.fully_qualified_name,
        )

        self.context.output_handler.handle_message(
            header=f"Schema validation {validation_status}.",
            message="",
            level=OutputMessageLevel.SUCCESS
            if validation_result
            else OutputMessageLevel.FAILURE,
        )
        return validation_result

    @validation_handler("Metrics validation failed.")
    @log
    @report_telemetry(params_list=["source_table_context", "target_table_context"])
    def execute_metrics_validation(
        self,
        source_table_context: TableContext,
        target_table_context: TableContext,
        columns_mappings: dict[str, str],
    ) -> bool:
        LOGGER.info(
            "Starting metrics validation for table: %s",
            source_table_context.fully_qualified_name,
        )

        extraction_message = (
            "Extracting Metrics metadata for: {fully_qualified_name} on {platform}"
        )

        self.context.output_handler.handle_message(
            message=extraction_message.format(
                fully_qualified_name=source_table_context.fully_qualified_name,
                platform=source_table_context.platform.value,
            ),
            level=OutputMessageLevel.INFO,
        )
        LOGGER.debug("Extracting source metrics metadata")
        source_metadata = self.source_extractor.extract_metrics_metadata(
            table_context=source_table_context,
            output_handler=self.context.output_handler,
        )

        self.context.output_handler.handle_message(
            message=extraction_message.format(
                fully_qualified_name=target_table_context.fully_qualified_name,
                platform=target_table_context.platform.value,
            ),
            level=OutputMessageLevel.INFO,
        )
        LOGGER.debug("Extracting target metrics metadata")
        target_metadata = self.target_extractor.extract_metrics_metadata(
            table_context=target_table_context,
            output_handler=self.context.output_handler,
        )

        LOGGER.debug("Validating metrics metadata")
        data_validator = MetricsDataValidator()
        validation_result = data_validator.validate_column_metadata(
            object_name=source_table_context.fully_qualified_name,
            target_df=target_metadata,
            source_df=source_metadata,
            context=self.context,
            columns_mappings=columns_mappings,
        )
        validation_status = "passed" if validation_result else "failed"
        LOGGER.info(
            "Metrics validation %s for table: %s",
            validation_status,
            source_table_context.fully_qualified_name,
        )
        self.context.output_handler.handle_message(
            header=f"Metrics validation {validation_status}.",
            message="",
            level=OutputMessageLevel.SUCCESS
            if validation_result
            else OutputMessageLevel.FAILURE,
        )
        return validation_result

    @validation_handler("Row validation failed.")
    @log
    @report_telemetry(params_list=["source_table_context", "target_table_context"])
    def execute_row_validation(
        self, source_table_context: TableContext, target_table_context: TableContext
    ) -> bool:

        LOGGER.info(
            "Starting row validation for table %s and table %s",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

        self._create_table_chunks_md5(
            source_table_context=source_table_context,
            target_table_context=target_table_context,
        )

        self._compute_md5(
            source_table_context=source_table_context,
            target_table_context=target_table_context,
        )

        LOGGER.debug(
            "Starting extracted chunks MD5 for table %s",
            source_table_context.fully_qualified_name,
        )

        source_md5_df = self.source_extractor.extract_chunks_md5(
            table_context=source_table_context
        )

        if source_md5_df.empty:
            LOGGER.error(
                "No MD5 chunks found for table %s. Skipping row validation.",
                source_table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Row validation failed.",
                message=(
                    f"No MD5 chunks found for table {source_table_context.fully_qualified_name}. "
                    "Skipping row validation."
                ),
                level=OutputMessageLevel.ERROR,
            )
            return True

        LOGGER.debug(
            "Successfully extracted chunks MD5 for table %s",
            source_table_context.fully_qualified_name,
        )

        LOGGER.debug(
            "Starting extracted chunks MD5 for table %s",
            target_table_context.fully_qualified_name,
        )

        target_md5_df = self.target_extractor.extract_chunks_md5(
            table_context=target_table_context
        )

        if target_md5_df.empty:
            LOGGER.error(
                "No MD5 chunks found for table %s. Skipping row validation.",
                target_table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Row validation failed.",
                message=(
                    f"No MD5 chunks found for table {target_table_context.fully_qualified_name}. "
                    "Skipping row validation."
                ),
                level=OutputMessageLevel.ERROR,
            )
            return True

        LOGGER.debug(
            "Successfully extracted chunks MD5 for table %s",
            target_table_context.fully_qualified_name,
        )

        LOGGER.info(
            "Starting chunks MD5 comparison between table %s and table %s",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

        self.context.output_handler.handle_message(
            message=(
                f"Starting MD5 comparison between table "
                f"{source_table_context.fully_qualified_name} and table "
                f"{target_table_context.fully_qualified_name}"
            ),
            level=OutputMessageLevel.INFO,
        )

        data_validator = RowDataValidator()
        compared_df = data_validator.get_diff_md5_chunks(
            source_md5_df=source_md5_df,
            target_md5_df=target_md5_df,
        )

        LOGGER.info(
            "Completing chunks MD5 comparison between table %s and table %s.",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

        if compared_df.empty:
            LOGGER.info(
                "No differences found in MD5 comparison between table %s and table %s.",
                source_table_context.fully_qualified_name,
                target_table_context.fully_qualified_name,
            )
            self.context.output_handler.handle_message(
                header="Row validation passed.",
                message=(
                    f"No differences found in MD5 comparison between table "
                    f"{source_table_context.fully_qualified_name} and table "
                    f"{target_table_context.fully_qualified_name}"
                ),
                level=OutputMessageLevel.SUCCESS,
            )
            return True
        else:
            LOGGER.info(
                "Differences found in MD5 comparison between table %s and table %s:\n%s",
                source_table_context.fully_qualified_name,
                target_table_context.fully_qualified_name,
                compared_df,
            )
            self.context.output_handler.handle_message(
                message=(
                    f"Differences found in MD5 comparison between table "
                    f"{source_table_context.fully_qualified_name} and table "
                    f"{target_table_context.fully_qualified_name}:"
                ),
                level=OutputMessageLevel.INFO,
                dataframe=compared_df,
            )

        self._validate_md5_rows_chunk(
            data_validator=data_validator,
            compared_df=compared_df,
            source_table_context=source_table_context,
            target_table_context=target_table_context,
        )

        self.context.output_handler.handle_message(
            header="Row validation failed.",
            level=OutputMessageLevel.FAILURE,
        )

        return True

    @log
    def _create_table_chunks_md5(
        self, source_table_context: TableContext, target_table_context: TableContext
    ) -> None:
        LOGGER.debug(
            "Creating table to store the md5 chunks for table %s",
            source_table_context.fully_qualified_name,
        )

        self.source_extractor.create_table_chunks_md5(
            table_context=source_table_context
        )

        LOGGER.debug(
            "Table to store the md5 chunks created for table %s",
            source_table_context.fully_qualified_name,
        )

        LOGGER.debug(
            "Creating table to store the md5 chunks for table %s",
            target_table_context.fully_qualified_name,
        )

        self.target_extractor.create_table_chunks_md5(
            table_context=target_table_context
        )

        LOGGER.debug(
            "Table to store the md5 chunks created for table %s",
            target_table_context.fully_qualified_name,
        )

    @log
    def _compute_md5(
        self, source_table_context: TableContext, target_table_context: TableContext
    ) -> None:
        self.context.output_handler.handle_message(
            message=(
                f"Computing MD5 for table {source_table_context.fully_qualified_name} "
                f"and table {target_table_context.fully_qualified_name}"
            ),
            level=OutputMessageLevel.INFO,
        )

        LOGGER.info(
            "Computing MD5 for table %s",
            source_table_context.fully_qualified_name,
        )

        self.source_extractor.compute_md5(
            table_context=source_table_context,
            other_table_name=target_table_context.table_name,
        )

        LOGGER.info(
            "Successfully computed MD5 for table %s",
            source_table_context.fully_qualified_name,
        )

        LOGGER.info(
            "Computing MD5 for table %s",
            target_table_context.fully_qualified_name,
        )

        self.target_extractor.compute_md5(
            table_context=target_table_context,
            other_table_name=source_table_context.table_name,
        )

        LOGGER.info(
            "Successfully computed MD5 for table %s",
            target_table_context.fully_qualified_name,
        )

        self.context.output_handler.handle_message(
            message=(
                f"Successfully computed MD5 for table "
                f"{source_table_context.fully_qualified_name} and table "
                f"{target_table_context.fully_qualified_name}"
            ),
            level=OutputMessageLevel.INFO,
        )

    @log
    def _validate_md5_rows_chunk(
        self,
        data_validator: RowDataValidator,
        compared_df: pd.DataFrame,
        source_table_context: TableContext,
        target_table_context: TableContext,
    ) -> None:

        source_index_column_collection = [
            column.name for column in source_table_context.index_column_collection
        ]
        target_index_column_collection = [
            column.name for column in target_table_context.index_column_collection
        ]

        rows_compared_df = pd.DataFrame()
        for _, row in compared_df.iterrows():

            current_chunk_id = row[CHUNK_ID_COLUMN_KEY]

            LOGGER.info(
                "Starting MD5 row validation for chunk %s in table %s and table %s",
                current_chunk_id,
                source_table_context.fully_qualified_name,
                target_table_context.fully_qualified_name,
            )

            LOGGER.debug(
                "Extracting MD5 rows for chunk %s in table %s",
                current_chunk_id,
                source_table_context.fully_qualified_name,
            )

            source_md5_rows_chunk = self.source_extractor.extract_md5_rows_chunk(
                chunk_id=current_chunk_id, table_context=source_table_context
            )

            LOGGER.debug(
                "Successfully extracted MD5 rows for chunk %s in table %s",
                current_chunk_id,
                source_table_context.fully_qualified_name,
            )

            LOGGER.debug(
                "Extracting MD5 rows for chunk %s in table %s",
                current_chunk_id,
                target_table_context.fully_qualified_name,
            )

            target_md5_rows_chunk = self.target_extractor.extract_md5_rows_chunk(
                chunk_id=current_chunk_id, table_context=target_table_context
            )

            LOGGER.debug(
                "Successfully extracted MD5 rows for chunk %s in table %s",
                current_chunk_id,
                target_table_context.fully_qualified_name,
            )

            LOGGER.info(
                "Starting MD5 rows for chunk %s comparison between table %s and table %s",
                current_chunk_id,
                source_table_context.fully_qualified_name,
                target_table_context.fully_qualified_name,
            )

            self.context.output_handler.handle_message(
                message=(
                    f"Starting MD5 rows for chunk {current_chunk_id} comparison between table "
                    f"{source_table_context.fully_qualified_name} and table "
                    f"{target_table_context.fully_qualified_name}"
                ),
                level=OutputMessageLevel.INFO,
            )

            source_index_column_suffix_collection = [
                column_name + SOURCE_SUFFIX
                for column_name in source_index_column_collection
            ]

            target_index_column_suffix_collection = [
                column_name + TARGET_SUFFIX
                for column_name in target_index_column_collection
            ]

            md5_rows_chunk_compared_df = data_validator.get_diff_md5_rows_chunk(
                source_md5_rows_chunk=source_md5_rows_chunk,
                target_md5_rows_chunk=target_md5_rows_chunk,
                source_index_column_collection=source_index_column_collection,
                target_index_column_collection=target_index_column_collection,
                source_index_column_suffix_collection=source_index_column_suffix_collection,
                target_index_column_suffix_collection=target_index_column_suffix_collection,
            )

            LOGGER.info(
                "Successfully completed MD5 rows for chunk %s comparison between table %s and table %s."
                "Differences found: \n%s",
                current_chunk_id,
                source_table_context.fully_qualified_name,
                target_table_context.fully_qualified_name,
                md5_rows_chunk_compared_df,
            )

            self.context.output_handler.handle_message(
                message=(
                    f"Successfully completed MD5 rows for chunk {current_chunk_id} "
                    f"comparison between table {source_table_context.fully_qualified_name} and table "
                    f"{target_table_context.fully_qualified_name}. Differences found:"
                ),
                level=OutputMessageLevel.INFO,
                dataframe=md5_rows_chunk_compared_df,
            )

            rows_compared_df = pd.concat([rows_compared_df, md5_rows_chunk_compared_df])

            if (
                len(md5_rows_chunk_compared_df)
                >= source_table_context.max_failed_rows_number
            ):
                LOGGER.warning(
                    "Maximum failed rows threshold (%d) reached during row validation "
                    "for tables %s and %s. Stopping further validation.",
                    source_table_context.max_failed_rows_number,
                    source_table_context.fully_qualified_name,
                    target_table_context.fully_qualified_name,
                )
                self.context.output_handler.handle_message(
                    header="Row validation stopped: maximum failed rows reached.",
                    message=(
                        f"Row validation between "
                        f"{source_table_context.fully_qualified_name} and "
                        f"{target_table_context.fully_qualified_name} was stopped because "
                        f"the number of failed rows ({len(md5_rows_chunk_compared_df)}) "
                        f"reached the configured threshold "
                        f"({source_table_context.max_failed_rows_number})."
                    ),
                    level=OutputMessageLevel.FAILURE,
                )
                break

            LOGGER.info(
                "Successfully completed MD5 row validation for chunk %s in table %s and table %s",
                current_chunk_id,
                source_table_context.fully_qualified_name,
                target_table_context.fully_qualified_name,
            )

        self.context.output_handler.handle_message(
            message=(
                f"Completing MD5 comparison between table "
                f"{source_table_context.fully_qualified_name} and table "
                f"{target_table_context.fully_qualified_name}"
            ),
            level=OutputMessageLevel.INFO,
        )

        LOGGER.info(
            "Generating row validation report for table %s and table %s",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

        data_validator.generate_row_validation_report(
            compared_df=rows_compared_df,
            fully_qualified_name=source_table_context.fully_qualified_name,
            target_fully_qualified_name=target_table_context.fully_qualified_name,
            source_index_column_suffix_collection=source_index_column_suffix_collection,
            target_index_column_suffix_collection=target_index_column_suffix_collection,
            context=self.context,
            table_id=source_table_context.id,
        )

        LOGGER.info(
            "Successfully generated row validation report for table %s and table %s",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

        LOGGER.info(
            "Generating row validation queries for table %s and table %s",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

        data_validator.generate_row_validation_queries(
            compared_df=rows_compared_df,
            fully_qualified_name=source_table_context.fully_qualified_name,
            target_fully_qualified_name=target_table_context.fully_qualified_name,
            source_index_column_suffix_collection=source_index_column_suffix_collection,
            target_index_column_suffix_collection=target_index_column_suffix_collection,
            context=self.context,
            table_id=source_table_context.id,
        )

        LOGGER.info(
            "Successfully generated row validation queries for table %s and table %s",
            source_table_context.fully_qualified_name,
            target_table_context.fully_qualified_name,
        )

    def _get_schema_validation_message(self, table_context: TableConfiguration) -> str:
        """Get sync validation message for schema validation."""
        return (
            f"Validating schema for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )

    def _get_metrics_validation_message(self, table_context: TableConfiguration) -> str:
        """Get sync validation message for metrics validation."""
        return (
            f"Validating metrics for {table_context.fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )

    def _get_row_validation_message(self, table_context: TableConfiguration) -> str:
        """Get sync validation message for row validation."""
        return (
            f"Validating rows for {table_context.fully_qualified_name} and {table_context.target_fully_qualified_name} "
            f"with columns {table_context.column_selection_list}."
        )
