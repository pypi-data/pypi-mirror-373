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

from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

from snowflake.snowflake_data_validation.redshift.redshift_cli import redshift_app
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode


class TestRedshiftCLIRunValidation:
    """Unit tests for Redshift CLI run-validation command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli._create_environment_from_config"
    )
    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli.ComparisonOrchestrator"
    )
    def test_run_validation_success(self, mock_orchestrator_class, mock_create_env):
        """Test successful validation run - happy path."""
        mock_env = MagicMock()
        mock_create_env.return_value = mock_env

        mock_orchestrator = MagicMock()
        mock_orchestrator_class.from_validation_environment.return_value = (
            mock_orchestrator
        )

        result = self.runner.invoke(
            redshift_app,
            ["run-validation", "--data-validation-config-file", "test_config.yaml"],
        )

        assert result.exit_code == 0
        assert "Starting Redshift validation..." in result.output
        assert "Validation completed successfully!" in result.output
        mock_create_env.assert_called_once_with(
            "test_config.yaml", ExecutionMode.SYNC_VALIDATION
        )
        mock_orchestrator.run_sync_comparison.assert_called_once()

    def test_run_validation_missing_config_file(self):
        """Test validation with missing required config file parameter."""
        result = self.runner.invoke(redshift_app, ["run-validation"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "Usage:" in result.output

    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli._create_environment_from_config"
    )
    def test_run_validation_file_not_found_error(self, mock_create_env):
        """Test validation with non-existent config file."""
        mock_create_env.side_effect = FileNotFoundError("Config file not found")

        result = self.runner.invoke(
            redshift_app,
            ["run-validation", "--data-validation-config-file", "nonexistent.yaml"],
        )

        assert result.exit_code == 1
        assert "Configuration file not found" in result.output

    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli._create_environment_from_config"
    )
    def test_run_validation_connection_error(self, mock_create_env):
        """Test validation with connection error."""
        mock_create_env.side_effect = ConnectionError("Database connection failed")

        result = self.runner.invoke(
            redshift_app,
            ["run-validation", "--data-validation-config-file", "test_config.yaml"],
        )

        assert result.exit_code == 1
        assert "Connection error" in result.output

    @patch(
        "snowflake.snowflake_data_validation.redshift.redshift_cli._create_environment_from_config"
    )
    def test_run_validation_generic_exception(self, mock_create_env):
        """Test validation with unexpected error."""
        mock_create_env.side_effect = Exception("Unexpected error")

        result = self.runner.invoke(
            redshift_app,
            ["run-validation", "--data-validation-config-file", "test_config.yaml"],
        )

        assert result.exit_code == 1
        assert "Operation failed" in result.output
