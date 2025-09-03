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
import threading
import time

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from queue import Empty, Queue

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.utils.connector_factory import (
    ConnectorFactory,
)
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_TIMEOUT,
    DEFAULT_MAX_CONNECTION_AGE,
    Platform,
)


LOGGER = logging.getLogger(__name__)


@dataclass
class ExecutionConnectors:

    """Represents a pair of source and target connectors."""

    source_connector: ConnectorBase
    target_connector: ConnectorBase
    creation_time: float
    in_use: bool = False

    def close_connections(self) -> None:
        """Close both source and target connections."""
        try:
            if self.source_connector:
                self.source_connector.close()
        except Exception as e:
            LOGGER.warning("Error closing source connector: %s", e)

        try:
            if self.target_connector:
                self.target_connector.close()
        except Exception as e:
            LOGGER.warning("Error closing target connector: %s", e)


class ConnectionPoolManager:

    """Manages a pool of database connection pairs for threaded validation processing.

    This class creates and manages connection pairs (source + target) that can be used
    by multiple threads during table validation processing. It uses connector factories
    to create platform-specific connectors from connection configurations.
    """

    def __init__(
        self,
        source_platform: Platform,
        target_platform: Platform,
        source_connection_config: Connection,
        target_connection_config: Connection,
        pool_size: int = 4,  # TODO: remove Default
        max_connection_age: float = DEFAULT_MAX_CONNECTION_AGE,
        connection_timeout: float = DEFAULT_CONNECTION_TIMEOUT,
    ):
        """Initialize the connection pool manager.

        Args:
            source_platform: Platform type for source connections (e.g., Platform.SQLSERVER)
            target_platform: Platform type for target connections (e.g., Platform.SNOWFLAKE)
            source_connection_config: Configuration for source database connections
            target_connection_config: Configuration for target database connections
            pool_size: Number of connection pairs to maintain in the pool
            max_connection_age: Maximum age of connections in seconds before refresh
            connection_timeout: Timeout for getting connections from pool

        Raises:
            ValueError: If pool_size <= 0 or max_connection_age <= 0

        """
        self.source_platform = source_platform
        self.target_platform = target_platform
        self.source_connection_config = source_connection_config
        self.target_connection_config = target_connection_config
        self.pool_size = pool_size
        self.max_connection_age = max_connection_age
        self.connection_timeout = connection_timeout

        self._pool: Queue[ExecutionConnectors] = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._initialized = False
        self._current_pool_size = 0  # Track actual number of connections created

    def initialize_pool(self) -> None:
        """Initialize the connection pool for lazy loading.

        This method only sets up the pool structure - connections are created on-demand.
        """
        with self._lock:
            if self._initialized:
                LOGGER.debug("Connection pool already initialized")
                return

            LOGGER.info(
                "Initializing connection pool for on-demand creation (max size: %d)",
                self.pool_size,
            )

            self._initialized = True
            LOGGER.info("Connection pool initialized successfully for lazy loading")

    def _create_connection_pair(self) -> ExecutionConnectors:
        """Create a new connection pair using the arguments manager.

        Returns:
            ExecutionConnectors: A new pair of connected source and target connectors

        Raises:
            Exception: If connection creation fails

        """
        LOGGER.debug("Creating new connection pair")

        try:
            source_connector = self._create_source_connector()
            target_connector = self._create_target_connector()

            connection_pair = ExecutionConnectors(
                source_connector=source_connector,
                target_connector=target_connector,
                creation_time=time.time(),
                in_use=False,
            )

            LOGGER.debug("Successfully created connection pair")
            return connection_pair

        except Exception as e:
            LOGGER.error("Failed to create connection pair: %s", e)
            raise

    def _create_source_connector(self) -> ConnectorBase:
        """Create a source connector using the connector factory.

        Uses the platform-specific connector factory to create the appropriate
        connector type from the connection configuration.
        """
        return ConnectorFactory.create_connector(
            self.source_platform, self.source_connection_config
        )

    def _create_target_connector(self) -> ConnectorBase:
        """Create a target connector using the connector factory.

        Uses the platform-specific connector factory to create the appropriate
        connector type from the connection configuration.
        """
        return ConnectorFactory.create_connector(
            self.target_platform, self.target_connection_config
        )

    @contextmanager
    def get_connection_pair(self) -> Generator[ExecutionConnectors, None, None]:
        """Get a connection pair from the pool as a context manager.

        Creates connections on-demand if pool is empty and under max capacity.

        Yields:
            ExecutionConnectors: A pair of source and target connectors

        Raises:
            TimeoutError: If no connection is available within the timeout
            RuntimeError: If pool is not initialized

        """
        if not self._initialized:
            raise RuntimeError(
                "Connection pool not initialized. Call initialize_pool() first."
            )

        connection_pair = None

        try:
            # Check if pool is empty first to avoid unnecessary timeout delay
            if self._pool.empty():
                LOGGER.debug("Pool is empty, creating new connection on-demand")
                connection_pair = self._get_or_create_connection_pair()
            else:
                # Try to get a connection pair from the pool with timeout
                try:
                    connection_pair = self._pool.get(timeout=self.connection_timeout)
                    LOGGER.debug("Retrieved existing connection pair from pool")
                except Empty:
                    # Pool became empty during the wait, create a new connection
                    LOGGER.debug(
                        "Pool became empty during wait, creating new connection on-demand"
                    )
                    connection_pair = self._get_or_create_connection_pair()

            # Check if connection pair is too old and needs refresh
            if time.time() - connection_pair.creation_time > self.max_connection_age:
                LOGGER.debug("Connection pair is too old, creating fresh pair")
                connection_pair.close_connections()
                connection_pair = self._create_connection_pair()

            # Mark as in use
            connection_pair.in_use = True

            yield connection_pair

        finally:
            # Always return the connection pair to the pool
            if connection_pair:
                connection_pair.in_use = False
                try:
                    self._pool.put_nowait(connection_pair)
                    LOGGER.debug("Returned connection pair to pool")
                except Exception as e:
                    LOGGER.warning("Failed to return connection pair to pool: %s", e)
                    # If we can't return it, close the connections
                    connection_pair.close_connections()
                    with self._lock:
                        self._current_pool_size -= 1

    def _get_or_create_connection_pair(self) -> ExecutionConnectors:
        """Get a connection pair from the pool or create one on-demand.

        Returns:
            ExecutionConnectors: A connection pair

        Raises:
            TimeoutError: If pool is at max capacity and no connections become available

        """
        with self._lock:
            # Check if we can create a new connection (haven't reached max pool size)
            if self._current_pool_size < self.pool_size:
                try:
                    LOGGER.debug(
                        "Creating new connection pair on-demand (%d/%d)",
                        self._current_pool_size + 1,
                        self.pool_size,
                    )
                    connection_pair = self._create_connection_pair()
                    self._current_pool_size += 1
                    return connection_pair
                except Exception as e:
                    LOGGER.error("Failed to create connection pair on-demand: %s", e)
                    raise

        # Pool is at max capacity, wait for an existing connection to become available
        LOGGER.debug(
            "Pool at max capacity (%d), waiting for available connection",
            self.pool_size,
        )
        try:
            return self._pool.get(timeout=self.connection_timeout)
        except Empty:
            raise TimeoutError(
                f"Pool at max capacity ({self.pool_size}) and no connection pair "
                f"available within {self.connection_timeout} seconds"
            ) from Empty

    def get_current_pool_size(self) -> int:
        """Get the current number of available connection pairs in the pool."""
        return self._pool.qsize()

    def get_total_connections_created(self) -> int:
        """Get the total number of connection pairs created so far."""
        with self._lock:
            return self._current_pool_size

    def cleanup_pool(self) -> None:
        """Clean up all connections in the pool."""
        LOGGER.info("Cleaning up connection pool")

        with self._lock:
            closed_count = 0
            while not self._pool.empty():
                try:
                    connection_pair = self._pool.get_nowait()
                    connection_pair.close_connections()
                    closed_count += 1
                except Empty:
                    break
                except Exception as e:
                    LOGGER.warning("Error during pool cleanup: %s", e)

            self._initialized = False
            self._current_pool_size = 0
            LOGGER.info("Closed %d connection pairs during cleanup", closed_count)

    def __enter__(self):
        """Context manager entry."""
        self.initialize_pool()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup_pool()


# Convenience function for creating connection pool managers
def create_connection_pool_manager(
    source_platform: Platform,
    target_platform: Platform,
    source_connection_config: Connection,
    target_connection_config: Connection,
    pool_size: int = 1,
) -> ConnectionPoolManager:
    """Create a connection pool manager with the given configuration.

    Args:
        source_platform: Platform type for source connections (e.g., Platform.SQLSERVER)
        target_platform: Platform type for target connections (e.g., Platform.SNOWFLAKE)
        source_connection_config: Configuration for source database connections
        target_connection_config: Configuration for target database connections
        pool_size: Number of connection pairs to maintain in the pool

    Returns:
        ConnectionPoolManager: Configured connection pool manager

    """
    return ConnectionPoolManager(
        source_platform=source_platform,
        target_platform=target_platform,
        source_connection_config=source_connection_config,
        target_connection_config=target_connection_config,
        pool_size=pool_size,
    )
