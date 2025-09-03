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

from typing import Optional

import pandas as pd

from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import COLUMN_VALIDATED


class HelperDataFrame:

    """Helper class for DataFrame processing utilities."""

    def __init__(self):
        """Initialize the HelperDataFrame instance."""
        pass

    def process_query_result_to_dataframe(
        self,
        columns_names: list[str],
        data_rows: list,
        output_handler: Optional[OutputHandlerBase] = None,
        header: Optional[str] = None,
        output_level: Optional[OutputMessageLevel] = None,
        apply_column_validated_uppercase: bool = True,
        sort_and_reset_index: bool = True,
    ) -> pd.DataFrame:
        """Process query results into a standardized DataFrame format.

        Args:
            columns_names: List of column names from the query result
            data_rows: List of data rows from the query result
            output_handler: Optional output handler for logging and reporting messages
            header: Optional header for output message
            output_level: Optional output message level
            apply_column_validated_uppercase: Whether to apply uppercase to COLUMN_VALIDATED column
            sort_and_reset_index: Whether to sort by all columns and reset index

        Returns:
            pd.DataFrame: Processed DataFrame with standardized formatting

        """
        # Convert column names to uppercase and data rows to lists
        columns_names_upper = [col.upper() for col in columns_names]
        data_rows_list = [list(row) for row in data_rows]

        # Create DataFrame
        df = pd.DataFrame(data_rows_list, columns=columns_names_upper)  # type: ignore

        # Apply sorting and index reset if requested
        if sort_and_reset_index:
            df = df.sort_values(by=list(df.columns)).reset_index(drop=True)

        # Apply uppercase transformation to COLUMN_VALIDATED column if requested
        if apply_column_validated_uppercase and COLUMN_VALIDATED in df.columns:
            df[COLUMN_VALIDATED] = df[COLUMN_VALIDATED].str.upper()

        # Handle output message if all parameters are provided
        if output_handler and header and output_level:
            output_handler.handle_message(
                header=header,
                dataframe=df,
                level=output_level,
            )

        return df
