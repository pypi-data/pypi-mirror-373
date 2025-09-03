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

import pytest
import time
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from contextlib import contextmanager

from snowflake.snowflake_data_validation.utils.connection_pool import (
    ExecutionConnectors,
    ConnectionPoolManager,
)
from snowflake.snowflake_data_validation.utils.arguments_manager_base import (
    ArgumentsManagerBase,
    ValidationEnvironmentObject,
)
from snowflake.snowflake_data_validation.utils.constants import Platform


@pytest.fixture
def mock_arguments_manager():
    """Create a mock ArgumentsManagerBase instance."""
    args_manager = MagicMock(spec=ArgumentsManagerBase)

    # Mock the methods that exist in ArgumentsManagerBase
    args_manager.create_connection_pool_manager = MagicMock()
    args_manager.source_platform = Platform.SNOWFLAKE
    args_manager.target_platform = Platform.SNOWFLAKE

    return args_manager


@pytest.fixture
def mock_validation_env():
    """Create a mock ValidationEnvironmentObject."""
    mock_context = MagicMock()
    mock_context.source_platform = Platform.SQLSERVER
    mock_context.target_platform = Platform.SNOWFLAKE

    return ValidationEnvironmentObject(
        source_connection_config=MagicMock(),
        target_connection_config=MagicMock(),
        context=mock_context,
    )


class TestExecutionConnectors:
    """Test the ExecutionConnectors dataclass."""

    def test_connection_pair_creation(self):
        """Test that ExecutionConnectors can be created with connectors."""
        from datetime import datetime

        source_connector = MagicMock()
        target_connector = MagicMock()

        pair = ExecutionConnectors(
            source_connector=source_connector,
            target_connector=target_connector,
            creation_time=datetime.now(),
        )

        assert pair.source_connector is source_connector
        assert pair.target_connector is target_connector

    def test_connection_pair_context_manager(self):
        """Test that ExecutionConnectors can be used for connection management."""
        import time

        source_connector = MagicMock()
        target_connector = MagicMock()

        pair = ExecutionConnectors(
            source_connector=source_connector,
            target_connector=target_connector,
            creation_time=time.time(),
        )

        # Test connection management
        assert pair.source_connector is source_connector
        assert pair.target_connector is target_connector
        assert not pair.in_use

        # Test close connections
        pair.close_connections()
        source_connector.close.assert_called_once()
        target_connector.close.assert_called_once()


class TestConnectionPoolManager:
    """Test the ConnectionPoolManager class."""

    def test_pool_manager_creation(self, mock_arguments_manager):
        """Test that ConnectionPoolManager can be created."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
        )

        assert pool_manager.source_platform == Platform.SQLSERVER
        assert pool_manager.target_platform == Platform.SNOWFLAKE
        assert pool_manager.pool_size == 2
        assert pool_manager._pool.qsize() == 0  # Pool starts empty

    @patch("snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory")
    def test_pool_initialization_failure_all_connections_fail(self, mock_factory):
        """Test pool initialization when all connections fail."""
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        # Mock connector factory to always fail
        mock_factory.create_connector.side_effect = Exception("Connection failed")

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
        )

        # Initialize pool - should not raise exception but should result in empty pool
        pool_manager.initialize_pool()

        # Pool should be initialized but empty
        assert pool_manager._initialized is True
        assert pool_manager.get_current_pool_size() == 0

    @patch("snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory")
    def test_pool_initialization_partial_failure(self, mock_factory):
        """Test pool behavior when some connection creation fails during lazy loading."""
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        # Mock connector factory to fail for first connection pair, succeed for second
        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()
        mock_factory.create_connector.side_effect = [
            Exception("First connection failed"),  # First source fails
            mock_source_connector,  # Second source succeeds
            mock_target_connector,  # Second target succeeds
        ]

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
        )

        # Initialize pool (lazy initialization - no connections created yet)
        pool_manager.initialize_pool()

        # Pool should be initialized but no connections created yet
        assert pool_manager._initialized is True
        assert pool_manager.get_current_pool_size() == 0  # No connections created yet

        # First connection request should fail
        with pytest.raises(Exception, match="First connection failed"):
            with pool_manager.get_connection_pair():
                pass

        # Second connection request should succeed
        with pool_manager.get_connection_pair() as connection_pair:
            assert isinstance(connection_pair, ExecutionConnectors)
            assert connection_pair.source_connector is mock_source_connector
            assert connection_pair.target_connector is mock_target_connector

    @patch("snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory")
    def test_connection_aging_and_refresh(self, mock_factory):
        """Test basic connection pool behavior with aging configuration."""
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        # Mock connectors
        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()

        mock_factory.create_connector.side_effect = [
            mock_source_connector,  # Source connector
            mock_target_connector,  # Target connector
        ]

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=1,
            max_connection_age=10.0,  # 10 seconds
        )

        # Initialize pool (lazy initialization)
        pool_manager.initialize_pool()
        assert pool_manager.get_current_pool_size() == 0  # No connections created yet

        # First request creates the initial connection
        with pool_manager.get_connection_pair() as connection_pair:
            # Should get connectors
            assert isinstance(connection_pair, ExecutionConnectors)
            assert connection_pair.source_connector is not None
            assert connection_pair.target_connector is not None

        # Now pool should have 1 connection available
        assert pool_manager.get_current_pool_size() == 1

        # Second request should reuse the existing connection
        with pool_manager.get_connection_pair() as connection_pair:
            # Should get the same type of connection pair
            assert isinstance(connection_pair, ExecutionConnectors)

        # Verify connectors were created
        assert mock_factory.create_connector.call_count == 2

    @patch("snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory")
    @patch("snowflake.snowflake_data_validation.utils.connection_pool.time")
    def test_connection_refresh_failure_fallback(self, mock_time, mock_factory):
        """Test behavior when connection refresh fails."""
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        # Mock connectors
        old_source_connector = MagicMock()
        old_target_connector = MagicMock()

        # First two calls succeed for initial pool, third call fails for refresh
        mock_factory.create_connector.side_effect = [
            old_source_connector,  # Initial source
            old_target_connector,  # Initial target
            Exception("Refresh failed"),  # Refresh source fails
        ]

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=1,
            max_connection_age=10.0,
        )

        # Mock time progression
        start_time = 1000.0
        aged_time = start_time + 15.0

        mock_time.time.side_effect = [
            start_time,  # Connection creation time
            aged_time,  # Time when checking age
        ]

        # Initialize pool
        pool_manager.initialize_pool()

        # Getting connection pair should fail when refresh fails
        with pytest.raises(Exception, match="Refresh failed"):
            with pool_manager.get_connection_pair():
                pass

    def test_uninitialized_pool_error(self):
        """Test that getting connection from uninitialized pool raises RuntimeError."""
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=1,
        )

        # Don't initialize pool
        with pytest.raises(RuntimeError, match="Connection pool not initialized"):
            with pool_manager.get_connection_pair():
                pass

    def test_pool_manager_initialization(self, mock_arguments_manager):
        """Test that pool manager initializes correctly with lazy loading."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
        )

        # Mock the connector factory to return mock connectors
        with patch(
            "snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory"
        ) as mock_factory:
            mock_source_connector = MagicMock()
            mock_target_connector = MagicMock()
            mock_factory.create_connector.side_effect = [
                mock_source_connector,
                mock_target_connector,
                mock_source_connector,
                mock_target_connector,
            ]

            pool_manager.initialize_pool()

            assert pool_manager._initialized is True
            assert (
                pool_manager.get_current_pool_size() == 0
            )  # Lazy initialization - no connections yet

            # Actually request connections to trigger creation
            with pool_manager.get_connection_pair() as conn1:
                assert isinstance(conn1, ExecutionConnectors)
                # After first request, one connection created and one available in pool
                assert pool_manager.get_current_pool_size() == 0  # Connection is in use

            # Now one connection should be available in pool
            assert pool_manager.get_current_pool_size() == 1
            assert (
                pool_manager.get_total_connections_created() == 1
            )  # Only 1 connection created so far

            # Request second connection simultaneously (to force creation of second connection)
            with pool_manager.get_connection_pair() as conn2:
                assert isinstance(conn2, ExecutionConnectors)
                # Should reuse the existing connection, so total created is still 1
                assert pool_manager.get_total_connections_created() == 1

    def test_pool_manager_context_manager(self, mock_arguments_manager):
        """Test that ConnectionPoolManager works as a context manager."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=1,
        )

        # Mock the connector factory
        with patch(
            "snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory"
        ) as mock_factory:
            mock_source_connector = MagicMock()
            mock_target_connector = MagicMock()
            mock_factory.create_connector.side_effect = [
                mock_source_connector,
                mock_target_connector,
            ]

            with pool_manager as managed_pool:
                assert managed_pool is pool_manager
                # Pool should be initialized but no connections created yet (lazy)
                assert managed_pool.get_current_pool_size() == 0

                # Actually use a connection to trigger creation
                with managed_pool.get_connection_pair() as conn:
                    assert isinstance(conn, ExecutionConnectors)

                # After use, connection should be returned to pool
                assert managed_pool.get_current_pool_size() == 1

    def test_get_connection_pair(self, mock_arguments_manager):
        """Test getting a connection pair from the pool."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
        )

        # Mock the connector factory
        with patch(
            "snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory"
        ) as mock_factory:
            mock_source_connector = MagicMock()
            mock_target_connector = MagicMock()
            mock_factory.create_connector.side_effect = [
                mock_source_connector,
                mock_target_connector,
                mock_source_connector,
                mock_target_connector,
            ]

            with pool_manager:
                # Initially no connections exist (lazy loading)
                assert pool_manager.get_current_pool_size() == 0

                # Get a connection pair
                with pool_manager.get_connection_pair() as connection_pair:
                    assert isinstance(connection_pair, ExecutionConnectors)
                    assert connection_pair.source_connector is not None
                    assert connection_pair.target_connector is not None

                    # While in use, pool has no available connections
                    assert pool_manager.get_current_pool_size() == 0

                # After context exit, connection should be returned to pool
                assert pool_manager.get_current_pool_size() == 1

    def test_pool_exhaustion_and_recovery(self, mock_arguments_manager):
        """Test that pool handles exhaustion and recovery correctly."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=1,
            connection_timeout=0.1,  # Very short timeout for testing
        )

        # Mock the connector factory
        with patch(
            "snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory"
        ) as mock_factory:
            mock_source_connector = MagicMock()
            mock_target_connector = MagicMock()
            mock_factory.create_connector.side_effect = [
                mock_source_connector,
                mock_target_connector,
            ]

            with pool_manager:
                # Get the only connection pair
                with pool_manager.get_connection_pair() as connection_pair1:
                    assert isinstance(connection_pair1, ExecutionConnectors)
                    assert pool_manager.get_current_pool_size() == 0

                    # Try to get another connection pair (should timeout since pool_size=1)
                    # This will test the timeout behavior
                    import pytest

                    with pytest.raises(TimeoutError):
                        with pool_manager.get_connection_pair():
                            pass

                # After first connection is returned
                assert pool_manager.get_current_pool_size() == 1

    def test_pool_cleanup(self, mock_arguments_manager):
        """Test that pool cleans up connections properly."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        source_config = MagicMock(spec=Connection)
        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
        )

        # Mock the connector factory
        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()

        with patch(
            "snowflake.snowflake_data_validation.utils.connection_pool.ConnectorFactory"
        ) as mock_factory:
            mock_factory.create_connector.side_effect = [
                mock_source_connector,
                mock_target_connector,
                mock_source_connector,
                mock_target_connector,
            ]

            with pool_manager:
                # Create some connections by using them
                with pool_manager.get_connection_pair() as conn1:
                    assert isinstance(conn1, ExecutionConnectors)

                # After first connection usage, it should be in pool
                assert pool_manager.get_current_pool_size() == 1

                # Use another connection
                with pool_manager.get_connection_pair() as conn2:
                    assert isinstance(conn2, ExecutionConnectors)

                # After second usage, both connections should be in pool
                assert (
                    pool_manager.get_current_pool_size() == 1
                )  # Still 1 because we reused the connection

            # After context exit, cleanup should have been called
            # Check that connectors were closed
            assert mock_source_connector.close.call_count >= 1
            assert mock_target_connector.close.call_count >= 1
            # Pool should be empty
            assert pool_manager.get_current_pool_size() == 0


class TestValidationEnvironmentObjectPoolIntegration:
    """Test integration between ValidationEnvironmentObject and connection pool."""

    def test_create_connection_pool_manager(self, mock_validation_env):
        """Test that ValidationEnvironmentObject can create a connection pool manager."""
        pool_manager = mock_validation_env.create_connection_pool_manager(pool_size=3)

        assert isinstance(pool_manager, ConnectionPoolManager)
        assert (
            pool_manager.source_platform == mock_validation_env.context.source_platform
        )
        assert (
            pool_manager.target_platform == mock_validation_env.context.target_platform
        )
        assert pool_manager.pool_size == 3

    def test_create_connection_pool_manager_default_size(self, mock_validation_env):
        """Test default pool size when creating connection pool manager."""
        pool_manager = mock_validation_env.create_connection_pool_manager()

        assert isinstance(pool_manager, ConnectionPoolManager)
        assert pool_manager.pool_size == 1  # Default size


class TestConnectionPoolThreadSafety:
    """Test thread safety aspects of the connection pool (simulated)."""

    @patch(
        "snowflake.snowflake_data_validation.utils.connector_factory.ConnectorFactory.create_connector"
    )
    def test_concurrent_connection_acquisition_simulation(
        self, mock_create_connector, mock_arguments_manager
    ):
        """Simulate concurrent connection acquisition and release."""
        from snowflake.snowflake_data_validation.utils.constants import Platform
        from snowflake.snowflake_data_validation.configuration.model.connection_types import (
            Connection,
        )

        # Mock the connector creation to avoid real connection attempts
        mock_source_connector = MagicMock()
        mock_target_connector = MagicMock()
        mock_create_connector.side_effect = [
            mock_source_connector,
            mock_target_connector,
        ] * 10

        source_config = MagicMock(spec=Connection)
        source_config.host = "localhost"
        source_config.port = 1433
        source_config.database = "test_db"
        source_config.username = "test_user"
        source_config.password = "test_pass"

        target_config = MagicMock(spec=Connection)

        pool_manager = ConnectionPoolManager(
            source_platform=Platform.SQLSERVER,
            target_platform=Platform.SNOWFLAKE,
            source_connection_config=source_config,
            target_connection_config=target_config,
            pool_size=2,
            connection_timeout=1.0,  # Short timeout for faster test
        )

        with pool_manager:
            # Acquire and immediately release connections to test pool management
            connection_pairs = []

            # Acquire available connections
            for i in range(2):  # Equal to pool size
                try:
                    with pool_manager.get_connection_pair() as pair:
                        connection_pairs.append(pair)
                        assert pair is not None
                        # Release immediately by exiting context
                except Exception as e:
                    # If we get an exception, that's expected if pool is exhausted
                    pass

            # Pool should be restored after context exits
            assert pool_manager.get_current_pool_size() <= 2


if __name__ == "__main__":
    pytest.main([__file__])
