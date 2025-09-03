import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    CALCULATED_COLUMN_SIZE_IN_BYTES_KEY,
    CHARACTER_LENGTH_KEY,
    COLUMN_NAME_KEY,
    DATA_TYPE_KEY,
    DATABASE_NAME_KEY,
    IS_DATA_TYPE_SUPPORTED_KEY,
    IS_PRIMARY_KEY_KEY,
    NULLABLE_KEY,
    PRECISION_KEY,
    ROW_COUNT_KEY,
    SCALE_KEY,
    SCHEMA_NAME_KEY,
    TABLE_NAME_KEY,
)
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)


def _get_properties(row: dict[str, any]) -> dict[str, any]:
    """Extract and return relevant column properties from the row dictionary."""
    keys = [CHARACTER_LENGTH_KEY, PRECISION_KEY, SCALE_KEY]
    return {key: row[key] for key in keys if not pd.isna(row[key])}


class TableColumnMetadata:
    def __init__(
        self,
        table_column_metadata_df: pd.DataFrame,
        column_selection_list: list[str],
    ) -> None:
        """Initialize the TableColumnMetadata object.

        Args:
            table_column_metadata_df (pd.DataFrame): A DataFrame containing metadata for columns in a Snowflake table.
            column_selection_list (list[str], optional): List of columns to include or exclude based on configuration.
            This DataFrame should have the following columns:
                - SCHEMA_NAME: The name of the schema containing the table.
                - TABLE_NAME: The name of the table.
                - COLUMN_NAME: The name of the column.
                - DATA_TYPE: The data type of the column.
                - NULLABLE: Indicates if the column can contain NULL values (boolean).
                - IS_PRIMARY_KEY: Indicates if the column is part of the primary key (boolean).
                - CALCULATED_COLUMN_SIZE_IN_BYTES: The calculated size of the column in bytes.
                - CHARACTER_LENGTH: The character length of the column (optional).
                - PRECISION: The precision of the column (optional).
                - SCALE: The scale of the column (optional).
                - ROW_COUNT: The number of rows in the table (optional).

        """
        table_column_metadata = table_column_metadata_df.to_dict(orient="records")
        if len(table_column_metadata) == 0:
            self.database_name = ""
            self.schema_name = ""
            self.table_name = ""
            self.row_count = 0
            self.columns = []
            self.column_selection_list = column_selection_list or []
            return

        self.column_selection_list = column_selection_list or []

        self.database_name: str = table_column_metadata[0][DATABASE_NAME_KEY]
        self.schema_name: str = table_column_metadata[0][SCHEMA_NAME_KEY]
        self.table_name: str = table_column_metadata[0][TABLE_NAME_KEY]
        self.row_count: int = int(table_column_metadata[0][ROW_COUNT_KEY])

        self.columns: list[ColumnMetadata] = []
        self.unsupported_columns: list[str] = []
        for row in table_column_metadata:
            if not row.get(IS_DATA_TYPE_SUPPORTED_KEY, True):
                self.unsupported_columns.append(row[COLUMN_NAME_KEY])
                continue
            column_metadata = ColumnMetadata(
                row[COLUMN_NAME_KEY],
                row[DATA_TYPE_KEY],
                bool(row[NULLABLE_KEY]),
                bool(row[IS_PRIMARY_KEY_KEY]),
                int(row[CALCULATED_COLUMN_SIZE_IN_BYTES_KEY]),
                _get_properties(row),
            )
            self.columns.append(column_metadata)
