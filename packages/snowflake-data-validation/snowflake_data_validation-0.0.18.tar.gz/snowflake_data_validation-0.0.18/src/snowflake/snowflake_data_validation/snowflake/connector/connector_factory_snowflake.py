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

"""Factory for creating Snowflake connectors from connection configurations."""


import typer

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.connector.connector_factory_base import (
    ConnectorFactoryBase,
)
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    Platform,
)


class SnowflakeConnectorFactory(ConnectorFactoryBase):

    """Factory for creating Snowflake connectors from connection configurations."""

    @staticmethod
    def create_connector(connection_config: Connection) -> ConnectorBase:
        """Create a Snowflake connector from connection configuration.

        Args:
            connection_config: Connection configuration object

        Returns:
            ConnectorBase: Configured Snowflake connector

        Raises:
            typer.BadParameter: If configuration is invalid or unsupported
            RuntimeError: If connection fails

        """
        mode = getattr(connection_config, "mode", DEFAULT_CONNECTION_MODE)

        if mode == CREDENTIALS_CONNECTION_MODE:
            return SnowflakeConnectorFactory._create_credentials_connector(
                connection_config
            )
        elif mode == NAME_CONNECTION_MODE:
            return SnowflakeConnectorFactory._create_name_connector(connection_config)
        elif mode == DEFAULT_CONNECTION_MODE:
            return SnowflakeConnectorFactory._create_default_connector()
        else:
            raise typer.BadParameter(
                message=f"Unsupported Snowflake connection mode: {mode}. "
                "Supported modes are 'credentials', 'name', and 'default'."
            )

    @staticmethod
    def _create_credentials_connector(
        connection_config: Connection,
    ) -> ConnectorSnowflake:
        """Create Snowflake connector using credentials."""

        def create_connector():
            connector = ConnectorSnowflake()

            connection_params = {
                "mode": CREDENTIALS_CONNECTION_MODE,
                "account": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "account", ""
                ),
                "username": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "username", ""
                ),
                "password": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "password", ""
                ),
                "database": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "database", ""
                ),
                "schema": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "schema", ""
                ),
                "warehouse": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "warehouse", ""
                ),
                "role": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "role", ""
                ),
                "authenticator": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "authenticator", ""
                ),
                "private_key_file": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "private_key_file", None
                ),
                "private_key_passphrase": SnowflakeConnectorFactory._get_optional_param(
                    connection_config, "private_key_passphrase", None
                ),
            }

            connector.connect(**connection_params)
            return connector

        return SnowflakeConnectorFactory._handle_connection_exceptions(
            Platform.SNOWFLAKE.value, create_connector
        )

    @staticmethod
    def _create_name_connector(connection_config: Connection) -> ConnectorSnowflake:
        """Create Snowflake connector using connection name."""
        connection_name = getattr(connection_config, "name", None)

        if not connection_name:
            raise typer.BadParameter(
                message="Connection name is required when using 'name' connection mode"
            )

        def create_connector():
            connector = ConnectorSnowflake()
            connection_params = {
                "mode": NAME_CONNECTION_MODE,
                "connection_name": connection_name,
            }

            connector.connect(**connection_params)
            return connector

        return SnowflakeConnectorFactory._handle_connection_exceptions(
            Platform.SNOWFLAKE.value, create_connector
        )

    @staticmethod
    def _create_default_connector() -> ConnectorSnowflake:
        """Create Snowflake connector using default connection."""

        def create_connector():
            connector = ConnectorSnowflake()
            connection_params = {"mode": DEFAULT_CONNECTION_MODE}

            connector.connect(**connection_params)
            return connector

        return SnowflakeConnectorFactory._handle_connection_exceptions(
            Platform.SNOWFLAKE.value, create_connector
        )
