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

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.utils.context import Context


LOGGER = logging.getLogger(__name__)


class ScriptWriterSnowflake(ScriptWriterBase):

    """Snowflake-specific implementation for printing database queries.

    This class inherits all query printing functionality from ScriptWriterBase.
    No method overrides are needed as the base class provides complete implementations
    that work with Snowflake's query generator.
    """

    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the Snowflake script printer.

        Args:
            connector: Snowflake database connector instance.
            query_generator: Query generator instance for generating Snowflake SQL queries.
            report_path: Optional path for output reports.

        """
        super().__init__(connector, query_generator, report_path)

    def extract_table_column_metadata(
        self, table_context: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        LOGGER.debug(
            "Extracting table column metadata for: %s",
            table_context.target_fully_qualified_name,
        )
        # Intentional return an empty DataFrame.
        LOGGER.debug(
            "Returning empty DataFrame for table column metadata (intentional)"
        )
        return pd.DataFrame()

    def extract_table_row_count(
        self,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        platform: Platform,
        context: Context,
    ) -> pd.DataFrame:
        query = self.query_generator.generate_table_row_count_query(
            fully_qualified_name=fully_qualified_name,
            where_clause=where_clause,
            has_where_clause=has_where_clause,
            platform=platform,
            context=context,
        )

        result = self.connector.execute_query(query)

        df = pd.DataFrame(result)
        return df
