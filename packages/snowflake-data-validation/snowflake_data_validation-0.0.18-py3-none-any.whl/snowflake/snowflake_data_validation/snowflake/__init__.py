# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Snowflake Data Validation Snowflake
=====================================

This package provides Snowflake-specific functionality for data validation,
enabling data quality checks and comparison operations between Snowflake and other sources.

Main Components
----------------
- Connector: Snowflake database connection management
- Extractor: Snowflake data extraction utilities

Example
-------
>>> from snowflake.snowflake_data_validation.snowflake import main
>>> main()

For more detailed examples and usage, please refer to the documentation.
"""
from snowflake.snowflake_data_validation.snowflake.connector.connector_snowflake import (
    ConnectorSnowflake,
)
from snowflake.snowflake_data_validation.snowflake.model import (
    SnowflakeDefaultConnection,
    SnowflakeNamedConnection,
)

__all__ = [
    "ConnectorSnowflake",
    "SnowflakeDefaultConnection",
    "SnowflakeNamedConnection",
]

# Import submodules - these will be lazily loaded
from . import connector  # noqa: F401
