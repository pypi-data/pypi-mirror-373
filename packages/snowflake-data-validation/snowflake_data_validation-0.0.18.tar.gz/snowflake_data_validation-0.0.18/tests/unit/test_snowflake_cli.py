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

from snowflake.snowflake_data_validation.snowflake.snowflake_cli import (
    snowflake_app,
)
from snowflake.snowflake_data_validation.utils.constants import (
    ExecutionMode,
    COLUMN_METRICS_TEMPLATE_NAME_FORMAT,
    COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT,
    Platform,
)


class TestSnowflakeCLI:
    """Test cases for SQL Server CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("snowflake.snowflake_data_validation.snowflake.snowflake_cli.Path")
    def test_snowflake_get_configuration_files(self, mock_path):
        """Test snowflake_get_configuration_files command to list available configuration files."""
        # Mock the config directory
        mock_config_dir = MagicMock()
        mock_path.return_value = mock_config_dir

        # Set up mock files with different extensions
        mock_files = [
            MagicMock(suffix=".yaml", name="snowflake_column_metrics_templates.yaml"),
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
            snowflake_app,
            ["get-configuration-files", "-td", current_dir := Path(__file__).parent],
        )

        # Assert command executed successfully
        assert result.exit_code == 0
        # delete the generated files from the test directory
        remove_files = [
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
