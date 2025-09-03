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

"""Tests for SQL Server CLI functions and commands."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import typer
from typer.testing import CliRunner

from snowflake.snowflake_data_validation.sqlserver.sqlserver_cli import (
    sqlserver_app,
    build_snowflake_credentials,
    create_environment_from_config,
    handle_validation_errors,
    sqlserver_run_validation,
    sqlserver_run_validation_ipc,
    sqlserver_run_async_generation,
)
from snowflake.snowflake_data_validation.utils.constants import (
    ExecutionMode,
    COLUMN_DATATYPES_MAPPING_NAME_FORMAT,
    COLUMN_METRICS_TEMPLATE_NAME_FORMAT,
    COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT,
    Platform,
)


class TestSqlServerCLI:
    """Test cases for SQL Server CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_build_snowflake_credentials_all_params(self):
        """Test building Snowflake credentials with all parameters."""
        credentials = build_snowflake_credentials(
            account="test_account",
            username="test_user",
            database="test_db",
            schema="test_schema",
            warehouse="test_wh",
            role="test_role",
            authenticator="snowflake",
            password="test_pass",
        )

        expected = {
            "account": "test_account",
            "username": "test_user",
            "database": "test_db",
            "schema": "test_schema",
            "warehouse": "test_wh",
            "role": "test_role",
            "authenticator": "snowflake",
            "password": "test_pass",
        }

        assert credentials == expected

    def test_build_snowflake_credentials_partial_params(self):
        """Test building Snowflake credentials with partial parameters."""
        credentials = build_snowflake_credentials(
            account="test_account", username="test_user", database="test_db"
        )

        expected = {
            "account": "test_account",
            "username": "test_user",
            "database": "test_db",
        }

        assert credentials == expected

    def test_build_snowflake_credentials_empty_params(self):
        """Test building Snowflake credentials with no parameters."""
        credentials = build_snowflake_credentials()
        assert credentials == {}

    @patch(
        "snowflake.snowflake_data_validation.utils.validation_utils.create_validation_environment_from_config"
    )
    @patch(
        "snowflake.snowflake_data_validation.utils.validation_utils.ConfigurationLoader"
    )
    @patch(
        "snowflake.snowflake_data_validation.utils.validation_utils.ConsoleOutputHandler"
    )
    def test_create_environment_from_config(
        self, mock_output_handler_class, mock_config_loader, mock_create_env
    ):
        """Test creating validation environment from config file."""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_model = Mock()
        mock_output_handler = Mock()
        mock_config_loader.return_value = mock_config_instance
        mock_config_instance.get_configuration_model.return_value = mock_config_model
        mock_output_handler_class.return_value = mock_output_handler
        mock_env = Mock()
        mock_create_env.return_value = mock_env

        result = create_environment_from_config(
            "test_config.yaml", ExecutionMode.SYNC_VALIDATION, console_output=True
        )

        # Verify the mocks were called correctly
        mock_config_loader.assert_called_once()
        mock_config_instance.get_configuration_model.assert_called_once()
        mock_output_handler_class.assert_called_once_with(enable_console_output=True)
        mock_create_env.assert_called_once_with(
            config_model=mock_config_model,
            data_validation_config_file="test_config.yaml",
            execution_mode=ExecutionMode.SYNC_VALIDATION,
            output_handler=mock_output_handler,
        )
        assert result == mock_env

    def test_handle_validation_errors_decorator(self):
        """Test the validation errors decorator."""

        @handle_validation_errors
        def test_func():
            raise typer.BadParameter("Test error")

        with pytest.raises(typer.Exit):
            test_func()

    def test_handle_validation_errors_file_not_found(self):
        """Test validation errors decorator with FileNotFoundError."""

        @handle_validation_errors
        def test_func():
            raise FileNotFoundError("Config file not found")

        with pytest.raises(typer.Exit):
            test_func()

    def test_handle_validation_errors_connection_error(self):
        """Test validation errors decorator with ConnectionError."""

        @handle_validation_errors
        def test_func():
            raise ConnectionError("Connection failed")

        with pytest.raises(typer.Exit):
            test_func()

    def test_handle_validation_errors_generic_exception(self):
        """Test validation errors decorator with generic exception."""

        @handle_validation_errors
        def test_func():
            raise Exception("Generic error")

        with pytest.raises(typer.Exit):
            test_func()

    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.create_environment_from_config"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.ComparisonOrchestrator"
    )
    def test_sqlserver_run_validation_success(self, mock_comp_orch, mock_create_env):
        """Test successful run-validation command."""
        mock_env = Mock()
        mock_create_env.return_value = mock_env
        mock_orchestrator = Mock()
        mock_comp_orch.from_validation_environment.return_value = mock_orchestrator

        result = self.runner.invoke(
            sqlserver_app,
            ["run-validation", "--data-validation-config-file", "test_config.yaml"],
        )

        assert result.exit_code == 0
        mock_create_env.assert_called_once_with(
            "test_config.yaml", ExecutionMode.SYNC_VALIDATION
        )
        mock_comp_orch.from_validation_environment.assert_called_once_with(mock_env)
        mock_orchestrator.run_sync_comparison.assert_called_once()

    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.validate_ipc_parameters"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.validate_snowflake_credentials"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.SqlServerArgumentsManager"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.build_snowflake_credentials"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.ComparisonOrchestrator"
    )
    def test_sqlserver_run_validation_ipc_success(
        self,
        mock_comp_orch,
        mock_build_creds,
        mock_args_manager,
        mock_validate_snowflake,
        mock_validate_ipc,
    ):
        """Test successful run-validation-ipc command."""
        # Mock the validation functions to pass
        mock_validate_ipc.return_value = None
        mock_validate_snowflake.return_value = None

        mock_args_instance = Mock()
        mock_args_manager.return_value = mock_args_instance
        mock_config = Mock()
        mock_config.output_directory_path = "/tmp/output"
        mock_validation_env = Mock()
        mock_orchestrator = Mock()

        mock_args_instance.load_configuration.return_value = mock_config
        mock_args_instance.setup_validation_environment.return_value = (
            mock_validation_env
        )
        mock_build_creds.return_value = {
            "account": "test_account",
            "username": "test_user",
            "database": "test_database",
            "warehouse": "test_warehouse",
        }
        mock_comp_orch.from_validation_environment.return_value = mock_orchestrator

        result = self.runner.invoke(
            sqlserver_app,
            [
                "run-validation-ipc",
                "--source-host",
                "localhost",
                "--source-port",
                "1433",
                "--source-username",
                "sa",
                "--source-password",
                "password",
                "--source-database",
                "testdb",
                "--source-trust-server-certificate",
                "no",
                "--source-encrypt",
                "yes",
                "--snow-account",
                "test_account",
                "--data-validation-config-file",
                "test_config.yaml",
            ],
        )

        assert result.exit_code == 0
        mock_validate_ipc.assert_called_once()
        mock_validate_snowflake.assert_called_once()
        mock_args_instance.setup_validation_environment.assert_called_once()
        mock_comp_orch.from_validation_environment.assert_called_once_with(
            mock_validation_env
        )
        mock_orchestrator.run_sync_comparison.assert_called_once()

    def test_sqlserver_run_validation_ipc_missing_required_params(self):
        """Test run-validation-ipc command with missing required parameters."""
        result = self.runner.invoke(
            sqlserver_app,
            [
                "run-validation-ipc",
                "--source-host",
                "localhost"
                # Missing other required parameters
            ],
        )

        assert result.exit_code != 0

    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.create_environment_from_config"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.ComparisonOrchestrator"
    )
    def test_sqlserver_run_async_generation_success(
        self, mock_comp_orch, mock_create_env
    ):
        """Test successful generate-validation-scripts command."""
        mock_env = Mock()
        mock_create_env.return_value = mock_env
        mock_orchestrator = Mock()
        mock_comp_orch.from_validation_environment.return_value = mock_orchestrator

        result = self.runner.invoke(
            sqlserver_app,
            [
                "generate-validation-scripts",
                "--data-validation-config-file",
                "test_config.yaml",
            ],
        )

        assert result.exit_code == 0
        mock_create_env.assert_called_once_with(
            "test_config.yaml", ExecutionMode.ASYNC_GENERATION
        )
        mock_comp_orch.from_validation_environment.assert_called_once_with(mock_env)
        mock_orchestrator.run_async_generation.assert_called_once()

    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.create_environment_from_config"
    )
    def test_sqlserver_run_validation_config_not_found(self, mock_create_env):
        """Test run-validation command with config file not found."""
        mock_create_env.side_effect = FileNotFoundError("Config file not found")

        result = self.runner.invoke(
            sqlserver_app,
            [
                "run-validation",
                "--data-validation-config-file",
                "nonexistent_config.yaml",
            ],
        )

        assert result.exit_code == 1

    def test_sqlserver_run_validation_missing_config_file(self):
        """Test run-validation command without config file parameter."""
        result = self.runner.invoke(sqlserver_app, ["run-validation"])

        assert result.exit_code != 0


class TestSqlServerArgumentsManagerIntegration:
    """Integration tests for SQL Server Arguments Manager used in CLI."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.validate_ipc_parameters"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.validate_snowflake_credentials"
    )
    @patch(
        "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.SqlServerArgumentsManager"
    )
    def test_source_connection_setup_integration(
        self, mock_args_manager, mock_validate_snowflake, mock_validate_ipc
    ):
        """Test source connection setup integration."""
        # Mock validation functions to pass
        mock_validate_ipc.return_value = None
        mock_validate_snowflake.return_value = None

        mock_args_instance = Mock()
        mock_args_manager.return_value = mock_args_instance
        mock_config = Mock()
        mock_config.output_directory_path = "/tmp/output"
        mock_validation_env = Mock()

        mock_args_instance.load_configuration.return_value = mock_config
        mock_args_instance.setup_validation_environment.return_value = (
            mock_validation_env
        )

        # Test that the source connection is set up with correct parameters
        from snowflake.snowflake_data_validation.sqlserver.sqlserver_cli import (
            sqlserver_run_validation_ipc,
        )

        with patch(
            "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.ComparisonOrchestrator"
        ):
            with patch(
                "snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.build_snowflake_credentials"
            ) as mock_build_creds:
                mock_build_creds.return_value = {}
                sqlserver_run_validation_ipc(
                    source_host="localhost",
                    source_port=1433,
                    source_username="sa",
                    source_password="password",
                    source_database="testdb",
                    source_trust_server_certificate="no",
                    source_encrypt="yes",
                )

        mock_validate_ipc.assert_called_once()
        mock_validate_snowflake.assert_called_once()
        mock_args_instance.setup_validation_environment.assert_called_once()

    @patch("snowflake.snowflake_data_validation.sqlserver.sqlserver_cli.Path")
    def test_sqlserver_get_configuration_files(self, mock_path):
        """Test sqlserver_get_configuration_files command to list available configuration files."""
        # Mock the config directory
        mock_config_dir = MagicMock()
        mock_path.return_value = mock_config_dir

        # Set up mock files with different extensions
        mock_files = [
            MagicMock(suffix=".yaml", name="sqlserver_column_metrics_templates.yaml"),
            MagicMock(
                suffix=".yaml",
                name=COLUMN_DATATYPES_MAPPING_NAME_FORMAT.format(
                    source_platform="sqlserver",
                    target_platform="snowflake",
                ),
            ),
        ]

        # Configure mock file behaviors
        for mock_file in mock_files:
            # Set is_file() behavior based on filename
            if mock_file.name == "subdirectory":
                mock_file.is_file.return_value = False
            else:
                mock_file.is_file.return_value = True

            # Make sure str(mock_file) returns the filename
            mock_file.__str__.return_value = mock_file.name

        # Configure directory mock
        mock_config_dir.exists.return_value = True
        mock_config_dir.glob.return_value = mock_files

        # Run the command
        result = self.runner.invoke(
            sqlserver_app,
            ["get-configuration-files", "-td", current_dir := Path(__file__).parent],
        )

        # Assert command executed successfully
        assert result.exit_code == 0
        # delete the generated files from the test directory
        remove_files = [
            # SQL Server specific files
            current_dir.joinpath(
                COLUMN_METRICS_TEMPLATE_NAME_FORMAT.format(
                    platform=Platform.SQLSERVER.value
                )
            ),
            current_dir.joinpath(
                COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT.format(
                    platform=Platform.SQLSERVER.value
                )
            ),
            current_dir.joinpath(
                COLUMN_DATATYPES_MAPPING_NAME_FORMAT.format(
                    source_platform=Platform.SQLSERVER.value,
                    target_platform=Platform.SNOWFLAKE.value,
                )
            ),
            # Snowflake files (also generated by sqlserver CLI)
            current_dir.joinpath(
                COLUMN_METRICS_TEMPLATE_NAME_FORMAT.format(
                    platform=Platform.SNOWFLAKE.value
                )
            ),
            current_dir.joinpath(
                COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT.format(
                    platform=Platform.SNOWFLAKE.value
                )
            ),
        ]
        for file in remove_files:
            if file.exists():
                file.unlink()
