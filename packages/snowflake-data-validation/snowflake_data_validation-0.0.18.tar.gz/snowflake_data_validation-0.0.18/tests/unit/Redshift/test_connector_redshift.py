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
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from snowflake.snowflake_data_validation.redshift.connector.connector_redshift import (
    ConnectorRedshift,
)

# Create a mock Error class for testing
class MockError(Exception):
    pass


@pytest.fixture(autouse=True)
def patch_import_redshift(monkeypatch):
    mock_connector = MagicMock()
    mock_connector.Error = MockError
    monkeypatch.setattr(
        "snowflake.snowflake_data_validation.redshift.connector.connector_redshift.import_redshift",
        lambda: mock_connector,
    )

    yield mock_connector


@pytest.fixture
def connector(patch_import_redshift):
    return ConnectorRedshift()


def test_connect_success(connector, patch_import_redshift, caplog):
    mock_connection = MagicMock(
        host="host", database="db", user="user", password="pass"
    )
    caplog.set_level(logging.INFO)
    patch_import_redshift.connect.return_value = mock_connection

    connector._verify_connection = MagicMock()
    connector.connect("host", "db", "user", "pass")

    patch_import_redshift.connect.assert_called_once()
    assert connector.connection == mock_connection
    assert "Connection established successfully" in caplog.text


def test_connect_failure(connector, patch_import_redshift):
    patch_import_redshift.connect.side_effect = MockError("fail")
    with pytest.raises(ConnectionError):
        # Use fast retry parameters for testing
        connector.connect(
            "host",
            "db",
            "user",
            "pass",
            max_attempts=1,
            delay_seconds=0.01,
            delay_multiplier=1.0,
        )


def test_execute_query_success(connector):
    connector.connection = MagicMock()
    mock_cursor = MagicMock()
    connector.connection.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(1,)]
    type(mock_cursor).description = PropertyMock(return_value=[("col1",)])

    columns, results = connector.execute_query("SELECT 1")

    assert columns == ["col1"]
    assert results == [(1,)]


def test_execute_query_no_connection(connector):
    connector.connection = None
    with pytest.raises(Exception):
        connector.execute_query("SELECT 1")


def test_execute_query_no_return_success(connector, caplog):
    connector.connection = MagicMock()
    caplog.set_level(logging.DEBUG)
    mock_cursor = MagicMock()
    mock_cursor.execute = MagicMock()
    connector.connection.cursor = MagicMock()
    connector.connection.cursor.return_value.__enter__.return_value = mock_cursor

    connector.execute_query_no_return("UPDATE table SET col=1")

    mock_cursor.execute.assert_called_once_with("UPDATE table SET col=1")
    assert "Query executed successfully, returned 0 rows" in caplog.text


def test_execute_query_no_return_no_connection(connector):
    connector.connection = None
    with pytest.raises(Exception):
        connector.execute_query_no_return("INSERT INTO ...")


def test_execute_statement_success(connector):
    connector.connection = MagicMock()
    mock_cursor = MagicMock()
    connector.connection.cursor.return_value.__enter__.return_value = mock_cursor
    connector.execute_statement("CREATE TABLE ...")
    mock_cursor.execute.assert_called_once()
    connector.connection.commit.assert_called_once()


def test_execute_statement_no_connection(connector):
    connector.connection = None
    with pytest.raises(Exception):
        connector.execute_statement("CREATE TABLE ...")


def test_close_success(connector):
    connector.connection = MagicMock()
    connector.close()
    connector.connection.close.assert_called_once()


def test_close_no_connection(connector):
    connector.connection = None
    connector.close()


def test_verify_connection_failure(connector):
    connector.connection = MagicMock()
    mock_cursor = MagicMock()
    connector.connection.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    with pytest.raises(ConnectionError):
        connector._verify_connection()


def test_verify_connection_none(connector):
    connector.connection = None
    with pytest.raises(ConnectionError):
        connector._verify_connection()
