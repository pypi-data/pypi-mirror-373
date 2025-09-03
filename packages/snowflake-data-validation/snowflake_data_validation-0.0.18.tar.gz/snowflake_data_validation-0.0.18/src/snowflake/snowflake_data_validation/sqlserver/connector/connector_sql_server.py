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

from typing import Optional

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALUES_CONCATENATED_ERROR_SQL_SERVER,
    CONNECTION_NOT_ESTABLISHED,
    EXCEED_MAX_STRING_LENGHT_SQL_SERVER_ERROR_CODE,
    FAILED_TO_EXECUTE_QUERY,
    FAILED_TO_EXECUTE_STATEMENT,
)
from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.telemetry import (
    report_telemetry,
)


LOGGER = logging.getLogger(__name__)


@Helper.import_dependencies("sqlserver")
def import_mssql():
    """Import the pyodbc module for SQL Server connection."""
    import pyodbc

    return pyodbc


SQLSERVER_CONNECTION_STRING = (
    "DRIVER={{ODBC Driver 18 for SQL Server}};"
    "SERVER={server},{port};"
    "DATABASE={database};"
    "UID={user};"
    "PWD={password};"
    "TrustServerCertificate={trust_server_certificate};"
    "Encrypt={encrypt}"
)


class ConnectorSqlServer(BaseConnector):

    """Connector for SQL Server database."""

    def __init__(self) -> None:
        """Initialize the SQL Server connector."""
        super().__init__()
        self.connection: Optional[object] = None
        self.pyodbc = import_mssql()

    @log(log_args=False)
    @report_telemetry(params_list=["host", "port", "database", "user"])
    def connect(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        trust_server_certificate: str = "no",
        encrypt: str = "yes",
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        delay_multiplier: float = 2.0,
    ):
        """Establish a connection to a SQL Server database using the provided connection details.

        Args:
            host (str): The hostname or IP address of the SQL Server.
            port (int): The port number on which the SQL Server is listening.
            database (str): The name of the database to connect to.
            user (str): The username for authentication.
            password (str): The password for authentication.
            trust_server_certificate (str): Whether to trust the server certificate. Defaults to "no".
            encrypt (str): Whether to encrypt the connection. Defaults to "yes".
            max_attempts (int): Maximum number of connection attempts. Defaults to 3.
            delay_seconds (float): Initial delay between retries in seconds. Defaults to 1.0.
            delay_multiplier (float): Multiplier for exponential backoff. Defaults to 2.0.

        Raises:
            ValueError: If any connection parameters are invalid
            ConnectionError: If connection cannot be established

        """
        LOGGER.info("Attempting to connect to SQL Server at %s:%d", host, port)

        if not all([host, port, database, user, password]):
            error_msg = "All connection parameters (host, port, database, user, password) are required"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)

        self.connect_with_retry(
            self._attempt_connection_and_verify,
            max_attempts,
            delay_seconds,
            delay_multiplier,
            self._internal_connect,
            host,
            port,
            database,
            user,
            password,
            trust_server_certificate,
            encrypt,
        )

    def _internal_connect(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        trust_server_certificate: str = "no",
        encrypt: str = "yes",
    ):
        """Establish the actual connection. Default implementation without retry logic.

        Args:
            host (str): The hostname or IP address of the SQL Server.
            port (int): The port number on which the SQL Server is listening.
            database (str): The name of the database to connect to.
            user (str): The username for authentication.
            password (str): The password for authentication.
            trust_server_certificate (str): Whether to trust the server certificate. Defaults to "no".
            encrypt (str): Whether to encrypt the connection. Defaults to "yes".

        Raises:
            ConnectionError: If connection cannot be established

        """
        try:
            # Build connection string
            self.string_connection = SQLSERVER_CONNECTION_STRING.format(
                server=host,
                port=port,
                database=database,
                user=user,
                password=password,
                trust_server_certificate=trust_server_certificate,
                encrypt=encrypt,
            )

            LOGGER.debug("Connecting to SQL Server database: %s", database)
            self.connection = self.pyodbc.connect(self.string_connection)

        except Exception as e:
            LOGGER.error("Failed to connect to SQL Server: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to connect to SQL Server: {e}") from e

    @log
    def _verify_connection(self):
        """Verify the connection by executing a simple test query.

        Raises:
            ConnectionError: If connection verification fails

        """
        try:
            LOGGER.debug("Verifying SQL Server connection")
            if self.connection is None:
                raise ConnectionError("Connection is None")
            cursor_method = getattr(self.connection, "cursor", None)
            if cursor_method is None:
                raise ConnectionError("Connection does not have cursor method")
            with cursor_method() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            LOGGER.debug("SQL Server connection verified successfully")
        except Exception as e:
            LOGGER.error("Failed to verify SQL Server connection: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to verify SQL Server connection: {e}") from e

    @log
    def execute_statement(self, statement: str) -> None:
        if self.connection is None:
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing SQL Server statement: %s", statement)
            with self.connection.cursor() as cursor:
                cursor.execute(statement)
                self.connection.commit()
            LOGGER.debug("Statement executed successfully")
        except self.pyodbc.Error as e:
            raise Exception(
                FAILED_TO_EXECUTE_STATEMENT.format(statement=statement)
            ) from e

    @log
    def execute_query_no_return(self, query: str) -> None:
        if self.connection is None:
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing SQL Server query: %s", query)
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            LOGGER.debug("Query executed successfully, returned 0 rows")
        except self.pyodbc.Error as e:
            error_message = str(e)

            is_concatenation_error = (
                EXCEED_MAX_STRING_LENGHT_SQL_SERVER_ERROR_CODE in error_message
            )
            if is_concatenation_error:
                error_message = COLUMN_VALUES_CONCATENATED_ERROR_SQL_SERVER
                LOGGER.error(error_message)
                raise Exception(error_message) from e

            LOGGER.error(FAILED_TO_EXECUTE_QUERY)
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

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
                "Executing SQL Server query: %s",
                query[:100] + "..." if len(query) > 100 else query,
            )
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                column_names = [desc[0] for desc in cursor.description]
                results = cursor.fetchall()
                LOGGER.debug(
                    "Query executed successfully, returned %d rows", len(results)
                )
                return column_names, results
        except self.pyodbc.Error as e:
            LOGGER.error("Failed to execute SQL Server query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def close(self):
        """Close the connection to the SQL Server database if it is open."""
        if self.connection:
            try:
                LOGGER.info("Closing SQL Server connection")
                self.connection.close()
                LOGGER.info("SQL Server connection closed successfully")
            except Exception as e:
                LOGGER.warning("Error while closing SQL Server connection: %s", str(e))
        else:
            LOGGER.debug("No active SQL Server connection to close")
