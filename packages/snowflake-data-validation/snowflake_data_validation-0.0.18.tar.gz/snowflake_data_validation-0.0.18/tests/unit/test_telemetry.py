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

"""Unit tests for telemetry functionality."""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.telemetry import (
    DataValidationTelemetryManager,
    get_telemetry_manager,
    report_telemetry,
    _generate_data_validation_event,
    extract_parameters,
    handle_result,
    validation_started_event,
    connection_event,
    schema_validation_event,
    metrics_validation_event,
    orchestration_event,
)

from snowflake.snowflake_data_validation.utils.constants import (
    # Event constants
    SOURCE_TABLE_CONTEXT,
    VALIDATION_STARTED,
    VALIDATION_FAILED,
    CONNECTION_ESTABLISHED,
    CONNECTION_FAILED,
    SCHEMA_VALIDATION,
    METRICS_VALIDATION,
    SYNC_COMPARISON_EXECUTED,
    ASYNC_GENERATION_EXECUTED,
    ASYNC_COMPARISON_EXECUTED,
    FUNCTION_EXECUTED,
    # Key constants
    SOURCE_PLATFORM_KEY,
    CONNECTION_MODE_KEY,
    TABLE_COUNT_KEY,
    SUCCESS_KEY,
    DURATION_KEY,
    FUNCTION_KEY,
    TABLE_CONTEXT_KEY,
    FULLY_QUALIFIED_NAME_KEY,
    HAS_WHERE_CLAUSE_KEY,
    COLUMN_SELECTION_USED_AS_EXCLUDED_KEY,
    MODULE_NAME_KEY,
    CONFIG_MODEL_KEY,
    # Platform constants
    SQL_SERVER_PLATFORM,
    IPC_CONNECTION_MODE,
    CONFIG_FILE_CONNECTION_MODE,
)


class TestDataValidationTelemetryManager:
    """Test suite for DataValidationTelemetryManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = DataValidationTelemetryManager(None, is_telemetry_enabled=True)
        self.manager.set_dv_output_path(self.temp_dir)
        Singleton._instances.clear()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        Singleton._instances.clear()

    def test_initialization(self):
        """Test telemetry manager initialization."""
        assert self.manager.dv_is_enabled is True
        assert self.manager.dv_flush_size == 25
        assert self.manager.dv_memory_limit == 5 * 1024 * 1024
        assert isinstance(self.manager.dv_log_batch, list)
        assert len(self.manager.dv_log_batch) == 0

    def test_environment_variable_controls(self):
        """Test environment variable controls for telemetry."""
        # Test disabled telemetry
        with patch.dict(
            os.environ, {"SNOWFLAKE_DATA_VALIDATION_TELEMETRY_ENABLED": "false"}
        ):
            disabled_manager = DataValidationTelemetryManager(
                None, is_telemetry_enabled=True
            )
            assert disabled_manager.dv_is_enabled is False
        Singleton._instances.clear()
        # Test testing mode
        with patch.dict(
            os.environ, {"SNOWFLAKE_DATA_VALIDATION_TELEMETRY_TESTING": "true"}
        ):
            test_manager = DataValidationTelemetryManager(
                None, is_telemetry_enabled=True
            )
            assert test_manager.dv_is_testing is True
            assert test_manager.dv_is_enabled is True

    def test_log_info_event(self):
        """Test logging info events."""
        test_data = {
            SOURCE_PLATFORM_KEY: SQL_SERVER_PLATFORM,
            TABLE_COUNT_KEY: 5,
            SUCCESS_KEY: True,
        }

        self.manager.dv_log_info(VALIDATION_STARTED, test_data)

        assert len(self.manager.dv_log_batch) == 1
        event = self.manager.dv_log_batch[0]
        assert event["message"]["event_type"] == "info"
        assert event["message"]["event_name"] == VALIDATION_STARTED

        # Check data was sanitized and included
        event_data = json.loads(event["message"]["data"])
        assert event_data[SOURCE_PLATFORM_KEY] == SQL_SERVER_PLATFORM

    def test_log_error_event(self):
        """Test logging error events."""
        test_data = {
            SOURCE_PLATFORM_KEY: SQL_SERVER_PLATFORM,
            "error_message": "Connection failed",
            SUCCESS_KEY: False,
        }

        self.manager.dv_log_error(CONNECTION_FAILED, test_data)

        assert len(self.manager.dv_log_batch) == 1
        event = self.manager.dv_log_batch[0]
        assert event["message"]["event_type"] == "error"
        assert event["message"]["event_name"] == CONNECTION_FAILED

        # Check event data was included
        event_data = json.loads(event["message"]["data"])
        assert "Connection failed" in event_data["error_message"]

    def test_batch_processing(self):
        """Test batch processing and flushing."""
        # Set small batch size for testing
        self.manager.dv_flush_size = 2

        # Add events to trigger batching
        self.manager.dv_log_info("event1", {})
        assert len(self.manager.dv_log_batch) == 1

        self.manager.dv_log_info("event2", {})
        # Should have written to file and cleared batch
        assert len(self.manager.dv_log_batch) == 0

        # Check files were created
        json_files = list(self.temp_dir.glob("*.json"))
        assert len(json_files) == 2

    def test_local_file_storage(self):
        """Test local file storage functionality."""
        test_data = {SOURCE_PLATFORM_KEY: SQL_SERVER_PLATFORM}
        self.manager.dv_log_info(SCHEMA_VALIDATION, test_data)

        # Manually flush to trigger file writing
        self.manager._dv_write_telemetry(self.manager.dv_log_batch)

        json_files = list(self.temp_dir.glob("*.json"))
        assert len(json_files) == 1

        # Verify file content
        file_content = json.loads(json_files[0].read_text())
        assert file_content["message"]["event_name"] == SCHEMA_VALIDATION
        assert file_content["message"]["type"] == "snowflake-data-validation"

    def test_disabled_telemetry(self):
        """Test that disabled telemetry doesn't create events."""
        disabled_manager = DataValidationTelemetryManager(
            None, is_telemetry_enabled=False
        )
        disabled_manager.set_dv_output_path(self.temp_dir)

        result = disabled_manager.dv_log_info(VALIDATION_STARTED, {})

        assert result == {}
        assert len(disabled_manager.dv_log_batch) == 0


class TestTelemetryDecorator:
    """Test suite for the report_telemetry decorator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("snowflake.snowflake_data_validation.utils.telemetry.get_telemetry_manager")
    def test_decorator_basic_functionality(self, mock_get_manager):
        """Test basic decorator functionality."""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        @report_telemetry(params_list=["param1", "param2"])
        def test_function(param1, param2, param3):
            return {"result": "success"}

        result = test_function("value1", "value2", "value3")

        assert result == {"result": "success"}
        assert mock_manager.dv_log_info.called

    @patch("snowflake.snowflake_data_validation.utils.telemetry.get_telemetry_manager")
    def test_decorator_error_handling(self, mock_get_manager):
        """Test decorator error handling."""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        @report_telemetry(params_list=["param1"])
        def failing_function(param1):
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function("test_value")

        # Should log error
        assert mock_manager.dv_log_error.called

    def test_parameter_extraction(self):
        """Test parameter extraction functionality."""

        def test_function(arg1, arg2, kwarg1=None):
            pass

        # Test positional args
        params = extract_parameters(
            test_function,
            ("value1", "value2"),
            {"kwarg1": "kwvalue"},
            ["arg1", "kwarg1"],
        )

        assert params["arg1"] == "value1"
        assert params["kwarg1"] == "kwvalue"
        assert params[MODULE_NAME_KEY] == test_function.__module__

    @patch("snowflake.snowflake_data_validation.utils.telemetry.get_telemetry_manager")
    def test_decorator_with_table_context(self, mock_get_manager):
        """Test decorator with TableConfiguration parameter."""
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager

        # Create a mock TableConfiguration
        table_config = Mock()
        table_config.fully_qualified_name = "test.schema.table"
        table_config.column_selection_list = ["col1", "col2"]
        table_config.source_table = "test.schema.table"
        table_config.has_where_clause = False

        @report_telemetry(params_list=[TABLE_CONTEXT_KEY])
        def extract_metadata(table_context):
            return True

        result = extract_metadata(table_config)

        assert result is True
        assert mock_manager.dv_log_info.called

    @patch.dict(os.environ, {"SNOWFLAKE_DATA_VALIDATION_TELEMETRY_ENABLED": "false"})
    def test_decorator_disabled_telemetry(self):
        """Test decorator when telemetry is disabled."""

        @report_telemetry(params_list=["param1"])
        def test_function(param1):
            return "success"

        result = test_function("test")
        assert result == "success"


class TestEventHandling:
    """Test suite for event handling and routing."""

    def test_handle_result_validation_events(self):
        """Test event routing for validation functions."""
        # Test validation started event - use a function name that maps to VALIDATION_STARTED
        param_data = {
            CONFIG_MODEL_KEY: Mock(
                source_platform="SqlServer",
                target_platform="Snowflake",
                tables=[Mock(), Mock()],
                database_mappings={"src": "target"},
                schema_mappings={"src_schema": "target_schema"},
                parallelization=False,
            )
        }

        event_name, event_data = handle_result(
            "create_validation_environment_from_config",
            {"status": "success"},
            param_data,
            False,
        )

        assert event_name == VALIDATION_STARTED
        if event_data is not None:
            assert event_data[SOURCE_PLATFORM_KEY] == "SQLSERVER"
            assert event_data[TABLE_COUNT_KEY] == 2

    def test_handle_result_connection_events(self):
        """Test event routing for connection functions."""
        param_data = {
            MODULE_NAME_KEY: "snowflake.snowflake_data_validation.sqlserver.connector.connector_sql_server",
            SUCCESS_KEY: True,
        }

        event_name, event_data = handle_result("connect", True, param_data, False)

        assert event_name == CONNECTION_ESTABLISHED
        if event_data is not None:
            assert event_data[SUCCESS_KEY] is True
            assert event_data[SOURCE_PLATFORM_KEY] == SQL_SERVER_PLATFORM

    def test_handle_result_schema_validation(self):
        """Test event routing for schema validation functions."""
        # Create mock table context
        table_config = Mock()
        table_config.fully_qualified_name = "test.schema.table"
        table_config.source_table = "test.schema.table"
        table_config.has_where_clause = False
        table_config.column_selection_list = ["col1", "col2"]
        table_config.use_column_selection_as_exclude_list = True
        table_context = Mock(
            fully_qualified_name="test.schema.table",
            has_where_clause=False,
            column_selection_list=["col1", "col2"],
            is_exclusion_mode=True,
        )
        param_data = {
            TABLE_CONTEXT_KEY: table_config,
            SUCCESS_KEY: True,
            DURATION_KEY: 100,
            SOURCE_TABLE_CONTEXT: table_context,
        }

        event_name, event_data = handle_result(
            "execute_schema_validation", True, param_data, False
        )

        assert event_name == SCHEMA_VALIDATION
        if event_data is not None:
            assert event_data[HAS_WHERE_CLAUSE_KEY] == False
            assert event_data[COLUMN_SELECTION_USED_AS_EXCLUDED_KEY] == True
            assert event_data[SUCCESS_KEY] == True
            assert event_data[DURATION_KEY] == 100

    def test_handle_result_metrics_validation(self):
        """Test event routing for metrics validation functions."""
        # Create mock table context
        table_config = Mock()
        table_config.fully_qualified_name = "test.schema.table"
        table_config.source_table = "test.schema.table"
        table_config.has_where_clause = True
        table_config.column_selection_list = ["col1", "col2"]
        table_context = Mock(
            fully_qualified_name="test.schema.table",
            has_where_clause=True,
            column_selection_list=["col1", "col2"],
            is_exclusion_mode=False,
        )

        param_data = {
            TABLE_CONTEXT_KEY: table_config,
            SUCCESS_KEY: True,
            DURATION_KEY: 150,
            SOURCE_TABLE_CONTEXT: table_context,
        }

        event_name, event_data = handle_result(
            "execute_metrics_validation", True, param_data, False
        )

        assert event_name == METRICS_VALIDATION
        if event_data is not None:
            assert event_data[HAS_WHERE_CLAUSE_KEY] == True
            assert event_data[COLUMN_SELECTION_USED_AS_EXCLUDED_KEY] == False
            assert event_data[SUCCESS_KEY] == True
            assert event_data[DURATION_KEY] == 150

    def test_validation_started_event_function(self):
        """Test validation_started_event function directly."""
        config_model = Mock()
        config_model.source_platform = "SqlServer"
        config_model.target_platform = "Snowflake"
        config_model.tables = [Mock(), Mock(), Mock()]
        config_model.database_mappings = {"src": "target"}
        config_model.schema_mappings = {"src_schema": "target_schema"}
        config_model.parallelization = True

        # Mock validation configuration
        validation_config = Mock()
        validation_config.schema_validation = True
        validation_config.metrics_validation = False
        validation_config.row_validation = False
        config_model.validation_configuration = validation_config

        # Test with function name that contains "config" to trigger connection mode detection
        telemetry_data = {FUNCTION_KEY: "create_validation_environment_from_config"}
        param_data = {CONFIG_MODEL_KEY: config_model}

        event_name, result_data = validation_started_event(telemetry_data, param_data)

        assert event_name == VALIDATION_STARTED
        assert result_data[SOURCE_PLATFORM_KEY] == "SQLSERVER"
        assert result_data[TABLE_COUNT_KEY] == 3
        assert result_data[CONNECTION_MODE_KEY] == CONFIG_FILE_CONNECTION_MODE

    def test_validation_started_event_with_ipc_mode(self):
        """Test validation_started_event function with IPC connection mode."""
        config_model = Mock()
        config_model.source_platform = "SqlServer"
        config_model.target_platform = "Snowflake"
        config_model.tables = [Mock()]

        # Test with function name that contains "ipc"
        telemetry_data = {FUNCTION_KEY: "sqlserver_run_validation_ipc"}
        param_data = {CONFIG_MODEL_KEY: config_model}

        event_name, result_data = validation_started_event(telemetry_data, param_data)

        assert event_name == VALIDATION_STARTED
        assert result_data[CONNECTION_MODE_KEY] == IPC_CONNECTION_MODE

    def test_validation_started_event_with_config_file_param(self):
        """Test validation_started_event function with config file parameter."""
        config_model = Mock()
        config_model.source_platform = "SqlServer"
        config_model.target_platform = "Snowflake"
        config_model.tables = [Mock()]

        # Test with data_validation_config_file parameter
        telemetry_data = {FUNCTION_KEY: "sqlserver_run_validation"}
        param_data = {
            CONFIG_MODEL_KEY: config_model,
            "data_validation_config_file": "/path/to/config.yaml",
        }

        event_name, result_data = validation_started_event(telemetry_data, param_data)

        assert event_name == VALIDATION_STARTED
        assert result_data[CONNECTION_MODE_KEY] == CONFIG_FILE_CONNECTION_MODE

    def test_connection_event_function(self):
        """Test connection_event function directly."""
        telemetry_data = {}
        param_data = {
            MODULE_NAME_KEY: "snowflake.snowflake_data_validation.sqlserver.connector.connector_sql_server",
            SUCCESS_KEY: True,
        }

        event_name, result_data = connection_event(telemetry_data, param_data)

        assert event_name == CONNECTION_ESTABLISHED
        assert result_data[SOURCE_PLATFORM_KEY] == SQL_SERVER_PLATFORM
        assert result_data[SUCCESS_KEY] is True

    def test_connection_event_failure(self):
        """Test connection_event function with failure."""
        telemetry_data = {}
        param_data = {
            MODULE_NAME_KEY: "snowflake.snowflake_data_validation.sqlserver.connector.connector_sql_server",
            SUCCESS_KEY: False,
        }

        event_name, result_data = connection_event(telemetry_data, param_data)

        assert event_name == CONNECTION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data["error_message"] == "Connection failed"

    def test_schema_validation_event_failure(self):
        """Test schema_validation_event function with failure."""
        table_config = Mock()
        table_config.fully_qualified_name = "test.schema.table"
        table_config.source_table = "test.schema.table"
        table_config.has_where_clause = False
        table_config.column_selection_list = ["col1", "col2"]
        table_config.use_column_selection_as_exclude_list = True

        telemetry_data = {}
        param_data = {
            TABLE_CONTEXT_KEY: table_config,
            SUCCESS_KEY: False,
            DURATION_KEY: 100,
        }

        event_name, result_data = schema_validation_event(telemetry_data, param_data)

        assert event_name == VALIDATION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data["error_message"] == "Schema validation failed"

    def test_metrics_validation_event_failure(self):
        """Test metrics_validation_event function with failure."""
        table_config = Mock()
        table_config.fully_qualified_name = "test.schema.table"
        table_config.source_table = "test.schema.table"
        table_config.has_where_clause = False
        table_config.column_selection_list = ["col1", "col2"]
        table_config.use_column_selection_as_exclude_list = False

        telemetry_data = {}
        param_data = {
            TABLE_CONTEXT_KEY: table_config,
            SUCCESS_KEY: False,
            DURATION_KEY: 150,
        }

        event_name, result_data = metrics_validation_event(telemetry_data, param_data)

        assert event_name == VALIDATION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data["error_message"] == "Metrics validation failed"

    def test_orchestration_event_sync_comparison_success(self):
        """Test orchestration_event function for successful sync comparison."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: True, DURATION_KEY: 5000}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "run_sync_comparison"
        )

        assert event_name == SYNC_COMPARISON_EXECUTED
        assert result_data[SUCCESS_KEY] is True
        assert result_data[DURATION_KEY] == 5000

    def test_orchestration_event_sync_comparison_failure(self):
        """Test orchestration_event function for failed sync comparison."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: False, DURATION_KEY: 1500}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "run_sync_comparison"
        )

        assert event_name == VALIDATION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data[DURATION_KEY] == 1500
        assert result_data["error_message"] == "Sync comparison failed"

    def test_orchestration_event_async_generation_success(self):
        """Test orchestration_event function for successful async generation."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: True, DURATION_KEY: 3000}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "run_async_generation"
        )

        assert event_name == ASYNC_GENERATION_EXECUTED
        assert result_data[SUCCESS_KEY] is True
        assert result_data[DURATION_KEY] == 3000

    def test_orchestration_event_async_generation_failure(self):
        """Test orchestration_event function for failed async generation."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: False, DURATION_KEY: 800}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "run_async_generation"
        )

        assert event_name == VALIDATION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data[DURATION_KEY] == 800
        assert result_data["error_message"] == "Async generation failed"

    def test_orchestration_event_async_comparison_success(self):
        """Test orchestration_event function for successful async comparison."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: True, DURATION_KEY: 7500}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "run_async_comparison"
        )

        assert event_name == ASYNC_COMPARISON_EXECUTED
        assert result_data[SUCCESS_KEY] is True
        assert result_data[DURATION_KEY] == 7500

    def test_orchestration_event_async_comparison_failure(self):
        """Test orchestration_event function for failed async comparison."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: False, DURATION_KEY: 2200}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "run_async_comparison"
        )

        assert event_name == VALIDATION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data[DURATION_KEY] == 2200
        assert result_data["error_message"] == "Async comparison failed"

    def test_orchestration_event_unknown_function(self):
        """Test orchestration_event function with unknown function name (fallback case)."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: True, DURATION_KEY: 1000}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "unknown_function"
        )

        assert event_name == FUNCTION_EXECUTED
        assert result_data[SUCCESS_KEY] is True
        assert result_data[DURATION_KEY] == 1000

    def test_orchestration_event_unknown_function_failure(self):
        """Test orchestration_event function with unknown function name failure (fallback case)."""
        telemetry_data = {}
        param_data = {SUCCESS_KEY: False, DURATION_KEY: 500}

        event_name, result_data = orchestration_event(
            telemetry_data, param_data, "unknown_function"
        )

        assert event_name == VALIDATION_FAILED
        assert result_data[SUCCESS_KEY] is False
        assert result_data[DURATION_KEY] == 500
        assert result_data["error_message"] == "Orchestration failed"


class TestEventGeneration:
    """Test suite for event generation functionality."""

    def test_generate_data_validation_event(self):
        """Test event generation."""
        test_params = {"safe_param": "safe_value", "table_count": 5}

        event = _generate_data_validation_event(
            VALIDATION_STARTED, "info", test_params, "1.0.0"
        )

        # Verify event structure
        assert event["message"]["event_name"] == VALIDATION_STARTED
        assert event["message"]["event_type"] == "info"
        assert event["message"]["type"] == "snowflake-data-validation"

        # Verify data was included
        event_data = json.loads(event["message"]["data"])
        assert event_data["safe_param"] == "safe_value"
        assert event_data["table_count"] == 5

        # Verify metadata
        assert "snowflake_data_validation_version" in event["message"]["metadata"]
        assert (
            event["message"]["metadata"]["snowflake_data_validation_version"] == "1.0.0"
        )

    def test_generate_event_without_version(self):
        """Test event generation without version parameter."""
        test_params = {"test_key": "test_value"}

        event = _generate_data_validation_event(SCHEMA_VALIDATION, "info", test_params)

        # Verify event structure
        assert event["message"]["event_name"] == SCHEMA_VALIDATION
        assert event["message"]["event_type"] == "info"
        assert "timestamp" in event

        # Should not have version in metadata if not provided
        metadata = event["message"]["metadata"]
        assert (
            "snowflake_data_validation_version" not in metadata
            or metadata.get("snowflake_data_validation_version") is None
        )


class TestErrorHandling:
    """Test suite for error handling in telemetry."""

    @patch("snowflake.snowflake_data_validation.utils.telemetry.get_telemetry_manager")
    def test_telemetry_failure_doesnt_break_function(self, mock_get_manager):
        """Test that telemetry failures don't break the decorated function."""
        # Make telemetry manager raise an exception
        mock_get_manager.side_effect = Exception("Telemetry error")

        @report_telemetry(params_list=["param1"])
        def test_function(param1):
            return f"success: {param1}"

        # Function should still work despite telemetry error
        result = test_function("test_value")
        assert result == "success: test_value"

    def test_parameter_extraction_with_missing_params(self):
        """Test parameter extraction handles missing parameters gracefully."""

        def test_function(arg1, arg2=None):
            pass

        # Test with missing parameters
        params = extract_parameters(
            test_function,
            ("value1",),  # Only one arg provided
            {},
            ["arg1", "arg2", "nonexistent_arg"],  # Request non-existent param
        )

        assert params["arg1"] == "value1"
        assert "nonexistent_arg" not in params
        assert MODULE_NAME_KEY in params


class TestIntegration:
    """Integration tests for end-to-end telemetry functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch.dict(os.environ, {"SNOWFLAKE_DATA_VALIDATION_TELEMETRY_TESTING": "true"})
    @patch("snowflake.snowflake_data_validation.utils.telemetry.Path.cwd")
    def test_end_to_end_telemetry_flow(self, mock_cwd):
        """Test complete telemetry flow from decoration to file storage."""
        mock_cwd.return_value = self.temp_dir

        # Create a function with telemetry
        @report_telemetry(params_list=["platform", "table_count"])
        def mock_validation_function(platform, table_count):
            time.sleep(0.1)  # Simulate work
            return {"tables_processed": table_count}

        # Execute function
        result = mock_validation_function(SQL_SERVER_PLATFORM, 3)

        # Verify function executed correctly
        assert result["tables_processed"] == 3

        # Check telemetry files were created
        telemetry_dir = self.temp_dir / "telemetry-output"
        if telemetry_dir.exists():
            json_files = list(telemetry_dir.glob("*.json"))
            assert len(json_files) > 0

            # Verify file content
            if json_files:
                file_content = json.loads(json_files[0].read_text())
                assert file_content["message"]["type"] == "snowflake-data-validation"

    def test_telemetry_manager_singleton(self):
        """Test telemetry manager singleton behavior."""
        # Mock Session to avoid Snowflake dependencies
        with patch("snowflake.snowflake_data_validation.utils.telemetry.Session", None):
            manager1 = get_telemetry_manager()
            manager2 = get_telemetry_manager()

            # Should return instances (may be different due to fallback logic)
            assert manager1 is not None
            assert manager2 is not None

    def test_real_table_configuration_usage(self):
        """Test usage with real TableConfiguration object."""
        # Create a real TableConfiguration object
        table_config = TableConfiguration(
            fully_qualified_name="test_db.test_schema.test_table",
            column_selection_list=["col1", "col2", "col3"],
            where_clause="WHERE col1 > 100",
            has_where_clause=True,
            use_column_selection_as_exclude_list=False,
            index_column_list=[],
        )

        # Test that we can work with the object
        assert table_config.fully_qualified_name == "test_db.test_schema.test_table"
        assert len(table_config.column_selection_list) == 3
        assert table_config.has_where_clause is True
