"""Shared utilities for validation CLIs."""

import logging

from pathlib import Path
from typing import Optional

import typer

from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_factory import (
    create_validation_environment_from_config,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode


LOGGER = logging.getLogger(__name__)


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


def build_snowflake_credentials(
    account: Optional[str] = None,
    username: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    warehouse: Optional[str] = None,
    role: Optional[str] = None,
    authenticator: Optional[str] = None,
    password: Optional[str] = None,
    private_key_file: Optional[str] = None,
    private_key_passphrase: Optional[str] = None,
) -> dict[str, Optional[str]]:
    """Build Snowflake credentials dictionary from parameters."""
    # Use dictionary comprehension to filter out None values
    return {
        key: value
        for key, value in {
            "account": account,
            "username": username,
            "database": database,
            "schema": schema,
            "warehouse": warehouse,
            "role": role,
            "authenticator": authenticator,
            "password": password,
            "private_key_file": private_key_file,
            "private_key_passphrase": private_key_passphrase,
        }.items()
        if value is not None
    }


def validate_snowflake_credentials(
    snow_credential_object: dict[str, Optional[str]]
) -> None:
    """Validate Snowflake credentials and provide helpful error messages.

    Args:
        snow_credential_object: Dictionary containing Snowflake credentials

    Raises:
        typer.BadParameter: If credentials are incomplete or invalid

    """
    if not snow_credential_object:
        # If no Snowflake credentials provided, assume using default connection
        LOGGER.debug("No Snowflake credentials provided - using default connection")
        return

    LOGGER.debug("Starting Snowflake credentials validation")
    missing_params = []

    # Check for essential Snowflake parameters
    if not snow_credential_object.get("account"):
        missing_params.append("--snow-account")
    if not snow_credential_object.get("username"):
        missing_params.append("--snow-username")
    if not snow_credential_object.get("database"):
        missing_params.append("--snow-database")
    if not snow_credential_object.get("warehouse"):
        missing_params.append("--snow-warehouse")

    # Check authentication method
    authenticator = snow_credential_object.get("authenticator", "snowflake")
    if (
        authenticator
        and authenticator.lower() == "snowflake"
        and not snow_credential_object.get("password")
    ):
        missing_params.append("--snow-password (required for snowflake authenticator)")
    if (
        authenticator
        and authenticator.lower() == "snowflake_jwt"
        and not snow_credential_object.get("private_key_file")
    ):
        missing_params.append(
            "--snow_private_key_file (required for key pair authenticator)"
        )

    if missing_params:
        LOGGER.error(
            "Incomplete Snowflake credentials - missing: %s", ", ".join(missing_params)
        )
        error_msg = (
            f"Incomplete Snowflake connection parameters: {', '.join(missing_params)}.\n\n"
            "For Snowflake credential-based authentication, the following parameters are required:\n"
            "  --snow-account: Snowflake account name (e.g., myorg-myaccount)\n"
            "  --snow-username: Snowflake username\n"
            "  --snow-database: Snowflake database name\n"
            "  --snow-warehouse: Snowflake warehouse name\n"
            "  --snow-password: Snowflake password (for snowflake authenticator)\n\n"
            "Optional parameters:\n"
            "  --snow-schema: Snowflake schema name (can be specified in queries if omitted)\n"
            "  --snow-role: Snowflake role (if not specified, uses default)\n"
            "  --snow-authenticator: Authentication method (default: snowflake)\n\n"
            "Alternatively, you can use a pre-configured Snowflake connection by omitting these parameters."
        )
        raise typer.BadParameter(message=error_msg)

    LOGGER.info("Snowflake credentials validation completed successfully")
