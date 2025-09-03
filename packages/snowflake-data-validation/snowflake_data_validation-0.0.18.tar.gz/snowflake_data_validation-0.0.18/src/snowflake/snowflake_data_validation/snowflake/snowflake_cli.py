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

"""Snowflake CLI commands for data validation."""

from functools import wraps
from pathlib import Path
from typing import Annotated, Optional

import typer

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.snowflake.snowflake_arguments_manager import (
    SnowflakeArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_factory import (
    create_validation_environment_from_config,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)


# Create Snowflake typer app
snowflake_app = typer.Typer()


def handle_validation_errors(func):
    """Handle validation errors and provide user-friendly messages."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except typer.BadParameter as e:
            typer.secho(f"Invalid parameter: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None
        except FileNotFoundError as e:
            typer.secho(
                f"Configuration file not found: {e}", fg=typer.colors.RED, err=True
            )
            raise typer.Exit(1) from None
        except ConnectionError as e:
            typer.secho(f"Connection error: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None
        except Exception as e:
            typer.secho(f"Validation failed: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None

    return wrapper


def create_environment_from_config(
    data_validation_config_file: str,
    execution_mode: ExecutionMode,
    console_output: bool = True,
):
    """Create validation environment from configuration file."""
    config_path = Path(data_validation_config_file)
    config_loader = ConfigurationLoader(config_path)
    config_model = config_loader.get_configuration_model()

    return create_validation_environment_from_config(
        config_model=config_model,
        data_validation_config_file=data_validation_config_file,
        execution_mode=execution_mode,
        output_handler=ConsoleOutputHandler(enable_console_output=console_output),
    )


@snowflake_app.command("run-validation")
@handle_validation_errors
def snowflake_run_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Run data validation for Snowflake to Snowflake."""
    typer.secho("Starting Snowflake to Snowflake validation...", fg=typer.colors.BLUE)

    validation_env = create_environment_from_config(
        data_validation_config_file, ExecutionMode.SYNC_VALIDATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@snowflake_app.command("run-async-validation")
@handle_validation_errors
def snowflake_run_async_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Run data validation for Snowflake to Snowflake."""
    typer.secho("Starting Snowflake to Snowflake validation...", fg=typer.colors.BLUE)

    validation_env = create_environment_from_config(
        data_validation_config_file, ExecutionMode.ASYNC_VALIDATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_async_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@snowflake_app.command("run-validation-ipc")
@handle_validation_errors
def snowflake_run_validation_ipc(
    snow_account: Annotated[
        str, typer.Option("--snow-account", "-sa", help="Source Snowflake account name")
    ],
    snow_username: Annotated[
        str, typer.Option("--snow_username", "-su", help="Source Snowflake Username")
    ],
    snow_database: Annotated[
        str,
        typer.Option("--snow_database", "-sd", help="Source Snowflake Database used"),
    ],
    snow_schema: Annotated[
        str, typer.Option("--snow_schema", "-ss", help="Source Snowflake Schema used")
    ],
    snow_warehouse: Annotated[
        str,
        typer.Option("--snow_warehouse", "-sw", help="Source Snowflake Warehouse used"),
    ],
    snow_role: Annotated[
        str, typer.Option("--snow_role", "-sr", help="Source Snowflake Role used")
    ] = None,
    snow_authenticator: Annotated[
        str,
        typer.Option(
            "--snow_authenticator",
            "-sau",
            help="Source Snowflake Authenticator method used",
        ),
    ] = None,
    snow_password: Annotated[
        str, typer.Option("--snow_password", "-sp", help="Source Snowflake Password")
    ] = None,
    # Target connection parameters
    target_snow_account: Annotated[
        str,
        typer.Option(
            "--target-snow-account", "-tsa", help="Target Snowflake account name"
        ),
    ] = None,
    target_snow_username: Annotated[
        str,
        typer.Option(
            "--target-snow_username", "-tsu", help="Target Snowflake Username"
        ),
    ] = None,
    target_snow_database: Annotated[
        str,
        typer.Option(
            "--target-snow_database", "-tsd", help="Target Snowflake Database used"
        ),
    ] = None,
    target_snow_schema: Annotated[
        str,
        typer.Option(
            "--target-snow_schema", "-tss", help="Target Snowflake Schema used"
        ),
    ] = None,
    target_snow_warehouse: Annotated[
        str,
        typer.Option(
            "--target-snow_warehouse", "-tsw", help="Target Snowflake Warehouse used"
        ),
    ] = None,
    target_snow_role: Annotated[
        str,
        typer.Option("--target-snow_role", "-tsr", help="Target Snowflake Role used"),
    ] = None,
    target_snow_authenticator: Annotated[
        str,
        typer.Option(
            "--target-snow_authenticator",
            "-tsau",
            help="Target Snowflake Authenticator method used",
        ),
    ] = None,
    target_snow_password: Annotated[
        str,
        typer.Option(
            "--target-snow_password", "-tsp", help="Target Snowflake Password"
        ),
    ] = None,
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ] = None,
):
    """Run Snowflake data validation with IPC (In-Process Communication).

    This command allows direct specification of connection parameters without requiring
    pre-saved connection files. If target parameters are not specified, the default
    session connection will be used for the target.
    """
    typer.secho(
        "Starting Snowflake to Snowflake validation (IPC mode)...",
        fg=typer.colors.BLUE,
    )

    # Set up arguments manager and connections
    args_manager = SnowflakeArgumentsManager()

    # Set up source connection
    source_connector = args_manager.setup_source_connection(
        snow_account=snow_account,
        snow_username=snow_username,
        snow_database=snow_database,
        snow_schema=snow_schema,
        snow_warehouse=snow_warehouse,
        snow_role=snow_role,
        snow_authenticator=snow_authenticator,
        snow_password=snow_password,
    )

    # Set up target connection
    if (
        target_snow_account
        and target_snow_username
        and target_snow_database
        and target_snow_schema
        and target_snow_warehouse
    ):
        # Use specific target connection parameters
        target_connector = args_manager.setup_target_connection(
            target_snow_account=target_snow_account,
            target_snow_username=target_snow_username,
            target_snow_database=target_snow_database,
            target_snow_schema=target_snow_schema,
            target_snow_warehouse=target_snow_warehouse,
            target_snow_role=target_snow_role,
            target_snow_authenticator=target_snow_authenticator,
            target_snow_password=target_snow_password,
        )
    else:
        # Use default session connection
        target_connector = args_manager.setup_target_connection(
            target_conn_mode=DEFAULT_CONNECTION_MODE,
        )

    # Set up validation environment
    validation_env = args_manager.setup_validation_environment(
        source_connector=source_connector,
        target_connector=target_connector,
        data_validation_config_file=data_validation_config_file,
        output_handler=ConsoleOutputHandler(enable_console_output=True),
    )

    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@snowflake_app.command("generate-validation-scripts")
@handle_validation_errors
def snowflake_run_async_generation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Generate validation scripts for Snowflake to Snowflake.

    This command uses ScriptWriter instances to write SQL queries to files
    instead of executing them for validation.
    """
    typer.secho(
        "Starting Snowflake validation script generation...", fg=typer.colors.BLUE
    )

    validation_env = create_environment_from_config(
        data_validation_config_file, ExecutionMode.ASYNC_GENERATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_async_generation()
    typer.secho("Validation scripts generated successfully!", fg=typer.colors.GREEN)


@snowflake_app.command(
    "get-configuration-files", help="Get configuration files for SQL Server validation."
)
def sqlserver_get_configuration_files(
    templates_directory: Annotated[
        Optional[str],
        typer.Option(
            "--templates-directory",
            "-td",
            help="Directory to save the configuration templates.",
        ),
    ]
):
    """Get configuration files for SQL Server validation."""
    try:
        typer.secho(
            "Retrieving SQL Server validation configuration files...",
            fg=typer.colors.BLUE,
        )
        args_manager = SnowflakeArgumentsManager()
        args_manager.dump_and_write_yaml_templates(
            source=Platform.SNOWFLAKE.value, templates_directory=templates_directory
        )
        typer.secho("Configuration files were generated ", fg=typer.colors.GREEN)
    except PermissionError as e:
        raise RuntimeError(
            f"Permission denied while writing template files: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to generate configuration files: {e}") from e
