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

"""Factory for creating Redshift connectors from connection configurations."""


from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.connector.connector_factory_base import (
    ConnectorFactoryBase,
)
from snowflake.snowflake_data_validation.redshift.connector.connector_redshift import (
    ConnectorRedshift,
)
from snowflake.snowflake_data_validation.utils.constants import Platform


class RedshiftConnectorFactory(ConnectorFactoryBase):

    """Factory for creating Redshift connectors from connection configurations."""

    @staticmethod
    def create_connector(connection_config: Connection) -> ConnectorBase:
        """Create a Redshift connector from connection configuration.

        Args:
            connection_config: Connection configuration object

        Returns:
            ConnectorBase: Configured Redshift connector

        Raises:
            typer.BadParameter: If configuration is invalid or unsupported
            ConnectionError: If connection fails

        """
        RedshiftConnectorFactory._check_credentials_mode_only(
            connection_config, Platform.REDSHIFT.value
        )

        return RedshiftConnectorFactory._create_credentials_connector(connection_config)

    @staticmethod
    def _create_credentials_connector(
        connection_config: Connection,
    ) -> ConnectorRedshift:
        """Create Redshift connector using credentials."""
        # Validate required parameters
        required_params = ["host", "database", "username", "password"]
        RedshiftConnectorFactory._validate_required_parameters(
            connection_config, required_params, Platform.REDSHIFT.value
        )

        def create_connector():
            connector = ConnectorRedshift()
            connector.connect(
                host=connection_config.host,
                database=connection_config.database,
                user=connection_config.username,
                password=connection_config.password,
                port=RedshiftConnectorFactory._get_optional_param(
                    connection_config, "port", 5439
                ),  # Default Redshift port
                max_attempts=RedshiftConnectorFactory._get_optional_param(
                    connection_config, "max_attempts", 3
                ),
                delay_seconds=RedshiftConnectorFactory._get_optional_param(
                    connection_config, "delay_seconds", 1.0
                ),
                delay_multiplier=RedshiftConnectorFactory._get_optional_param(
                    connection_config, "delay_multiplier", 2.0
                ),
            )
            return connector

        return RedshiftConnectorFactory._handle_connection_exceptions(
            Platform.REDSHIFT.value, create_connector
        )
