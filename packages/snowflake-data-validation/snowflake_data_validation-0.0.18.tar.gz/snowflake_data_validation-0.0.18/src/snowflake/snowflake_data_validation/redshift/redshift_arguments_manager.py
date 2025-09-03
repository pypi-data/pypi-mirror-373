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
    RedshiftCredentialsConnection,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    MISSING_SOURCE_CONNECTION_ERROR,
    ExecutionMode,
    Platform,
)


class RedshiftArgumentsManager(ArgumentsManagerBase):

    """Class to manage Redshift arguments for data validation.

    This class is a placeholder and can be extended with specific methods
    for handling Redshift arguments as needed.
    """

    def __init__(self):
        super().__init__(
            source_platform=Platform.REDSHIFT, target_platform=Platform.SNOWFLAKE
        )

    @property
    def is_snowflake_to_snowflake(self) -> bool:
        return False

    def create_validation_environment_from_config(
        self,
        config_model: ConfigurationModel,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_handler: Optional[ConsoleOutputHandler] = None,
    ):
        source_connection_config = self._setup_source_connection_config_from_config(
            config_model
        )
        target_connection_config = self._setup_target_connection_config_from_config(
            config_model
        )

        return self.setup_validation_environment(
            source_connection_config=source_connection_config,
            target_connection_config=target_connection_config,
            data_validation_config_file=data_validation_config_file,
            output_directory_path=config_model.output_directory_path,
            output_handler=output_handler or ConsoleOutputHandler(),
            execution_mode=execution_mode,
        )

    def get_source_templates_path(self) -> str:
        """Get Teradata templates path.

        TODO: Implement actual Teradata-specific templates in future PR.
        For now, using placeholder templates to avoid file not found errors.
        """
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "extractor", "templates")

    def get_target_templates_path(self) -> str:
        """Get Snowflake target templates path."""
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "..", "snowflake", "extractor", "templates")

    def _setup_source_connection_config_from_config(
        self, config_model: ConfigurationModel
    ) -> RedshiftCredentialsConnection:
        """Set up source connection configuration from configuration model."""
        if not config_model.source_connection:
            raise typer.BadParameter(MISSING_SOURCE_CONNECTION_ERROR)

        source_connection = config_model.source_connection
        mode = getattr(source_connection, "mode", CREDENTIALS_CONNECTION_MODE)
        if mode == CREDENTIALS_CONNECTION_MODE:
            return RedshiftCredentialsConnection(
                mode=CREDENTIALS_CONNECTION_MODE,
                host=source_connection.host,
                port=source_connection.port,
                username=source_connection.username,
                password=source_connection.password,
                database=source_connection.database,
            )
        else:
            raise typer.BadParameter(
                f"Unsupported source connection mode for Redshift: {mode}. "
                f"Only '{CREDENTIALS_CONNECTION_MODE}' is supported."
            )

    def _setup_target_connection_config_from_config(
        self, config_model: ConfigurationModel
    ):
        """Set up target connection configuration from configuration model."""
        try:
            return super()._setup_target_connection_config_from_config(config_model)
        except ValueError as e:
            raise typer.BadParameter(message=str(e)) from e
