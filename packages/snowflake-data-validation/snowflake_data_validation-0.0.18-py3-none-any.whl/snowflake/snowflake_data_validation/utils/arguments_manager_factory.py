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

"""Factory for creating appropriate arguments managers based on source and target platforms."""

from typing import Optional

import typer

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.redshift.redshift_arguments_manager import (
    RedshiftArgumentsManager,
)
from snowflake.snowflake_data_validation.snowflake.snowflake_arguments_manager import (
    SnowflakeArgumentsManager,
)
from snowflake.snowflake_data_validation.sqlserver.sqlserver_arguments_manager import (
    SqlServerArgumentsManager,
)
from snowflake.snowflake_data_validation.teradata.teradata_arguments_manager import (
    TeradataArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode, Platform
from snowflake.snowflake_data_validation.utils.telemetry import report_telemetry


# Registry for platform-specific arguments managers
_ARGUMENTS_MANAGER_REGISTRY = {
    Platform.SQLSERVER: {
        "manager_class": SqlServerArgumentsManager,
        "supported_targets": {Platform.SNOWFLAKE},
    },
    Platform.SNOWFLAKE: {
        "manager_class": SnowflakeArgumentsManager,
        "supported_targets": {Platform.SNOWFLAKE},
    },
    Platform.TERADATA: {
        "manager_class": TeradataArgumentsManager,
        "supported_targets": {Platform.SNOWFLAKE},
    },
    Platform.REDSHIFT: {
        "manager_class": RedshiftArgumentsManager,
        "supported_targets": {Platform.SNOWFLAKE},
    },
}


@report_telemetry(params_list=["config_model"])
def create_validation_environment_from_config(
    config_model: ConfigurationModel,
    data_validation_config_file: str,
    execution_mode: ExecutionMode,
    output_handler: Optional[ConsoleOutputHandler] = None,
):
    """Create a validation environment using the appropriate args manager based on platform.

    Args:
        config_model: The loaded configuration model
        data_validation_config_file: Path to the config file
        execution_mode: Execution mode (required, e.g., ExecutionMode.SYNC_VALIDATION)
        output_handler: Optional output handler

    Returns:
        Validation environment ready to run

    Raises:
        typer.BadParameter: If platform combination is not supported
        ValueError: If required platforms are missing

    """
    source_platform = getattr(config_model, "source_platform", None)
    target_platform = getattr(config_model, "target_platform", "Snowflake")

    if not source_platform:
        raise typer.BadParameter(
            message="source_platform is required in configuration. "
            "Please specify 'SqlServer' or 'Snowflake'."
        )

    # Create appropriate args manager based on source platform
    args_manager = get_arguments_manager(source_platform, target_platform)

    # Use the args manager to create validation environment
    return args_manager.create_validation_environment_from_config(
        config_model=config_model,
        data_validation_config_file=data_validation_config_file,
        execution_mode=execution_mode,
        output_handler=output_handler or ConsoleOutputHandler(),
    )


def get_arguments_manager(
    source_platform: str, target_platform: str = "Snowflake"
) -> ArgumentsManagerBase:
    """Get the appropriate arguments manager for the given source and target platforms.

    Args:
        source_platform: Source platform name (SqlServer, Snowflake)
        target_platform: Target platform name (defaults to Snowflake)

    Returns:
        Appropriate arguments manager instance

    Raises:
        typer.BadParameter: If platform combination is not supported

    """
    source_platform_enum = Platform(source_platform.lower())

    # Get platform configuration
    platform_config = _ARGUMENTS_MANAGER_REGISTRY[source_platform_enum]

    return platform_config["manager_class"]()
