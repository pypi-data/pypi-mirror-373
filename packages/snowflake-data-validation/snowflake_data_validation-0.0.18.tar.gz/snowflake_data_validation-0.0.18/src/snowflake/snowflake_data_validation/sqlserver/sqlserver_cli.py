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
"""SQL Server CLI commands for data validation."""

import logging

from functools import wraps
from pathlib import Path
from typing import Annotated, Optional

import typer

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.configuration.model.connections import (
    SnowflakeCredentialsConnection,
    SnowflakeDefaultConnection,
    SqlServerCredentialsConnection,
)
from snowflake.snowflake_data_validation.sqlserver.sqlserver_arguments_manager import (
    SqlServerArgumentsManager,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)
from snowflake.snowflake_data_validation.utils.validation_utils import (
    build_snowflake_credentials,
    create_environment_from_config,
    validate_snowflake_credentials,
)


# Create SQL Server typer app
sqlserver_app = typer.Typer()


# Create logger for this module
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


def validate_ipc_parameters(
    source_host: str,
    source_port: int,
    source_username: str,
    source_password: str,
    source_database: str,
    source_trust_server_certificate: str = "no",
    source_encrypt: str = "yes",
    data_validation_config_file: Optional[str] = None,
) -> None:
    """Validate IPC command parameters and provide helpful error messages.

    Args:
        source_host: Source database host
        source_port: Source database port
        source_username: Source database username
        source_password: Source database password
        source_database: Source database name
        source_trust_server_certificate: Trust server certificate setting
        source_encrypt: Encrypt connection setting
        data_validation_config_file: Optional config file path

    Raises:
        typer.BadParameter: If any required parameters are missing or invalid

    """
    LOGGER.debug("Starting IPC parameter validation")
    missing_params = []

    # Check required SQL Server connection parameters
    if not source_host or not source_host.strip():
        missing_params.append("--source-host")
    if not source_port or source_port <= 0:
        missing_params.append("--source-port (must be > 0)")
    if not source_username or not source_username.strip():
        missing_params.append("--source-username")
    if not source_password or not source_password.strip():
        missing_params.append("--source-password")
    if not source_database or not source_database.strip():
        missing_params.append("--source-database")

    # Validate SSL/TLS parameters
    valid_trust_values = ["yes", "no"]
    if source_trust_server_certificate.lower() not in valid_trust_values:
        LOGGER.error(
            "Invalid trust_server_certificate value: %s",
            source_trust_server_certificate,
        )
        raise typer.BadParameter(
            message=f"Invalid value for --source-trust-server-certificate: '{source_trust_server_certificate}'. "
            f"Valid values are: {', '.join(valid_trust_values)}"
        )

    valid_encrypt_values = ["yes", "no", "optional"]
    if source_encrypt.lower() not in valid_encrypt_values:
        LOGGER.error("Invalid encrypt value: %s", source_encrypt)
        raise typer.BadParameter(
            message=f"Invalid value for --source-encrypt: '{source_encrypt}'. "
            f"Valid values are: {', '.join(valid_encrypt_values)}"
        )

    if missing_params:
        LOGGER.error("Missing required parameters: %s", ", ".join(missing_params))
        error_msg = (
            f"Missing required SQL Server connection parameters: {', '.join(missing_params)}.\n\n"
            "The following parameters are required for SQL Server IPC validation:\n"
            "  --source-host: SQL Server hostname or IP address\n"
            "  --source-port: SQL Server port number (e.g., 1433)\n"
            "  --source-username: SQL Server username\n"
            "  --source-password: SQL Server password\n"
            "  --source-database: SQL Server database name\n\n"
            "Optional SSL/TLS parameters:\n"
            "  --source-trust-server-certificate: Trust server certificate (yes/no, default: no)\n"
            "  --source-encrypt: Encrypt connection (yes/no/optional, default: yes)\n\n"
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


@sqlserver_app.command("run-validation")
@handle_validation_errors
def sqlserver_run_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Run data validation for SQL Server to Snowflake."""
    typer.secho("Starting SQL Server to Snowflake validation...", fg=typer.colors.BLUE)

    # Create validation environment from config file
    validation_env = create_environment_from_config(
        data_validation_config_file, ExecutionMode.SYNC_VALIDATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@sqlserver_app.command("run-async-validation")
@handle_validation_errors
def sqlserver_run_async_validation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Run async data validation for SQL Server to Snowflake."""
    typer.secho(
        "Starting SQL Server to Snowflake async validation...", fg=typer.colors.BLUE
    )

    validation_env = create_environment_from_config(
        data_validation_config_file, ExecutionMode.ASYNC_VALIDATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_async_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@sqlserver_app.command("run-validation-ipc", hidden=True)
@handle_validation_errors
def sqlserver_run_validation_ipc(
    source_host: Annotated[
        str, typer.Option("--source-host", "-srch", help="Source Host name")
    ],
    source_port: Annotated[
        int, typer.Option("--source-port", "-srcp", help="Source Port number")
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
    source_trust_server_certificate: Annotated[
        str,
        typer.Option(
            "--source-trust-server-certificate",
            "-srctsc",
            help="Trust server certificate (yes/no)",
        ),
    ] = "no",
    source_encrypt: Annotated[
        str,
        typer.Option(
            "--source-encrypt", "-srce", help="Encrypt connection (yes/no/optional)"
        ),
    ] = "yes",
    snow_account: Annotated[
        str, typer.Option("--snow-account", "-sa", help="Snowflake account name")
    ] = None,
    snow_username: Annotated[
        str, typer.Option("--snow_username", "-su", help="Snowflake Username")
    ] = None,
    snow_database: Annotated[
        str, typer.Option("--snow_database", "-sd", help="Snowflake Database used")
    ] = None,
    snow_schema: Annotated[
        str, typer.Option("--snow_schema", "-ss", help="Snowflake Schema used")
    ] = None,
    snow_warehouse: Annotated[
        str, typer.Option("--snow_warehouse", "-sw", help="Snowflake Warehouse used")
    ] = None,
    snow_role: Annotated[
        str, typer.Option("--snow_role", "-sr", help="Snowflake Role used")
    ] = None,
    snow_authenticator: Annotated[
        str,
        typer.Option(
            "--snow_authenticator", "-sau", help="Snowflake Authenticator method used"
        ),
    ] = None,
    snow_password: Annotated[
        str, typer.Option("--snow_password", "-sp", help="Snowflake Password")
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
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path.",
        ),
    ] = None,
):
    """Run data validation for SQL Server to Snowflake with IPC (In-Process Communication).

    This command allows direct specification of connection parameters without requiring
    pre-saved connection files.
    """
    # Validate required parameters early and provide clear error messages
    validate_ipc_parameters(
        source_host=source_host,
        source_port=source_port,
        source_username=source_username,
        source_password=source_password,
        source_database=source_database,
        source_trust_server_certificate=source_trust_server_certificate,
        source_encrypt=source_encrypt,
        data_validation_config_file=data_validation_config_file,
    )

    # Build Snowflake credentials
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

    # Create connection objects directly
    # Create source connection
    source_connection = SqlServerCredentialsConnection(
        mode=CREDENTIALS_CONNECTION_MODE,
        host=source_host,
        port=source_port,
        username=source_username,
        password=source_password,
        database=source_database,
        trust_server_certificate=source_trust_server_certificate,
        encrypt=source_encrypt,
    )

    # Create target connection
    if snow_credential_object:
        target_connection = SnowflakeCredentialsConnection(
            mode=CREDENTIALS_CONNECTION_MODE,
            account=snow_credential_object.get("account"),
            username=snow_credential_object.get("username"),
            database=snow_credential_object.get("database"),
            warehouse=snow_credential_object.get("warehouse"),
            schema=snow_credential_object.get("schema"),
            role=snow_credential_object.get("role"),
            authenticator=snow_credential_object.get("authenticator"),
            password=snow_credential_object.get("password"),
            private_key_file=snow_credential_object.get("private_key_file"),
            private_key_passphrase=snow_credential_object.get("private_key_passphrase"),
        )
    else:
        target_connection = SnowflakeDefaultConnection(mode=DEFAULT_CONNECTION_MODE)

    # Create validation environment using the new infrastructure
    args_manager = SqlServerArgumentsManager()
    validation_env = args_manager.setup_validation_environment(
        source_connection_config=source_connection,
        target_connection_config=target_connection,
        data_validation_config_file=data_validation_config_file,
        output_handler=ConsoleOutputHandler(enable_console_output=False),
        execution_mode=ExecutionMode.SYNC_VALIDATION,
    )

    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_sync_comparison()
    typer.secho("Validation completed successfully!", fg=typer.colors.GREEN)


@sqlserver_app.command("generate-validation-scripts")
@handle_validation_errors
def sqlserver_run_async_generation(
    data_validation_config_file: Annotated[
        str,
        typer.Option(
            "--data-validation-config-file",
            "-dvf",
            help="Data validation configuration file path. ",
        ),
    ],
):
    """Generate validation scripts for SQL Server to Snowflake.

    This command uses ScriptWriter instances to write SQL queries to files
    instead of executing them for validation.
    """
    typer.secho(
        "Starting SQL Server to Snowflake validation script generation...",
        fg=typer.colors.BLUE,
    )

    validation_env = create_environment_from_config(
        data_validation_config_file, ExecutionMode.ASYNC_GENERATION
    )
    orchestrator = ComparisonOrchestrator.from_validation_environment(validation_env)
    orchestrator.run_async_generation()
    typer.secho("Validation scripts generated successfully!", fg=typer.colors.GREEN)


@sqlserver_app.command(
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
        args_manager = SqlServerArgumentsManager()
        args_manager.dump_and_write_yaml_templates(
            source=Platform.SQLSERVER.value, templates_directory=templates_directory
        )
        typer.secho("Configuration files were generated ", fg=typer.colors.GREEN)
    except PermissionError as e:
        raise RuntimeError(
            f"Permission denied while writing template files: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to generate configuration files: {e}") from e
