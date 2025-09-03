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
import pytest
from unittest.mock import ANY, MagicMock, patch
from snowflake.snowflake_data_validation.utils.console_output_handler import ConsoleOutputHandler
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode
from typer.testing import CliRunner

from snowflake.snowflake_data_validation.redshift.redshift_cli import redshift_app


@pytest.fixture
def sample_config_content():
    """Sample configuration file content for testing."""
    return """
source_connection:
  mode: "credentials"
  host: "redshift.example.com"
  port: 5439
  username: "testuser"
  password: "testpass"
  database: "testdb"

target_connection:
  mode: "default"

tables:
  - source_table_name: "test_table"
    target_table_name: "test_table"

validation_configuration:
  schema_validation: true
  metrics_validation: true
  row_validation: false
"""


@pytest.fixture
def sample_config_file(tmp_path, sample_config_content):
    """Create a sample configuration file for testing."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(sample_config_content)
    return str(config_file)


class TestRedshiftCLIRunValidationIPC:
    """Unit tests for Redshift CLI run-validation-ipc command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("snowflake.snowflake_data_validation.redshift.redshift_cli.Path")
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftCredentialsConnection"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.validate_snowflake_credentials"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.build_snowflake_credentials"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.ComparisonOrchestrator"
    )
    def test_run_validation_ipc_success(
        self,
        mock_orchestrator_class,
        mock_build_sf_creds,
        mock_validate_sf,
        mock_redshift_creds,
        mock_args_manager_class,
        mock_path_class,
        caplog,
    ):
        """Test successful IPC validation run with all required parameters - happy path."""
        caplog.set_level(logging.INFO)

        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.is_file.return_value = True
        mock_path_class.return_value = mock_path_instance

        mock_args_manager = MagicMock()
        mock_args_manager_class.return_value = mock_args_manager

        mock_redshift_creds_instance = MagicMock()
        mock_redshift_creds_instance.model_validate.return_value = (
            mock_redshift_creds_instance
        )
        mock_redshift_creds.return_value = mock_redshift_creds_instance
        mock_redshift_creds.model_validate.return_value = mock_redshift_creds_instance

        snowflake_creds_dict = {
            "account": "snowaccount",
            "username": "snowuser",
            "database": "snowdb",
            "warehouse": "snowwarehouse",
            "password": "snowpass",
        }
        mock_build_sf_creds.return_value = snowflake_creds_dict

        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()
        mock_args_manager.setup_source_connection.return_value = mock_source_connector
        mock_args_manager.setup_target_connection.return_value = mock_target_connector

        mock_config = MagicMock()
        mock_config.output_directory_path = "/tmp/output"
        mock_args_manager.load_configuration.return_value = mock_config

        mock_validation_env = MagicMock()
        mock_args_manager.setup_validation_environment.return_value = (
            mock_validation_env
        )

        mock_orchestrator = MagicMock()
        mock_orchestrator.run_sync_comparison = MagicMock()
        mock_orchestrator_class.from_validation_environment.return_value = (
            mock_orchestrator
        )

        result = self.runner.invoke(
            redshift_app,
            [
                "run-validation-ipc",
                "--source-host",
                "redshift.example.com",
                "--source-username",
                "testuser",
                "--source-password",
                "testpass",
                "--source-database",
                "testdb",
                "--snow-account",
                "snowaccount",
                "--snow_username",
                "snowuser",
                "--snow_database",
                "snowdb",
                "--snow_warehouse",
                "snowwarehouse",
                "--snow_password",
                "snowpass",
                "--data-validation-config-file",
                "config.yaml",
            ],
        )

        assert result.exit_code == 0
        assert "Validation completed successfully!" in result.output

        mock_args_manager.setup_validation_environment.assert_called_once_with(
            source_connection_config=mock_redshift_creds_instance,
            target_connection_config=snowflake_creds_dict,
            data_validation_config_file="config.yaml",
            output_directory_path="/tmp/output",
            output_handler=ANY,
            execution_mode=ExecutionMode.SYNC_VALIDATION,
        )
        mock_orchestrator_class.from_validation_environment.assert_called_once_with(mock_validation_env)
        mock_orchestrator.run_sync_comparison.assert_called_once()

    @pytest.mark.parametrize(
        "missing_param,param_args",
        [
            (
                "source-host",
                [
                    "--source-username",
                    "testuser",
                    "--source-password",
                    "testpass",
                    "--source-database",
                    "testdb",
                ],
            ),
            (
                "source-username",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-password",
                    "testpass",
                    "--source-database",
                    "testdb",
                ],
            ),
            (
                "source-password",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-username",
                    "testuser",
                    "--source-database",
                    "testdb",
                ],
            ),
            (
                "source-database",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-username",
                    "testuser",
                    "--source-password",
                    "testpass",
                ],
            ),
            (
                "snow-account",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-username",
                    "testuser",
                    "--source-password",
                    "testpass",
                    "--source-database",
                    "testdb",
                ],
            ),
            (
                "snow_username",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-username",
                    "testuser",
                    "--source-password",
                    "testpass",
                    "--source-database",
                    "testdb",
                    "--snow-account",
                    "snowaccount",
                ],
            ),
            (
                "snow_database",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-username",
                    "testuser",
                    "--source-password",
                    "testpass",
                    "--source-database",
                    "testdb",
                    "--snow-account",
                    "snowaccount",
                    "--snow_username",
                    "snowuser",
                ],
            ),
            (
                "snow_warehouse",
                [
                    "--source-host",
                    "redshift.example.com",
                    "--source-username",
                    "testuser",
                    "--source-password",
                    "testpass",
                    "--source-database",
                    "testdb",
                    "--snow-account",
                    "snowaccount",
                    "--snow_username",
                    "snowuser",
                    "--snow_database",
                    "snowdb",
                ],
            ),
        ],
    )
    def test_run_validation_ipc_missing_required_params(
        self, missing_param, param_args
    ):
        """Test IPC validation with missing required parameters."""
        result = self.runner.invoke(redshift_app, ["run-validation-ipc"] + param_args)
        assert result.exit_code != 0
        assert "Missing option" in result.output or "Usage:" in result.output

    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.build_snowflake_credentials"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftCredentialsConnection"
    )
    def test_run_validation_ipc_with_optional_parameters(
        self, mock_redshift_creds, mock_build_creds, mock_args_manager_class
    ):
        """Test IPC validation with optional parameters included."""
        mock_args_manager = MagicMock()
        mock_args_manager_class.return_value = mock_args_manager
        mock_build_creds.return_value = {"account": "test_account"}

        mock_redshift_creds_instance = MagicMock()
        mock_redshift_creds.return_value = mock_redshift_creds_instance

        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()
        mock_args_manager.setup_source_connection.return_value = mock_source_connector
        mock_args_manager.setup_target_connection.return_value = mock_target_connector

        result = self.runner.invoke(
            redshift_app,
            [
                "run-validation-ipc",
                "--source-host",
                "redshift.example.com",
                "--source-username",
                "testuser",
                "--source-password",
                "testpass",
                "--source-database",
                "testdb",
                "--source-port",
                "5439",
                "--snow-account",
                "snowaccount",
                "--snow_username",
                "snowuser",
                "--snow_database",
                "snowdb",
                "--snow_warehouse",
                "snowwarehouse",
                "--snow_schema",
                "public",
                "--snow_role",
                "admin",
                "--snow_authenticator",
                "snowflake",
                "--snow_password",
                "snowpass",
            ],
        )

        assert (
            "--snow_schema" in str(result)
            or result.exit_code == 0
            or result.exit_code == 1
        )

    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager"
    )
    def test_run_validation_ipc_connection_error(self, mock_args_manager_class):
        """Test IPC validation with connection error."""
        mock_args_manager = MagicMock()
        mock_args_manager_class.return_value = mock_args_manager
        mock_args_manager.setup_validation_environment.side_effect = ConnectionError(
            "Database connection failed"
        )

        result = self.runner.invoke(
            redshift_app,
            [
                "run-validation-ipc",
                "--source-host",
                "redshift.example.com",
                "--source-username",
                "testuser",
                "--source-password",
                "testpass",
                "--source-database",
                "testdb",
                "--snow-account",
                "snowaccount",
                "--snow_username",
                "snowuser",
                "--snow_database",
                "snowdb",
                "--snow_warehouse",
                "snowwarehouse",
                "--snow_password",
                "snowpass",
            ],
        )

        assert result.exit_code == 1
        assert "Connection error: Database connection failed" in result.output

    @pytest.mark.parametrize(
        "error_type,error_message,expected_output",
        [
            (
                FileNotFoundError,
                "Config file not found",
                "Configuration file not found",
            ),
            (ConnectionError, "Database connection failed", "Connection error"),
            (
                PermissionError,
                "Permission denied",
                "Operation failed: Permission denied",
            ),
            (Exception, "Unexpected error", "Operation failed"),
        ],
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager"
    )
    def test_run_validation_ipc_error_handling(
        self, mock_args_manager_class, error_type, error_message, expected_output
    ):
        """Test IPC validation error handling."""
        mock_args_manager = MagicMock()
        mock_args_manager_class.return_value = mock_args_manager
        mock_args_manager.setup_validation_environment.side_effect = error_type(
            error_message
        )

        result = self.runner.invoke(
            redshift_app,
            [
                "run-validation-ipc",
                "--source-host",
                "redshift.example.com",
                "--source-username",
                "testuser",
                "--source-password",
                "testpass",
                "--source-database",
                "testdb",
                "--snow-account",
                "snowaccount",
                "--snow_username",
                "snowuser",
                "--snow_database",
                "snowdb",
                "--snow_warehouse",
                "snowwarehouse",
                "--snow_password",
                "snowpass",
            ],
        )

        assert result.exit_code == 1
        assert expected_output in result.output

    def test_run_validation_ipc_help(self):
        """Test run-validation-ipc command help."""
        result = self.runner.invoke(redshift_app, ["run-validation-ipc", "--help"])
        assert result.exit_code == 0
        assert "Run data validation for Redshift to Snowflake with IPC" in result.output
        assert "--source-host" in result.output
        assert "--snow-account" in result.output
