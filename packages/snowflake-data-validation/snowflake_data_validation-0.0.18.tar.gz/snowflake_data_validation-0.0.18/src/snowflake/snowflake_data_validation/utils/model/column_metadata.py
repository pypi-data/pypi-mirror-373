class ColumnMetadata:

    """Represents metadata for a column in a Snowflake table."""

    def __init__(
        self,
        name: str,
        data_type: str,
        nullable: bool,
        is_primary_key: bool,
        calculated_column_size_in_bytes: int,
        properties: dict[str, any],
    ):
        """Initialize the ColumnMetadata object.

        Args:
            name (str): The name of the column.
            data_type (str): The data type of the column.
            nullable (bool): Indicates if the column can contain NULL values.
            is_primary_key (bool): Indicates if the column is part of the primary key.
            calculated_column_size_in_bytes (int): The calculated size of the column in bytes.
            properties (dict[str, any]): Additional properties of the column.

        """
        self.name: str = name
        self.data_type: str = data_type
        self.nullable: bool = nullable
        self.is_primary_key: bool = is_primary_key
        self.calculated_column_size_in_bytes: int = calculated_column_size_in_bytes
        self.properties: dict[str, any] = properties

    def copy(self) -> "ColumnMetadata":
        """Create a copy of the ColumnMetadata instance."""
        return ColumnMetadata(
            self.name,
            self.data_type,
            self.nullable,
            self.is_primary_key,
            self.calculated_column_size_in_bytes,
            self.properties.copy(),
        )

    def to_upper_name(self) -> None:
        """Convert the column name to uppercase."""
        self.name = self.name.upper()
