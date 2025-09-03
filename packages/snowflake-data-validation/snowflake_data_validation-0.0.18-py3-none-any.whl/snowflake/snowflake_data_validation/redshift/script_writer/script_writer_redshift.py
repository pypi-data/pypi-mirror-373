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
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALIDATED,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context


LOGGER = logging.getLogger(__name__)


class ScriptWriterRedshift(ScriptWriterBase):

    """Redshift-specific implementation for printing database queries.

    This class inherits all query printing functionality from ScriptWriterBase.
    No method overrides are needed as the base class provides complete implementations
    that work with Redshift's query generator.
    """

    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the Redshift script printer.

        Args:
            connector: Redshift database connector instance.
            query_generator: Query generator instance for generating Redshift queries.
            report_path: Optional path for output reports.

        """
        super().__init__(connector, query_generator, report_path)

    def extract_table_column_metadata(
        self, table_configuration: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        sql_query = context.sql_generator.extract_table_column_metadata(
            database_name=table_configuration.source_database,
            schema_name=table_configuration.source_schema,
            table_name=table_configuration.source_table,
            platform=Platform.REDSHIFT.value,
        )

        try:
            result_columns, result = self.connector.execute_query(sql_query)

        except Exception:
            error_message = (
                f"[Redshift] Metadata extraction query failed for table: "
                f"{table_configuration.fully_qualified_name}."
            )

            LOGGER.critical(error_message)
            raise

        return self._process_query_result_to_dataframe(
            columns_names=result_columns,
            data_rows=result,
            output_handler=context.output_handler,
            header=None,
            output_level=None,
            apply_column_validated_uppercase=False,
            sort_and_reset_index=False,
        )

    def _process_query_result_to_dataframe(
        self,
        columns_names: list[str],
        data_rows: list,
        output_handler: OutputHandlerBase = None,
        header: str = None,
        output_level: OutputMessageLevel = None,
        apply_column_validated_uppercase: bool = True,
        sort_and_reset_index: bool = True,
    ) -> pd.DataFrame:
        """Process query results into a standardized DataFrame format.

        Args:
            columns_names: List of column names from the query result
            data_rows: List of data rows from the query result
            output_handler: Optional output handler for logging messages
            header: Optional header for output message
            output_level: Optional output message level
            apply_column_validated_uppercase: Whether to apply uppercase to COLUMN_VALIDATED column
            sort_and_reset_index: Whether to sort by all columns and reset index

        Returns:
            pd.DataFrame: Processed DataFrame with standardized formatting

        """
        columns_names_upper = [col.upper() for col in columns_names]
        data_rows_list = [list(row) for row in data_rows]
        df = pd.DataFrame(data_rows_list, columns=columns_names_upper)
        if sort_and_reset_index:
            df = df.sort_values(by=list(df.columns)).reset_index(drop=True)
        if apply_column_validated_uppercase and COLUMN_VALIDATED in df.columns:
            df[COLUMN_VALIDATED] = df[COLUMN_VALIDATED].str.upper()
        if output_handler and header and output_level:
            output_handler.handle_message(
                header=header,
                dataframe=df,
                level=output_level,
            )

        return df
