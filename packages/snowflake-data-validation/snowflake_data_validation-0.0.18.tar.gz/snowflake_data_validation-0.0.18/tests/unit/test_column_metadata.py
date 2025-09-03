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
from snowflake.snowflake_data_validation.utils.constants import (
    CHARACTER_LENGTH_KEY,
    PRECISION_KEY,
    SCALE_KEY,
)
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)


def test_column_metadata_generation():
    column_metadata = ColumnMetadata(
        name="test_column",
        data_type="VARCHAR",
        nullable=True,
        is_primary_key=False,
        calculated_column_size_in_bytes=256,
        properties={CHARACTER_LENGTH_KEY: 255, PRECISION_KEY: 38, SCALE_KEY: 0},
    )

    assert column_metadata.name == "test_column"
    assert column_metadata.data_type == "VARCHAR"
    assert column_metadata.nullable is True
    assert column_metadata.is_primary_key is False
    assert column_metadata.calculated_column_size_in_bytes == 256

    expected_properties = {CHARACTER_LENGTH_KEY: 255, PRECISION_KEY: 38, SCALE_KEY: 0}

    diff = DeepDiff(
        column_metadata.properties,
        expected_properties,
        ignore_order=True,
    )

    assert diff == {}


def test_copy():
    column_metadata = ColumnMetadata(
        name="test_column",
        data_type="VARCHAR",
        nullable=True,
        is_primary_key=False,
        calculated_column_size_in_bytes=256,
        properties={CHARACTER_LENGTH_KEY: 255, PRECISION_KEY: 38, SCALE_KEY: 0},
    )

    copied_metadata = column_metadata.copy()

    assert copied_metadata.name == column_metadata.name
    assert copied_metadata.data_type == column_metadata.data_type
    assert copied_metadata.nullable == column_metadata.nullable
    assert copied_metadata.is_primary_key == column_metadata.is_primary_key
    assert (
        copied_metadata.calculated_column_size_in_bytes
        == column_metadata.calculated_column_size_in_bytes
    )
    assert copied_metadata.properties == column_metadata.properties


def test_to_upper_name():
    column_metadata = ColumnMetadata(
        name="test_column",
        data_type="VARCHAR",
        nullable=True,
        is_primary_key=False,
        calculated_column_size_in_bytes=256,
        properties={CHARACTER_LENGTH_KEY: 255, PRECISION_KEY: 38, SCALE_KEY: 0},
    )

    column_metadata.to_upper_name()

    assert column_metadata.name == "TEST_COLUMN"
