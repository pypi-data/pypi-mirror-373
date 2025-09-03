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

import pytest

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_CONNECTION_MODE,
)


class ConnectorBaseTestHelper(ConnectorBase):
    def connect(
        self, mode: str = DEFAULT_CONNECTION_MODE, connection_name: str = ""
    ) -> None:
        pass

    def execute_query(self, query: str) -> list[tuple]:
        return []

    def execute_statement(self, statement: str) -> None:
        pass

    def execute_query_no_return(self, query: str) -> None:
        pass

    def close(self) -> None:
        pass


def test_connector_base_methods():
    connector = ConnectorBaseTestHelper()
    assert connector.connect() is None
    assert connector.execute_query("SELECT 1") == []
    assert connector.close() is None
