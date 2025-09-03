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

from typer.testing import CliRunner

from snowflake.snowflake_data_validation.redshift.redshift_cli import redshift_app

class TestRedshiftCLIGeneral:
    """Unit tests for general Redshift CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_app_help(self):
        """Test that the main app help works."""
        result = self.runner.invoke(redshift_app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_invalid_command(self):
        """Test behavior with invalid command."""
        result = self.runner.invoke(redshift_app, ["invalid-command"])
        assert result.exit_code != 0

    def test_short_flag_options(self):
        """Test that short flag options work correctly."""
        result = self.runner.invoke(redshift_app, [
            "run-validation",
            "-dvf", "test_config.yaml"
        ])
        assert result.exit_code != 0
        assert "Missing option" not in result.output or "Configuration file not found" in result.output 