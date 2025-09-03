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

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CONNECTION_NOT_ESTABLISHED,
    FAILED_TO_EXECUTE_QUERY,
    FAILED_TO_EXECUTE_STATEMENT,
)
from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.telemetry import (
    report_telemetry,
)


LOGGER = logging.getLogger(__name__)


@Helper.import_dependencies("teradata")
def import_teradata():
    """Import the teradatasql module for native Teradata connection."""
    import teradatasql

    return teradatasql


class ConnectorTeradata(BaseConnector):

    """Connector for Teradata database using native Python connector."""

    def __init__(self) -> None:
        """Initialize the Teradata connector."""
        super().__init__()
        self.connection = None
        self.teradatasql = import_teradata()

    @log(log_args=False)
    @report_telemetry(params_list=["host", "database", "user"])
    def connect(
        self,
        host: str,
        user: str,
        password: str,
        database: str = "",
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        delay_multiplier: float = 2.0,
    ):
        """Establish a connection to a Teradata database using the native Python connector.

        Args:
            host (str): The hostname or IP address of the Teradata server.
            user (str): The username for authentication.
            password (str): The password for authentication.
            database (str, optional): The default database to use after connection.
            max_attempts (int): Maximum number of connection attempts. Defaults to 3.
            delay_seconds (float): Initial delay between retries in seconds. Defaults to 1.0.
            delay_multiplier (float): Multiplier for exponential backoff. Defaults to 2.0.

        Raises:
            ValueError: If any connection parameters are invalid
            ConnectionError: If connection cannot be established

        """
        LOGGER.info(
            "Attempting to connect to Teradata at %s using native connector", host
        )

        if not all([host, user, password]):
            error_msg = "Host, user, and password are required connection parameters"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)

        self.connect_with_retry(
            self._attempt_connection_and_verify,
            max_attempts,
            delay_seconds,
            delay_multiplier,
            self._internal_connect,
            host,
            user,
            password,
            database,
        )

    def _internal_connect(
        self,
        host: str,
        user: str,
        password: str,
        database: str = "",
    ):
        """Establish the actual connection. Default implementation without retry logic.

        Args:
            host (str): The hostname or IP address of the Teradata server.
            user (str): The username for authentication.
            password (str): The password for authentication.
            database (str, optional): The default database to use after connection.

        Raises:
            ConnectionError: If connection cannot be established

        """
        try:
            LOGGER.debug("Connecting to Teradata database: %s", database or "DBC")

            # Create connection using teradatasql
            self.connection = self.teradatasql.connect(
                host=host,
                user=user,
                password=password,
                database=database or "DBC",
                logmech="TD2",  # Default authentication mechanism
            )

        except Exception as e:
            LOGGER.error("Failed to connect to Teradata: %s", str(e))
            LOGGER.error("Detailed error type: %s", type(e).__name__)
            self.connection = None
            raise ConnectionError(f"Failed to connect to Teradata: {e}") from e

    @log
    def _verify_connection(self):
        """Verify the connection by executing a simple test query.

        Raises:
            ConnectionError: If connection verification fails

        """
        try:
            LOGGER.debug("Verifying Teradata connection")
            if self.connection is not None:
                # Execute a simple query to verify connection
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 as test_col")
                result = cursor.fetchone()
                cursor.close()
                if result is not None:
                    LOGGER.debug("Teradata connection verified successfully")
                else:
                    raise ConnectionError("Connection verification failed")
            else:
                raise ConnectionError("Connection is None")
        except Exception as e:
            LOGGER.error("Failed to verify Teradata connection: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to verify Teradata connection: {e}") from e

    @log
    def execute_query(self, query: str):
        """Execute a given SQL query and return the column names and fetched results.

        Args:
            query (str): The SQL query to be executed.

        Returns:
            tuple: A tuple containing a list of column names and a list of fetched rows.

        Raises:
            Exception: If the database connection is not established.

        """
        if self.connection is None:
            error_msg = (
                "Database connection is not established. Please call connect() first."
            )
            LOGGER.error(error_msg)
            raise Exception(error_msg)

        try:
            LOGGER.debug(
                "Executing Teradata query: %s",
                query[:100] + "..." if len(query) > 100 else query,
            )

            cursor = self.connection.cursor()
            cursor.execute(query)

            # Get column names from cursor description
            column_names = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch all results
            results = cursor.fetchall()

            cursor.close()

            LOGGER.debug("Query executed successfully, returned %d rows", len(results))
            return column_names, results

        except Exception as e:
            LOGGER.error("Failed to execute Teradata query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def execute_query_no_return(self, query: str) -> None:
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Teradata query: %s", query)
            cursor = self.connection.cursor()

            self.connection.autocommit = False
            cursor.execute(query)

            # Commit once at the end
            self.connection.commit()
            cursor.close()
            LOGGER.debug("Query executed successfully")
        except Exception as e:
            LOGGER.error("Failed to execute query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def execute_statement(self, statement: str) -> None:
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Teradata statement: %s", statement)
            cursor = self.connection.cursor()
            cursor.execute(statement)
            self.connection.commit()
            cursor.close()
            LOGGER.debug("Statement executed successfully")
        except Exception as e:
            LOGGER.error("Failed to execute statement: %s", str(e))
            raise Exception(
                FAILED_TO_EXECUTE_STATEMENT.format(statement=statement)
            ) from e

    @log
    def close(self):
        """Close the connection to the Teradata database if it is open."""
        if self.connection:
            try:
                LOGGER.info("Closing Teradata connection")
                self.connection.close()
                LOGGER.info("Teradata connection closed successfully")
                self.connection = None
            except Exception as e:
                LOGGER.warning("Error while closing Teradata connection: %s", str(e))
        else:
            LOGGER.debug("No active Teradata connection to close")
