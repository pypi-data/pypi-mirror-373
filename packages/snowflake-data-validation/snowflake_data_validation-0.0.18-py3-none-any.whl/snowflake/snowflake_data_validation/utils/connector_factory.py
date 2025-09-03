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

"""Generic connector factory for all supported platforms."""

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.redshift.connector.connector_factory_redshift import (
    RedshiftConnectorFactory,
)
from snowflake.snowflake_data_validation.snowflake.connector.connector_factory_snowflake import (
    SnowflakeConnectorFactory,
)
from snowflake.snowflake_data_validation.sqlserver.connector.connector_factory_sql_server import (
    SqlServerConnectorFactory,
)
from snowflake.snowflake_data_validation.teradata.connector.connector_factory_teradata import (
    TeradataConnectorFactory,
)
from snowflake.snowflake_data_validation.utils.constants import Platform


class ConnectorFactory:

    """Generic factory for creating connectors based on platform and connection configuration."""

    # Registry mapping platforms to their respective factory classes
    _PLATFORM_FACTORIES = {
        Platform.SNOWFLAKE: SnowflakeConnectorFactory,
        Platform.SQLSERVER: SqlServerConnectorFactory,
        Platform.REDSHIFT: RedshiftConnectorFactory,
        Platform.TERADATA: TeradataConnectorFactory,
    }

    @staticmethod
    def create_connector(
        platform: Platform, connection_config: Connection
    ) -> ConnectorBase:
        """Create a connector for the specified platform and connection configuration.

        Args:
            platform: The platform type (e.g., Platform.SNOWFLAKE, Platform.SQLSERVER)
            connection_config: Connection configuration object

        Returns:
            ConnectorBase: Configured connector for the specified platform

        Raises:
            ValueError: If platform is not supported
            typer.BadParameter: If configuration is invalid
            ConnectionError: If connection fails

        """
        factory_class = ConnectorFactory._PLATFORM_FACTORIES.get(platform)
        if factory_class is None:
            raise ValueError(f"Unsupported platform: {platform}")

        return factory_class.create_connector(connection_config)
