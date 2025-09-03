from pathlib import Path

import pytest
from deepdiff import DeepDiff
from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.configuration.model.validation_configuration import (
    ValidationConfiguration,
)
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_THREAD_COUNT_OPTION,
    MAX_FAILED_ROWS_NUMBER_DEFAULT_VALUE,
    SCHEMA_VALIDATION_KEY,
    METRICS_VALIDATION_KEY,
    ROW_VALIDATION_KEY,
    TOLERANCE_KEY,
    TYPE_MAPPING_FILE_PATH_KEY,
)

VALIDATION_CONFIGURATION = {
    SCHEMA_VALIDATION_KEY: True,
    METRICS_VALIDATION_KEY: True,
    ROW_VALIDATION_KEY: False,
}

COMPARISON_CONFIGURATION = {
    TOLERANCE_KEY: 1.23,
    TYPE_MAPPING_FILE_PATH_KEY: "/dir1/file.yaml",
}

SQL_SERVER_SOURCE_PLATFORM = "SQL server"
SNOWFLAKE_TARGET_PLATFORM = "Snowflake"
OUTPUT_DIRECTORY_PATH = "/test/reports"


@pytest.fixture(autouse=True)
def table_id_counter():
    TableConfiguration._id_counter = 0


def test_configuration_model_generation_default_values():
    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
    )

    model_dict = configuration_model.model_dump()
    expected_model_dict = {
        "comparison_configuration": None,
        "database_mappings": {},
        "output_directory_path": "/test/reports",
        "max_threads": DEFAULT_THREAD_COUNT_OPTION,
        "schema_mappings": {},
        "source_connection": None,
        "source_platform": "SQL server",
        "source_validation_files_path": None,
        "target_database": None,
        "tables": [],
        "target_connection": None,
        "target_platform": "Snowflake",
        "target_validation_files_path": None,
        "validation_configuration": {
            "custom_templates_path": None,
            "metrics_validation": True,
            "row_validation": True,
            "schema_validation": True,
            "max_failed_rows_number": 100,
            "exclude_metrics": False,
        },
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_configuration_model_generation_custom_values():
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        target_database="tgt_example_database",
        target_schema="tgt_example_schema",
        target_name="tgt_example_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["excluded_column_1"],
        chunk_number=6,
        column_mappings={"column_1": "column_2"},
        max_failed_rows_number=10,
    )

    default_validation_configuration = ValidationConfiguration(
        schema_validation=True,
        metrics_validation=True,
        row_validation=True,
        custom_templates_path=Path("dir1/file1.yaml"),
        max_failed_rows_number=5,
        exclude_metrics=False,
    )

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        max_threads=4,
        validation_configuration=default_validation_configuration,
        comparison_configuration=COMPARISON_CONFIGURATION,
        database_mappings={"db1": "t_db2"},
        schema_mappings={"shm1": "t_shm2"},
        source_validation_files_path="/dir1/dir2",
        target_validation_files_path="/dir1/dir2",
        tables=[table_configuration],
    )

    model_dict = configuration_model.model_dump()
    expected_model_dict = {
        "comparison_configuration": {
            "tolerance": 1.23,
            "type_mapping_file_path": "/dir1/file.yaml",
        },
        "database_mappings": {"db1": "t_db2"},
        "max_threads": 4,
        "output_directory_path": "/test/reports",
        "schema_mappings": {"shm1": "t_shm2"},
        "source_connection": None,
        "source_platform": "SQL server",
        "source_validation_files_path": "/dir1/dir2",
        "tables": [
            {
                "chunk_number": 6,
                "column_mappings": {"COLUMN_1": "COLUMN_2"},
                "column_selection_list": ["excluded_column_1", "excluded_column_2"],
                "exclude_metrics": False,
                "fully_qualified_name": "ex_database.ex_schema.ex_table",
                "has_target_where_clause": False,
                "has_where_clause": False,
                "id": 1,
                "index_column_list": ["excluded_column_1"],
                "is_case_sensitive": False,
                "max_failed_rows_number": 10,
                "source_database": "ex_database",
                "source_schema": "ex_schema",
                "source_table": "ex_table",
                "target_database": "tgt_example_database",
                "target_fully_qualified_name": "tgt_example_database.tgt_example_schema.tgt_example_table",
                "target_index_column_list": ["excluded_column_1", "excluded_column_1"],
                "target_name": "tgt_example_table",
                "target_schema": "tgt_example_schema",
                "target_where_clause": "",
                "use_column_selection_as_exclude_list": True,
                "validation_configuration": None,
                "where_clause": "",
            }
        ],
        "target_connection": None,
        "target_database": None,
        "target_platform": "Snowflake",
        "target_validation_files_path": "/dir1/dir2",
        "validation_configuration": {
            "exclude_metrics": False,
            "custom_templates_path": Path("dir1/file1.yaml"),
            "max_failed_rows_number": 5,
            "metrics_validation": True,
            "row_validation": True,
            "schema_validation": True,
        },
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_configuration_model_generation_pydantic_default_values():
    file_content = f"""source_platform: {SQL_SERVER_SOURCE_PLATFORM}
target_platform: {SNOWFLAKE_TARGET_PLATFORM}
output_directory_path: {OUTPUT_DIRECTORY_PATH}"""

    configuration_model = parse_yaml_raw_as(ConfigurationModel, file_content)

    model_dict = configuration_model.model_dump()
    expected_model_dict = {
        "comparison_configuration": None,
        "database_mappings": {},
        "output_directory_path": "/test/reports",
        "max_threads": DEFAULT_THREAD_COUNT_OPTION,
        "schema_mappings": {},
        "source_connection": None,
        "source_platform": "SQL server",
        "source_validation_files_path": None,
        "target_database": None,
        "tables": [],
        "target_connection": None,
        "target_platform": "Snowflake",
        "target_validation_files_path": None,
        "validation_configuration": {
            "exclude_metrics": False,
            "custom_templates_path": None,
            "metrics_validation": True,
            "row_validation": True,
            "schema_validation": True,
            "max_failed_rows_number": MAX_FAILED_ROWS_NUMBER_DEFAULT_VALUE,
        },
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_configuration_model_generation_pydantic_custom_values():
    file_content = r"""source_platform: SQL server
target_platform: Snowflake
output_directory_path: /test/reports
max_threads: 4
source_validation_files_path: /dir1/dir2
target_validation_files_path: /dir1/dir2
database_mappings:
    db1: t_db2
schema_mappings:
    shm1: t_shm2
validation_configuration:
  metrics_validation: true
  row_validation: false
  schema_validation: true
comparison_configuration:
  tolerance: 1.23
  type_mapping_file_path: /dir1/file.yaml
tables:
  - fully_qualified_name: ex_database.ex_schema.ex_table
    use_column_selection_as_exclude_list: true
    column_selection_list:
      - excluded_column_example_1
      - excluded_column_example_2
    index_column_list:
      - excluded_column_1
    chunk_number: 2
    max_failed_rows_number: 10
"""

    configuration_model = parse_yaml_raw_as(ConfigurationModel, file_content)

    model_dict = configuration_model.model_dump()
    expected_model_dict = {
        "comparison_configuration": {
            "tolerance": 1.23,
            "type_mapping_file_path": "/dir1/file.yaml",
        },
        "database_mappings": {"db1": "t_db2"},
        "output_directory_path": "/test/reports",
        "max_threads": 4,
        "schema_mappings": {"shm1": "t_shm2"},
        "source_connection": None,
        "source_platform": "SQL server",
        "source_validation_files_path": "/dir1/dir2",
        "tables": [
            {
                "chunk_number": 2,
                "column_mappings": {},
                "column_selection_list": [
                    "excluded_column_example_1",
                    "excluded_column_example_2",
                ],
                "exclude_metrics": False,
                "fully_qualified_name": "ex_database.ex_schema.ex_table",
                "has_where_clause": False,
                "has_target_where_clause": False,
                "id": 1,
                "index_column_list": ["excluded_column_1"],
                "is_case_sensitive": False,
                "source_database": "ex_database",
                "source_schema": "ex_schema",
                "source_table": "ex_table",
                "target_database": "ex_database",
                "target_fully_qualified_name": "ex_database.ex_schema.ex_table",
                "target_index_column_list": ["excluded_column_1"],
                "target_name": "ex_table",
                "target_schema": "ex_schema",
                "target_where_clause": "",
                "use_column_selection_as_exclude_list": True,
                "validation_configuration": None,
                "where_clause": "",
                "max_failed_rows_number": 10,
            }
        ],
        "target_connection": None,
        "target_database": None,
        "target_platform": "Snowflake",
        "target_validation_files_path": "/dir1/dir2",
        "validation_configuration": {
            "custom_templates_path": None,
            "metrics_validation": True,
            "row_validation": False,
            "schema_validation": True,
            "max_failed_rows_number": 100,
            "exclude_metrics": False,
        },
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_configuration_model_generation_pydantic_load_missing_fields_exception():
    file_content = r"""field: value"""

    with (pytest.raises(ValueError) as ex_info):
        parse_yaml_raw_as(ConfigurationModel, file_content)

    assert r"""3 validation errors for ConfigurationModel
source_platform
  Field required [type=missing, input_value={'field': 'value'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
target_platform
  Field required [type=missing, input_value={'field': 'value'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
output_directory_path
  Field required [type=missing, input_value={'field': 'value'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing""" == str(
        ex_info.value
    )


def test_configuration_model_with_report_path():
    """Test that ConfigurationModel correctly handles the output_directory_path field."""
    file_content = r"""source_platform: SQL server
target_platform: Snowflake
max_threads: 1
output_directory_path: /custom/output/path
validation_configuration:
  schema_validation: true
  metrics_validation: true
  row_validation: false
tables:
  - fully_qualified_name: example_database.example_schema.table_1
    use_column_selection_as_exclude_list: false
    column_selection_list: []
    index_column_list: []
    chunk_number: 3
"""

    configuration_model = parse_yaml_raw_as(ConfigurationModel, file_content)

    model_dict = configuration_model.model_dump()
    expected_model_dict = {
        "comparison_configuration": None,
        "database_mappings": {},
        "output_directory_path": "/custom/output/path",
        "max_threads": 1,
        "schema_mappings": {},
        "source_connection": None,
        "source_platform": "SQL server",
        "source_validation_files_path": None,
        "tables": [
            {
                "chunk_number": 3,
                "column_mappings": {},
                "column_selection_list": [],
                "exclude_metrics": False,
                "fully_qualified_name": "example_database.example_schema.table_1",
                "has_where_clause": False,
                "has_target_where_clause": False,
                "id": 1,
                "index_column_list": [],
                "is_case_sensitive": False,
                "source_database": "example_database",
                "source_schema": "example_schema",
                "source_table": "table_1",
                "target_database": "example_database",
                "target_fully_qualified_name": "example_database.example_schema.table_1",
                "target_index_column_list": [],
                "target_name": "table_1",
                "target_schema": "example_schema",
                "target_where_clause": "",
                "use_column_selection_as_exclude_list": False,
                "validation_configuration": None,
                "where_clause": "",
                "max_failed_rows_number": 100,
            }
        ],
        "target_connection": None,
        "target_database": None,
        "target_platform": "Snowflake",
        "target_validation_files_path": None,
        "validation_configuration": {
            "exclude_metrics": False,
            "custom_templates_path": None,
            "metrics_validation": True,
            "row_validation": False,
            "schema_validation": True,
            "max_failed_rows_number": 100,
        },
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_configuration_model_missing_output_directory_path_exception():
    """Test that ConfigurationModel raises validation error when output_directory_path is missing."""
    file_content_no_output_directory = r"""source_platform: SQL server"""

    with pytest.raises(ValueError) as ex_info:
        parse_yaml_raw_as(ConfigurationModel, file_content_no_output_directory)

    # Check that the error mentions output_directory_path is required
    assert "output_directory_path" in str(ex_info.value)
    assert "Field required" in str(ex_info.value)


def test_configuration_model_max_failed_rows_number_harmonization():

    # SCENARIO 1: default value
    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
    )

    assert (
        configuration_model.validation_configuration.max_failed_rows_number
        == MAX_FAILED_ROWS_NUMBER_DEFAULT_VALUE
    )

    # SCENARIO 2: global value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    validation_configuration = ValidationConfiguration(max_failed_rows_number=10)

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        validation_configuration=validation_configuration,
        tables=[table_configuration],
    )

    assert configuration_model.validation_configuration.max_failed_rows_number == 10
    assert configuration_model.tables[0].max_failed_rows_number == 10

    # SCENARIO 3: table value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
        max_failed_rows_number=67,
    )

    validation_configuration = ValidationConfiguration(max_failed_rows_number=10)

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        validation_configuration=validation_configuration,
        tables=[table_configuration],
    )

    assert configuration_model.validation_configuration.max_failed_rows_number == 10
    assert configuration_model.tables[0].max_failed_rows_number == 67

    # SCENARIO 4: table default value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        tables=[table_configuration],
    )

    assert configuration_model.validation_configuration.max_failed_rows_number == 100
    assert configuration_model.tables[0].max_failed_rows_number == 100

    # SCENARIO 5: table with value and table with global value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
        max_failed_rows_number=45,
    )

    table_configuration2 = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    validation_configuration = ValidationConfiguration(max_failed_rows_number=12)

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        validation_configuration=validation_configuration,
        tables=[table_configuration, table_configuration2],
    )

    assert configuration_model.validation_configuration.max_failed_rows_number == 12
    assert configuration_model.tables[0].max_failed_rows_number == 45
    assert configuration_model.tables[1].max_failed_rows_number == 12


def test_configuration_model_exclude_metrics_harmonization():
    # SCENARIO 1: default value
    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
    )

    assert configuration_model.validation_configuration.exclude_metrics is False

    # SCENARIO 2: global value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    validation_configuration = ValidationConfiguration(exclude_metrics=True)

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        validation_configuration=validation_configuration,
        tables=[table_configuration],
    )

    assert configuration_model.validation_configuration.exclude_metrics == True
    assert configuration_model.tables[0].exclude_metrics == True

    # SCENARIO 3: table value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
        exclude_metrics=True,
    )

    validation_configuration = ValidationConfiguration(exclude_metrics=False)

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        validation_configuration=validation_configuration,
        tables=[table_configuration],
    )

    assert configuration_model.validation_configuration.exclude_metrics is False
    assert configuration_model.tables[0].exclude_metrics is True

    # SCENARIO 4: table default value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        tables=[table_configuration],
    )

    assert configuration_model.validation_configuration.exclude_metrics is False
    assert configuration_model.tables[0].exclude_metrics is False

    # SCENARIO 5: table with value and table with global value
    table_configuration = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
        exclude_metrics=False,
    )

    table_configuration2 = TableConfiguration(
        fully_qualified_name="ex_database.ex_schema.ex_table",
        use_column_selection_as_exclude_list=True,
        column_selection_list=["excluded_column_1", "excluded_column_2"],
        index_column_list=["index_column_1", "index_column_2"],
    )

    validation_configuration = ValidationConfiguration(exclude_metrics=True)

    configuration_model = ConfigurationModel(
        source_platform=SQL_SERVER_SOURCE_PLATFORM,
        target_platform=SNOWFLAKE_TARGET_PLATFORM,
        output_directory_path=OUTPUT_DIRECTORY_PATH,
        validation_configuration=validation_configuration,
        tables=[table_configuration, table_configuration2],
    )

    assert configuration_model.validation_configuration.exclude_metrics == True
    assert configuration_model.tables[0].exclude_metrics is False
    assert configuration_model.tables[1].exclude_metrics is True
