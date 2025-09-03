import os
import tempfile
from unittest.mock import MagicMock

import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    Result,
    ROW_NUMBER_COLUMN_KEY,
    TABLE_NAME_KEY,
    RESULT_COLUMN_KEY,
    SOURCE_QUERY_COLUMN_KEY,
    TARGET_QUERY_COLUMN_KEY,
    Platform,
    NOT_APPLY,
)
from snowflake.snowflake_data_validation.validation.row_data_validator import (
    RowDataValidator,
    ROW_VALIDATION_REPORT_NAME,
    ROW_VALIDATION_DIFF_QUERY_NAME,
    SOURCE_SUFFIX,
    TARGET_SUFFIX,
)


def test_get_diff_md5_chunks_no_equals_scenario():
    source_df = pd.DataFrame(
        {
            "CHUNK_ID": ["CHUNK_ID_1", "CHUNK_ID_2", "CHUNK_ID_3"],
            "CHUNK_MD5_VALUE": ["MD5_1", "MD5_2", "MD5_3"],
        }
    )
    target_df = pd.DataFrame(
        {
            "CHUNK_ID": ["CHUNK_ID_1", "CHUNK_ID_2", "CHUNK_ID_3"],
            "CHUNK_MD5_VALUE": ["MD5_1", "MD5_2", "MD5_4"],
        }
    )

    row_data_validator = RowDataValidator()
    diff_chunks = row_data_validator.get_diff_md5_chunks(
        source_md5_df=source_df,
        target_md5_df=target_df,
    )

    expected_diff_chunks_df = pd.DataFrame(
        {
            "CHUNK_ID": ["CHUNK_ID_3"],
            "CHUNK_MD5_VALUE_SOURCE": ["MD5_3"],
            "CHUNK_MD5_VALUE_TARGET": ["MD5_4"],
        }
    )

    assert expected_diff_chunks_df.equals(diff_chunks) == True


def test_get_diff_md5_chunks_equals_scenario():
    source_df = pd.DataFrame(
        {
            "CHUNK_ID": ["CHUNK_ID_1", "CHUNK_ID_2", "CHUNK_ID_3"],
            "CHUNK_MD5_VALUE": ["MD5_1", "MD5_2", "MD5_3"],
        }
    )
    target_df = pd.DataFrame(
        {
            "CHUNK_ID": ["CHUNK_ID_1", "CHUNK_ID_2", "CHUNK_ID_3"],
            "CHUNK_MD5_VALUE": ["MD5_1", "MD5_2", "MD5_3"],
        }
    )

    row_data_validator = RowDataValidator()
    diff_chunks = row_data_validator.get_diff_md5_chunks(
        source_md5_df=source_df,
        target_md5_df=target_df,
    )

    assert diff_chunks.empty == True


def test_get_diff_md5_rows_chunk_no_equals_scenario():
    source_df = pd.DataFrame(
        {
            "ID_1": ["A1", "A2", "A3"],
            "ID_2": ["B1", "B2", "B3"],
            "ROW_MD5": ["MD5_1", "MD5_2", "MD5_3"],
        }
    )
    target_df = pd.DataFrame(
        {
            "IDA_1": ["A1", "A2", "A3"],
            "IDB_2": ["B1", "B2", "B3"],
            "ROW_MD5": ["MD5_1", "MD5_2", "MD5_4"],
        }
    )
    source_index_column_collection = ["ID_1", "ID_2"]
    target_index_column_collection = ["IDA_1", "IDB_2"]

    source_index_column_suffix_collection = [
        column_name + SOURCE_SUFFIX for column_name in source_index_column_collection
    ]
    target_index_column_suffix_collection = [
        column_name + TARGET_SUFFIX for column_name in target_index_column_collection
    ]

    row_data_validator = RowDataValidator()
    md5_rows_chunk_compared_df = row_data_validator.get_diff_md5_rows_chunk(
        source_md5_rows_chunk=source_df,
        target_md5_rows_chunk=target_df,
        source_index_column_collection=source_index_column_collection,
        target_index_column_collection=target_index_column_collection,
        source_index_column_suffix_collection=source_index_column_suffix_collection,
        target_index_column_suffix_collection=target_index_column_suffix_collection,
    )

    expected_md5_rows_chunk_compared_df = pd.DataFrame(
        {
            "ID_1_SOURCE": ["A3"],
            "ID_2_SOURCE": ["B3"],
            "IDA_1_TARGET": ["A3"],
            "IDB_2_TARGET": ["B3"],
            "RESULT": [Result.FAILURE.value],
        }
    ).convert_dtypes()

    assert expected_md5_rows_chunk_compared_df.equals(md5_rows_chunk_compared_df)


def test_get_diff_md5_rows_chunk_equals_scenario():
    source_df = pd.DataFrame(
        {
            "ID_1": ["A1", "A2", "A3"],
            "ID_2": ["B1", "B2", "B3"],
            "ROW_MD5": ["MD5_1", "MD5_2", "MD5_3"],
        }
    )
    target_df = pd.DataFrame(
        {
            "IDA_1": ["A1", "A2", "A3"],
            "IDB_2": ["B1", "B2", "B3"],
            "ROW_MD5": ["MD5_1", "MD5_2", "MD5_3"],
        }
    )
    source_index_column_collection = ["ID_1", "ID_2"]
    target_index_column_collection = ["IDA_1", "IDB_2"]

    source_index_column_suffix_collection = [
        column_name + SOURCE_SUFFIX for column_name in source_index_column_collection
    ]
    target_index_column_suffix_collection = [
        column_name + TARGET_SUFFIX for column_name in target_index_column_collection
    ]

    row_data_validator = RowDataValidator()
    md5_rows_chunk_compared_df = row_data_validator.get_diff_md5_rows_chunk(
        source_md5_rows_chunk=source_df,
        target_md5_rows_chunk=target_df,
        source_index_column_collection=source_index_column_collection,
        target_index_column_collection=target_index_column_collection,
        source_index_column_suffix_collection=source_index_column_suffix_collection,
        target_index_column_suffix_collection=target_index_column_suffix_collection,
    )

    assert md5_rows_chunk_compared_df.empty


def test_generate_row_validation_report():
    compared_df = pd.DataFrame(
        {
            "ID_1_SOURCE": ["A0001", "A0002", ""],
            "ID_1_TARGET": ["A0001", "A0002", "A0003"],
            "RESULT": [
                Result.FAILURE.value,
                Result.FAILURE.value,
                Result.NOT_FOUND_SOURCE.value,
            ],
        }
    )

    source_fully_qualified_name = "database.schema.source_test"
    target_fully_qualified_name = "database.schema.target_test"
    index_column_collection = ["ID_1"]

    mock_context = MagicMock()
    mock_context.get_row_number.return_value = 1
    mock_context.run_start_time = "ABC"
    mock_context.report_path = tempfile.mkdtemp()

    source_index_column_suffix_collection = [
        column_name + SOURCE_SUFFIX for column_name in index_column_collection
    ]
    target_index_column_suffix_collection = [
        column_name + TARGET_SUFFIX for column_name in index_column_collection
    ]

    row_data_validator = RowDataValidator()
    row_data_validator.generate_row_validation_report(
        compared_df=compared_df,
        fully_qualified_name=source_fully_qualified_name,
        target_fully_qualified_name=target_fully_qualified_name,
        source_index_column_suffix_collection=source_index_column_suffix_collection,
        target_index_column_suffix_collection=target_index_column_suffix_collection,
        table_id=1,
        context=mock_context,
    )

    report_name = ROW_VALIDATION_REPORT_NAME.format(
        fully_qualified_name=source_fully_qualified_name, table_id=1
    )

    report_file = os.path.join(
        mock_context.report_path, f"{mock_context.run_start_time}_{report_name}"
    )

    assert os.path.exists(report_file)

    report_df = pd.read_csv(report_file)

    source_query_column_values = [
        f"SELECT * FROM {source_fully_qualified_name} WHERE \"ID_1\" = 'A0001'",
        f"SELECT * FROM {source_fully_qualified_name} WHERE \"ID_1\" = 'A0002'",
        NOT_APPLY,
    ]

    target_query_column_values = [
        f"SELECT * FROM {target_fully_qualified_name} WHERE \"ID_1\" = 'A0001'",
        f"SELECT * FROM {target_fully_qualified_name} WHERE \"ID_1\" = 'A0002'",
        f"SELECT * FROM {target_fully_qualified_name} WHERE \"ID_1\" = 'A0003'",
    ]

    expected_report_df = pd.DataFrame(
        {
            ROW_NUMBER_COLUMN_KEY: [1, 1, 1],
            TABLE_NAME_KEY: [
                source_fully_qualified_name,
                source_fully_qualified_name,
                source_fully_qualified_name,
            ],
            RESULT_COLUMN_KEY: [
                Result.FAILURE.value,
                Result.FAILURE.value,
                Result.NOT_FOUND_SOURCE.value,
            ],
            "ID_1_SOURCE": ["A0001", "A0002", NOT_APPLY],
            "ID_1_TARGET": ["A0001", "A0002", "A0003"],
            SOURCE_QUERY_COLUMN_KEY: source_query_column_values,
            TARGET_QUERY_COLUMN_KEY: target_query_column_values,
        }
    )

    report_df = report_df.fillna(NOT_APPLY)
    assert expected_report_df.equals(report_df)


def test_generate_row_validation_queries():
    compared_df = pd.DataFrame(
        {
            "ID_1_SOURCE": ["A0001", "A0002"],
            "ID_1_TARGET": ["A0001", "A0002"],
            "RESULT": [Result.FAILURE.value, Result.FAILURE.value],
        }
    )

    source_fully_qualified_name = "database.schema.source_test"
    target_fully_qualified_name = "database.schema.target_test"

    index_column_collection = ["ID_1"]

    mock_context = MagicMock()
    mock_context.source_platform = Platform.SQLSERVER
    mock_context.target_platform = Platform.SNOWFLAKE
    mock_context.report_path = tempfile.mkdtemp()
    mock_context.run_start_time = "ABC"

    source_index_column_suffix_collection = [
        column_name + SOURCE_SUFFIX for column_name in index_column_collection
    ]
    target_index_column_suffix_collection = [
        column_name + TARGET_SUFFIX for column_name in index_column_collection
    ]

    row_data_validator = RowDataValidator()
    row_data_validator.generate_row_validation_queries(
        compared_df=compared_df,
        fully_qualified_name=source_fully_qualified_name,
        target_fully_qualified_name=target_fully_qualified_name,
        source_index_column_suffix_collection=source_index_column_suffix_collection,
        target_index_column_suffix_collection=target_index_column_suffix_collection,
        context=mock_context,
        table_id=1,
    )

    source_query_expected = """SELECT * FROM database.schema.source_test WHERE "ID_1" = 'A0001'
 OR \"ID_1\" = 'A0002'
"""
    validate_row_validation_query(
        platform=Platform.SQLSERVER,
        fully_qualified_name=source_fully_qualified_name,
        report_path=mock_context.report_path,
        run_start_time=mock_context.run_start_time,
        expected=source_query_expected,
        table_id=1,
    )

    target_query_expected = """SELECT * FROM database.schema.target_test WHERE "ID_1" = 'A0001'
 OR \"ID_1\" = 'A0002'
"""
    validate_row_validation_query(
        platform=Platform.SNOWFLAKE,
        fully_qualified_name=target_fully_qualified_name,
        report_path=mock_context.report_path,
        run_start_time=mock_context.run_start_time,
        expected=target_query_expected,
        table_id=1,
    )


def validate_row_validation_query(
    platform: Platform,
    fully_qualified_name: str,
    report_path: str,
    run_start_time: str,
    expected: str,
    table_id: int,
):
    report_name = ROW_VALIDATION_DIFF_QUERY_NAME.format(
        platform=platform,
        fully_qualified_name=fully_qualified_name,
        table_id=table_id,
    )

    report_file = os.path.join(
        report_path,
        f"{run_start_time}_{report_name}",
    )

    assert os.path.exists(report_file)

    report_file_content = open(report_file).read()

    assert report_file_content == expected


def test_generate_select_all_columns_query():
    fully_qualified_name = "database.schema.source_test"
    index_column_collection = ["ID_SOURCE"]
    row = pd.Series({"ID_SOURCE": "A1"})

    row_data_validator = RowDataValidator()
    query = row_data_validator._generate_select_all_columns_query(
        fully_qualified_name=fully_qualified_name,
        index_column_collection=index_column_collection,
        df_row=row,
        postfix=SOURCE_SUFFIX,
    )

    assert query == f"SELECT * FROM {fully_qualified_name} WHERE \"ID\" = 'A1'"


def test_generate_where_clause():
    index_column_collection = ["ID_SOURCE"]
    row = pd.Series({"ID_SOURCE": "A1"})

    row_data_validator = RowDataValidator()
    where_clause = row_data_validator._generate_where_clause(
        index_column_collection=index_column_collection,
        df_row=row,
        postfix=SOURCE_SUFFIX,
    )

    assert where_clause == "\"ID\" = 'A1'"


def test_generate_clause():
    row_data_validator = RowDataValidator()
    clause = row_data_validator._generate_clause(
        column_name="clm1",
        value=1000,
    )

    assert clause == '"clm1" = 1000'

    clause = row_data_validator._generate_clause(
        column_name="clm1",
        value="ABC",
    )

    assert clause == "\"clm1\" = 'ABC'"
