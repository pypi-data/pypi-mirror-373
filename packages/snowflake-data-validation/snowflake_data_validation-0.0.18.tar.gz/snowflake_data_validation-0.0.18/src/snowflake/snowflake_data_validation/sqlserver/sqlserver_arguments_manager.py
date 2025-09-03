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

import os

from typing import Optional

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.configuration.model.connections import (
    SqlServerCredentialsConnection,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)


class SqlServerArgumentsManager(ArgumentsManagerBase):

    """Arguments manager for SQL Server connections and configuration."""

    def __init__(self):
        """Initialize the SQL Server arguments manager."""
        super().__init__(Platform.SQLSERVER, Platform.SNOWFLAKE)

    @property
    def is_snowflake_to_snowflake(self) -> bool:
        """Check if this is a Snowflake-to-Snowflake validation scenario.

        Returns:
            bool: True if both source and target are Snowflake

        """
        return False  # SQL Server to Snowflake

    def create_validation_environment_from_config(
        self,
        config_model: ConfigurationModel,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_handler: Optional[ConsoleOutputHandler] = None,
    ):
        """Create a complete validation environment from configuration model.

        Args:
            config_model: The loaded configuration model
            data_validation_config_file: Path to the config file
            execution_mode: Execution mode for the validation process
            output_handler: Optional output handler

        Returns:
            Validation environment ready to run

        Raises:
            typer.BadParameter: If configuration is invalid
            ValueError: If required connections are missing

        """
        # Set up connection configurations
        source_connection_config = self._setup_source_connection_config_from_config(
            config_model
        )
        target_connection_config = self._setup_target_connection_config_from_config(
            config_model
        )

        # Create validation environment using output_directory_path from config
        return self.setup_validation_environment(
            source_connection_config=source_connection_config,
            target_connection_config=target_connection_config,
            data_validation_config_file=data_validation_config_file,
            output_directory_path=config_model.output_directory_path,
            output_handler=output_handler or ConsoleOutputHandler(),
            execution_mode=execution_mode,
        )

    def _setup_source_connection_config_from_config(
        self, config_model: ConfigurationModel
    ) -> SqlServerCredentialsConnection:
        """Set up source connection configuration from configuration model."""
        if not config_model.source_connection:
            raise typer.BadParameter(
                message="No source connection configured in YAML file. "
                "Please add a source_connection section to your configuration file."
            )

        source_conn = config_model.source_connection

        mode = getattr(source_conn, "mode", CREDENTIALS_CONNECTION_MODE)
        if mode == CREDENTIALS_CONNECTION_MODE:
            # Create connection configuration from the source connection
            return SqlServerCredentialsConnection(
                mode=CREDENTIALS_CONNECTION_MODE,
                host=source_conn.host,
                port=source_conn.port,
                username=source_conn.username,
                password=source_conn.password,
                database=source_conn.database,
                trust_server_certificate=getattr(
                    source_conn, "trust_server_certificate", "no"
                ),
                encrypt=getattr(source_conn, "encrypt", "yes"),
            )
        else:
            raise typer.BadParameter(
                message=f"Unsupported source connection mode for SQL Server: {mode}. "
                "Only 'credentials' mode is supported."
            )

    def _setup_target_connection_config_from_config(
        self, config_model: ConfigurationModel
    ):
        """Set up target connection configuration from configuration model."""
        try:
            return super()._setup_target_connection_config_from_config(config_model)
        except ValueError as e:
            raise typer.BadParameter(message=str(e)) from e

    def get_source_templates_path(self) -> str:
        """Get SQL Server templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "extractor", "templates")

    def get_target_templates_path(self) -> str:
        """Get Snowflake target templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "..", "snowflake", "extractor", "templates")
