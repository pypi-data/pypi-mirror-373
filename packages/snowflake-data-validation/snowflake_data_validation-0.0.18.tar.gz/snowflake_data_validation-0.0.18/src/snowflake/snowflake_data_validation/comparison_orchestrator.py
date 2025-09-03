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

from typing import Optional, Union

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.executer import (
    ExecutorFactory,
)
from snowflake.snowflake_data_validation.orchestration.parallel_execution_engine import (
    ParallelExecutionEngine,
)
from snowflake.snowflake_data_validation.orchestration.table_metadata_processor import (
    TableMetadataProcessor,
)
from snowflake.snowflake_data_validation.orchestration.validation_progress_reporter import (
    ValidationProgressReporter,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ValidationEnvironmentObject,
)
from snowflake.snowflake_data_validation.utils.connection_pool import (
    ConnectionPoolManager,
)
from snowflake.snowflake_data_validation.utils.constants import (
    TEMPORARY_DEFAULT_OPTIMAL_LIMIT,
    ExecutionMode,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.telemetry import (
    report_telemetry,
)


LOGGER = logging.getLogger(__name__)


class ComparisonOrchestrator:

    """Orchestrator for validation operations that creates appropriate components based on command type."""

    @log
    def __init__(
        self,
        connection_pool_manager: ConnectionPoolManager,
        context: Context,
        max_threads: int,
    ):
        """Initialize the orchestrator.

        Args:
            connection_pool_manager: Connection pool manager for threaded processing
            context: Validation context containing configuration and runtime info
            max_threads: Maximum number of threads for parallel table processing

        """
        LOGGER.debug("Initializing ComparisonOrchestrator")

        self.connection_pool_manager = connection_pool_manager
        self.context = context
        self.executor_factory = ExecutorFactory()
        self.max_threads = max_threads

        # Initialize orchestration modules
        self.metadata_processor = TableMetadataProcessor()
        self.execution_engine = ParallelExecutionEngine(max_threads=self.max_threads)
        self.progress_reporter = ValidationProgressReporter()

        LOGGER.debug(
            "ComparisonOrchestrator initialized with max_threads=%d", self.max_threads
        )

    @classmethod
    @log(log_args=False)
    def from_validation_environment(
        cls,
        validation_env: ValidationEnvironmentObject,
    ) -> "ComparisonOrchestrator":
        """Create a ComparisonOrchestrator from a ValidationEnvironmentObject.

        Args:
            validation_env: ValidationEnvironmentObject instance containing all required components

        Returns:
            ComparisonOrchestrator: Configured orchestrator ready to run validation

        """
        LOGGER.debug("Creating ComparisonOrchestrator from validation environment")

        config = validation_env.context.configuration
        num_tables: int = len(config.tables)
        max_threads_config: Union[str, int] = config.max_threads

        # Hardcoded optimal pool size for now, can be adjusted later on based on changes in SnowConvert AI
        optimal_max_threads: int = TEMPORARY_DEFAULT_OPTIMAL_LIMIT
        # CpuOptimizer.get_optimal_thread_count(num_tables=num_tables, max_threads=max_threads_config)
        optimal_pool_size: int = TEMPORARY_DEFAULT_OPTIMAL_LIMIT
        # optimal_max_threads

        LOGGER.debug(
            "Using CPUOptimizer: num_tables=%d, config_max_threads=%s, optimal_max_threads=%d, optimal_pool_size=%d",
            num_tables,
            max_threads_config,
            optimal_max_threads,
            optimal_pool_size,
        )

        connection_pool_manager: ConnectionPoolManager = (
            validation_env.create_connection_pool_manager(pool_size=optimal_pool_size)
        )

        return cls(
            connection_pool_manager=connection_pool_manager,
            context=validation_env.context,
            max_threads=optimal_max_threads,
        )

    @log
    @report_telemetry()
    def run_sync_comparison(self) -> None:
        """Run the complete synchronous validation comparison process using parallel execution.

        Uses the sync validation executor with metadata extractors for real-time validation.
        Each table is processed in a separate thread.
        """
        LOGGER.info("Starting synchronous validation comparison")
        self._execute_parallel_validation(ExecutionMode.SYNC_VALIDATION)
        self.progress_reporter.flush_validation_reports(self.context)
        LOGGER.info("Synchronous validation comparison completed")

    @log
    @report_telemetry()
    def run_async_generation(self) -> None:
        """Generate validation scripts for all tables in parallel.

        Uses script printers to write SQL queries to files.
        Each table is processed in a separate thread for maximum throughput.
        """
        LOGGER.info("Starting async script generation")
        self._execute_parallel_validation(
            ExecutionMode.ASYNC_GENERATION, use_script_printer=True
        )
        self.progress_reporter.flush_validation_reports(self.context)
        LOGGER.info("Async script generation completed")

    @log
    @report_telemetry()
    def run_async_comparison(self) -> None:
        """Run the asynchronous validation comparison process using parallel execution.

        Uses the async validation executor with metadata extractors for deferred validation.
        Each table is processed in a separate thread for maximum throughput.
        """
        LOGGER.info("Starting asynchronous validation comparison")
        self._execute_parallel_validation(ExecutionMode.ASYNC_VALIDATION)
        self.progress_reporter.flush_validation_reports(self.context)
        LOGGER.info("Asynchronous validation comparison completed")

    @log(log_args=False)
    def _get_validation_configuration(
        self,
        table: TableConfiguration,
        default_configuration: Optional[ValidationConfiguration],
    ) -> ValidationConfiguration:
        """Get the validation configuration for a table.

        Args:
            table: Table configuration object
            default_configuration: Default validation configuration

        Returns:
            ValidationConfiguration: The configuration to use for this table

        """
        if table.validation_configuration:
            LOGGER.debug(
                "Using table-specific validation configuration for %s",
                table.fully_qualified_name,
            )
            return table.validation_configuration
        elif default_configuration:
            LOGGER.debug(
                "Using default validation configuration for %s",
                table.fully_qualified_name,
            )
            return default_configuration
        else:
            LOGGER.debug(
                "Using empty validation configuration for %s",
                table.fully_qualified_name,
            )
            return ValidationConfiguration()

    @log
    def _execute_parallel_validation(
        self, execution_mode: ExecutionMode, use_script_printer: bool = False
    ) -> None:
        """Execute validation using parallel threads with connection pool.

        Args:
            execution_mode: The execution mode to use
            use_script_printer: Whether to use script printers instead of metadata extractors

        """
        self.connection_pool_manager.initialize_pool()

        LOGGER.debug(
            "Executing parallel validation with execution_mode=%s, use_script_printer=%s",
            execution_mode,
            use_script_printer,
        )

        self.execution_engine.execute_parallel_validation(
            tables=self.context.configuration.tables,
            default_configuration=self.context.configuration.validation_configuration,
            execution_mode=execution_mode,
            context=self.context,
            connection_pool=self.connection_pool_manager,
            use_script_printer=use_script_printer,
            progress_callback=lambda table_name, columns: self.progress_reporter.report_progress_for_table(
                table_name=table_name,
                column_selection_list=columns,
                context=self.context,
            ),
            validation_config_callback=lambda table, default_config: (
                self._get_validation_configuration(
                    table=table, default_configuration=default_config
                )
            ),
        )
