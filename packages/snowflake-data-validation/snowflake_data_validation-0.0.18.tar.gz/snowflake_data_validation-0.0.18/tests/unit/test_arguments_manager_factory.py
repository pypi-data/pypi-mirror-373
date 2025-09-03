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

"""Tests for arguments_manager_factory module."""

import pytest
from unittest.mock import Mock, patch

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.snowflake.snowflake_arguments_manager import (
    SnowflakeArgumentsManager,
)
from snowflake.snowflake_data_validation.sqlserver.sqlserver_arguments_manager import (
    SqlServerArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_factory import (
    create_validation_environment_from_config,
    get_arguments_manager,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode


class TestGetArgumentsManager:
    """Test cases for get_arguments_manager function."""

    def test_get_arguments_manager_sqlserver_to_snowflake(self):
        """Test getting SqlServerArgumentsManager for SQL Server source."""
        args_manager = get_arguments_manager("SqlServer", "Snowflake")
        assert isinstance(args_manager, SqlServerArgumentsManager)

    def test_get_arguments_manager_snowflake_to_snowflake(self):
        """Test getting SnowflakeArgumentsManager for Snowflake source."""
        args_manager = get_arguments_manager("Snowflake", "Snowflake")
        assert isinstance(args_manager, SnowflakeArgumentsManager)


class TestCreateValidationEnvironmentFromConfig:
    """Test cases for create_validation_environment_from_config function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_config_model = Mock(spec=ConfigurationModel)
        self.mock_config_model.source_platform = "SqlServer"
        self.mock_config_model.target_platform = "Snowflake"
        self.data_validation_config_file = "/path/to/config.yaml"
        self.execution_mode = ExecutionMode.SYNC_VALIDATION

    @patch(
        "snowflake.snowflake_data_validation.utils.arguments_manager_factory.get_arguments_manager"
    )
    def test_create_validation_environment_from_config_with_output_handler(
        self, mock_get_args_manager
    ):
        """Test creating validation environment with provided output handler."""
        mock_args_manager = Mock()
        mock_validation_env = Mock()
        mock_output_handler = Mock(spec=ConsoleOutputHandler)
        mock_args_manager.create_validation_environment_from_config.return_value = (
            mock_validation_env
        )
        mock_get_args_manager.return_value = mock_args_manager

        result = create_validation_environment_from_config(
            config_model=self.mock_config_model,
            data_validation_config_file=self.data_validation_config_file,
            execution_mode=self.execution_mode,
            output_handler=mock_output_handler,
        )

        mock_get_args_manager.assert_called_once_with("SqlServer", "Snowflake")
        mock_args_manager.create_validation_environment_from_config.assert_called_once_with(
            config_model=self.mock_config_model,
            data_validation_config_file=self.data_validation_config_file,
            execution_mode=self.execution_mode,
            output_handler=mock_output_handler,
        )
        assert result == mock_validation_env

    @patch(
        "snowflake.snowflake_data_validation.utils.arguments_manager_factory.get_arguments_manager"
    )
    @patch(
        "snowflake.snowflake_data_validation.utils.arguments_manager_factory.ConsoleOutputHandler"
    )
    def test_create_validation_environment_from_config_without_output_handler(
        self, mock_console_handler_class, mock_get_args_manager
    ):
        """Test creating validation environment without provided output handler (uses default)."""
        mock_args_manager = Mock()
        mock_validation_env = Mock()
        mock_default_output_handler = Mock()
        mock_args_manager.create_validation_environment_from_config.return_value = (
            mock_validation_env
        )
        mock_get_args_manager.return_value = mock_args_manager
        mock_console_handler_class.return_value = mock_default_output_handler

        result = create_validation_environment_from_config(
            config_model=self.mock_config_model,
            data_validation_config_file=self.data_validation_config_file,
            execution_mode=self.execution_mode,
        )

        mock_get_args_manager.assert_called_once_with("SqlServer", "Snowflake")
        mock_console_handler_class.assert_called_once()
        mock_args_manager.create_validation_environment_from_config.assert_called_once_with(
            config_model=self.mock_config_model,
            data_validation_config_file=self.data_validation_config_file,
            execution_mode=self.execution_mode,
            output_handler=mock_default_output_handler,
        )
        assert result == mock_validation_env

    def test_create_validation_environment_from_config_missing_source_platform(self):
        """Test error handling when source_platform is missing from config."""
        config_without_source = Mock(spec=ConfigurationModel)
        config_without_source.source_platform = None

        with pytest.raises(typer.BadParameter) as exc_info:
            create_validation_environment_from_config(
                config_model=config_without_source,
                data_validation_config_file=self.data_validation_config_file,
                execution_mode=self.execution_mode,
            )

        assert "source_platform is required in configuration" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.utils.arguments_manager_factory.get_arguments_manager"
    )
    def test_create_validation_environment_from_config_propagates_errors(
        self, mock_get_args_manager
    ):
        """Test that errors from get_arguments_manager are properly propagated."""
        mock_get_args_manager.side_effect = typer.BadParameter(
            "Test error from get_arguments_manager"
        )

        with pytest.raises(typer.BadParameter) as exc_info:
            create_validation_environment_from_config(
                config_model=self.mock_config_model,
                data_validation_config_file=self.data_validation_config_file,
                execution_mode=self.execution_mode,
            )

        assert "Test error from get_arguments_manager" in str(exc_info.value)
