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
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

from snowflake.snowflake_data_validation.redshift.redshift_cli import redshift_app
from snowflake.snowflake_data_validation.utils.constants import Platform

class TestRedshiftCLIGetConfigurationFiles:
    """Unit tests for Redshift CLI get-configuration-files command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager')
    def test_get_configuration_files_with_directory(self, mock_args_manager_class):
        """Test configuration file generation with specified directory - happy path."""
        mock_args_manager = MagicMock()
        mock_args_manager_class.return_value = mock_args_manager

        result = self.runner.invoke(redshift_app, [
            "get-configuration-files",
            "--templates-directory", "/tmp/test"
        ])

        assert result.exit_code == 0
        assert "Retrieving Redshift validation configuration files..." in result.output
        assert "Configuration files were generated" in result.output
        mock_args_manager.dump_and_write_yaml_templates.assert_called_once_with(
            source=Platform.REDSHIFT.value, 
            templates_directory="/tmp/test"
        )

    @patch('snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager')
    def test_get_configuration_files_default_directory(self, mock_args_manager_class):
        """Test configuration file generation without directory (uses default)."""
        mock_args_manager = MagicMock()
        mock_args_manager_class.return_value = mock_args_manager

        result = self.runner.invoke(redshift_app, ["get-configuration-files"])

        assert result.exit_code == 0
        assert "Retrieving Redshift validation configuration files..." in result.output
        assert "Configuration files were generated" in result.output
        mock_args_manager.dump_and_write_yaml_templates.assert_called_once_with(
            source=Platform.REDSHIFT.value, 
            templates_directory="."
        )

    @patch('snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager')
    def test_get_configuration_files_permission_error(self, mock_args_manager_class, caplog):
        """Test configuration file generation with permission error."""
        mock_args_manager = MagicMock()
        caplog.set_level(logging.ERROR)
        mock_args_manager_class.return_value = mock_args_manager
        mock_args_manager.dump_and_write_yaml_templates.side_effect = PermissionError("Permission denied")

        result = self.runner.invoke(redshift_app, ["get-configuration-files"])

        assert result.exit_code != 0
        assert "Permission denied while writing template files: Permission denied" in caplog.text

    @patch('snowflake.snowflake_data_validation.redshift.redshift_cli.RedshiftArgumentsManager')
    def test_get_configuration_files_generic_error(self, mock_args_manager_class, caplog):
        """Test configuration file generation with generic error."""
        mock_args_manager = MagicMock()
        caplog.set_level(logging.ERROR)
        mock_args_manager_class.return_value = mock_args_manager
        mock_args_manager.dump_and_write_yaml_templates.side_effect = Exception("Some error")

        result = self.runner.invoke(redshift_app, ["get-configuration-files"])

        assert result.exit_code != 0
        assert "Failed to generate configuration files: Some error" in caplog.text

    def test_get_configuration_files_help(self):
        """Test get-configuration-files command help."""
        result = self.runner.invoke(redshift_app, ["get-configuration-files", "--help"])
        assert result.exit_code == 0
        assert "Get configuration files" in result.output
        assert "--templates-directory" in result.output 