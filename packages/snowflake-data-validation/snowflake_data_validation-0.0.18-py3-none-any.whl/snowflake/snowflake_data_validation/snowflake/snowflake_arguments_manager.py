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
    SnowflakeDefaultConnection,
    SnowflakeNamedConnection,
)
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)


class SnowflakeArgumentsManager(ArgumentsManagerBase):

    """Arguments manager for Snowflake-to-Snowflake connections and configuration."""

    def __init__(self):
        """Initialize the Snowflake arguments manager."""
        super().__init__(Platform.SNOWFLAKE, Platform.SNOWFLAKE)

    @property
    def is_snowflake_to_snowflake(self) -> bool:
        """Check if this is a Snowflake-to-Snowflake validation scenario.

        Returns:
            bool: True if both source and target are Snowflake

        """
        return True  # This manager is only used for Snowflake-to-Snowflake

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
        # Set up source and target connection configurations
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
    ):
        """Set up source connection configuration from configuration model."""
        if not config_model.source_connection:
            raise typer.BadParameter(
                message="No source connection configured in YAML file. "
                "Please add a source_connection section to your configuration file."
            )

        source_conn = config_model.source_connection

        mode = getattr(source_conn, "mode", NAME_CONNECTION_MODE)
        if mode == NAME_CONNECTION_MODE:
            return SnowflakeNamedConnection(
                mode=NAME_CONNECTION_MODE,
                name=getattr(source_conn, "name", None),
            )
        elif mode == DEFAULT_CONNECTION_MODE:
            return SnowflakeDefaultConnection(
                mode=DEFAULT_CONNECTION_MODE,
            )
        else:
            raise typer.BadParameter(
                message=f"Unsupported source connection mode for Snowflake: {mode}. "
                "Supported modes are 'name' and 'default'. Use IPC commands for credentials mode."
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
        """Get Snowflake templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "extractor", "templates")

    def get_target_templates_path(self) -> str:
        """Get Snowflake target templates path (same as source for Snowflake-to-Snowflake)."""
        return self.get_source_templates_path()

    def _setup_snowflake_connection(
        self,
        conn_mode: str,
        snowflake_conn_file: Optional[str],
        snowflake_credential_object: Optional[dict[str, str]] = None,
    ) -> ConnectorSnowflake:
        """Set up Snowflake connector based on connection mode."""
        try:
            connector_snowflake = ConnectorSnowflake()

            connection_params: dict[str, str] = {"mode": conn_mode}

            if conn_mode == NAME_CONNECTION_MODE:
                connection_params["connection_name"] = snowflake_conn_file

            if snowflake_credential_object:
                # Validate required parameters for credentials mode
                if conn_mode == CREDENTIALS_CONNECTION_MODE:
                    required_params = [
                        "account",
                        "username",
                        "database",
                        "schema",
                        "warehouse",
                    ]
                    missing_params = [
                        param
                        for param in required_params
                        if not snowflake_credential_object.get(param)
                    ]
                    if missing_params:
                        raise typer.BadParameter(
                            message=f"Missing required Snowflake connection parameters: {', '.join(missing_params)}"
                        )

                connection_params.update(snowflake_credential_object)

            try:
                connector_snowflake.connect(**connection_params)
            except ConnectionError as e:
                raise ConnectionError(
                    f"Failed to establish Snowflake connection: {e}"
                ) from e
            except ImportError as e:
                raise ImportError(f"Snowflake dependencies not available: {e}") from e
            except typer.BadParameter:
                raise  # Re-raise parameter errors as-is

            return connector_snowflake

        except (typer.BadParameter, ConnectionError, ImportError):
            raise  # Re-raise these as-is
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error setting up Snowflake connection: {e}"
            ) from e
