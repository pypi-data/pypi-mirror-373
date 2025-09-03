# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Snowflake Data Validation Redshift
=====================================

This package provides Redshift-specific functionality for data validation,
enabling data quality checks and comparison operations between Redshift and other sources.

Main Components
----------------
- Connector: Redshift database connection management
- Extractor: Redshift data extraction utilities

Example
-------
>>> from snowflake.snowflake_data_validation.redshift import main
>>> main()

For more detailed examples and usage, please refer to the documentation.
"""
from snowflake.snowflake_data_validation.redshift.connector.connector_redshift import (
    ConnectorRedshift,
)
from snowflake.snowflake_data_validation.redshift.model import (
    RedshiftCredentialsConnection
)

__all__ = [
    "ConnectorRedshift",
    "RedshiftCredentialsConnection",
]

# Import submodules - these will be lazily loaded
from . import connector  # noqa: F401
