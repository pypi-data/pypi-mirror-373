import logging

from typing import ClassVar, Optional

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.helper import Helper


LOGGER = logging.getLogger(__name__)


class TableConfiguration(BaseModel):

    """Table configuration model.

    Args:
        pydantic.BaseModel (pydantic.BaseModel): pydantic BaseModel

    """

    _id_counter: ClassVar[int] = 0
    id: Optional[int] = None

    fully_qualified_name: str
    use_column_selection_as_exclude_list: bool
    column_selection_list: list[str]
    validation_configuration: Optional[ValidationConfiguration] = None

    source_database: Optional[str] = None
    source_schema: Optional[str] = None
    source_table: Optional[str] = None
    target_name: Optional[str] = None

    target_fully_qualified_name: str = ""
    where_clause: str = ""
    target_where_clause: str = ""
    has_where_clause: bool = False
    has_target_where_clause: bool = False
    target_database: Optional[str] = None
    target_schema: Optional[str] = None
    index_column_list: list[str] = []
    target_index_column_list: list[str] = []
    is_case_sensitive: bool = False
    chunk_number: Optional[int] = None
    column_mappings: dict[str, str] = {}
    max_failed_rows_number: Optional[int] = None
    exclude_metrics: Optional[bool] = None

    @model_validator(mode="after")
    def load(self) -> Self:
        self._assign_id()
        self._load_source_decomposed_fully_qualified_name()
        self._load_target_fully_qualified_name()
        self._set_has_where_clause()
        self._set_has_target_where_clause()
        self._set_target_index_column_list()
        self._check_chunk_number()
        self._check_target_where_clause()
        self._set_column_mappings()
        self._check_max_failed_rows_number()
        return self

    def _assign_id(self) -> None:
        if self.id is None:
            TableConfiguration._id_counter += 1
            self.id = TableConfiguration._id_counter

    def _load_source_decomposed_fully_qualified_name(self) -> None:
        decomposed_tuple = Helper.get_decomposed_fully_qualified_name(
            self.fully_qualified_name
        )
        self.source_database = decomposed_tuple[0]
        self.source_schema = decomposed_tuple[1]
        self.source_table = decomposed_tuple[2]

    def _load_target_fully_qualified_name(self) -> None:
        if self.target_database is None:
            self.target_database = self.source_database

        if self.target_schema is None:
            self.target_schema = self.source_schema

        if self.target_name is None:
            self.target_name = self.source_table

        self.target_fully_qualified_name = (
            f"{self.target_database}.{self.target_schema}.{self.target_name}"
        )

    def _set_has_where_clause(self) -> None:
        self.has_where_clause = self.where_clause != ""

    def _set_has_target_where_clause(self) -> None:
        self.has_target_where_clause = self.target_where_clause != ""

    def _check_target_where_clause(self) -> None:
        if not self.has_target_where_clause:
            LOGGER.warning(
                "Target where clause was not set for table %s. This may lead to unexpected results.",
                self.target_fully_qualified_name,
            )

    def _set_target_index_column_list(self) -> None:
        for source_column_name in self.index_column_list:
            self.target_index_column_list.append(
                self.column_mappings.get(source_column_name, source_column_name)
            )

    def _check_chunk_number(self) -> None:
        if self.chunk_number is None:
            return
        elif self.chunk_number < 1:
            raise ValueError("Chunk number must be greater than or equal to 1.")

    def _set_column_mappings(self) -> None:
        """Normalize the keys and values of the column mappings dictionary to uppercase."""
        local_column_mapping = {}
        for key in self.column_mappings.keys():
            local_column_mapping[key.upper()] = self.column_mappings[key].upper()
        self.column_mappings = local_column_mapping

    def _check_max_failed_rows_number(self) -> None:
        # Accept None, because it will be overwritten by ConfigurationModel
        # based on the value of ValidationConfiguration model.
        if self.max_failed_rows_number is None:
            return
        elif self.max_failed_rows_number < 1:
            raise ValueError(
                f"Invalid value for max failed rows number in table f{self.fully_qualified_name}. "
                "Value must be greater than or equal to 1."
            )
