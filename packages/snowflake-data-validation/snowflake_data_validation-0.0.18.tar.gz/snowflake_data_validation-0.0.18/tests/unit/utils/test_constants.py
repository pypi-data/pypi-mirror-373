"""Constants and enums for testing purposes."""

from enum import Enum


class SQLServerDataType(str, Enum):
    """Enumeration of SQL Server data types for testing.

    This enum is used exclusively for testing purposes to validate
    the SQL Server data type mappings.
    """

    # Numeric types
    BIGINT = "BIGINT"
    BIT = "BIT"
    DECIMAL = "DECIMAL"
    FLOAT = "FLOAT"
    INT = "INT"
    MONEY = "MONEY"
    NUMERIC = "NUMERIC"
    REAL = "REAL"
    SMALLINT = "SMALLINT"
    SMALLMONEY = "SMALLMONEY"
    TINYINT = "TINYINT"

    # Date and Time types
    DATE = "DATE"
    DATETIME = "DATETIME"
    DATETIME2 = "DATETIME2"
    DATETIMEOFFSET = "DATETIMEOFFSET"
    SMALLDATETIME = "SMALLDATETIME"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"

    # Character types
    CHAR = "CHAR"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    NCHAR = "NCHAR"
    NVARCHAR = "NVARCHAR"
    NTEXT = "NTEXT"

    # Binary types
    BINARY = "BINARY"
    VARBINARY = "VARBINARY"
    IMAGE = "IMAGE"

    # Other types
    SQL_VARIANT = "SQL_VARIANT"
    GEOGRAPHY = "GEOGRAPHY"
    UNIQUEIDENTIFIER = "UNIQUEIDENTIFIER"
    XML = "XML"
    SYSNAME = "SYSNAME"

    @classmethod
    def list(cls) -> set[str]:
        """Return a set of all SQL Server data type values."""
        return {member.value for member in cls}
