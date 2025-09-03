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

from pathlib import Path

import pytest
from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton


@pytest.fixture(autouse=True)
def singleton():
    Singleton._instances = {}


ASSETS_DIRECTORY_NAME = "assets"
TEST_CONFIGURATION_LOADER_DIRECTORY_NAME = "test_configuration_loader"


def test_load_configuration_model():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_CONFIGURATION_LOADER_DIRECTORY_NAME)
        .joinpath("test_load_configuration_model")
        .joinpath("conf.yaml")
    )

    configuration_loader = ConfigurationLoader(configuration_file_path)
    configuration_model = configuration_loader.get_configuration_model()

    model_dict = configuration_model.model_dump()
    expected_model_dict = {
        "comparison_configuration": {
            "tolerance": 0.01,
            "type_mapping_file_path": "/dir1/file.yaml",
        },
        "database_mappings": {"example_database_2": "tgt_example_database"},
        "max_threads": "auto",
        "output_directory_path": "/test/reports",
        "schema_mappings": {"example_schema_2": "tgt_example_schema"},
        "source_connection": None,
        "source_platform": "SQL server",
        "source_validation_files_path": None,
        "tables": [
            {
                "chunk_number": 5,
                "column_mappings": {"SOURCE_COLUMN_1": "TARGET_COLUMN_2"},
                "column_selection_list": [
                    "excluded_column_example_1",
                    "excluded_column_example_2",
                ],
                "exclude_metrics": True,
                "fully_qualified_name": "example_database.example_schema.table_1",
                "has_target_where_clause": False,
                "has_where_clause": False,
                "id": 1,
                "index_column_list": ["index_column_1", "index_column_2"],
                "is_case_sensitive": False,
                "max_failed_rows_number": 10,
                "source_database": "example_database",
                "source_schema": "example_schema",
                "source_table": "table_1",
                "target_database": "example_database",
                "target_fully_qualified_name": "example_database.example_schema.table_1",
                "target_index_column_list": ["index_column_1", "index_column_2"],
                "target_name": "table_1",
                "target_schema": "example_schema",
                "target_where_clause": "",
                "use_column_selection_as_exclude_list": True,
                "validation_configuration": None,
                "where_clause": "",
            },
            {
                "chunk_number": 0,
                "column_mappings": {},
                "column_selection_list": [],
                "exclude_metrics": True,
                "fully_qualified_name": "example_database.example_schema.table_2",
                "has_target_where_clause": True,
                "has_where_clause": True,
                "id": 2,
                "index_column_list": [],
                "is_case_sensitive": False,
                "max_failed_rows_number": 5,
                "source_database": "example_database",
                "source_schema": "example_schema",
                "source_table": "table_2",
                "target_database": "example_database",
                "target_fully_qualified_name": "example_database.example_schema.table_2",
                "target_index_column_list": [],
                "target_name": "table_2",
                "target_schema": "example_schema",
                "target_where_clause": "ProductID != 5",
                "use_column_selection_as_exclude_list": False,
                "validation_configuration": None,
                "where_clause": "ProductID <= 45",
            },
            {
                "chunk_number": 0,
                "column_mappings": {},
                "column_selection_list": [],
                "exclude_metrics": False,
                "fully_qualified_name": "example_database_2.example_schema_2.table_3",
                "has_target_where_clause": False,
                "has_where_clause": False,
                "id": 3,
                "index_column_list": [],
                "is_case_sensitive": False,
                "max_failed_rows_number": 50,
                "source_database": "example_database_2",
                "source_schema": "example_schema_2",
                "source_table": "table_3",
                "target_database": "tgt_example_database",
                "target_fully_qualified_name": "tgt_example_database.tgt_example_schema.tgt_example_table",
                "target_index_column_list": [],
                "target_name": "tgt_example_table",
                "target_schema": "tgt_example_schema",
                "target_where_clause": "",
                "use_column_selection_as_exclude_list": False,
                "validation_configuration": None,
                "where_clause": "",
            },
            {
                "chunk_number": 0,
                "column_mappings": {},
                "column_selection_list": [],
                "exclude_metrics": False,
                "fully_qualified_name": "example_database.example_schema.table_4",
                "has_target_where_clause": False,
                "has_where_clause": False,
                "id": 4,
                "index_column_list": [],
                "is_case_sensitive": False,
                "max_failed_rows_number": 50,
                "source_database": "example_database",
                "source_schema": "example_schema",
                "source_table": "table_4",
                "target_database": "example_database",
                "target_fully_qualified_name": "example_database.example_schema.table_4",
                "target_index_column_list": [],
                "target_name": "table_4",
                "target_schema": "example_schema",
                "target_where_clause": "",
                "use_column_selection_as_exclude_list": False,
                "validation_configuration": {
                    "exclude_metrics": False,
                    "custom_templates_path": None,
                    "max_failed_rows_number": 100,
                    "metrics_validation": False,
                    "row_validation": False,
                    "schema_validation": True,
                },
                "where_clause": "",
            },
        ],
        "target_connection": None,
        "target_database": "data1",
        "target_platform": "Snowflake",
        "target_validation_files_path": None,
        "validation_configuration": {
            "exclude_metrics": False,
            "custom_templates_path": None,
            "max_failed_rows_number": 50,
            "metrics_validation": True,
            "row_validation": False,
            "schema_validation": True,
        },
    }

    diff = DeepDiff(
        model_dict,
        expected_model_dict,
        ignore_order=False,
    )

    assert diff == {}


def test_load_configuration_model_file_not_found_exception():
    configuration_file_path = (
        Path(__file__).parent.joinpath(ASSETS_DIRECTORY_NAME).joinpath("conf.yaml")
    )

    with (pytest.raises(FileNotFoundError) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert str(ex_info.value).startswith("Configuration file not found in")


def test_load_configuration_model_not_valid_name_exception():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_CONFIGURATION_LOADER_DIRECTORY_NAME)
        .joinpath("data_validation.xml")
    )

    with (pytest.raises(Exception) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert "The configuration file must have a .yaml or .yml extension" == str(
        ex_info.value
    )


def test_load_configuration_model_reading_file_exception():
    configuration_file_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_CONFIGURATION_LOADER_DIRECTORY_NAME)
        .joinpath("test_load_configuration_model_reading_file_exception")
        .joinpath("conf.yaml")
    )

    with (pytest.raises(Exception) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert r"""An error occurred while loading the configuration file:
3 validation errors for ConfigurationModel
source_platform
  Input should be a valid string [type=string_type, input_value=3045, input_type=int]
    For further information visit https://errors.pydantic.dev/2.11/v/string_type
target_platform
  Field required [type=missing, input_value={'source_platform': 3045,...ndex_column_list': []}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing
output_directory_path
  Field required [type=missing, input_value={'source_platform': 3045,...ndex_column_list': []}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.11/v/missing""" == str(
        ex_info.value
    )


def test_load_configuration_model_path_file_is_none_exception():
    configuration_file_path: Path = None

    with (pytest.raises(ValueError) as ex_info):
        ConfigurationLoader(configuration_file_path)

    assert "The configuration file path cannot be None value" == str(ex_info.value)
