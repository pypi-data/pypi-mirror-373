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

"""Tests for ConnectorTeradata."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from snowflake.snowflake_data_validation.teradata.connector.connector_teradata import (
    ConnectorTeradata,
)
from snowflake.snowflake_data_validation.utils.constants import (
    FAILED_TO_EXECUTE_QUERY,
    CONNECTION_NOT_ESTABLISHED,
    FAILED_TO_EXECUTE_STATEMENT,
)


class TestConnectorTeradata:

    """Test cases for ConnectorTeradata."""

    def setup_method(self):
        """Set up test fixtures."""
        self.connector = ConnectorTeradata()

    def test_init(self):
        """Test ConnectorTeradata initialization."""
        assert self.connector.connection is None
        assert hasattr(self.connector, "teradatasql")

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_success(self, mock_import_teradata):
        """Test successful connection to Teradata."""
        # Mock teradatasql module
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        # Mock successful connection
        mock_connection = Mock()
        mock_teradatasql.connect.return_value = mock_connection

        # Mock successful verification query
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        # Initialize connector with mocked teradatasql
        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql

        # Test connection
        connector.connect(
            host="test_host",
            user="test_user",
            password="test_password",
            database="test_db",
        )

        # Verify connection was created with correct parameters
        mock_teradatasql.connect.assert_called_once_with(
            host="test_host",
            user="test_user",
            password="test_password",
            database="test_db",
            logmech="TD2",
        )

        # Verify connection verification query was executed
        mock_cursor.execute.assert_called_once_with("SELECT 1 as test_col")
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()

        assert connector.connection == mock_connection

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_missing_required_params(self, mock_import_teradata):
        """Test connection with missing required parameters."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql

        with pytest.raises(ValueError) as exc_info:
            connector.connect(host="test_host", user="", password="test_password")

        assert "Host, user, and password are required connection parameters" in str(
            exc_info.value
        )

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_default_database(self, mock_import_teradata):
        """Test connection with default database (DBC)."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        mock_connection = Mock()
        mock_teradatasql.connect.return_value = mock_connection

        # Mock successful verification query
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql

        connector.connect(
            host="test_host",
            user="test_user",
            password="test_password"
            # No database specified - should default to "DBC"
        )

        mock_teradatasql.connect.assert_called_once_with(
            host="test_host",
            user="test_user",
            password="test_password",
            database="DBC",  # Default database
            logmech="TD2",
        )

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_connection_fails(self, mock_import_teradata):
        """Test connection when Teradata connection fails."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql
        mock_teradatasql.connect.side_effect = Exception("Connection failed")

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql

        with pytest.raises(ConnectionError) as exc_info:
            connector.connect(
                host="test_host",
                user="test_user",
                password="test_password",
                database="test_db",
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Failed to connect to Teradata: Connection failed" in str(exc_info.value)
        assert connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_connect_verification_fails(self, mock_import_teradata):
        """Test connection when verification query fails."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        mock_connection = Mock()
        mock_teradatasql.connect.return_value = mock_connection
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = Exception("Verification failed")

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql

        with pytest.raises(ConnectionError) as exc_info:
            connector.connect(
                host="test_host",
                user="test_user",
                password="test_password",
                database="test_db",
                max_attempts=1,
                delay_seconds=0.01,
                delay_multiplier=1.0,
            )

        assert "Failed to verify Teradata connection" in str(exc_info.value)
        assert connector.connection is None

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_success(self, mock_import_teradata):
        """Test successful query execution."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        # Mock successful connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        # Mock cursor description and results
        mock_cursor.description = [("col1", None, None, None, None, None, None), ("col2", None, None, None, None, None, None)]
        mock_cursor.fetchall.return_value = [(1, "a"), (2, "b"), (3, "c")]

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = mock_connection

        column_names, results = connector.execute_query("SELECT * FROM test_table")

        # Verify query was executed
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()

        # Verify results format
        expected_columns = ["col1", "col2"]
        expected_results = [(1, "a"), (2, "b"), (3, "c")]

        assert column_names == expected_columns
        assert results == expected_results

    def test_execute_query_no_connection(self):
        """Test query execution without established connection."""
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query("SELECT 1")

        assert (
            "Database connection is not established. Please call connect() first."
            in str(exc_info.value)
        )

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_fails(self, mock_import_teradata):
        """Test query execution when query fails."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql
        mock_cursor = Mock()
        mock_teradatasql.connect.return_value = Mock() # Mock connection
        mock_cursor.execute.side_effect = Exception("Query execution failed")

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = Mock()  # Simulate established connection

        with pytest.raises(Exception) as exc_info:
            connector.execute_query("SELECT * FROM test_table")

        assert FAILED_TO_EXECUTE_QUERY in str(exc_info.value)

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_close_with_connection(self, mock_import_teradata):
        """Test closing connection when connection exists."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        mock_connection = Mock()

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = mock_connection

        connector.close()

        mock_connection.close.assert_called_once()

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_close_with_exception(self, mock_import_teradata):
        """Test closing connection when exception occurs during close."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql
        mock_connection = Mock()
        mock_connection.close.side_effect = Exception("Close failed")

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = mock_connection  # Simulate established connection

        # Should not raise exception, only log warning
        connector.close()

        mock_connection.close.assert_called_once()

    def test_close_without_connection(self):
        """Test closing connection when no connection exists."""
        # Should not raise exception, only log debug message
        self.connector.close()

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_import_teradata_dependency(self, mock_import_teradata):
        """Test import of teradataml dependency."""
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        connector = ConnectorTeradata()

        # Verify import_teradata was called during initialization
        mock_import_teradata.assert_called_once()
        assert connector.teradatasql == mock_teradatasql

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_without_return_success(self, mock_import_teradata):
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql

        # Mock successful query execution
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = mock_connection

        connector.execute_query_no_return("CREATE TABLE TEST_TABLE (INDEX_ INTEGER)")

        # Verify query was executed
        mock_cursor.execute.assert_called_once_with(
            "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_query_without_return_no_connection_exception(self):
        with pytest.raises(Exception) as exc_info:
            self.connector.execute_query_no_return(
                "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
            )

        assert str(exc_info.value) == CONNECTION_NOT_ESTABLISHED

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_query_without_return_fails(self, mock_import_teradata):
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql
        
        # Set up mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query execution failed")

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = mock_connection

        with pytest.raises(Exception) as exc_info:
            connector.execute_query_no_return(
                "CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
            )

        assert str(exc_info.value) == FAILED_TO_EXECUTE_QUERY

    @patch(
        "snowflake.snowflake_data_validation.teradata.connector.connector_teradata.import_teradata"
    )
    def test_execute_statement_fails(self, mock_import_teradata):
        mock_teradatasql = Mock()
        mock_import_teradata.return_value = mock_teradatasql
        
        # Set up mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query execution failed")

        connector = ConnectorTeradata()
        connector.teradatasql = mock_teradatasql
        connector.connection = mock_connection

        with pytest.raises(Exception) as exc_info:
            connector.execute_statement("CREATE TABLE TEST_TABLE (INDEX_ INTEGER)")

        assert str(exc_info.value) == FAILED_TO_EXECUTE_STATEMENT.format(
            statement="CREATE TABLE TEST_TABLE (INDEX_ INTEGER)"
        )
