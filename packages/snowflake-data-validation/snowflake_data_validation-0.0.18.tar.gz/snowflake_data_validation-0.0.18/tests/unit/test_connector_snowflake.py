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

"""Tests for ConnectorSnowflake."""

import pytest
from unittest.mock import Mock, patch
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CONNECTION_NOT_ESTABLISHED,
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    FAILED_TO_EXECUTE_QUERY,
    INVALID_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
)


class TestConnectorSnowflake:
    """Test cases for ConnectorSnowflake."""

    def setup_method(self):
        """Set up test fixtures."""
        self.connector = ConnectorSnowflake()

    def test_init(self):
        """Test ConnectorSnowflake initialization."""
        assert self.connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Session"
    )
    def test_connect_default_mode_success(self, mock_session):
        """Test successful connection in default mode."""
        mock_session_instance = Mock()
        mock_session.builder.getOrCreate.return_value = mock_session_instance

        self.connector.connect(mode=DEFAULT_CONNECTION_MODE)

        mock_session.builder.getOrCreate.assert_called_once()
        mock_session_instance.sql.assert_called_once_with("SELECT 1")
        mock_session_instance.sql.return_value.collect.assert_called_once()
        assert self.connector.connection == mock_session_instance

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Session"
    )
    def test_connect_name_mode_success(self, mock_session):
        """Test successful connection in name mode."""
        mock_session_instance = Mock()
        mock_session.builder.config.return_value.create.return_value = (
            mock_session_instance
        )

        self.connector.connect(mode=NAME_CONNECTION_MODE, connection_name="test_conn")

        mock_session.builder.config.assert_called_once_with(
            "connection_name", "test_conn"
        )
        mock_session.builder.config.return_value.create.assert_called_once()
        mock_session_instance.sql.assert_called_once_with("SELECT 1")
        assert self.connector.connection == mock_session_instance

    def test_connect_name_mode_missing_connection_name(self):
        """Test connection in name mode with missing connection name."""
        with pytest.raises(ConnectionError) as exc_info:
            self.connector.connect(mode=NAME_CONNECTION_MODE)

        assert "Connection name is required for 'name' mode" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Session"
    )
    def test_connect_credentials_mode_success(self, mock_session):
        """Test successful connection in credentials mode."""
        mock_session_instance = Mock()
        mock_session.builder.configs.return_value.create.return_value = (
            mock_session_instance
        )

        self.connector.connect(
            mode=CREDENTIALS_CONNECTION_MODE,
            account="test_account",
            username="test_user",
            database="test_db",
            warehouse="test_wh",
            schema="test_schema",
            role="test_role",
            password="test_pass",
            authenticator="snowflake",
        )

        expected_config = {
            "account": "test_account",
            "user": "test_user",
            "database": "test_db",
            "warehouse": "test_wh",
            "schema": "test_schema",
            "role": "test_role",
            "password": "test_pass",
            "authenticator": "snowflake",
        }

        mock_session.builder.configs.assert_called_once_with(expected_config)
        mock_session.builder.configs.return_value.create.assert_called_once()
        mock_session_instance.sql.assert_called_once_with("SELECT 1")
        assert self.connector.connection == mock_session_instance

    def test_connect_credentials_mode_missing_required_params(self):
        """Test connection in credentials mode with missing required parameters."""
        with pytest.raises(ConnectionError) as exc_info:
            self.connector.connect(
                mode=CREDENTIALS_CONNECTION_MODE,
                account="test_account",
                username="test_user",
                # Missing database and warehouse
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert (
            "Account, username, database, and warehouse are required for 'credentials' mode"
            in str(exc_info.value)
        )

    def test_connect_invalid_mode(self):
        """Test connection with invalid mode."""
        with pytest.raises(ConnectionError) as exc_info:
            self.connector.connect(
                mode="invalid_mode",
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert INVALID_CONNECTION_MODE in str(exc_info.value)
        assert "invalid_mode" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Session"
    )
    def test_connect_connection_verification_fails(self, mock_session):
        """Test connection when verification query fails."""
        mock_session_instance = Mock()
        mock_session.builder.getOrCreate.return_value = mock_session_instance
        mock_session_instance.sql.return_value.collect.side_effect = Exception(
            "Connection test failed"
        )

        with pytest.raises(ConnectionError) as exc_info:
            # Use fast retry parameters for testing
            self.connector.connect(
                mode=DEFAULT_CONNECTION_MODE,
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Failed to verify Snowflake connection" in str(exc_info.value)
        assert self.connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Session"
    )
    def test_connect_import_error(self, mock_session):
        """Test connection when Snowflake dependencies are missing."""
        mock_session.builder.getOrCreate.side_effect = ImportError(
            "No module named 'snowflake'"
        )

        with pytest.raises(ConnectionError) as exc_info:
            # Use fast retry parameters for testing
            self.connector.connect(
                mode=DEFAULT_CONNECTION_MODE,
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "No module named 'snowflake'" in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake.Session"
    )
    def test_connect_generic_exception(self, mock_session):
        """Test connection when generic exception occurs."""
        mock_session.builder.getOrCreate.side_effect = Exception("Generic error")

        with pytest.raises(ConnectionError) as exc_info:
            # Use fast retry parameters for testing
            self.connector.connect(
                mode=DEFAULT_CONNECTION_MODE,
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Generic error" in str(exc_info.value)

    def test_execute_query_success(self):
        """Test successful query execution."""
        mock_connection = Mock()
        mock_results = [("result1",), ("result2",)]
        mock_connection.sql.return_value.collect.return_value = mock_results

        self.connector.connection = mock_connection

        result = self.connector.execute_query("SELECT * FROM test_table")

        mock_connection.sql.assert_called_once_with("SELECT * FROM test_table")
        mock_connection.sql.return_value.collect.assert_called_once()
        assert result == mock_results

    def test_execute_query_no_connection(self):
        """Test query execution without established connection."""
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("SELECT 1")

        assert CONNECTION_NOT_ESTABLISHED in str(exc_info.value)

    def test_execute_query_execution_fails(self):
        """Test query execution when query fails."""
        mock_connection = Mock()
        mock_connection.sql.return_value.collect.side_effect = Exception("Query failed")

        self.connector.connection = mock_connection

        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("SELECT * FROM test_table")

        assert FAILED_TO_EXECUTE_QUERY in str(exc_info.value)

    def test_close_with_connection(self):
        """Test closing connection when connection exists."""
        mock_connection = Mock()
        self.connector.connection = mock_connection

        self.connector.close()

        mock_connection.close.assert_called_once()

    def test_close_without_connection(self):
        """Test closing connection when no connection exists."""
        self.connector.connection = None

        # Should not raise any exception
        self.connector.close()

    def test_execute_query_no_return(self):
        mock_connection = Mock()

        self.connector.connection = mock_connection

        self.connector.execute_query_no_return("CREATE TABLE test_table (id INT)")

        mock_connection.sql.assert_called_once_with("CREATE TABLE test_table (id INT)")

    def test_execute_query_no_return_exception(self):
        mock_connection = Mock()

        self.connector.connection = mock_connection

        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("CREATE TABLE test_table (id INT)")

        assert FAILED_TO_EXECUTE_QUERY in str(exc_info.value)

    def test_execute_query_no_return_no_connection(self):
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("CREATE TABLE test_table (id INT)")

        assert CONNECTION_NOT_ESTABLISHED in str(exc_info.value)
