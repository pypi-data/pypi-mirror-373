from typing import Optional, Union

from pydantic import BaseModel, field_validator, model_validator
from typing_extensions import Self

from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_THREAD_COUNT_OPTION,
    VALIDATION_CONFIGURATION_DEFAULT_VALUE,
)


class ConfigurationModel(BaseModel):

    """Configuration model.

    Args:
        pydantic.BaseModel (pydantic.BaseModel): pydantic BaseModel

    """

    source_platform: str
    target_platform: str
    output_directory_path: str
    max_threads: Union[
        str, int
    ] = "auto"  # "auto" for auto-detection or number for specific thread count
    source_connection: Optional[Connection] = None
    target_connection: Optional[Connection] = None
    source_validation_files_path: Optional[str] = None
    target_validation_files_path: Optional[str] = None
    target_database: Optional[str] = None
    validation_configuration: ValidationConfiguration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )
    comparison_configuration: Optional[dict[str, Union[str, float, int]]] = None
    database_mappings: dict[str, str] = {}
    schema_mappings: dict[str, str] = {}
    tables: list[TableConfiguration] = []

    @field_validator("max_threads")
    @classmethod
    def validate_max_threads(cls, value: Union[str, int]) -> Union[str, int]:
        """Validate max_threads field accepts only 'auto' or positive integers."""
        if isinstance(value, str):
            if value.lower() != DEFAULT_THREAD_COUNT_OPTION:
                raise ValueError(
                    f"String value for max_threads must be '{DEFAULT_THREAD_COUNT_OPTION}'"
                )
            return value.lower()
        elif isinstance(value, int):
            if value < 1:
                raise ValueError(
                    "Numeric value for max_threads must be a positive integer"
                )
            return value
        else:
            raise ValueError(
                f"max_threads must be either '{DEFAULT_THREAD_COUNT_OPTION}' or a positive integer"
            )

    @model_validator(mode="after")
    def load(self) -> Self:
        self.check_tables()
        return self

    def check_tables(self) -> None:
        table: TableConfiguration
        for table in self.tables:
            self._load_target_fully_qualified_name(table)
            self._check_max_failed_rows_number(table)
            self._check_chunk_number(table)
            self.set_exclude_metrics(table)

    def _load_target_fully_qualified_name(self, table: TableConfiguration) -> None:
        # If target_database is set in config, use it for Teradata sources
        if self.target_database is not None and table.source_database is None:
            table.target_database = self.target_database
        # Otherwise use database mappings if available
        elif (
            table.source_database is not None
            and self.database_mappings.get(table.source_database) is not None
        ):
            table.target_database = self.database_mappings[table.source_database]

        if (
            table.source_schema is not None
            and self.schema_mappings.get(table.source_schema) is not None
        ):
            table.target_schema = self.schema_mappings[table.source_schema]

        table._load_target_fully_qualified_name()

    def _check_max_failed_rows_number(self, table: TableConfiguration) -> None:
        if table.max_failed_rows_number is None:
            table.max_failed_rows_number = (
                self.validation_configuration.max_failed_rows_number
            )

    def _check_chunk_number(self, table: TableConfiguration) -> None:
        if table.chunk_number is None:
            table.chunk_number = 0

    def set_exclude_metrics(self, table: TableConfiguration) -> None:
        if table.exclude_metrics is None:
            table.exclude_metrics = self.validation_configuration.exclude_metrics
