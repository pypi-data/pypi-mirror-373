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

"""Factory for creating SQL Server connectors from connection configurations."""


from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.connector.connector_factory_base import (
    ConnectorFactoryBase,
)
from snowflake.snowflake_data_validation.sqlserver.connector.connector_sql_server import (
    ConnectorSqlServer,
)
from snowflake.snowflake_data_validation.utils.constants import Platform


class SqlServerConnectorFactory(ConnectorFactoryBase):

    """Factory for creating SQL Server connectors from connection configurations."""

    @staticmethod
    def create_connector(connection_config: Connection) -> ConnectorBase:
        """Create a SQL Server connector from connection configuration.

        Args:
            connection_config: Connection configuration object

        Returns:
            ConnectorBase: Configured SQL Server connector

        Raises:
            typer.BadParameter: If configuration is invalid or unsupported
            ConnectionError: If connection fails

        """
        SqlServerConnectorFactory._check_credentials_mode_only(
            connection_config, Platform.SQLSERVER.value
        )

        return SqlServerConnectorFactory._create_credentials_connector(
            connection_config
        )

    @staticmethod
    def _create_credentials_connector(
        connection_config: Connection,
    ) -> ConnectorSqlServer:
        """Create SQL Server connector using credentials."""
        # Validate required parameters
        required_params = [
            "host",
            "database",
            "username",
            "password",
            "port",
        ]
        SqlServerConnectorFactory._validate_required_parameters(
            connection_config, required_params, Platform.SQLSERVER.value
        )

        def create_connector():
            connector = ConnectorSqlServer()
            connector.connect(
                host=connection_config.host,
                database=connection_config.database,
                user=connection_config.username,
                password=connection_config.password,
                port=connection_config.port,
                trust_server_certificate=getattr(
                    connection_config, "trust_server_certificate", "no"
                ),
                encrypt=getattr(connection_config, "encrypt", "yes"),
            )
            return connector

        return SqlServerConnectorFactory._handle_connection_exceptions(
            Platform.SQLSERVER.value, create_connector
        )
