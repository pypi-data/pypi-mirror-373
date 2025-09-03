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
Snowflake Data Validation
=========================

This package provides comprehensive data validation functionality for Snowflake,
enabling robust data quality checks and migration validation between different
database systems.

Features
--------
- Multi-level data validation (Level 1: table metadata, Level 2: column metadata)
- Support for multiple source systems (SQL Server, Snowflake)
- CLI interface for validation operations
- Configurable validation processes
- Progress reporting and detailed validation reports

Main Components
---------------
ComparisonOrchestrator
    Main class for orchestrating data comparisons between source and target systems

CLI Interface
    Command-line interface available via `main_cli` module for:
    - Setting up database connections
    - Running validation operations
    - Managing configuration files

Supported Dialects
------------------
- Snowflake to Snowflake validation
- SQL Server to Snowflake migration validation

Example Usage
-------------
Programmatic API:
>>> from snowflake.snowflake_data_validation import ComparisonOrchestrator
>>> # Set up extractors, context, and configuration
>>> orchestrator = ComparisonOrchestrator(
...     source_extractor=source_extractor,
...     target_extractor=target_extractor,
...     context=context
... )
>>> orchestrator.run_sync_comparison()

Command Line Interface:

.. code-block:: bash

    # Set up SQL Server connection
    python -m snowflake.snowflake_data_validation sqlserver source-connection \
        --host localhost --port 1433 --username user --password pass --database mydb

    # Run validation
    python -m snowflake.snowflake_data_validation sqlserver run-validation \
        --data-validation-config-file config.json

For more detailed examples and usage, please refer to the documentation.
"""

from snowflake.snowflake_data_validation.comparison_orchestrator import (
    ComparisonOrchestrator,
)
from snowflake.snowflake_data_validation.__version__ import __version__

# Import submodules and make them available at the package level
# This helps Sphinx properly document the submodules
import snowflake.snowflake_data_validation.validation as validation
import snowflake.snowflake_data_validation.extractor as extractor
import snowflake.snowflake_data_validation.connector as connector
import snowflake.snowflake_data_validation.utils as utils
import snowflake.snowflake_data_validation.snowflake as snowflake
import snowflake.snowflake_data_validation.sqlserver as sqlserver
import snowflake.snowflake_data_validation.redshift as redshift
import logging


# Add a NullHandler to prevent logging messages from being output to
# sys.stderr if no logging configuration is provided.
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Define the public API
__all__ = [
    "__version__",
    "ComparisonOrchestrator",
    # Submodules
    "validation",
    "extractor",
    "connector",
    "utils",
    "snowflake",
    "sqlserver",
    "redshift"
]


# Version information
__version_info__ = tuple(int(i) for i in __version__.split(".") if i.isdigit())
