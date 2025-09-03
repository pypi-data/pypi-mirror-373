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

from typing import Optional

from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.progress_reporter import (
    ProgressMetadata,
    report_progress,
)
from snowflake.snowflake_data_validation.validation.validation_report_buffer import (
    ValidationReportBuffer,
)


LOGGER = logging.getLogger(__name__)


class ValidationProgressReporter:

    """Handles progress reporting and validation report management."""

    @log
    def report_progress_for_table(
        self,
        table_name: str,
        column_selection_list: list[str],
        context: Optional[Context] = None,
    ) -> None:
        """Report progress for a specific table.

        Args:
            table_name: Name of the table being processed
            column_selection_list: List of columns being validated
            context: Validation context for run_id and run_start_time (optional)

        """
        # Only report progress if console output is not enabled
        if (
            context
            and hasattr(context, "output_handler")
            and not context.output_handler.console_output_enabled
        ):
            LOGGER.debug(
                "Reporting progress for table: %s with %d columns",
                table_name,
                len(column_selection_list),
            )
            progress_metadata = ProgressMetadata(
                table=table_name,
                columns=column_selection_list,
                run_id=context.run_id,
                run_start_time=context.run_start_time,
            )
            try:
                report_progress(progress_metadata)
            except OSError as e:
                if (
                    isinstance(e, BrokenPipeError) or e.errno == 32
                ):  # 32 is the error code for BrokenPipeError
                    LOGGER.warning(
                        "BrokenPipeError: Failed to report progress for table: %s. "
                        "This typically occurs when the parent process has closed the pipe. "
                        "This is non-critical and validation will continue.",
                        table_name,
                    )
                else:
                    LOGGER.warning(
                        "OSError reporting progress for table %s: %s. "
                        "This is non-critical and validation will continue.",
                        table_name,
                        str(e),
                    )
            except Exception as e:
                LOGGER.warning(
                    "Error reporting progress for table %s: %s. "
                    "This is non-critical and validation will continue.",
                    table_name,
                    str(e),
                )

    @log
    def flush_validation_reports(self, context: Context) -> None:
        """Flush all buffered validation data to the report file.

        This method is called after all tables have been processed to write
        all accumulated validation results to the CSV report file.

        Args:
            context: Validation context containing report path and timing info

        """
        buffer = ValidationReportBuffer()

        if buffer.has_data():
            report_file_path = buffer.flush_to_file(context)
            LOGGER.info(
                "Successfully flushed validation report buffer to: %s", report_file_path
            )
        else:
            LOGGER.info("No validation data to flush - buffer is empty")
