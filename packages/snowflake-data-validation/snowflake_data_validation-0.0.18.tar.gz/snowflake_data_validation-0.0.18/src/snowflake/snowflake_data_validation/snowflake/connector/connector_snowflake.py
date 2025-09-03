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

import typer

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase as BaseConnector,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALUES_CONCATENATED_ERROR_SNOWFLAKE,
    CONNECTION_NOT_ESTABLISHED,
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    EXCEED_MAX_STRING_LENGHT_SNOWFLAKE_ERROR_CODE,
    FAILED_TO_EXECUTE_QUERY,
    FAILED_TO_EXECUTE_STATEMENT,
    INVALID_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
)
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowpark import Session


LOGGER = logging.getLogger(__name__)


class ConnectorSnowflake(BaseConnector):

    """A class to manage connections and queries to a Snowflake database."""

    @log
    def __init__(self) -> None:
        """Initialize the SnowflakeConnector class."""
        super().__init__()
        self.connection: Optional[Session] = None

    @log(log_args=False)
    def connect(
        self,
        mode: str = DEFAULT_CONNECTION_MODE,
        connection_name: str = "",
        account: str = "",
        username: str = "",
        database: str = "",
        schema: str = "",
        warehouse: str = "",
        role: str = "",
        password: str = "",
        authenticator: str = "",
        private_key_file: Optional[str] = None,
        private_key_passphrase: Optional[str] = None,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        delay_multiplier: float = 2.0,
    ) -> None:
        """Establish a connection to the Snowflake database.

        Args:
            mode (str): The mode of connection. Defaults to "default".
                        - "default": Connects using the default session configuration.
                        - "name": Connects using a named connection configuration.
                        - "credentials": Connects using the provided credentials.
            connection_name (str): The name of the connection configuration to use
                when mode is "name". Defaults to an empty string.
            account (str): The Snowflake account name.
            username (str): The username for the Snowflake account.
            database (str): The name of the database to connect to.
            schema (str): The schema within the database to use.
            warehouse (str): The name of the warehouse to use.
            role (str): The role to assume for the session.
            password (str): The password for the Snowflake account.
            authenticator (str): The authenticator to use for the Snowflake connection.
            private_key_file (Optional[str]): The path to the private key file for authentication.
            private_key_passphrase (Optional[str]): The passphrase for the private key file, if required.
            max_attempts (int): Maximum number of connection attempts. Defaults to 3.
            delay_seconds (float): Initial delay between retries in seconds. Defaults to 1.0.
            delay_multiplier (float): Multiplier for exponential backoff. Defaults to 2.0.

        Returns:
            None: Returns a Snowflake session object.

        Raises:
            ConnectionError: If the connection cannot be established.
            typer.BadParameter: If invalid parameters are provided.
            ImportError: If Snowflake connector dependencies are missing.

        """
        try:
            self.connect_with_retry(
                self._attempt_connection_and_verify,
                max_attempts,
                delay_seconds,
                delay_multiplier,
                self._internal_connect,
                mode,
                connection_name,
                account,
                username,
                database,
                schema,
                warehouse,
                role,
                password,
                authenticator,
                private_key_file,
                private_key_passphrase,
            )

        except ImportError as e:
            LOGGER.error("Failed to import Snowflake dependencies: %s", str(e))
            raise ImportError(
                f"Failed to import Snowflake dependencies: {e}. "
                "Please ensure snowflake-snowpark-python is installed."
            ) from e
        except typer.BadParameter:
            raise
        except ConnectionError:
            raise
        except Exception as e:
            LOGGER.error("Failed to establish Snowflake connection: %s", str(e))
            raise ConnectionError(
                f"Failed to establish Snowflake connection: {e}"
            ) from e

    def _internal_connect(
        self,
        mode: str = DEFAULT_CONNECTION_MODE,
        connection_name: str = "",
        account: str = "",
        username: str = "",
        database: str = "",
        schema: str = "",
        warehouse: str = "",
        role: str = "",
        password: str = "",
        authenticator: str = "",
        private_key_file: Optional[str] = None,
        private_key_passphrase: Optional[str] = None,
    ) -> None:
        """Establish the actual connection. Default implementation without retry logic.

        Args:
            mode (str): The mode of connection. Defaults to "default".
            connection_name (str): The name of the connection configuration to use
                when mode is "name". Defaults to an empty string.
            account (str): The Snowflake account name.
            username (str): The username for the Snowflake account.
            database (str): The name of the database to connect to.
            schema (str): The schema within the database to use.
            warehouse (str): The name of the warehouse to use.
            role (str): The role to assume for the session.
            password (str): The password for the Snowflake account.
            authenticator (str): The authenticator to use for the Snowflake connection.
            private_key_file (Optional[str]): The path to the private key file for authentication.
            private_key_passphrase (Optional[str]): The passphrase for the private key file, if required.

        Raises:
            ConnectionError: If the connection cannot be established.
            typer.BadParameter: If invalid parameters are provided.

        """
        if mode == DEFAULT_CONNECTION_MODE:
            # Use the current Snowflake session
            self.connection = Session.builder.getOrCreate()

        elif mode == NAME_CONNECTION_MODE:
            if not connection_name:
                raise typer.BadParameter("Connection name is required for 'name' mode")
            # Use named connection
            self.connection = Session.builder.config(
                "connection_name", connection_name
            ).create()

        elif mode == CREDENTIALS_CONNECTION_MODE:
            if not all([account, username, database, warehouse]):
                raise typer.BadParameter(
                    "Account, username, database, and warehouse are required for 'credentials' mode"
                )

            # Build connection configuration
            connection_config = {
                "account": account,
                "user": username,
                "database": database,
                "warehouse": warehouse,
            }

            if schema:
                connection_config["schema"] = schema
            if role:
                connection_config["role"] = role
            if password:
                connection_config["password"] = password
            if authenticator:
                connection_config["authenticator"] = authenticator
            if private_key_file:
                connection_config["private_key_file"] = private_key_file
            if private_key_passphrase:
                connection_config["private_key_passphrase"] = private_key_passphrase

            # Create session with credentials
            self.connection = Session.builder.configs(connection_config).create()

        else:
            raise typer.BadParameter(
                message=f"{INVALID_CONNECTION_MODE}. Selected mode: {mode}. "
                f"Valid modes are 'default', 'name', or 'credentials'."
            )

    def _verify_connection(self) -> None:
        """Verify the connection by executing a simple test query.

        Raises:
            ConnectionError: If connection verification fails

        """
        try:
            LOGGER.debug("Verifying Snowflake connection")
            if self.connection is None:
                raise ConnectionError("Connection is None")
            sql_method = getattr(self.connection, "sql", None)
            if sql_method is None:
                raise ConnectionError("Connection does not have sql method")
            sql_method("SELECT 1").collect()
            LOGGER.debug("Snowflake connection verified successfully")
        except Exception as e:
            LOGGER.error("Failed to verify Snowflake connection: %s", str(e))
            self.connection = None
            raise ConnectionError(f"Failed to verify Snowflake connection: {e}") from e

    @log
    def execute_statement(self, statement: str) -> None:
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Snowflake statement: %s", statement)
            self.connection.sql(statement).collect()
            LOGGER.debug("Statement executed successfully")
            return True
        except Exception as e:
            LOGGER.error("Failed to execute statement: %s", str(e))
            raise Exception(
                FAILED_TO_EXECUTE_STATEMENT.format(statement=statement)
            ) from e

    @log
    def execute_query_no_return(self, query: str) -> None:
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)

        try:
            LOGGER.debug("Executing Snowflake query: %s", query)
            self.connection.sql(query).collect()
            LOGGER.debug("Query executed successfully, returned 0 rows")
        except Exception as e:
            error_message = str(e)

            is_concatenation_error = (
                EXCEED_MAX_STRING_LENGHT_SNOWFLAKE_ERROR_CODE in error_message
            )
            if is_concatenation_error:
                error_message = COLUMN_VALUES_CONCATENATED_ERROR_SNOWFLAKE
                LOGGER.error(error_message)
                raise Exception(error_message) from e

            LOGGER.error("Failed to execute query: %s", error_message)
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def execute_query(self, query: str) -> list[tuple]:
        """Execute a given SQL query using the Snowflake connector and return the results.

        Args:
            query (str): The SQL query to be executed.

        Returns:
            list[tuple]: A list of tuples containing the query results.

        Raises:
            Exception: If the connector is not established or if the query execution fails.

        """
        if self.connection is None:
            LOGGER.error("Database connection not established")
            raise Exception(CONNECTION_NOT_ESTABLISHED)
        try:
            results = self.connection.sql(query).collect()
            LOGGER.debug("Query executed successfully, returned %d rows", len(results))
            return results
        except Exception as e:
            LOGGER.error("Failed to execute query: %s", str(e))
            raise Exception(FAILED_TO_EXECUTE_QUERY) from e

    @log
    def close(self) -> None:
        """Close the connection to the Snowflake database."""
        if self.connection:
            self.connection.close()
            LOGGER.info("Snowflake connection closed successfully")
        else:
            LOGGER.debug("No active connection to close")
