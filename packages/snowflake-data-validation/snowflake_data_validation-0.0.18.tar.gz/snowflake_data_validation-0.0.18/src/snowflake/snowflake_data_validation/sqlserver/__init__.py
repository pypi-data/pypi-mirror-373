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


"""
Snowflake Data Validation SQL Server
=====================================

This package provides SQL Server-specific functionality for data validation in Snowflake,
enabling data quality checks and comparison operations between SQL Server and Snowflake.

Main Components
----------------
- Connector: SQL Server database connection management
- Extractor: SQL Server-specific data extraction utilities
- Main: Entry point for SQL Server validation


For more detailed examples and usage, please refer to the documentation.
"""
from snowflake.snowflake_data_validation.sqlserver.connector.connector_sql_server import (
    ConnectorSqlServer,
)
from snowflake.snowflake_data_validation.sqlserver.model import (
    SqlServerCredentialsConnection,
)

__all__ = [
    "ConnectorSqlServer",
    "SqlServerCredentialsConnection",
]

# Import submodules - these will be lazily loaded
from . import connector  # noqa: F401
