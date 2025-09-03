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
from snowflake.snowflake_data_validation.redshift.model.redshift_credentials_connection import (
    RedshiftCredentialsConnection,
)
from snowflake.snowflake_data_validation.redshift.redshift_arguments_manager import (
    RedshiftArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_factory import (
    create_validation_environment_from_config,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode, Platform
from snowflake.snowflake_data_validation.utils.validation_utils import (
    build_snowflake_credentials,
    validate_snowflake_credentials,
)


redshift_app = typer.Typer()
LOGGER = logging.getLogger(__name__)


def handle_validation_errors(func):
    """Handle validation errors and provide user-friendly messages."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except typer.BadParameter as e:
            error_msg = f"Invalid parameter: {e}"
            LOGGER.error("Parameter validation failed: %s", str(e))
            typer.secho(error_msg, fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None
        except FileNotFoundError as e:
            error_msg = f"Configuration file not found: {e}"
            LOGGER.error("File not found error: %s", str(e))
            typer.secho(error_msg, fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None
        except ConnectionError as e:
            error_msg = f"Connection error: {e}"
            LOGGER.error("Database connection failed: %s", str(e))
            typer.secho(error_msg, fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None
        except Exception as e:
            error_msg = f"Operation failed: {e}"
            LOGGER.exception("Unexpected error occurred: %s", str(e))
            typer.secho(error_msg, fg=typer.colors.RED, err=True)
            raise typer.Exit(1) from None

    return wrapper


@redshift_app.command("run-validation")
@handle_validation_errors
def redshift_run_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Run data validation for Redshift."""
    typer.secho("Starting Redshift validation...", fg=typer.colors.BLUE)

    validation_env = _create_environment_from_config(
        data_validation_config_file, ExecutionMode.SYNC_VALIDATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@redshift_app.command("run-async-validation")
@handle_validation_errors
def redshift_run_async_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Run async data validation for Redshift to Snowflake."""
    typer.secho(
        "Starting Redshift to Snowflake async validation...", fg=typer.colors.BLUE
    )

    validation_env = _create_environment_from_config(
        data_validation_config_file, ExecutionMode.ASYNC_VALIDATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_async_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@redshift_app.command("run-validation-ipc", hidden=True)
@handle_validation_errors
def redshift_run_validation_ipc(
    source_host: Annotated[
        str, typer.Option("--source-host", "-srch", help="Source Host name")
    ],
    source_username: Annotated[
        str, typer.Option("--source-username", "-srcu", help="Source Username")
    ],
    source_password: Annotated[
        str, typer.Option("--source-password", "-srcpw", help="Source Password")
    ],
    source_database: Annotated[
        str, typer.Option("--source-database", "-srcd", help="Source Database used")
    ],
    snow_account: Annotated[
        str, typer.Option("--snow-account", "-sa", help="Snowflake account name")
    ],
    snow_username: Annotated[
        str, typer.Option("--snow_username", "-su", help="Snowflake Username")
    ],
    snow_database: Annotated[
        str, typer.Option("--snow_database", "-sd", help="Snowflake Database used")
    ],
    snow_warehouse: Annotated[
        str, typer.Option("--snow_warehouse", "-sw", help="Snowflake Warehouse used")
    ],
    source_port: Annotated[
        int, typer.Option("--source-port", "-srcp", help="Source Port number")
    ] = 5439,
    snow_schema: Annotated[
        Optional[str],
        typer.Option("--snow_schema", "-ss", help="Snowflake Schema used"),
    ] = None,
    snow_role: Annotated[
        Optional[str], typer.Option("--snow_role", "-sr", help="Snowflake Role used")
    ] = None,
    snow_authenticator: Annotated[
        Optional[str],
        typer.Option(
            "--snow_authenticator", "-sau", help="Snowflake Authenticator method used"
        ),
    ] = None,
    snow_password: Annotated[
        Optional[str], typer.Option("--snow_password", "-sp", help="Snowflake Password")
    ] = None,
    snow_private_key_file: Annotated[
        str,
        typer.Option(
            "--snow_private_key_file", "-spk", help="Snowflake Private Key File"
        ),
    ] = None,
    snow_private_key_passphrase: Annotated[
        str,
        typer.Option(
            "--snow_private_key_passphrase",
            "-spkp",
            help="Snowflake Private Key Passphrase",
        ),
    ] = None,
    data_validation_config_file: Annotated[
        Optional[str],
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path.",
        ),
    ] = None,
):
    """Run data validation for Redshift to Snowflake with IPC (In-Process Communication).

    This command allows direct specification of connection parameters without requiring
    pre-saved connection files.
    """
    args_manager = RedshiftArgumentsManager()

    snow_credential_object = build_snowflake_credentials(
        account=snow_account,
        username=snow_username,
        database=snow_database,
        schema=snow_schema,
        warehouse=snow_warehouse,
        role=snow_role,
        authenticator=snow_authenticator,
        password=snow_password,
        private_key_file=snow_private_key_file,
        private_key_passphrase=snow_private_key_passphrase,
    )

    validate_snowflake_credentials(snow_credential_object)

    redshift_credentials = RedshiftCredentialsConnection(
        host=source_host,
        port=source_port,
        username=source_username,
        password=source_password,
        database=source_database,
    )
    redshift_credentials.model_validate(redshift_credentials)

    if data_validation_config_file:
        configuration = args_manager.load_configuration(
            data_validation_config_file=data_validation_config_file
        )
        output_directory_path = configuration.output_directory_path
    else:
        output_directory_path = None

    validation_env = args_manager.setup_validation_environment(
        source_connection_config=redshift_credentials,
        target_connection_config=snow_credential_object,
        data_validation_config_file=data_validation_config_file or "default",
        output_directory_path=output_directory_path,
        output_handler=ConsoleOutputHandler(enable_console_output=False),
        execution_mode=ExecutionMode.SYNC_VALIDATION,
    )

    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@redshift_app.command("generate-validation-scripts")
@handle_validation_errors
def redshift_run_async_generation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Generate validation scripts for Redshift to Snowflake."""
    typer.secho(
        "Starting Redshift to Snowflake validation script generation...",
        fg=typer.colors.BLUE,
    )

    validation_env = _create_environment_from_config(
        data_validation_config_file, ExecutionMode.ASYNC_GENERATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_async_generation()
    typer.secho(
        "Validation script generation completed successfully!", fg=typer.colors.GREEN
    )


@redshift_app.command(
    "get-configuration-files", help="Get configuration files for Redshift validation."
)
def redshift_get_configuration_files(
    templates_directory: Annotated[
        Optional[str],
        typer.Option(
            "--templates-directory",
            "-td",
            help="Directory to save the configuration templates.",
        ),
    ] = None
):
    """Get configuration files for Redshift validation."""
    try:
        typer.secho(
            "Retrieving Redshift validation configuration files...",
            fg=typer.colors.BLUE,
        )
        args_manager = RedshiftArgumentsManager()
        output_dir = templates_directory if templates_directory else "."
        args_manager.dump_and_write_yaml_templates(
            source=Platform.REDSHIFT.value, templates_directory=output_dir
        )
        typer.secho("Configuration files were generated ", fg=typer.colors.GREEN)
    except PermissionError as e:
        permission_error_msg = f"Permission denied while writing template files: {e}"
        LOGGER.error(permission_error_msg)
        raise RuntimeError(permission_error_msg) from e
    except Exception as e:
        runtime_error_msg = f"Failed to generate configuration files: {e}"
        LOGGER.error(runtime_error_msg)
        raise RuntimeError(runtime_error_msg) from e


def _create_environment_from_config(
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
