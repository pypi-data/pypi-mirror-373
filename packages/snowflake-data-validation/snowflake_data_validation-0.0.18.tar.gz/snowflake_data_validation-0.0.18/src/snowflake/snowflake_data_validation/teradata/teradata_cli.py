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

"""Teradata CLI commands for data validation."""

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
from snowflake.snowflake_data_validation.snowflake.model.snowflake_credentials_connection import (
    SnowflakeCredentialsConnection,
)
from snowflake.snowflake_data_validation.teradata.model.teradata_credentials_connection import (
    TeradataCredentialsConnection,
)
from snowflake.snowflake_data_validation.teradata.teradata_arguments_manager import (
    TeradataArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    ExecutionMode,
)
from snowflake.snowflake_data_validation.utils.validation_utils import (
    build_snowflake_credentials,
    create_environment_from_config,
    validate_snowflake_credentials,
)


# Create Teradata typer app
teradata_app = typer.Typer()


# Create logger for this module
LOGGER = logging.getLogger(__name__)


def validate_ipc_parameters(
    source_host: str,
    source_username: str,
    source_password: str,
    source_database: str,
    data_validation_config_file: Optional[str] = None,
) -> None:
    """Validate IPC command parameters and provide helpful error messages.

    Args:
        source_host: Source database host
        source_username: Source database username
        source_password: Source database password
        source_database: Source database name
        data_validation_config_file: Optional config file path

    Raises:
        typer.BadParameter: If any required parameters are missing or invalid

    """
    LOGGER.debug("Starting IPC parameter validation")
    missing_params = []

    # Check required Teradata connection parameters
    if not source_host or not source_host.strip():
        missing_params.append("--source-host")
    if not source_username or not source_username.strip():
        missing_params.append("--source-username")
    if not source_password or not source_password.strip():
        missing_params.append("--source-password")
    if not source_database or not source_database.strip():
        missing_params.append("--source-database")

    if missing_params:
        LOGGER.error("Missing required parameters: %s", ", ".join(missing_params))
        error_msg = (
            f"Missing required Teradata connection parameters: {', '.join(missing_params)}.\n\n"
            "The following parameters are required for Teradata IPC validation:\n"
            "  --source-host: Teradata hostname or IP address\n"
            "  --source-username: Teradata username\n"
            "  --source-password: Teradata password\n"
            "  --source-database: Teradata database name\n\n"
        )
        raise typer.BadParameter(message=error_msg)

    # Validate config file if provided
    if data_validation_config_file:
        config_path = Path(data_validation_config_file)
        if not config_path.exists():
            LOGGER.error(
                "Configuration file not found: %s", data_validation_config_file
            )
            raise typer.BadParameter(
                message=f"Configuration file not found: {data_validation_config_file}\n"
                "Please ensure the file exists and the path is correct."
            )
        if not config_path.is_file():
            LOGGER.error(
                "Configuration path is not a file: %s", data_validation_config_file
            )
            raise typer.BadParameter(
                message=f"Configuration path is not a file: {data_validation_config_file}\n"
                "Please provide a valid YAML configuration file."
            )

    LOGGER.info("IPC parameter validation completed successfully")


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


@teradata_app.command("run-validation")
@handle_validation_errors
def teradata_run_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path.",
        ),
    ],
    teradata_host: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-host",
            help="Teradata server hostname or IP address",
        ),
    ] = None,
    teradata_username: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-username",
            help="Teradata username for authentication",
        ),
    ] = None,
    teradata_password: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-password",
            help="Teradata password for authentication",
            hide_input=True,
        ),
    ] = None,
    teradata_database: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-database",
            help="Teradata database name (default: DBC)",
        ),
    ] = None,
    snowflake_connection_name: Annotated[
        Optional[str],
        typer.Option(
            "--snowflake-connection-name",
            help="Snowflake connection name (when using named connections)",
        ),
    ] = None,
    output_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--output-directory",
            help="Directory to save validation results and reports",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """Perform synchronous validation of data between Teradata and Snowflake.

    This command validates data between a Teradata source and Snowflake target
    by comparing table schemas and column-level metrics.
    """
    typer.secho("Starting Teradata to Snowflake validation...", fg=typer.colors.BLUE)

    # Load configuration from file
    config_loader = ConfigurationLoader(Path(data_validation_config_file))
    config_model = config_loader.get_configuration_model()

    if output_directory:
        config_model.output_directory_path = str(output_directory)

    # Handle command line overrides for connections
    if any([teradata_host, teradata_username, teradata_password]):
        # Use TeradataArgumentsManager for IPC-style parameter handling
        args_manager = TeradataArgumentsManager()

        # Create validation environment using direct connection parameters
        validation_env = args_manager.setup_validation_environment(
            source_connector=args_manager.setup_source_connection(
                source_conn_mode=CREDENTIALS_CONNECTION_MODE,
                source_host=teradata_host,
                source_username=teradata_username,
                source_password=teradata_password,
                source_database=teradata_database,
            ),
            target_connector=args_manager.setup_target_connection(
                snowflake_connection_name=snowflake_connection_name,
            ),
            data_validation_config_file=data_validation_config_file,
            execution_mode=ExecutionMode.SYNC_VALIDATION,
            output_directory_path=config_model.output_directory_path,
            output_handler=ConsoleOutputHandler(),
        )
    else:
        # Use configuration file for connections
        validation_env = create_environment_from_config(
            data_validation_config_file, ExecutionMode.SYNC_VALIDATION
        )

    # Execute validation
    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@teradata_app.command("generate-validation-scripts")
@handle_validation_errors
def teradata_generate_validation_scripts(
    config_file: Annotated[
        Path,
        typer.Argument(
            help="Path to the YAML configuration file for validation",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    teradata_host: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-host",
            help="Teradata server hostname or IP address",
        ),
    ] = None,
    teradata_username: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-username",
            help="Teradata username for authentication",
        ),
    ] = None,
    teradata_password: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-password",
            help="Teradata password for authentication",
            hide_input=True,
        ),
    ] = None,
    teradata_database: Annotated[
        Optional[str],
        typer.Option(
            "--teradata-database",
            help="Teradata database name (default: DBC)",
        ),
    ] = None,
    output_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--output-directory",
            help="Directory to save generated SQL scripts",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """Generate SQL scripts for asynchronous validation between Teradata and Snowflake.

    This command generates SQL scripts that can be executed separately to extract
    metadata from both Teradata and Snowflake for later comparison.
    """
    typer.secho(
        "Starting Teradata to Snowflake validation script generation...",
        fg=typer.colors.BLUE,
    )

    # Load configuration from file
    config_loader = ConfigurationLoader(Path(config_file))
    config_model = config_loader.get_configuration_model()

    if output_directory:
        config_model.output_directory_path = str(output_directory)

    # Handle command line overrides for connections
    if any([teradata_host, teradata_username, teradata_password]):
        # Use TeradataArgumentsManager for IPC-style parameter handling
        args_manager = TeradataArgumentsManager()

        # Create validation environment using direct connection parameters
        validation_env = args_manager.setup_validation_environment(
            source_connector=args_manager.setup_source_connection(
                source_conn_mode=CREDENTIALS_CONNECTION_MODE,
                source_host=teradata_host,
                source_username=teradata_username,
                source_password=teradata_password,
                source_database=teradata_database,
            ),
            target_connector=args_manager.setup_target_connection(),
            data_validation_config_file=str(config_file),
            execution_mode=ExecutionMode.SYNC_VALIDATION,
            output_directory_path=config_model.output_directory_path,
            output_handler=ConsoleOutputHandler(),
        )
    else:
        # Use configuration file for connections
        validation_env = create_environment_from_config(
            str(config_file), ExecutionMode.ASYNC_GENERATION
        )

    # Execute script generation
    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_async_generation()
    typer.secho("Validation scripts generated successfully!", fg=typer.colors.GREEN)


@teradata_app.command("run-async-validation")
@handle_validation_errors
def teradata_run_async_validation(
    config_file: Annotated[
        Path,
        typer.Argument(
            help="Path to the YAML configuration file for validation",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output_directory: Annotated[
        Optional[Path],
        typer.Option(
            "--output-directory",
            help="Directory containing metadata files from async-generate",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """Perform validation using pre-generated metadata files.

    This command compares metadata files that were generated using the async-generate
    command to produce validation results without connecting to databases.
    """
    typer.secho(
        "Starting Teradata to Snowflake async validation...", fg=typer.colors.BLUE
    )

    # Load configuration from file
    config_loader = ConfigurationLoader(Path(config_file))
    config_model = config_loader.get_configuration_model()

    if output_directory:
        config_model.output_directory_path = str(output_directory)

    # Use configuration file for async validation
    validation_env = create_environment_from_config(
        str(config_file), ExecutionMode.ASYNC_VALIDATION
    )

    # Execute async validation
    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_async_validation()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@teradata_app.command("run-validation-ipc", hidden=True)
@handle_validation_errors
def teradata_run_validation_ipc(
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
        Optional[str],
        typer.Option("--snow-account", "-sa", help="Snowflake account name"),
    ] = None,
    snow_username: Annotated[
        Optional[str], typer.Option("--snow_username", "-su", help="Snowflake Username")
    ] = None,
    snow_database: Annotated[
        Optional[str],
        typer.Option("--snow_database", "-sd", help="Snowflake Database used"),
    ] = None,
    snow_schema: Annotated[
        Optional[str],
        typer.Option("--snow_schema", "-ss", help="Snowflake Schema used"),
    ] = None,
    snow_warehouse: Annotated[
        Optional[str],
        typer.Option("--snow_warehouse", "-sw", help="Snowflake Warehouse used"),
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
    """Run data validation for Teradata to Snowflake with IPC (In-Process Communication).

    This command allows direct specification of connection parameters without requiring
    pre-saved connection files.
    """
    # Validate required parameters early and provide clear error messages
    validate_ipc_parameters(
        source_host=source_host,
        source_username=source_username,
        source_password=source_password,
        source_database=source_database,
        data_validation_config_file=data_validation_config_file,
    )

    # Set up arguments manager and connections
    args_manager = TeradataArgumentsManager()

    # Build Snowflake credentials target (first)
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

    # Validate Snowflake credentials if provided
    validate_snowflake_credentials(snow_credential_object)

    target_connection_config = SnowflakeCredentialsConnection(
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

    source_connection_config = TeradataCredentialsConnection(
        host=source_host,
        username=source_username,
        password=source_password,
        database=source_database,
    )



    configuration = args_manager.load_configuration(
        data_validation_config_file=data_validation_config_file or "default"
    )

    # Set up validation environment
    validation_env = args_manager.setup_validation_environment(
        source_connection_config=source_connection_config,
        target_connection_config=target_connection_config,
        data_validation_config_file=data_validation_config_file or "default",
        execution_mode=ExecutionMode.SYNC_VALIDATION,
        output_directory_path=configuration.output_directory_path,
        output_handler=ConsoleOutputHandler(enable_console_output=False),
    )

    orchestrator = ComparisonOrchestrator.from_validation_environment(
        validation_env  # type: ignore
    )
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)
