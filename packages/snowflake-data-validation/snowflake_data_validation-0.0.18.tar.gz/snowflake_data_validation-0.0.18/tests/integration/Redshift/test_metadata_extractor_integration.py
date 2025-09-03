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

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift import (
    MetadataExtractorRedshift,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.query.query_generator_base import QueryGeneratorBase
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import COLUMN_VALIDATED, Platform
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class TestMetadataExtractorRedshiftIntegration:

    def setup_method(self):
        self.mock_connector = Mock(spec=ConnectorBase)
        self.mock_query_generator = Mock(spec=QueryGeneratorBase)
        self.report_path = "/test/reports"
        
        with patch('snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift.LOGGER'):
            self.extractor = MetadataExtractorRedshift(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path=self.report_path,
            )  

    def test_init_integration(self):
        with patch('snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift.LOGGER') as mock_logger:
            extractor = MetadataExtractorRedshift(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path=self.report_path,
            )
            
            assert extractor is not None
            assert extractor.connector == self.mock_connector
            assert extractor.query_generator == self.mock_query_generator
            assert extractor.report_path == self.report_path
            assert extractor.platform == Platform.REDSHIFT
            assert hasattr(extractor, 'helper_dataframe')
            
            mock_logger.debug.assert_any_call("Initializing MetadataExtractorRedshift")
            mock_logger.debug.assert_any_call("MetadataExtractorRedshift initialized successfully")

    def test_init_with_empty_report_path(self):
        with patch('snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift.LOGGER'):
            extractor = MetadataExtractorRedshift(
                connector=self.mock_connector,
                query_generator=self.mock_query_generator,
                report_path="",
            )
            
            assert extractor.report_path == ""
            assert extractor.platform == Platform.REDSHIFT

    def _create_mock_output_handler(self):
        mock_handler = Mock(spec=OutputHandlerBase)
        mock_handler.handle_message = Mock()
        return mock_handler

    def test_process_schema_query_result_integration(self):
        mock_output_handler = self._create_mock_output_handler()
        
        columns_names = ("TABLE_NAME", "COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "COLUMN_DEFAULT")
        metadata_info = [
            ("users", "id", "integer", "NO", None),
            ("users", "username", "character varying", "NO", None),
            ("users", "email", "character varying", "YES", None),
            ("users", "created_at", "timestamp without time zone", "NO", "now()"),
            ("orders", "order_id", "bigint", "NO", None),
            ("orders", "user_id", "integer", "YES", None),
            ("orders", "amount", "numeric", "NO", "0.00"),
        ]
        
        result = [columns_names, metadata_info]
        
        df = self.extractor.process_schema_query_result(result, mock_output_handler)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 7
        expected_columns = ["TABLE_NAME", "COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "COLUMN_DEFAULT"]
        assert list(df.columns) == expected_columns
        
        actual_dict = df.to_dict('records')
        expected_dict = [
            {"TABLE_NAME": "orders", "COLUMN_NAME": "amount", "DATA_TYPE": "numeric", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": "0.00"},
            {"TABLE_NAME": "orders", "COLUMN_NAME": "order_id", "DATA_TYPE": "bigint", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "orders", "COLUMN_NAME": "user_id", "DATA_TYPE": "integer", "IS_NULLABLE": "YES", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "users", "COLUMN_NAME": "created_at", "DATA_TYPE": "timestamp without time zone", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": "now()"},
            {"TABLE_NAME": "users", "COLUMN_NAME": "email", "DATA_TYPE": "character varying", "IS_NULLABLE": "YES", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "users", "COLUMN_NAME": "id", "DATA_TYPE": "integer", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": None},
            {"TABLE_NAME": "users", "COLUMN_NAME": "username", "DATA_TYPE": "character varying", "IS_NULLABLE": "NO", "COLUMN_DEFAULT": None}
        ]
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True)
        assert not diff, f"DataFrames differ: {diff}"

    def test_process_metrics_query_result_integration(self):
        mock_output_handler = self._create_mock_output_handler()
        expected_columns = [COLUMN_VALIDATED, "COUNT_METRIC", "SUM_METRIC", "AVG_METRIC", "MAX_METRIC", "MIN_METRIC"]
        result_columns = (COLUMN_VALIDATED, "COUNT_METRIC", "SUM_METRIC", "AVG_METRIC", "MAX_METRIC", "MIN_METRIC")
        result_data = [
            ("id", 1000, 500500, 500.5, 1000, 1),
            ("username", 1000, None, None, None, None),
            ("email", 950, None, None, None, None),
            ("amount", 500, 125000.50, 250.001, 999.99, 0.01),
            ("created_at", 1000, None, None, "2025-01-15 10:30:00", "2023-01-01 00:00:00"),
        ]
        
        result = [result_columns, result_data]
        
        df = self.extractor.process_metrics_query_result(result, mock_output_handler)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert list(df.columns) == expected_columns
        
        actual_dict = df.to_dict('records')
        expected_dict = [
            {COLUMN_VALIDATED: "AMOUNT", "COUNT_METRIC": 500, "SUM_METRIC": 125000.50, "AVG_METRIC": 250.001, "MAX_METRIC": 999.99, "MIN_METRIC": 0.01},
            {COLUMN_VALIDATED: "CREATED_AT", "COUNT_METRIC": 1000, "SUM_METRIC": np.nan, "AVG_METRIC": np.nan, "MAX_METRIC": "2025-01-15 10:30:00", "MIN_METRIC": "2023-01-01 00:00:00"},
            {COLUMN_VALIDATED: "EMAIL", "COUNT_METRIC": 950, "SUM_METRIC": np.nan, "AVG_METRIC": np.nan, "MAX_METRIC": None, "MIN_METRIC": None},
            {COLUMN_VALIDATED: "ID", "COUNT_METRIC": 1000, "SUM_METRIC": 500500, "AVG_METRIC": 500.5, "MAX_METRIC": 1000, "MIN_METRIC": 1},
            {COLUMN_VALIDATED: "USERNAME", "COUNT_METRIC": 1000, "SUM_METRIC": np.nan, "AVG_METRIC": np.nan, "MAX_METRIC": None, "MIN_METRIC": None}
        ]
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True, ignore_nan_inequality=True)
        assert not diff, f"DataFrames differ: {diff}"
        
    def test_process_table_column_metadata_result_integration(self):
        mock_output_handler = self._create_mock_output_handler()
        
        result_columns = ("COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "CHARACTER_MAXIMUM_LENGTH", "NUMERIC_PRECISION", "NUMERIC_SCALE")
        result_data = [
            ("id", "integer", "NO", None, 32, 0),
            ("username", "character varying", "NO", 255, None, None),
            ("email", "character varying", "YES", 320, None, None),
            ("balance", "numeric", "NO", None, 10, 2),
            ("is_active", "boolean", "NO", None, None, None),
            ("created_at", "timestamp without time zone", "NO", None, None, None),
        ]
        
        result = [result_columns, result_data]
        
        df = self.extractor.process_table_column_metadata_result(result, mock_output_handler)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6
        expected_columns = ["COLUMN_NAME", "DATA_TYPE", "IS_NULLABLE", "CHARACTER_MAXIMUM_LENGTH", "NUMERIC_PRECISION", "NUMERIC_SCALE"]
        assert list(df.columns) == expected_columns
        
        actual_dict = df.to_dict('records')
        expected_dict = [
            {"COLUMN_NAME": "id", "DATA_TYPE": "integer", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": 32.0, "NUMERIC_SCALE": 0.0},
            {"COLUMN_NAME": "username", "DATA_TYPE": "character varying", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": 255.0, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan},
            {"COLUMN_NAME": "email", "DATA_TYPE": "character varying", "IS_NULLABLE": "YES", "CHARACTER_MAXIMUM_LENGTH": 320.0, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan},
            {"COLUMN_NAME": "balance", "DATA_TYPE": "numeric", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": 10.0, "NUMERIC_SCALE": 2.0},
            {"COLUMN_NAME": "is_active", "DATA_TYPE": "boolean", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan},
            {"COLUMN_NAME": "created_at", "DATA_TYPE": "timestamp without time zone", "IS_NULLABLE": "NO", "CHARACTER_MAXIMUM_LENGTH": np.nan, "NUMERIC_PRECISION": np.nan, "NUMERIC_SCALE": np.nan}
        ]
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_nan_inequality=True)
        assert not diff, f"DataFrames differ: {diff}"

    def test_create_table_chunks_md5_integration(self):
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.normalized_fully_qualified_name = "test_users"
        mock_table_context.platform = Platform.REDSHIFT
        mock_table_context.database_name = "testdb"
        mock_table_context.schema_name = "public"
        
        expected_ddl = "CREATE TABLE IF NOT EXISTS CHUNKS_MD5_test_users (CHUNK_ID VARCHAR(255), CHUNK_MD5_VALUE VARCHAR(32));"
        self.mock_query_generator.generate_statement_table_chunks_md5.return_value = expected_ddl
        
        self.extractor.create_table_chunks_md5(mock_table_context)
        
        self.mock_query_generator.generate_statement_table_chunks_md5.assert_called_once_with(
            table_context=mock_table_context
        )
        
        self.mock_connector.execute_statement.assert_called_once_with(expected_ddl)

    def test_compute_md5_integration(self):
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.fully_qualified_name = "testdb.public.users"
        other_table_name = "snowflake_users"
        
        expected_queries = [
            "CREATE TEMPORARY TABLE IF NOT EXISTS ROW_CONCATENATED_chunk1 (user_id_IDX BIGINT, ROW_CONCAT_VALUES VARCHAR(MAX));",
            "INSERT INTO ROW_CONCATENATED_chunk1 SELECT user_id_IDX, CAST(username || email AS VARCHAR(MAX)) FROM (SELECT user_id AS user_id_IDX, username, email FROM testdb.public.users ORDER BY user_id_IDX LIMIT 1000 OFFSET 0) AS RW;",
            "CREATE TEMPORARY TABLE IF NOT EXISTS ROW_MD5_chunk1 (user_id BIGINT, ROW_MD5 VARCHAR(MAX));",
            "INSERT INTO ROW_MD5_chunk1 SELECT user_id_IDX, UPPER(MD5(ROW_CONCAT_VALUES)) FROM ROW_CONCATENATED_chunk1 ORDER BY user_id_IDX;",
            "INSERT INTO CHUNKS_MD5_testdb_public_users SELECT 'chunk1', UPPER(MD5(LISTAGG(CAST(ROW_MD5 AS VARCHAR(MAX)), '') WITHIN GROUP (ORDER BY user_id))) FROM ROW_MD5_chunk1;"
        ]
        
        self.mock_query_generator.generate_compute_md5_query.return_value = expected_queries
        
        self.extractor.compute_md5(mock_table_context, other_table_name)
        
        self.mock_query_generator.generate_compute_md5_query.assert_called_once_with(
            table_context=mock_table_context,
            other_table_name=other_table_name
        )
        
        assert self.mock_connector.execute_query_no_return.call_count == 5
        for i, expected_query in enumerate(expected_queries):
            actual_call = self.mock_connector.execute_query_no_return.call_args_list[i]
            assert actual_call[0][0] == expected_query

    def test_extract_chunks_md5_integration(self):
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.normalized_fully_qualified_name = "testdb_public_orders"
        
        expected_query = "SELECT CHUNK_ID, CHUNK_MD5_VALUE FROM CHUNKS_MD5_testdb_public_orders ORDER BY CHUNK_ID;"
        self.mock_query_generator.generate_extract_chunks_md5_query.return_value = expected_query
        
        result_columns = ("CHUNK_ID", "CHUNK_MD5_VALUE")
        result_data = [
            ("chunk_001", "a1b2c3d4e5f6789012345678901234ab"),
            ("chunk_002", "b2c3d4e5f6789012345678901234abc1"),
            ("chunk_003", "c3d4e5f6789012345678901234abc12d"),
        ]
        self.mock_connector.execute_query.return_value = (result_columns, result_data)
        
        result_df = self.extractor.extract_chunks_md5(mock_table_context)
        
        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 3
        assert list(result_df.columns) == ["CHUNK_ID", "CHUNK_MD5_VALUE"]
        
        expected_dict = [
            {"CHUNK_ID": "chunk_001", "CHUNK_MD5_VALUE": "a1b2c3d4e5f6789012345678901234ab"},
            {"CHUNK_ID": "chunk_002", "CHUNK_MD5_VALUE": "b2c3d4e5f6789012345678901234abc1"},
            {"CHUNK_ID": "chunk_003", "CHUNK_MD5_VALUE": "c3d4e5f6789012345678901234abc12d"}
        ]
        actual_dict = result_df.to_dict('records')
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True)
        assert not diff, f"DataFrames differ: {diff}"

    def test_extract_md5_rows_chunk_integration(self):
        chunk_id = "chunk_test_001"
        mock_table_context = Mock(spec=TableContext)
        mock_table_context.index_column_collection = [
            Mock(name="order_id", data_type="BIGINT"),
            Mock(name="created_date", data_type="DATE")
        ]
        mock_table_context.database_name = "ecommerce"
        mock_table_context.schema_name = "sales"
        
        expected_query = f"SELECT order_id, created_date, ROW_MD5 FROM ecommerce.sales.ROW_MD5_{chunk_id} ORDER BY order_id, created_date;"
        self.mock_query_generator.generate_extract_md5_rows_chunk_query.return_value = expected_query
        
        result_columns = ("order_id", "created_date", "ROW_MD5")
        result_data = [
            (1001, "2024-01-15", "d1e2f3a4b5c6789012345678901234ef"),
            (1002, "2024-01-15", "e2f3a4b5c6789012345678901234efab"),
            (1003, "2024-01-16", "f3a4b5c6789012345678901234efabcd"),
            (1004, "2024-01-16", "a4b5c6789012345678901234efabcdef"),
        ]
        self.mock_connector.execute_query.return_value = (result_columns, result_data)
        
        result_df = self.extractor.extract_md5_rows_chunk(chunk_id, mock_table_context)
        
        self.mock_query_generator.generate_extract_md5_rows_chunk_query.assert_called_once_with(
            chunk_id=chunk_id,
            table_context=mock_table_context
        )

        assert isinstance(result_df, pd.DataFrame)
        assert len(result_df) == 4
        assert list(result_df.columns) == ["ORDER_ID", "CREATED_DATE", "ROW_MD5"]
        
        expected_dict = [
            {"ORDER_ID": 1001, "CREATED_DATE": "2024-01-15", "ROW_MD5": "d1e2f3a4b5c6789012345678901234ef"},
            {"ORDER_ID": 1002, "CREATED_DATE": "2024-01-15", "ROW_MD5": "e2f3a4b5c6789012345678901234efab"},
            {"ORDER_ID": 1003, "CREATED_DATE": "2024-01-16", "ROW_MD5": "f3a4b5c6789012345678901234efabcd"},
            {"ORDER_ID": 1004, "CREATED_DATE": "2024-01-16", "ROW_MD5": "a4b5c6789012345678901234efabcdef"}
        ]
        actual_dict = result_df.to_dict('records')
        
        diff = DeepDiff(expected_dict, actual_dict, ignore_order=True)
        assert not diff, f"DataFrames differ: {diff}"