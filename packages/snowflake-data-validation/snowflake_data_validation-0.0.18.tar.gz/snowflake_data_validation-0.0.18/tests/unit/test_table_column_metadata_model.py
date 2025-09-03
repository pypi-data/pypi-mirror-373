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


from deepdiff import DeepDiff
import pandas as pd
from snowflake.snowflake_data_validation.utils.constants import (
    SCHEMA_NAME_KEY,
    TABLE_NAME_KEY,
    COLUMN_NAME_KEY,
    DATA_TYPE_KEY,
    NULLABLE_KEY,
    IS_PRIMARY_KEY_KEY,
    CALCULATED_COLUMN_SIZE_IN_BYTES_KEY,
    CHARACTER_LENGTH_KEY,
    PRECISION_KEY,
    SCALE_KEY,
    DATABASE_NAME_KEY,
    ROW_COUNT_KEY,
)
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.table_column_metadata import (
    TableColumnMetadata,
)


def test_table_column_metadata_generation_empty_df():
    pd_df = pd.DataFrame()
    table_column_metadata = TableColumnMetadata(pd_df, column_selection_list=[])

    assert table_column_metadata.database_name == ""
    assert table_column_metadata.schema_name == ""
    assert table_column_metadata.table_name == ""
    assert len(table_column_metadata.columns) == 0


def test_table_column_metadata_generation():
    column_name_list = [
        DATABASE_NAME_KEY,
        SCHEMA_NAME_KEY,
        TABLE_NAME_KEY,
        COLUMN_NAME_KEY,
        NULLABLE_KEY,
        DATA_TYPE_KEY,
        IS_PRIMARY_KEY_KEY,
        CHARACTER_LENGTH_KEY,
        PRECISION_KEY,
        SCALE_KEY,
        CALCULATED_COLUMN_SIZE_IN_BYTES_KEY,
        ROW_COUNT_KEY,
    ]

    column_data_list = [
        [
            "inv",
            "dbo",
            "Employees",
            "EmployeeID",
            False,
            "INT",
            True,
            None,
            10,
            0,
            4,
            18,
        ],
        [
            "inv",
            "dbo",
            "Employees",
            "FirstName",
            False,
            "NVARCHAR",
            False,
            50,
            None,
            None,
            100,
            0,
        ],
        [
            "inv",
            "dbo",
            "Employees",
            "BirthDate",
            False,
            "DATE",
            False,
            None,
            10,
            0,
            3,
            0,
        ],
        [
            "inv",
            "dbo",
            "Employees",
            "Salary",
            False,
            "DECIMAL",
            False,
            None,
            10,
            2,
            9,
            0,
        ],
        ["inv", "dbo", "Employees", "IsActive", True, "BIT", False, None, 1, 0, 1, 0],
    ]

    pd_df = pd.DataFrame(column_data_list, columns=column_name_list)
    table_column_metadata = TableColumnMetadata(pd_df, column_selection_list=[])

    assert table_column_metadata.database_name == "inv"
    assert table_column_metadata.schema_name == "dbo"
    assert table_column_metadata.table_name == "Employees"
    assert len(table_column_metadata.columns) == 5

    _validate_column_metadata(
        table_column_metadata.columns[0],
        "EmployeeID",
        False,
        "INT",
        True,
        4,
        {PRECISION_KEY: 10.0, SCALE_KEY: 0.0},
    )

    _validate_column_metadata(
        table_column_metadata.columns[1],
        "FirstName",
        False,
        "NVARCHAR",
        False,
        100,
        {CHARACTER_LENGTH_KEY: 50.0},
    )

    _validate_column_metadata(
        table_column_metadata.columns[2],
        "BirthDate",
        False,
        "DATE",
        False,
        3,
        {PRECISION_KEY: 10.0, SCALE_KEY: 0.0},
    )

    _validate_column_metadata(
        table_column_metadata.columns[3],
        "Salary",
        False,
        "DECIMAL",
        False,
        9,
        {PRECISION_KEY: 10.0, SCALE_KEY: 2.0},
    )

    _validate_column_metadata(
        table_column_metadata.columns[4],
        "IsActive",
        True,
        "BIT",
        False,
        1,
        {PRECISION_KEY: 1.0, SCALE_KEY: 0.0},
    )


def test_get_properties():
    from snowflake.snowflake_data_validation.utils.model import table_column_metadata

    row_dict = {PRECISION_KEY: 10.0, SCALE_KEY: 2.0, CHARACTER_LENGTH_KEY: None}
    properties = table_column_metadata._get_properties(row_dict)

    expected_properties = {PRECISION_KEY: 10.0, SCALE_KEY: 2.0}

    diff = DeepDiff(
        expected_properties,
        properties,
        ignore_order=True,
    )

    assert diff == {}


def _validate_column_metadata(
    source_column_metadata: ColumnMetadata,
    expected_name: str,
    expected_nullable: bool,
    expected_data_type: str,
    expected_is_primary_key: bool,
    expected_calculated_column_size_in_bytes: int,
    expected_properties: dict[str, any],
):

    assert source_column_metadata.name == expected_name
    assert source_column_metadata.nullable is expected_nullable
    assert source_column_metadata.data_type == expected_data_type
    assert source_column_metadata.is_primary_key is expected_is_primary_key
    assert (
        source_column_metadata.calculated_column_size_in_bytes
        is expected_calculated_column_size_in_bytes
    )

    diff = DeepDiff(
        expected_properties,
        source_column_metadata.properties,
        ignore_order=True,
    )

    assert diff == {}
