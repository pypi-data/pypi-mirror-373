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
import time

from abc import ABC, abstractmethod
from typing import Optional

from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_MODE,
)


class ConnectorBase(ABC):

    """Abstract base class for database connectors."""

    def __init__(self, output_path: Optional[str] = None):
        self.connection: Optional[object] = None
        self.output_path = output_path
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        """Establish a connection to the database."""
        pass

    def connect_with_retry(
        self,
        connect_func,
        max_attempts: int = 3,
        delay_seconds: float = 1.0,
        delay_multiplier: float = 2.0,
        *args,
        **kwargs,
    ) -> None:
        """Establish a connection with retry logic.

        Args:
            connect_func: The connection function to call
            max_attempts: Maximum number of connection attempts
            delay_seconds: Initial delay between retries in seconds
            delay_multiplier: Multiplier for exponential backoff
            *args: Arguments to pass to connect_func
            **kwargs: Keyword arguments to pass to connect_func

        Raises:
            ConnectionError: If all connection attempts fail

        """
        last_exception = None
        current_delay = delay_seconds

        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.info(f"Connection attempt {attempt}/{max_attempts}")
                connect_func(*args, **kwargs)
                self.logger.info("Connection established successfully")
                return

            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"Connection attempt {attempt}/{max_attempts} failed: {str(e)}"
                )
                if attempt < max_attempts:
                    self.logger.info(f"Retrying in {current_delay:.1f} seconds...")
                    time.sleep(current_delay)
                    current_delay *= delay_multiplier
                else:
                    self.logger.error(f"All {max_attempts} connection attempts failed")
        raise ConnectionError(
            f"Failed to establish connection after {max_attempts} attempts. "
            f"Last error: {last_exception}"
        ) from last_exception

    def _verify_connection(self) -> None:
        """Verify the connection by executing a simple test query.

        Default implementation that can be overridden by child classes.
        Child classes should implement their own verification logic.

        Raises:
            ConnectionError: If connection verification fails

        """
        if self.connection is None:
            raise ConnectionError("Connection is None")

        # Default implementation - child classes should override this
        self.logger.debug("Using default connection verification (no-op)")

    def _attempt_connection_and_verify(self, connect_func, *args, **kwargs) -> None:
        """Attempt connection and verify it.

        Args:
            connect_func: The connection function to call
            *args: Arguments to pass to connect_func
            **kwargs: Keyword arguments to pass to connect_func

        Raises:
            ConnectionError: If connection or verification fails

        """
        try:
            connect_func(*args, **kwargs)
            self._verify_connection()

        except Exception:
            if self.connection is not None:
                try:
                    close_method = getattr(self.connection, "close", None)
                    if close_method is not None:
                        close_method()
                except Exception:
                    pass  # Ignore errors during cleanup
                self.connection = None
            raise

    @abstractmethod
    def execute_query(self, query: str) -> list[tuple]:
        """Execute a query on the database."""
        pass

    @abstractmethod
    def execute_statement(self, statement: str) -> None:
        """Execute a statement on the database."""
        pass

    @abstractmethod
    def execute_query_no_return(self, query: str) -> None:
        """Execute a query on the database without returning results."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the database."""
        pass


class NullConnector(ConnectorBase):

    """A connector that does nothing. Used as a null object for async validation scenarios."""

    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        pass

    def execute_query(self, query: str) -> list[tuple]:
        return []

    def execute_query_no_return(self, query: str) -> None:
        pass

    def execute_statement(self, statement: str) -> None:
        pass

    def close(self) -> None:
        pass
