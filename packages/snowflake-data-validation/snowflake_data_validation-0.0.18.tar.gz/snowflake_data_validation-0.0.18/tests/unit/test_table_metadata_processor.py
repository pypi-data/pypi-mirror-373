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

import logging
from unittest.mock import MagicMock

from snowflake.snowflake_data_validation.orchestration.table_metadata_processor import (
    TableMetadataProcessor,
)

from snowflake.snowflake_data_validation.utils.constants import Platform


class TestTableMetadataProcessor:
    """Test class for TableMetadataProcessor."""

    def setup_method(self):
        self.processor = TableMetadataProcessor()
        
        self.mock_context = MagicMock()
        self.mock_context.source_platform = Platform.REDSHIFT
        self.mock_context.target_platform = Platform.SNOWFLAKE
        self.mock_context.output_handler = MagicMock()
        
        self.processor.context = self.mock_context

    def test_map_column_datatype_with_existing_mapping(self):
        column_datatype = "VARCHAR"
        datatypes_mappings = {
            "VARCHAR": "STRING",
            "INTEGER": "NUMBER"
        }
        column_name = "test_column"
        
        result = self.processor._map_column_datatype(
            column_datatype, datatypes_mappings, column_name
        )
        
        assert result == "STRING"
        self.mock_context.output_handler.handle_message.assert_not_called()

    def test_map_column_datatype_with_missing_mapping(self, caplog):
        
        caplog.set_level(logging.WARNING)
        column_datatype = "CUSTOM_TYPE"
        datatypes_mappings = {
            "VARCHAR": "STRING",
            "INTEGER": "NUMBER"
        }
        column_name = "custom_column"
        
        result = self.processor._map_column_datatype(
            column_datatype,
            datatypes_mappings,
            column_name
        )
        
        assert result == column_datatype
        
        assert "Datatype CUSTOM_TYPE not found in datatypes mappings." in caplog.text
        assert "Column: custom_column will be skipped." in caplog.text
        assert "Please define it in the redshift_datatypes_mapping_template.yaml file." in caplog.text
        self.mock_context.output_handler.handle_message.assert_called_once()