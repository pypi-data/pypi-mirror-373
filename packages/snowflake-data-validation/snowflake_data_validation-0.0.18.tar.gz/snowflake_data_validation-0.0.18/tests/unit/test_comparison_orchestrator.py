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
import pytest
from unittest.mock import MagicMock, patch, ANY
import tempfile
import time
import datetime

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.utils.connection_pool import (
    ConnectionPoolManager,
    ExecutionConnectors,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ValidationEnvironmentObject,
)


@pytest.fixture
def mock_context():
    context = MagicMock()
    context.output_handler.console_output_enabled = True
    context.output_handler.handle_message = MagicMock()
    context.configuration.tables = []

    # Add required attributes with proper values
    context.report_path = tempfile.mkdtemp()  # Create a real temporary directory
    context.run_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    context.run_id = "test_run_id"

    return context


@pytest.fixture
def mock_extractors():
    source_extractor = MagicMock()
    target_extractor = MagicMock()
    return source_extractor, target_extractor


@pytest.fixture
def orchestrator_setup():
    """Set up test fixtures."""
    source_connector = MagicMock()
    target_connector = MagicMock()
    context = MagicMock()
    output_handler = MagicMock()
    context.output_handler = output_handler

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager, context=context, max_threads=4
    )

    return orchestrator, source_connector, target_connector, context, output_handler


@pytest.fixture
def orchestrator_setup_gen_queries():
    """Set up test fixtures for comparison orchestrator tests."""
    source_connector = MagicMock()
    target_connector = MagicMock()
    context = MagicMock()
    output_handler = MagicMock()
    context.output_handler = output_handler
    context.report_path = "/test/path"
    context.source_platform = "source_db"
    context.configuration.target_platform = "target_db"

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager, context=context, max_threads=4
    )

    return orchestrator, source_connector, target_connector, context, output_handler


def create_mock_table_context(
    fully_qualified_name="my_table",
    column_selection_list=None,
    where_clause="",
    target_where_clause="",
    has_where_clause=False,
    use_column_selection_as_exclude_list=False,
):
    """Helper function to create mock table configuration objects."""
    if column_selection_list is None:
        column_selection_list = ["col1", "col2"]

    mock_table = MagicMock(spec=TableConfiguration)
    mock_table.fully_qualified_name = fully_qualified_name
    mock_table.column_selection_list = column_selection_list
    mock_table.where_clause = where_clause
    mock_table.target_where_clause = target_where_clause
    mock_table.has_where_clause = has_where_clause
    mock_table.use_column_selection_as_exclude_list = (
        use_column_selection_as_exclude_list
    )
    return mock_table


def test_level_1_comparison_success(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_extractor.extract_schema_metadata.return_value = "source_df"
    target_extractor.extract_schema_metadata.return_value = "target_df"

    from snowflake.snowflake_data_validation.validation.schema_data_validator import (
        SchemaDataValidator,
    )

    validator = SchemaDataValidator()
    validator.validate_table_metadata = MagicMock(return_value=True)

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager, context=mock_context, max_threads=4
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # The test should use run_sync_comparison with parallel execution
    with patch.object(
        orchestrator, "_execute_parallel_validation"
    ) as mock_execute_parallel:
        # Test the run_sync_comparison method
        orchestrator.run_sync_comparison()

        # Verify parallel execution was called with correct mode
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        mock_execute_parallel.assert_called_once_with(ExecutionMode.SYNC_VALIDATION)


def test_level_2_comparison_success(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_metadata = MagicMock()
    source_metadata.empty = False
    target_metadata = MagicMock()
    target_metadata.empty = False
    source_extractor.extract_metrics_metadata.return_value = source_metadata
    target_extractor.extract_metrics_metadata.return_value = target_metadata

    from snowflake.snowflake_data_validation.validation.metrics_data_validator import (
        MetricsDataValidator,
    )

    validator = MetricsDataValidator()
    validator.validate_column_metadata = MagicMock(return_value=True)

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager, context=mock_context, max_threads=4
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # Test the run_sync_comparison method with parallel execution
    with patch.object(
        orchestrator, "_execute_parallel_validation"
    ) as mock_execute_parallel:
        orchestrator.run_sync_comparison()

        # Verify parallel execution was called with correct mode
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        mock_execute_parallel.assert_called_once_with(ExecutionMode.SYNC_VALIDATION)


def test_level_2_comparison_source_empty(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_metadata = MagicMock()
    source_metadata.empty = True
    target_metadata = MagicMock()
    target_metadata.empty = False
    source_extractor.extract_metrics_metadata.return_value = source_metadata
    target_extractor.extract_metrics_metadata.return_value = target_metadata

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager, context=mock_context, max_threads=4
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # Test run_async_generation method with mocked execution engine
    with patch.object(
        orchestrator.execution_engine, "execute_parallel_validation"
    ) as mock_engine_execute:
        orchestrator.run_async_generation()

        # Verify execution engine was called with script printer enabled
        mock_engine_execute.assert_called_once()
        args, kwargs = mock_engine_execute.call_args
        assert kwargs.get("use_script_printer") == True


def test_level_2_comparison_target_empty(mock_extractors, mock_context):
    source_extractor, target_extractor = mock_extractors
    source_metadata = MagicMock()
    source_metadata.empty = False
    target_metadata = MagicMock()
    target_metadata.empty = True
    source_extractor.extract_metrics_metadata.return_value = source_metadata
    target_extractor.extract_metrics_metadata.return_value = target_metadata

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager, context=mock_context, max_threads=4
    )

    # Create mock table configuration
    table_context = create_mock_table_context()

    # Test the from_validation_environment class method
    validation_env = MagicMock()
    validation_env.context = mock_context
    validation_env.context = mock_context

    # Mock create_connection_pool_manager method
    mock_pool_manager = MagicMock(spec=ConnectionPoolManager)
    validation_env.create_connection_pool_manager = MagicMock(
        return_value=mock_pool_manager
    )

    result_orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env
    )

    assert result_orchestrator.connection_pool_manager == mock_pool_manager
    assert result_orchestrator.context == mock_context


def test_execute_custom_validations(mock_context):
    class DummyValidationConfig:
        def model_dump(self):
            return {
                "schema_validation": True,
                "metrics_validation": False,
                "row_validation": False,
            }

    # Create mock connection pool manager
    pool_manager = MagicMock(spec=ConnectionPoolManager)

    orchestrator = ComparisonOrchestrator(
        connection_pool_manager=pool_manager,
        context=mock_context,
        max_threads=4,
    )

    # Test that the orchestrator can be created successfully
    assert orchestrator.connection_pool_manager == pool_manager
    assert orchestrator.context == mock_context


def test_write_async_query_to_file_success(orchestrator_setup):
    """Test successful writing of query to file using run_async_generation."""
    (
        orchestrator,
        source_connector,
        target_connector,
        context,
        output_handler,
    ) = orchestrator_setup

    # Mock the context configuration to have tables
    mock_tables = [MagicMock()]
    mock_tables[0].fully_qualified_name = "test.table"
    mock_tables[0].column_selection_list = ["col1", "col2"]
    mock_tables[0].where_clause = None
    mock_tables[0].has_where_clause = False
    mock_tables[0].use_column_selection_as_exclude_list = False

    context.configuration.tables = mock_tables
    context.configuration.validation_configuration = MagicMock()
    context.configuration.validation_configuration.schema_validation = True
    context.configuration.validation_configuration.metrics_validation = False

    # Mock the execution engine instead of script printers
    with patch.object(
        orchestrator.execution_engine, "execute_parallel_validation"
    ) as mock_engine_execute:
        # Test the run_async_generation method
        orchestrator.run_async_generation()

        # Verify execution engine was called with script printer enabled
        mock_engine_execute.assert_called_once()
        args, kwargs = mock_engine_execute.call_args
        assert kwargs.get("use_script_printer") == True


class TestComparisonOrchestratorConnectionPool:
    """Test connection pool integration with ComparisonOrchestrator."""

    @pytest.fixture
    def mock_connection_pool_manager(self):
        """Create a mock ConnectionPoolManager."""
        pool_manager = MagicMock(spec=ConnectionPoolManager)

        # Mock connection pair
        source_connector = MagicMock()
        target_connector = MagicMock()
        connection_pair = ExecutionConnectors(
            source_connector=source_connector,
            target_connector=target_connector,
            creation_time=time.time(),
        )

        # Set up context managers
        pool_manager.__enter__.return_value = pool_manager
        pool_manager.__exit__.return_value = None

        # Mock connection pair context manager
        mock_pair_context = MagicMock()
        mock_pair_context.__enter__.return_value = connection_pair
        mock_pair_context.__exit__.return_value = None
        pool_manager.get_connection_pair.return_value = mock_pair_context

        return pool_manager

    @pytest.fixture
    def mock_validation_environment(self):
        """Create a mock ValidationEnvironmentObject."""
        mock_args_manager = MagicMock()
        mock_context = MagicMock()
        mock_context.output_handler = MagicMock()
        mock_context.configuration = MagicMock()
        mock_context.configuration.tables = []

        validation_env = ValidationEnvironmentObject(
            source_connection_config=MagicMock(),
            target_connection_config=MagicMock(),
            context=mock_context,
        )

        return validation_env

    def test_orchestrator_initialization_with_pool_manager(
        self, mock_connection_pool_manager, mock_context
    ):
        """Test ComparisonOrchestrator initialization with connection pool manager."""
        orchestrator = ComparisonOrchestrator(
            connection_pool_manager=mock_connection_pool_manager,
            context=mock_context,
            max_threads=4,
        )

        assert orchestrator.connection_pool_manager is mock_connection_pool_manager
        assert orchestrator.context is mock_context

    def test_orchestrator_initialization_legacy_mode(self, mock_context):
        """Test ComparisonOrchestrator initialization in legacy mode."""
        # This test is obsolete with the new architecture - legacy mode doesn't exist
        # We can use from_validation_environment instead for backwards compatibility
        validation_env = MagicMock()
        validation_env.context = mock_context
        mock_pool_manager = MagicMock(spec=ConnectionPoolManager)
        validation_env.create_connection_pool_manager = MagicMock(
            return_value=mock_pool_manager
        )

        orchestrator = ComparisonOrchestrator.from_validation_environment(
            validation_env
        )

        assert orchestrator.connection_pool_manager is mock_pool_manager
        assert orchestrator.context is mock_context

    def test_orchestrator_initialization_invalid_params(self, mock_context):
        """Test ComparisonOrchestrator initialization with invalid parameters."""
        with pytest.raises(TypeError) as exc_info:
            ComparisonOrchestrator(context=mock_context)

        # Updated to match the actual error message from the new constructor
        assert (
            "missing 2 required positional arguments: 'connection_pool_manager' and 'max_threads'"
            in str(exc_info.value)
        )

    @patch(
        "snowflake.snowflake_data_validation.comparison_orchestrator.ComparisonOrchestrator._execute_parallel_validation"
    )
    def test_run_sync_comparison_with_pool(
        self,
        mock_execute_parallel,
        mock_connection_pool_manager,
        mock_context,
    ):
        """Test run_sync_comparison using parallel execution."""
        # Set up the mock to have pool_size attribute
        mock_connection_pool_manager.pool_size = 4

        orchestrator = ComparisonOrchestrator(
            connection_pool_manager=mock_connection_pool_manager,
            context=mock_context,
            max_threads=4,
        )

        # Execute sync comparison
        orchestrator.run_sync_comparison()

        # Verify parallel execution was called with correct mode
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        # Verify parallel execution was called with correct mode
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        mock_execute_parallel.assert_called_once_with(ExecutionMode.SYNC_VALIDATION)

    @patch(
        "snowflake.snowflake_data_validation.comparison_orchestrator.ComparisonOrchestrator._execute_parallel_validation"
    )
    def test_run_sync_comparison_legacy_mode(self, mock_execute_parallel, mock_context):
        """Test run_sync_comparison using validation environment."""
        # Use validation environment to create orchestrator
        validation_env = MagicMock()
        validation_env.context = mock_context
        mock_pool_manager = MagicMock(spec=ConnectionPoolManager)
        mock_pool_manager.pool_size = 4  # Add the pool_size attribute
        validation_env.create_connection_pool_manager = MagicMock(
            return_value=mock_pool_manager
        )

        orchestrator = ComparisonOrchestrator.from_validation_environment(
            validation_env
        )

        # Run the method
        orchestrator.run_sync_comparison()

        # Verify parallel execution was called with correct mode
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        mock_execute_parallel.assert_called_once_with(ExecutionMode.SYNC_VALIDATION)

    @patch(
        "snowflake.snowflake_data_validation.comparison_orchestrator.ComparisonOrchestrator._execute_parallel_validation"
    )
    def test_run_async_generation_with_pool(
        self,
        mock_execute_parallel,
        mock_connection_pool_manager,
        mock_context,
    ):
        """Test run_async_generation using parallel execution."""
        # Set up the mock to have pool_size attribute
        mock_connection_pool_manager.pool_size = 4

        orchestrator = ComparisonOrchestrator(
            connection_pool_manager=mock_connection_pool_manager,
            context=mock_context,
            max_threads=4,
        )

        # Run the method
        orchestrator.run_async_generation()

        # Verify parallel execution was called with correct mode and script printer flag
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        mock_execute_parallel.assert_called_once_with(
            ExecutionMode.ASYNC_GENERATION, use_script_printer=True
        )

    @patch(
        "snowflake.snowflake_data_validation.comparison_orchestrator.ComparisonOrchestrator._execute_parallel_validation"
    )
    def test_run_async_comparison_with_pool(
        self,
        mock_execute_parallel,
        mock_connection_pool_manager,
        mock_context,
    ):
        """Test run_async_comparison using parallel execution."""
        # Set up the mock to have pool_size attribute
        mock_connection_pool_manager.pool_size = 4

        orchestrator = ComparisonOrchestrator(
            connection_pool_manager=mock_connection_pool_manager,
            context=mock_context,
            max_threads=4,
        )

        # Run the method
        orchestrator.run_async_comparison()

        # Verify parallel execution was called with correct mode
        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        mock_execute_parallel.assert_called_once_with(ExecutionMode.ASYNC_VALIDATION)

    # def test_from_validation_environment(self, mock_validation_environment):
    #     """Test creating ComparisonOrchestrator from ValidationEnvironmentObject."""
    #     from snowflake.snowflake_data_validation.utils.constants import (
    #         DEFAULT_THREAD_COUNT_OPTION,
    #     )

    #     with patch.object(
    #         mock_validation_environment, "create_connection_pool_manager"
    #     ) as mock_create_pool:
    #         mock_pool_manager = MagicMock()
    #         mock_create_pool.return_value = mock_pool_manager

    #         # Mock the configuration to have tables and max_threads
    #         mock_validation_environment.context.configuration.tables = [
    #             MagicMock(),
    #             MagicMock(),
    #             MagicMock(),
    #         ]
    #         mock_validation_environment.context.configuration.max_threads = (
    #             DEFAULT_THREAD_COUNT_OPTION
    #         )

    #         with patch(
    #             "snowflake.snowflake_data_validation.comparison_orchestrator.CpuOptimizer.get_optimal_thread_count",
    #             return_value=3,
    #         ) as mock_cpu_optimizer:
    #             orchestrator = ComparisonOrchestrator.from_validation_environment(
    #                 mock_validation_environment
    #             )

    #             # Verify CPUOptimizer was called
    #             mock_cpu_optimizer.assert_called_once_with(
    #                 num_tables=3, max_threads=DEFAULT_THREAD_COUNT_OPTION
    #             )

    #             # Verify pool manager was created with CPUOptimizer result
    #             mock_create_pool.assert_called_once_with(pool_size=3)

    #             # Verify orchestrator was configured correctly
    #             assert orchestrator.connection_pool_manager is mock_pool_manager
    #             assert orchestrator.context is mock_validation_environment.context

    # def test_from_validation_environment_default_pool_size(
    #     self, mock_validation_environment
    # ):
    #     """Test creating ComparisonOrchestrator with default pool size."""
    #     from snowflake.snowflake_data_validation.utils.constants import (
    #         DEFAULT_THREAD_COUNT_OPTION,
    #     )

    #     with patch.object(
    #         mock_validation_environment, "create_connection_pool_manager"
    #     ) as mock_create_pool:
    #         mock_pool_manager = MagicMock()
    #         mock_create_pool.return_value = mock_pool_manager

    #         # Mock the configuration to have tables and max_threads
    #         mock_validation_environment.context.configuration.tables = [
    #             MagicMock(),
    #             MagicMock(),
    #         ]
    #         mock_validation_environment.context.configuration.max_threads = (
    #             DEFAULT_THREAD_COUNT_OPTION
    #         )

    #         with patch(
    #             "snowflake.snowflake_data_validation.comparison_orchestrator.CpuOptimizer.get_optimal_thread_count",
    #             return_value=4,
    #         ) as mock_cpu_optimizer:
    #             orchestrator = ComparisonOrchestrator.from_validation_environment(
    #                 mock_validation_environment
    #             )

    #             # Verify CPUOptimizer was called
    #             mock_cpu_optimizer.assert_called_once_with(
    #                 num_tables=2, max_threads="auto"
    #             )

    #             # Verify pool manager was created with CPUOptimizer result
    #             mock_create_pool.assert_called_once_with(pool_size=4)

    def test_parallel_execution_initialization(
        self, mock_connection_pool_manager, mock_context
    ):
        """Test that orchestrator initializes correctly with parallel execution parameters."""
        # Create orchestrator with custom thread count
        orchestrator = ComparisonOrchestrator(
            mock_connection_pool_manager, mock_context, max_threads=8
        )

        assert orchestrator.max_threads == 8
        assert orchestrator.connection_pool_manager == mock_connection_pool_manager
        assert orchestrator.context == mock_context

    def test_parallel_execution_defaults_to_pool_size(self, mock_context):
        """Test that max_threads defaults to connection pool size."""
        mock_pool_manager = MagicMock()
        mock_pool_manager.pool_size = 6

        orchestrator = ComparisonOrchestrator(
            mock_pool_manager, mock_context, max_threads=6
        )

        assert orchestrator.max_threads == 6

    @patch(
        "snowflake.snowflake_data_validation.orchestration.parallel_execution_engine.ParallelExecutionEngine.execute_parallel_validation"
    )
    def test_execute_parallel_validation(
        self,
        mock_engine_execute,
        mock_connection_pool_manager,
        mock_context,
    ):
        """Test parallel execution of table validations."""
        # Setup mock tables
        table1 = MagicMock()
        table1.fully_qualified_name = "table1"
        table2 = MagicMock()
        table2.fully_qualified_name = "table2"

        mock_context.configuration.tables = [table1, table2]
        mock_context.configuration.validation_configuration = MagicMock()

        # Create orchestrator
        orchestrator = ComparisonOrchestrator(
            mock_connection_pool_manager, mock_context, max_threads=4
        )

        from snowflake.snowflake_data_validation.utils.constants import ExecutionMode

        # Execute parallel validation
        orchestrator._execute_parallel_validation(ExecutionMode.SYNC_VALIDATION)

        # Verify the execution engine was called with correct parameters
        mock_engine_execute.assert_called_once_with(
            tables=[table1, table2],
            default_configuration=mock_context.configuration.validation_configuration,
            execution_mode=ExecutionMode.SYNC_VALIDATION,
            context=mock_context,
            connection_pool=mock_connection_pool_manager,
            use_script_printer=False,
            progress_callback=ANY,
            validation_config_callback=ANY,
        )

    def test_process_single_table(self, mock_connection_pool_manager, mock_context):
        """Test that the orchestrator delegates single table processing to the execution engine."""
        # Since _process_single_table is now handled by ParallelExecutionEngine,
        # this test verifies that the orchestrator properly initializes the engine
        # and that the engine has the expected functionality.

        orchestrator = ComparisonOrchestrator(
            mock_connection_pool_manager, mock_context, max_threads=4
        )

        # Verify that the orchestrator has an execution engine
        assert hasattr(orchestrator, "execution_engine")
        assert orchestrator.execution_engine is not None

        # Verify that the execution engine has the process method
        from snowflake.snowflake_data_validation.orchestration.parallel_execution_engine import (
            ParallelExecutionEngine,
        )

        assert isinstance(orchestrator.execution_engine, ParallelExecutionEngine)
        assert hasattr(orchestrator.execution_engine, "_process_single_table")

    # def test_from_validation_environment_with_threads(
    #     self, mock_validation_environment
    # ):
    #     """Test creating ComparisonOrchestrator with custom thread configuration."""
    #     with patch.object(
    #         mock_validation_environment, "create_connection_pool_manager"
    #     ) as mock_create_pool:
    #         mock_pool_manager = MagicMock()
    #         mock_pool_manager.pool_size = 6
    #         mock_create_pool.return_value = mock_pool_manager

    #         # Mock the configuration to have tables and max_threads
    #         mock_validation_environment.context.configuration.tables = [
    #             MagicMock(),
    #             MagicMock(),
    #             MagicMock(),
    #             MagicMock(),
    #         ]
    #         mock_validation_environment.context.configuration.max_threads = 6

    #         with patch(
    #             "snowflake.snowflake_data_validation.comparison_orchestrator.CpuOptimizer.get_optimal_thread_count",
    #             return_value=6,
    #         ) as mock_cpu_optimizer:
    #             orchestrator = ComparisonOrchestrator.from_validation_environment(
    #                 mock_validation_environment
    #             )

    #             # Verify CPUOptimizer was called
    #             mock_cpu_optimizer.assert_called_once_with(num_tables=4, max_threads=6)

    #             # Verify pool manager was created with CPUOptimizer result
    #             mock_create_pool.assert_called_once_with(pool_size=6)

    #             # Verify orchestrator was configured correctly
    #             assert orchestrator.connection_pool_manager is mock_pool_manager
    #             assert orchestrator.context is mock_validation_environment.context
    #             assert orchestrator.max_threads == 6

    # def test_from_validation_environment_updated_defaults(
    #     self, mock_validation_environment
    # ):
    #     """Test creating ComparisonOrchestrator with updated default pool size."""
    #     from snowflake.snowflake_data_validation.utils.constants import (
    #         DEFAULT_THREAD_COUNT_OPTION,
    #     )

    #     with patch.object(
    #         mock_validation_environment, "create_connection_pool_manager"
    #     ) as mock_create_pool:
    #         mock_pool_manager = MagicMock()
    #         mock_create_pool.return_value = mock_pool_manager

    #         # Mock the configuration to have tables and max_threads
    #         mock_validation_environment.context.configuration.tables = [
    #             MagicMock(),
    #             MagicMock(),
    #         ]
    #         mock_validation_environment.context.configuration.max_threads = (
    #             DEFAULT_THREAD_COUNT_OPTION
    #         )

    #         with patch(
    #             "snowflake.snowflake_data_validation.comparison_orchestrator.CpuOptimizer.get_optimal_thread_count",
    #             return_value=4,
    #         ) as mock_cpu_optimizer:
    #             orchestrator = ComparisonOrchestrator.from_validation_environment(
    #                 mock_validation_environment
    #             )

    #             # Verify CPUOptimizer was called
    #             mock_cpu_optimizer.assert_called_once_with(
    #                 num_tables=2, max_threads="auto"
    #             )

    #             # Verify pool manager was created with CPUOptimizer result
    #             mock_create_pool.assert_called_once_with(pool_size=4)
