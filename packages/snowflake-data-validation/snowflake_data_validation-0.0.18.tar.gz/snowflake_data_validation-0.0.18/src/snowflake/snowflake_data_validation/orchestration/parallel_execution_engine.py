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
import threading

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Callable, Optional

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.executer import ExecutorFactory
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
)
from snowflake.snowflake_data_validation.executer.extractor_types import ExtractorType
from snowflake.snowflake_data_validation.orchestration.table_metadata_processor import (
    TableMetadataProcessor,
)
from snowflake.snowflake_data_validation.utils.connection_pool import (
    ConnectionPoolManager,
    ExecutionConnectors,
)
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode, Platform
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log


LOGGER = logging.getLogger(__name__)


class ParallelExecutionEngine:

    """Handles parallel execution of table validation tasks using thread pools."""

    def __init__(self, max_threads: int):
        """Initialize the parallel execution engine.

        Args:
            max_threads: Maximum number of threads for parallel processing

        """
        self.max_threads = max_threads
        self.executor_factory = ExecutorFactory()
        self.metadata_processor = TableMetadataProcessor()

    @log
    def execute_parallel_validation(
        self,
        tables: list[TableConfiguration],
        default_configuration: ValidationConfiguration,
        execution_mode: ExecutionMode,
        context: Context,
        connection_pool: ConnectionPoolManager,
        use_script_printer: bool = False,
        progress_callback: Optional[Callable[[str, list[str]], None]] = None,
        validation_config_callback: Optional[
            Callable[
                [TableConfiguration, ValidationConfiguration], ValidationConfiguration
            ]
        ] = None,
    ) -> None:
        """Execute validation for tables in parallel using thread pool.

        Args:
            tables: List of table configurations to process
            default_configuration: Default validation configuration
            execution_mode: The execution mode to use
            context: Validation context
            connection_pool: Connection pool manager
            use_script_printer: Whether to use script printers instead of metadata extractors
            progress_callback: Optional callback for progress reporting
            validation_config_callback: Optional callback for getting validation configuration

        """
        LOGGER.info(
            "Starting parallel validation execution for %d tables using %d threads",
            len(tables),
            self.max_threads,
        )

        with ThreadPoolExecutor(max_workers=self.max_threads) as thread_executor:
            # Submit all table validation tasks
            future_to_table: dict[Future[None], TableConfiguration] = {}

            for table_configuration in tables:
                future = thread_executor.submit(
                    self._process_single_table,
                    table_configuration,
                    default_configuration,
                    execution_mode,
                    context,
                    connection_pool,
                    use_script_printer,
                    progress_callback,
                    validation_config_callback,
                )
                future_to_table[future] = table_configuration

            # Process completed tasks
            completed_count = 0
            failed_count = 0

            for future in as_completed(future_to_table):
                table_config = future_to_table[future]

                try:
                    future.result()  # This will raise any exception from the thread
                    completed_count += 1
                    LOGGER.info(
                        "Successfully completed table %s (%d/%d)",
                        table_config.fully_qualified_name,
                        completed_count + failed_count,
                        len(tables),
                    )
                except Exception as e:
                    failed_count += 1
                    LOGGER.error(
                        "Failed to process table %s: %s (%d/%d)",
                        table_config.fully_qualified_name,
                        str(e),
                        completed_count + failed_count,
                        len(tables),
                    )

        LOGGER.info(
            "Parallel validation execution completed. Success: %d, Failed: %d, Total: %d",
            completed_count,
            failed_count,
            len(tables),
        )

    @log
    def _process_single_table(
        self,
        table_configuration: TableConfiguration,
        default_configuration: ValidationConfiguration,
        execution_mode: ExecutionMode,
        context: Context,
        connection_pool: ConnectionPoolManager,
        use_script_printer: bool,
        progress_callback: Optional[Callable[[str, list[str]], None]] = None,
        validation_config_callback: Optional[
            Callable[
                [TableConfiguration, ValidationConfiguration], ValidationConfiguration
            ]
        ] = None,
    ) -> None:
        """Process a single table validation in a separate thread.

        Args:
            table_configuration: Configuration for the table to process
            default_configuration: Default validation configuration
            execution_mode: The execution mode to use
            context: Validation context
            connection_pool: Connection pool manager to get connections from
            use_script_printer: Whether to use script printers instead of metadata extractors
            progress_callback: Optional callback for progress reporting
            validation_config_callback: Optional callback for getting validation configuration

        """
        LOGGER.info(
            "Processing table: %s (Thread: %s)",
            table_configuration.fully_qualified_name,
            threading.current_thread().name,
        )

        # Report progress for this table (IPC mode)
        if progress_callback:
            try:
                progress_callback(
                    table_configuration.fully_qualified_name,
                    table_configuration.column_selection_list,
                )
            except OSError as e:
                if (
                    isinstance(e, BrokenPipeError) or e.errno == 32
                ):  # 32 is the error code for BrokenPipeError
                    LOGGER.warning(
                        "BrokenPipeError: Failed to report progress for table %s: %s. "
                        "This is non-critical and validation will continue.",
                        table_configuration.fully_qualified_name,
                        str(e),
                    )
                else:
                    LOGGER.error(
                        "OSError when reporting progress for table %s: %s",
                        table_configuration.fully_qualified_name,
                        str(e),
                    )
            except Exception as e:
                LOGGER.error(
                    "Unexpected error when reporting progress for table %s: %s",
                    table_configuration.fully_qualified_name,
                    str(e),
                )

        # Get validation configuration for this table (each table can have its own config)
        if validation_config_callback:
            validation_config = validation_config_callback(
                table_configuration, default_configuration
            )
        else:
            validation_config = default_configuration

        with connection_pool.get_connection_pair() as connection_pair:
            try:
                source_extractor, target_extractor = self._create_extractors(
                    connection_pair,
                    context,
                    execution_mode,
                    use_script_printer,
                )

                executor: BaseValidationExecutor = (
                    self.executor_factory.create_executor(
                        execution_mode,
                        source_extractor=source_extractor,
                        target_extractor=target_extractor,
                        context=context,
                    )
                )

                (
                    source_table_column_metadata,
                    target_table_column_metadata,
                ) = self.metadata_processor.generate_table_column_metadata(
                    table_configuration=table_configuration,
                    source_extractor=source_extractor,
                    target_extractor=target_extractor,
                    context=context,
                )

                # Execute validation for this table
                executor.execute_validation_levels(
                    validation_config,
                    table_configuration,
                    source_table_column_metadata,
                    target_table_column_metadata,
                )

                LOGGER.info(
                    "Completed processing table: %s (Thread: %s)",
                    table_configuration.fully_qualified_name,
                    threading.current_thread().name,
                )

            except Exception as e:
                LOGGER.error(
                    "Error processing table %s in thread %s: %s",
                    table_configuration.fully_qualified_name,
                    threading.current_thread().name,
                    str(e),
                )
                raise

    def _create_metadata_extractor(
        self, connector: ConnectorBase, platform: Platform, context: Context
    ) -> ConnectorBase:
        """Create the appropriate metadata extractor based on platform."""
        return self.executor_factory.create_extractor_from_connector(
            connector=connector,
            extractor_type=ExtractorType.METADATA_EXTRACTOR,
            platform=platform,
            report_path=context.report_path,
        )

    def _create_script_printer(
        self, connector: ConnectorBase, platform: Platform, context: Context
    ) -> ConnectorBase:
        """Create the appropriate script printer based on platform."""
        return self.executor_factory.create_extractor_from_connector(
            connector=connector,
            extractor_type=ExtractorType.SCRIPT_WRITER,
            platform=platform,
            report_path=context.report_path,
        )

    def _create_extractors(
        self,
        connection_pair: ExecutionConnectors,
        context: Context,
        execution_mode: ExecutionMode,
        use_script_printer: bool,
    ) -> tuple[ConnectorBase, ConnectorBase]:
        """Create source and target extractors based on the configuration.

        Args:
            connection_pair: The connection pair containing source and target connectors
            context: Validation context
            execution_mode: The execution mode to use
            use_script_printer: Whether to use script printers instead of metadata extractors

        Returns:
            tuple: (source_extractor, target_extractor)

        """
        if use_script_printer:
            source_extractor = self._create_script_printer(
                connection_pair.source_connector,
                context.source_platform,
                context,
            )
            target_extractor = self._create_script_printer(
                connection_pair.target_connector,
                context.target_platform,
                context,
            )
        else:
            source_extractor = self._create_metadata_extractor(
                connection_pair.source_connector,
                context.source_platform,
                context,
            )
            target_extractor = self._create_metadata_extractor(
                connection_pair.target_connector,
                context.target_platform,
                context,
            )

        return source_extractor, target_extractor
