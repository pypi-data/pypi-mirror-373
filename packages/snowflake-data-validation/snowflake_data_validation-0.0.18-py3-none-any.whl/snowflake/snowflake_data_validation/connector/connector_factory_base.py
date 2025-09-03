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

"""Base connector factory providing common functionality for all database connectors."""

from abc import ABC, abstractmethod

import typer

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
)


class ConnectorFactoryBase(ABC):

    """Abstract base class for database connector factories.

    This class provides common functionality for creating database connectors
    from connection configurations, including parameter validation and
    standardized error handling.
    """

    @staticmethod
    @abstractmethod
    def create_connector(connection_config: Connection) -> ConnectorBase:
        """Create a connector from connection configuration.

        Args:
            connection_config: Connection configuration object

        Returns:
            ConnectorBase: Configured connector

        Raises:
            typer.BadParameter: If configuration is invalid or unsupported
            ConnectionError: If connection fails

        """
        pass

    @staticmethod
    def _validate_required_parameters(
        connection_config: Connection, required_params: list[str], platform_name: str
    ) -> None:
        """Validate that all required parameters are present in the connection config.

        Args:
            connection_config: Connection configuration object
            required_params: List of required parameter names
            platform_name: Name of the platform (for error messages)

        Raises:
            typer.BadParameter: If any required parameters are missing

        """
        missing_params = []

        for param in required_params:
            if not hasattr(connection_config, param) or not getattr(
                connection_config, param
            ):
                missing_params.append(param)

        if missing_params:
            raise typer.BadParameter(
                message=f"Missing required {platform_name} connection parameters: {', '.join(missing_params)}"
            )

    @staticmethod
    def _handle_connection_exceptions(
        platform_name: str, connect_func: callable, *args, **kwargs
    ) -> ConnectorBase:
        """Handle common connection exceptions with standardized error messages.

        Args:
            platform_name: Name of the platform (for error messages)
            connect_func: Function to call for creating the connection
            *args: Positional arguments to pass to connect_func
            **kwargs: Keyword arguments to pass to connect_func

        Returns:
            ConnectorBase: Successfully connected connector

        Raises:
            ConnectionError: If connection fails
            ImportError: If platform dependencies are not available
            typer.BadParameter: If connection parameters are invalid
            RuntimeError: For unexpected errors

        """
        try:
            return connect_func(*args, **kwargs)
        except ConnectionError as e:
            raise ConnectionError(
                f"Failed to establish {platform_name} connection: {e}"
            ) from e
        except ImportError as e:
            raise ImportError(f"{platform_name} dependencies not available: {e}") from e
        except ValueError as e:
            raise typer.BadParameter(
                f"Invalid {platform_name} connection parameters: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error setting up {platform_name} connection: {e}"
            ) from e

    @staticmethod
    def _check_credentials_mode_only(
        connection_config: Connection, platform_name: str
    ) -> None:
        """Check that the connection mode is credentials (for platforms that only support this mode).

        Args:
            connection_config: Connection configuration object
            platform_name: Name of the platform (for error messages)

        Raises:
            typer.BadParameter: If mode is not credentials

        """
        mode = getattr(connection_config, "mode", CREDENTIALS_CONNECTION_MODE)

        if mode != CREDENTIALS_CONNECTION_MODE:
            raise typer.BadParameter(
                message=f"Unsupported {platform_name} connection mode: {mode}. "
                "Only 'credentials' mode is supported."
            )

    @staticmethod
    def _get_optional_param(
        connection_config: Connection, param_name: str, default_value
    ):
        """Get an optional parameter from connection config with a default value.

        Args:
            connection_config: Connection configuration object
            param_name: Name of the parameter to retrieve
            default_value: Default value if parameter is not present

        Returns:
            Parameter value or default value

        """
        return getattr(connection_config, param_name, default_value)
