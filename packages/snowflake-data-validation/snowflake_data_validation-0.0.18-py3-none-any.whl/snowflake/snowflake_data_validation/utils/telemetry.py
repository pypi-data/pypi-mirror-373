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

"""Telemetry system for Snowflake Data Validation."""

import atexit
import datetime
import hashlib
import inspect
import json
import os
import re
import time

from contextlib import suppress
from functools import wraps
from pathlib import Path
from platform import python_version
from sys import platform
from typing import Any, Callable, Optional, TypeVar
from uuid import getnode

from snowflake.snowflake_data_validation.configuration.singleton import Singleton
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext
from snowflake.snowflake_data_validation.utils.run_context import RunContext

from .constants import (
    ASYNC_COMPARISON_EXECUTED,
    ASYNC_GENERATION_EXECUTED,
    COLUMN_SELECTION_USED_AS_EXCLUDED_KEY,
    CONFIG_FILE_CONNECTION_MODE,
    # Configuration model keys
    CONFIG_MODEL_KEY,
    CONNECTION_ESTABLISHED,
    CONNECTION_FAILED,
    CONNECTION_MODE_KEY,
    DATA_VALIDATION,
    DATA_VALIDATION_CONFIG_FILE_KEY,
    DURATION_KEY,
    ERROR_MESSAGE_KEY,
    FUNCTION_EXECUTED,
    # Telemetry data key constants
    FUNCTION_KEY,
    HAS_WHERE_CLAUSE_KEY,
    # Connection mode constants
    IPC_CONNECTION_MODE,
    IS_DATABASE_MAPPING_USED_KEY,
    IS_SCHEMA_MAPPING_USED_KEY,
    METRICS_VALIDATION,
    METRICS_VALIDATION_KEY,
    MODULE_NAME_KEY,
    PARALLELIZATION_KEY,
    ROW_VALIDATION_KEY,
    SCHEMA_VALIDATION,
    SCHEMA_VALIDATION_KEY,
    SOURCE_PLATFORM_KEY,
    SOURCE_TABLE_CONTEXT,
    # Platform constants
    SQL_SERVER_PLATFORM,
    # Module patterns
    SQLSERVER_MODULE_PATTERNS,
    SUCCESS_KEY,
    SYNC_COMPARISON_EXECUTED,
    # Table configuration keys
    TABLE_COUNT_KEY,
    TABLE_NAME_KEY,
    TARGET_PLATFORM_KEY,
    VALIDATION_FAILED,
    # Telemetry event constants
    VALIDATION_STARTED,
)


try:
    from snowflake.connector import SNOWFLAKE_CONNECTOR_VERSION, time_util
    from snowflake.connector.constants import DIRS as SNOWFLAKE_DIRS
    from snowflake.connector.network import SnowflakeRestful
    from snowflake.connector.telemetry import TelemetryClient
    from snowflake.snowpark.session import Session
    from snowflake.snowpark.version import VERSION as SNOWPARK_VERSION
except Exception:
    # Fallback values for environments without Snowflake dependencies
    SNOWFLAKE_CONNECTOR_VERSION = ""
    time_util = None
    SNOWFLAKE_DIRS = None
    SnowflakeRestful = None
    TelemetryClient = object
    SNOWPARK_VERSION = (0, 0, 0)
    Session = None


VERSION_VARIABLE_PATTERN = r"^__version__ = ['\"]([^'\"]*)['\"]"
VERSION_FILE_NAME = "__version__.py"


class DataValidationTelemetryManager(TelemetryClient, metaclass=Singleton):

    """Telemetry manager for data validation events.

    This is a singleton to ensure we only have one telemetry manager
    instance across all processes/threads during parallel execution.
    """

    def __init__(
        self,
        rest: Optional["SnowflakeRestful"] = None,
        is_telemetry_enabled: bool = True,
    ):
        """Initialize the DataValidationTelemetryManager."""
        if TelemetryClient is not object:
            super().__init__(rest)
        self._rest = rest

        # Setup telemetry configuration
        if SNOWFLAKE_DIRS:
            self.dv_folder_path = (
                Path(SNOWFLAKE_DIRS.user_config_path)
                / "snowflake-data-validation-telemetry"
            )
        else:
            self.dv_folder_path = (
                Path.home() / ".snowflake" / "snowflake-data-validation-telemetry"
            )

        self.dv_sf_path_telemetry = "/telemetry/send"
        self.dv_flush_size = 25
        self.dv_is_enabled = is_telemetry_enabled and self._dv_is_telemetry_enabled()
        self.dv_is_testing = self._dv_is_telemetry_testing()
        self.dv_memory_limit = 5 * 1024 * 1024  # 5MB
        self.dv_log_batch = []
        self.dv_version = _get_version()

        # Upload any existing local telemetry
        self._dv_upload_local_telemetry()

        # Register cleanup
        if rest and not self.dv_is_testing:
            atexit.register(self._dv_close_at_exit)

    def set_dv_output_path(self, path: Path) -> None:
        """Set the output path for testing."""
        path.mkdir(parents=True, exist_ok=True)
        self.dv_folder_path = path

    def dv_log_error(
        self, event_name: str, parameters_info: Optional[dict] = None
    ) -> dict:
        """Log an error telemetry event.

        Args:
            event_name (str): The name of the event.
            parameters_info (dict, optional): Additional parameters for the event. Defaults to None.

        Returns:
            dict: The logged event, or empty dict if telemetry is disabled.

        """
        if event_name is not None:
            return self._dv_log_telemetry(event_name, "error", parameters_info)
        return {}

    def dv_log_info(
        self, event_name: str, parameters_info: Optional[dict] = None
    ) -> dict:
        """Log an information telemetry event.

        Args:
            event_name (str): The name of the event.
            parameters_info (dict, optional): Additional parameters for the event. Defaults to None.

        Returns:
            dict: The logged event, or empty dict if telemetry is disabled.

        """
        if event_name is not None:
            return self._dv_log_telemetry(event_name, "info", parameters_info)
        return {}

    def _dv_log_telemetry(
        self, event_name: str, event_type: str, parameters_info: Optional[dict] = None
    ) -> dict:
        """Log a telemetry event if enabled."""
        if not self.dv_is_enabled:
            return {}

        event = _generate_data_validation_event(
            event_name, event_type, parameters_info, self.dv_version
        )
        self._dv_add_log_to_batch(event)
        return event

    def _dv_add_log_to_batch(self, event: dict) -> None:
        """Add a log event to the batch."""
        self.dv_log_batch.append(event)

        if self.dv_is_testing:
            self._dv_write_telemetry(self.dv_log_batch)
            self.dv_log_batch = []
            return

        if len(self.dv_log_batch) >= self.dv_flush_size:
            self.dv_send_batch(self.dv_log_batch)
            self.dv_log_batch = []

    def dv_send_batch(self, to_sent: list) -> bool:
        """Send a batch of events to the API."""
        if not self.dv_is_enabled:
            return False

        if self._rest is None:
            self._dv_write_telemetry(to_sent)
            self.dv_log_batch = []
            return False

        body = {"logs": to_sent}
        try:
            ret = self._rest.request(
                self.dv_sf_path_telemetry,
                body=body,
                method="post",
                client=None,
                timeout=5,
            )
            if ret.get("success"):
                return True
        except Exception:
            pass

        # Fallback to local storage
        self._dv_write_telemetry(to_sent)
        self.dv_log_batch = []
        return False

    def _dv_write_telemetry(self, batch: list) -> None:
        """Write telemetry events to local folder."""
        try:
            self.dv_folder_path.mkdir(parents=True, exist_ok=True)

            for event in batch:
                message = event.get("message")
                if message is not None:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
                    event_type = message.get("event_name", "unknown")
                    file_path = (
                        self.dv_folder_path / f"{timestamp}_telemetry_{event_type}.json"
                    )

                    json_content = self._dv_validate_folder_space(event)
                    file_path.write_text(json_content)
        except Exception:
            pass  # Silently fail telemetry writing

    def _dv_validate_folder_space(self, event: dict) -> str:
        """Validate and manage folder space for new events."""
        json_content = json.dumps(event, indent=4, sort_keys=True)
        new_file_size = len(json_content.encode("utf-8"))

        folder_size = _get_folder_size(self.dv_folder_path)
        if folder_size + new_file_size > self.dv_memory_limit:
            _free_up_space(self.dv_folder_path, self.dv_memory_limit - new_file_size)

        return json_content

    def _dv_upload_local_telemetry(self) -> None:
        """Upload any existing local telemetry events."""
        if not self.dv_is_enabled or self.dv_is_testing or not self._rest:
            return

        if not self.dv_folder_path.exists():
            return

        batch = []
        try:
            for file_path in self.dv_folder_path.glob("*.json"):
                json_content = file_path.read_text()
                data_dict = json.loads(json_content)
                batch.append(data_dict)

            if not batch:
                return

            body = {"logs": batch}
            ret = self._rest.request(
                self.dv_sf_path_telemetry,
                body=body,
                method="post",
                client=None,
                timeout=5,
            )

            if ret.get("success"):
                # Clean up uploaded files
                for file_path in self.dv_folder_path.glob("*.json"):
                    file_path.unlink()
        except Exception:
            pass  # Silently fail

    def _dv_is_telemetry_enabled(self) -> bool:
        """Check if telemetry is enabled by environment variable."""
        return (
            os.getenv("SNOWFLAKE_DATA_VALIDATION_TELEMETRY_ENABLED", "true").lower()
            == "true"
        )

    def _dv_is_telemetry_testing(self) -> bool:
        """Check if in testing mode."""
        is_testing = (
            os.getenv("SNOWFLAKE_DATA_VALIDATION_TELEMETRY_TESTING", "false").lower()
            == "true"
        )
        if is_testing:
            local_telemetry_path = Path.cwd() / "telemetry-output"
            self.set_dv_output_path(local_telemetry_path)
            self.dv_is_enabled = True
        return is_testing

    def _dv_close(self) -> None:
        """Close the telemetry manager and upload collected events."""
        atexit.unregister(self._dv_close_at_exit)
        if self.dv_log_batch and self.dv_is_enabled and not self.dv_is_testing:
            self.dv_send_batch(self.dv_log_batch)

    def _dv_close_at_exit(self) -> None:
        """Close the telemetry manager at exit."""
        with suppress(Exception):
            self._dv_close()


def _generate_data_validation_event(
    event_name: str,
    event_type: str,
    parameters_info: Optional[dict] = None,
    dv_version: Optional[str] = None,
) -> dict:
    """Generate a data validation telemetry event."""
    metadata = _get_metadata()
    if dv_version is not None:
        metadata["snowflake_data_validation_version"] = dv_version
    processed_params = parameters_info or {}

    message = {
        "event_type": event_type,
        "type": "snowflake-data-validation",
        "event_name": event_name,
        "driver_type": "PythonConnector",
        "driver_version": SNOWFLAKE_CONNECTOR_VERSION,
        "metadata": metadata,
        "data": json.dumps(processed_params),
    }

    timestamp = time_util.get_time_millis() if time_util else int(time.time() * 1000)
    return {"message": message, "timestamp": str(timestamp)}


def _get_metadata() -> dict:
    """Get metadata for telemetry events."""
    run_context = RunContext()

    metadata = {
        "os_version": platform,
        "python_version": python_version(),
        "device_id": _get_unique_id(),
        "run_id": run_context.run_id,
        "run_start_time": run_context.run_start_time,
    }

    if SNOWFLAKE_CONNECTOR_VERSION:
        metadata["snowflake_connector_version"] = SNOWFLAKE_CONNECTOR_VERSION
    if SNOWPARK_VERSION:
        metadata["snowpark_version"] = ".".join(
            str(x) for x in SNOWPARK_VERSION if x is not None
        )

    return metadata


def _get_version() -> Optional[str]:
    """Get the package version."""
    try:
        # Navigate up to find the version file
        current_dir = Path(__file__).resolve().parent
        for _ in range(5):  # Look up to 5 levels up
            version_file = current_dir / VERSION_FILE_NAME
            if version_file.exists():
                content = version_file.read_text()
                match = re.search(VERSION_VARIABLE_PATTERN, content, re.MULTILINE)
                if match:
                    return match.group(1)
            current_dir = current_dir.parent
        return None
    except Exception:
        return None


def _get_folder_size(folder_path: Path) -> int:
    """Get the size of a folder (JSON files only)."""
    total_size = 0
    if folder_path.exists():
        for file_path in folder_path.glob("*.json"):
            total_size += file_path.stat().st_size
    return total_size


def _free_up_space(folder_path: Path, max_size: int) -> None:
    """Free up space by deleting oldest files."""
    if not folder_path.exists():
        return

    files = sorted(folder_path.glob("*.json"), key=lambda f: f.stat().st_mtime)

    current_size = _get_folder_size(folder_path)
    for file_path in files:
        if current_size <= max_size:
            break
        current_size -= file_path.stat().st_size
        file_path.unlink()


def _get_unique_id() -> str:
    """Get a unique device ID based on hashed MAC address."""
    node_id_str = str(getnode())
    hashed_id = hashlib.sha256(node_id_str.encode()).hexdigest()
    return hashed_id


def get_telemetry_manager() -> DataValidationTelemetryManager:
    """Get the telemetry manager singleton instance."""
    try:
        if Session:
            connection = Session.builder.getOrCreate().connection
            return DataValidationTelemetryManager(
                connection._rest, connection.telemetry_enabled
            )
    except Exception:
        pass

    # Fallback to standalone telemetry manager
    telemetry_manager = DataValidationTelemetryManager(None, is_telemetry_enabled=True)
    telemetry_manager.dv_flush_size = 1
    return telemetry_manager


def extract_parameters(
    func: Callable, args: tuple, kwargs: dict, params_list: Optional[list[str]]
) -> dict:
    """Extract parameters from function arguments."""
    parameters = inspect.signature(func).parameters
    param_data = {}
    param_data["module_name"] = func.__module__

    if params_list:
        for param in params_list:
            try:
                if param in kwargs:
                    param_data[param] = kwargs[param]
                elif len(args) > 0:
                    param_names = list(parameters.keys())
                    if param in param_names:
                        index = param_names.index(param)
                        if index < len(args):
                            param_data[param] = args[index]
            except (IndexError, KeyError, ValueError):
                continue  # Skip parameters that can't be extracted

    return param_data


def validation_started_event(
    telemetry_data: dict, param_data: dict
) -> tuple[str, dict]:
    """Handle validation started event."""
    func_name = telemetry_data.get(FUNCTION_KEY, "")

    config_model = param_data.get(CONFIG_MODEL_KEY, None)
    if config_model:
        if hasattr(config_model, "source_platform") and config_model.source_platform:
            source_platform = config_model.source_platform.upper()
            telemetry_data[SOURCE_PLATFORM_KEY] = source_platform

        if hasattr(config_model, "target_platform") and config_model.target_platform:
            target_platform = config_model.target_platform.upper()
            telemetry_data[TARGET_PLATFORM_KEY] = target_platform

        if hasattr(config_model, "tables") and config_model.tables:
            telemetry_data[TABLE_COUNT_KEY] = len(config_model.tables)

        # Extract database mappings usage
        if hasattr(config_model, "database_mappings"):
            telemetry_data[IS_DATABASE_MAPPING_USED_KEY] = bool(
                config_model.database_mappings
            )

        # Extract schema mappings usage
        if hasattr(config_model, "schema_mappings"):
            telemetry_data[IS_SCHEMA_MAPPING_USED_KEY] = bool(
                config_model.schema_mappings
            )

        # Extract parallelization setting
        if hasattr(config_model, "parallelization"):
            telemetry_data[PARALLELIZATION_KEY] = config_model.parallelization

        # Extract validation configuration
        if (
            hasattr(config_model, "validation_configuration")
            and config_model.validation_configuration
        ):
            validation_config = config_model.validation_configuration
            if hasattr(validation_config, "schema_validation"):
                telemetry_data[
                    SCHEMA_VALIDATION_KEY
                ] = validation_config.schema_validation
            if hasattr(validation_config, "metrics_validation"):
                telemetry_data[
                    METRICS_VALIDATION_KEY
                ] = validation_config.metrics_validation
            if hasattr(validation_config, "row_validation"):
                telemetry_data[ROW_VALIDATION_KEY] = validation_config.row_validation

    if CONNECTION_MODE_KEY not in telemetry_data:
        if "ipc" in func_name:
            telemetry_data[CONNECTION_MODE_KEY] = IPC_CONNECTION_MODE
        elif "config" in func_name or DATA_VALIDATION_CONFIG_FILE_KEY in param_data:
            telemetry_data[CONNECTION_MODE_KEY] = CONFIG_FILE_CONNECTION_MODE

    return VALIDATION_STARTED, telemetry_data


def _extract_table_config_data(telemetry_data: dict, param_data: dict) -> dict:
    """Extract table configuration data for validation events."""
    source_context = param_data.get(SOURCE_TABLE_CONTEXT)
    table_context: TableContext = source_context

    if table_context:
        telemetry_data[HAS_WHERE_CLAUSE_KEY] = table_context.has_where_clause
        telemetry_data[COLUMN_SELECTION_USED_AS_EXCLUDED_KEY] = table_context.is_exclusion_mode
        telemetry_data[TABLE_NAME_KEY] = table_context.fully_qualified_name

    telemetry_data[SUCCESS_KEY] = param_data[SUCCESS_KEY]
    telemetry_data[DURATION_KEY] = param_data[DURATION_KEY]
    return telemetry_data


def schema_validation_event(telemetry_data: dict, param_data: dict) -> tuple[str, dict]:
    """Handle schema validation event."""
    telemetry_data = _extract_table_config_data(telemetry_data, param_data)

    if not telemetry_data[SUCCESS_KEY]:
        telemetry_data[ERROR_MESSAGE_KEY] = "Schema validation failed"
        return VALIDATION_FAILED, telemetry_data
    else:
        return SCHEMA_VALIDATION, telemetry_data


def metrics_validation_event(
    telemetry_data: dict, param_data: dict
) -> tuple[str, dict]:
    """Handle metrics validation event."""
    telemetry_data = _extract_table_config_data(telemetry_data, param_data)

    if not telemetry_data[SUCCESS_KEY]:
        telemetry_data[ERROR_MESSAGE_KEY] = "Metrics validation failed"
        return VALIDATION_FAILED, telemetry_data
    else:
        return METRICS_VALIDATION, telemetry_data


def row_validation_event(telemetry_data: dict, param_data: dict) -> tuple[str, dict]:
    """Handle row validation event."""
    telemetry_data = _extract_table_config_data(telemetry_data, param_data)

    if not telemetry_data[SUCCESS_KEY]:
        telemetry_data[ERROR_MESSAGE_KEY] = "Row validation failed"
        return VALIDATION_FAILED, telemetry_data
    else:
        return DATA_VALIDATION, telemetry_data


def connection_event(telemetry_data: dict, param_data: dict) -> tuple[str, dict]:
    """Handle connection event."""
    if MODULE_NAME_KEY in param_data:
        module_name = param_data[MODULE_NAME_KEY].lower()
        if any(pattern in module_name for pattern in SQLSERVER_MODULE_PATTERNS):
            telemetry_data[SOURCE_PLATFORM_KEY] = SQL_SERVER_PLATFORM

    telemetry_data[SUCCESS_KEY] = param_data[SUCCESS_KEY]

    if not telemetry_data[SUCCESS_KEY]:
        telemetry_data[ERROR_MESSAGE_KEY] = "Connection failed"
        return CONNECTION_FAILED, telemetry_data
    else:
        return CONNECTION_ESTABLISHED, telemetry_data


def orchestration_event(
    telemetry_data: dict, param_data: dict, func_name: str
) -> tuple[str, dict]:
    """Handle orchestration events for sync/async operations."""
    telemetry_data[SUCCESS_KEY] = param_data[SUCCESS_KEY]
    telemetry_data[DURATION_KEY] = param_data[DURATION_KEY]

    # Map function names to their success events and error messages
    if func_name == "run_sync_comparison":
        success_event = SYNC_COMPARISON_EXECUTED
        error_message = "Sync comparison failed"
    elif func_name == "run_async_generation":
        success_event = ASYNC_GENERATION_EXECUTED
        error_message = "Async generation failed"
    elif func_name == "run_async_comparison":
        success_event = ASYNC_COMPARISON_EXECUTED
        error_message = "Async comparison failed"
    else:
        # Fallback - shouldn't happen if called correctly
        success_event = FUNCTION_EXECUTED
        error_message = "Orchestration failed"

    if not telemetry_data[SUCCESS_KEY]:
        telemetry_data[ERROR_MESSAGE_KEY] = error_message
        return VALIDATION_FAILED, telemetry_data
    else:
        return success_event, telemetry_data


def handle_result(
    func_name: str,
    result: Any,
    param_data: dict,
    multiple_return: bool,
    return_indexes: Optional[list[tuple[str, int]]] = None,
) -> tuple[Optional[str], Optional[dict]]:
    """Handle the result of a function and collect telemetry data."""
    if result is not None and return_indexes is not None:
        if multiple_return:
            for name, index in return_indexes:
                try:
                    param_data[name] = result[index]
                except (IndexError, TypeError):
                    continue
        else:
            try:
                param_data[return_indexes[0][0]] = result[return_indexes[0][1]]
            except (IndexError, TypeError):
                pass

    telemetry_data = {FUNCTION_KEY: func_name}

    # Route to appropriate event handler based on function name
    # CLI Commands - Validation Started Events
    if func_name in ["create_validation_environment_from_config"]:
        return validation_started_event(telemetry_data, param_data)

    # Connection Events - detect platform from context
    elif func_name in ["connect"]:
        return connection_event(telemetry_data, param_data)

    # Schema Validation Events (was level_1_comparison)
    elif func_name in ["execute_schema_validation"]:
        return schema_validation_event(telemetry_data, param_data)

    # Metrics Validation Events (was level_2_comparison)
    elif func_name in ["execute_metrics_validation"]:
        return metrics_validation_event(telemetry_data, param_data)

    # Row Validation Events (new)
    elif func_name in ["execute_row_validation"]:
        return row_validation_event(telemetry_data, param_data)

    # Orchestration Events
    elif func_name in [
        "run_sync_comparison",
        "run_async_generation",
        "run_async_comparison",
    ]:
        return orchestration_event(telemetry_data, param_data, func_name)

    else:
        telemetry_data.update(param_data)
        return FUNCTION_EXECUTED, telemetry_data


fn = TypeVar("fn", bound=Callable)


def report_telemetry(
    params_list: Optional[list[str]] = None,
    return_indexes: Optional[list[tuple[str, int]]] = None,
    multiple_return: bool = False,
) -> Callable[[fn], fn]:
    """Report telemetry events for a function."""

    def report_telemetry_decorator(func: fn) -> fn:
        func_name = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            func_exception = None
            result = None
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
            except Exception as err:
                func_exception = err

            end_time = time.time()
            duration = int((end_time - start_time) * 1000)  # Duration in milliseconds

            # Check if telemetry is disabled
            if (
                os.getenv("SNOWFLAKE_DATA_VALIDATION_TELEMETRY_ENABLED", "true").lower()
                == "false"
            ):
                if func_exception is not None:
                    raise func_exception
                return result

            telemetry_event = None
            data = None
            telemetry_m = None

            try:
                param_data = extract_parameters(func, args, kwargs, params_list)
                # Add success and duration to param_data
                param_data[SUCCESS_KEY] = func_exception is None
                param_data[DURATION_KEY] = duration

                telemetry_m = get_telemetry_manager()
                telemetry_event, data = handle_result(
                    func_name,
                    result,
                    param_data,
                    multiple_return,
                    return_indexes,
                )
            except Exception:
                pass
            finally:
                if telemetry_m is not None and telemetry_event is not None:
                    if func_exception is not None:
                        telemetry_m.dv_log_error(telemetry_event, data)
                    else:
                        telemetry_m.dv_log_info(telemetry_event, data)

                if func_exception is not None:
                    raise func_exception

            return result

        return wrapper

    return report_telemetry_decorator
