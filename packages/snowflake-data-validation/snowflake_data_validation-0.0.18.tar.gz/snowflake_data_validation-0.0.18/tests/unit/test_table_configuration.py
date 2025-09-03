import pytest
from deepdiff import DeepDiff
from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import (
    VALIDATION_CONFIGURATION_DEFAULT_VALUE,
)


@pytest.fixture(autouse=True)
def table_id_counter():
    TableConfiguration._id_counter = 0


def test_table_configuration_generation_default_values():
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    model_dict = table_configuration.model_dump()
    expected_model_dict = {
        "column_selection_list": ["excluded_column_1", "excluded_column_2"],
        "column_mappings": {},
        "exclude_metrics": None,
        "fully_qualified_name": "ex_database.ex_schema.ex_table",
        "has_where_clause": False,
        "has_target_where_clause": False,
        "index_column_list": ["index_column_1", "index_column_2"],
        "is_case_sensitive": False,
        "source_database": "ex_database",
        "source_schema": "ex_schema",
        "source_table": "ex_table",
        "target_database": "ex_database",
        "target_fully_qualified_name": "ex_database.ex_schema.ex_table",
        "target_index_column_list": ["index_column_1", "index_column_2"],
        "target_name": "ex_table",
        "target_schema": "ex_schema",
        "target_where_clause": "",
        "use_column_selection_as_exclude_list": True,
        "validation_configuration": None,
        "where_clause": "",
        "chunk_number": None,
        "max_failed_rows_number": None,
        "id": 1,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_table_configuration_generation_custom_values():
    default_validation_configuration = ValidationConfiguration(
        **VALIDATION_CONFIGURATION_DEFAULT_VALUE
    )
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        target_database="target_database",
        target_schema="target_schema",
        target_name="target_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1"],
        validation_configuration=default_validation_configuration,
        where_clause="id > 1 AND id < 100",
        target_where_clause="id > 1 AND id < 100",
        has_where_clause=True,
        index_column_list=["index_column_1"],
        chunk_number=10,
        column_mappings={"id": "IDD"},
        max_failed_rows_number=65,
    )

    model_dict = table_configuration.model_dump()
    expected_model_dict = {
        "column_selection_list": ["excluded_column_1"],
        "column_mappings": {"ID": "IDD"},
        "exclude_metrics": None,
        "fully_qualified_name": "ex_database.ex_schema.ex_table",
        "has_where_clause": True,
        "has_target_where_clause": True,
        "id": 1,
        "index_column_list": ["index_column_1"],
        "is_case_sensitive": False,
        "source_database": "ex_database",
        "source_schema": "ex_schema",
        "source_table": "ex_table",
        "target_database": "target_database",
        "target_fully_qualified_name": "target_database.target_schema.target_table",
        "target_index_column_list": ["index_column_1"],
        "target_name": "target_table",
        "target_schema": "target_schema",
        "target_where_clause": "id > 1 AND id < 100",
        "use_column_selection_as_exclude_list": True,
        "validation_configuration": {
            "exclude_metrics": False,
            "custom_templates_path": None,
            "metrics_validation": True,
            "row_validation": True,
            "schema_validation": True,
            "max_failed_rows_number": 100,
        },
        "where_clause": "id > 1 AND id < 100",
        "chunk_number": 10,
        "max_failed_rows_number": 65,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )
    assert diff == {}


def test_table_configuration_generation_pydantic_default_values():
    file_content = r"""fully_qualified_name: example_database.example_schema.table
use_column_selection_as_exclude_list: true
column_selection_list:
  - excluded_column_example_1
  - excluded_column_example_2
index_column_list: []
"""

    table_configuration = parse_yaml_raw_as(TableConfiguration, file_content)

    assert table_configuration is not None

    model_dict = table_configuration.model_dump()
    expected_model_dict = {
        "column_selection_list": [
            "excluded_column_example_1",
            "excluded_column_example_2",
        ],
        "column_mappings": {},
        "exclude_metrics": None,
        "fully_qualified_name": "example_database.example_schema.table",
        "has_where_clause": False,
        "has_target_where_clause": False,
        "id": 1,
        "index_column_list": [],
        "is_case_sensitive": False,
        "source_database": "example_database",
        "source_schema": "example_schema",
        "source_table": "table",
        "target_database": "example_database",
        "target_fully_qualified_name": "example_database.example_schema.table",
        "target_index_column_list": [],
        "target_name": "table",
        "target_schema": "example_schema",
        "target_where_clause": "",
        "use_column_selection_as_exclude_list": True,
        "validation_configuration": None,
        "where_clause": "",
        "chunk_number": None,
        "max_failed_rows_number": None,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_table_configuration_generation_pydantic_custom_values():
    file_content = r"""fully_qualified_name: example_database.example_schema.table
use_column_selection_as_exclude_list: false
column_selection_list: []
target_database: target_database
target_schema: target_schema
target_name: target_table
validation_configuration:
    metrics_validation: true
    row_validation: true
    schema_validation: true
index_column_list: ['index_column_1', 'index_column_2']
where_clause: id > 1 AND id < 100
chunk_number: 10
column_mappings:
    source_column_1 : target_column_1
max_failed_rows_number: 43
"""
    table_configuration = parse_yaml_raw_as(TableConfiguration, file_content)

    assert table_configuration is not None

    model_dict = table_configuration.model_dump()
    expected_model_dict = {
        "column_selection_list": [],
        "column_mappings": {"SOURCE_COLUMN_1": "TARGET_COLUMN_1"},
        "exclude_metrics": None,
        "fully_qualified_name": "example_database.example_schema.table",
        "has_where_clause": True,
        "has_target_where_clause": False,
        "id": 1,
        "index_column_list": ["index_column_1", "index_column_2"],
        "is_case_sensitive": False,
        "source_database": "example_database",
        "source_schema": "example_schema",
        "source_table": "table",
        "target_database": "target_database",
        "target_fully_qualified_name": "target_database.target_schema.target_table",
        "target_index_column_list": ["index_column_1", "index_column_2"],
        "target_name": "target_table",
        "target_schema": "target_schema",
        "target_where_clause": "",
        "use_column_selection_as_exclude_list": False,
        "validation_configuration": {
            "exclude_metrics": False,
            "custom_templates_path": None,
            "metrics_validation": True,
            "row_validation": True,
            "schema_validation": True,
            "max_failed_rows_number": 100,
        },
        "where_clause": "id > 1 AND id < 100",
        "chunk_number": 10,
        "max_failed_rows_number": 43,
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_table_configuration_generation_pydantic_load_source_decomposed_fully_qualified_name_exception():
    file_content = r"""fully_qualified_name: table
use_column_selection_as_exclude_list: false
column_selection_list: []
index_column_list: []
"""

    with (pytest.raises(ValueError) as ex_info):
        parse_yaml_raw_as(TableConfiguration, file_content)

    assert r"""1 validation error for TableConfiguration
  Value error, Invalid fully qualified name: table. Expected format: 'database.schema.table' or 'schema.table' [type=value_error, input_value={'fully_qualified_name': ...'index_column_list': []}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/value_error""" == str(
        ex_info.value
    )


def test_table_configuration_generation_pydantic_load_missing_fields_exception():
    file_content = r"""fully_qualified_name: example_database.example_schema.table"""

    with (pytest.raises(ValueError) as ex_info):
        parse_yaml_raw_as(TableConfiguration, file_content)

    assert r"""2 validation errors for TableConfiguration
use_column_selection_as_exclude_list
  Field required [type=missing, input_value={'fully_qualified_name': ...e.example_schema.table'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
column_selection_list
  Field required [type=missing, input_value={'fully_qualified_name': ...e.example_schema.table'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing""" == str(
        ex_info.value
    )


def test_table_configuration_invalid_max_failed_rows_number_value_exception():
    with (pytest.raises(ValueError) as ex_info):
        TableConfiguration(
            fully_qualified_name="ex_database.ex_schema.ex_table",
            use_column_selection_as_exclude_list=True,
            column_selection_list=["excluded_column_1", "excluded_column_2"],
            index_column_list=["index_column_1", "index_column_2"],
            max_failed_rows_number=0,
        )

    assert r"""1 validation error for TableConfiguration
  Value error, Invalid value for max failed rows number in table fex_database.ex_schema.ex_table. Value must be greater than or equal to 1. [type=value_error, input_value={'fully_qualified_name': ..._failed_rows_number': 0}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/value_error""" == str(
        ex_info.value
    )
