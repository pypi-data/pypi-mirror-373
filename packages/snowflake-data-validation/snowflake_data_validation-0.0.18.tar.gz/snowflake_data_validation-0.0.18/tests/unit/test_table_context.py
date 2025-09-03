from snowflake.snowflake_data_validation.utils.constants import Origin, Platform
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


def test_table_context_generation():
    table_context = TableContext(
        column_selection_list=["columnA"],
        database_name="test_db",
        columns=[make_col(name="columnA", is_primary_key=True)],
        fully_qualified_name="test_db.test_schema.test_table",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=False,
        origin=Origin.TARGET,
        platform=Platform.SNOWFLAKE,
        run_id="test_run_id",
        run_start_time="test_run_start_time",
        schema_name="test_schema",
        sql_generator=None,
        table_name="test_table",
        templates_loader_manager=None,
        user_index_column_collection=["columnA"],
        where_clause="",
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    assert table_context.column_selection_list == ["columnA"]
    assert table_context.database_name == "test_db"
    assert table_context.columns[0].name == "columnA"
    assert table_context.columns[0].data_type == "VARCHAR"
    assert table_context.columns[0].nullable == True
    assert table_context.columns[0].is_primary_key == True
    assert table_context.columns[0].calculated_column_size_in_bytes == 0
    assert table_context.columns[0].properties == {}
    assert table_context.fully_qualified_name == "test_db.test_schema.test_table"
    assert table_context.has_where_clause == False
    assert table_context.is_case_sensitive == False
    assert table_context.is_exclusion_mode == False
    assert table_context.origin == Origin.TARGET
    assert table_context.platform == Platform.SNOWFLAKE
    assert table_context.run_id == "test_run_id"
    assert table_context.run_start_time == "test_run_start_time"
    assert table_context.schema_name == "test_schema"
    assert table_context.sql_generator is None
    assert table_context.table_name == "test_table"
    assert table_context.templates_loader_manager is None
    assert table_context.column_selection_list == ["columnA"]
    assert table_context.where_clause == ""
    assert table_context.chunk_number == 1
    assert table_context.row_count == 10
    assert table_context.max_failed_rows_number == 100
    assert table_context.exclude_metrics is False


def make_col(name: str, is_primary_key: bool = False):
    return ColumnMetadata(
        name=name,
        data_type="VARCHAR",
        nullable=True,
        is_primary_key=is_primary_key,
        calculated_column_size_in_bytes=0,
        properties={},
    )


def test_get_columns_to_validate_inclusion():
    cols = [make_col("A"), make_col("B"), make_col("C")]
    # Only include B and C
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_exclusion_mode=False,
        is_case_sensitive=False,
        column_selection_list=["B", "C"],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
        user_index_column_collection=["A"],
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["B", "C"]


def test_get_columns_to_validate_exclusion():
    cols = [make_col("A"), make_col("B"), make_col("C")]
    # Exclude B
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=True,
        column_selection_list=["B"],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
        user_index_column_collection=["A"],
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )
    result = test_context.columns_to_validate
    # Should return A and C, excluding B
    assert [c.name for c in result] == ["A", "C"]


def test_get_columns_to_validate_empty_column_list():
    cols = [make_col("A"), make_col("B")]
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_exclusion_mode=False,
        is_case_sensitive=False,
        column_selection_list=[],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
        user_index_column_collection=["A"],
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )
    # No filter, should return all
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["A", "B"]


def test_get_columns_to_validate_regex():
    cols = [make_col("foo"), make_col("bar"), make_col("baz")]
    test_context = TableContext(
        platform=Platform.SNOWFLAKE,
        origin=Origin.TARGET,
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_exclusion_mode=False,
        is_case_sensitive=False,
        column_selection_list=['r"^ba"'],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
        user_index_column_collection=[],
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    # Regex for all names starting with 'ba'
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["bar", "baz"]


def test_get_columns_to_validate_exclusion_regex():
    cols = [make_col("foo"), make_col("bar"), make_col("baz")]
    # Exclude all names starting with 'ba'
    test_context = TableContext(
        platform=Platform.SNOWFLAKE,
        origin=Origin.TARGET,
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_exclusion_mode=True,
        column_selection_list=['r"^ba"'],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
        is_case_sensitive=True,
        user_index_column_collection=[],
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["foo"]


def test_get_chunk_id():
    table_context = TableContext(
        column_selection_list=[],
        database_name="test_db",
        columns=[make_col(name="columnA", is_primary_key=True)],
        fully_qualified_name="test_db.test_schema.test_table",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=False,
        origin=Origin.TARGET,
        platform=Platform.SNOWFLAKE,
        run_id="test_run_id",
        run_start_time="test_run_start_time",
        schema_name="test_schema",
        sql_generator=None,
        table_name="test_table",
        templates_loader_manager=None,
        user_index_column_collection=["columnA"],
        where_clause="",
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    chunk_id = table_context.get_chunk_id(other_table_name="other_table")

    assert chunk_id == "CHUNK_other_table_test_table_1"

    table_context.origin = Origin.SOURCE

    chunk_id = table_context.get_chunk_id(other_table_name="other_table")

    assert chunk_id == "CHUNK_test_table_other_table_2"


def test_normalized_fully_qualified_name():
    table_context = TableContext(
        column_selection_list=[],
        database_name="test_db",
        columns=[make_col(name="columnA", is_primary_key=True)],
        fully_qualified_name="test_db.test_schema.test_table",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=False,
        origin=Origin.TARGET,
        platform=Platform.SNOWFLAKE,
        run_id="test_run_id",
        run_start_time="test_run_start_time",
        schema_name="test_schema",
        sql_generator=None,
        table_name="test_table",
        templates_loader_manager=None,
        user_index_column_collection=["columnA"],
        where_clause="",
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    table_context.fully_qualified_name = "test_db.test_schema.test_table"
    table_context.normalized_fully_qualified_name = "test_db_test_schema_test_table"


def test_join_column_names_with_commas():
    table_context = TableContext(
        column_selection_list=[],
        database_name="test_db",
        columns=[
            make_col(name="columnA", is_primary_key=True),
            make_col(name="columnB"),
            make_col(name="columnC"),
        ],
        fully_qualified_name="test_db.test_schema.test_table",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=False,
        origin=Origin.TARGET,
        platform=Platform.SNOWFLAKE,
        run_id="test_run_id",
        run_start_time="test_run_start_time",
        schema_name="test_schema",
        sql_generator=None,
        table_name="test_table",
        templates_loader_manager=None,
        user_index_column_collection=["columnA"],
        where_clause="",
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    column_names_separate_by_comma = table_context.join_column_names_with_commas()
    assert column_names_separate_by_comma == '"columnA", "columnB", "columnC"'


def test_index_column_collection_custom():
    table_context = TableContext(
        column_selection_list=[],
        database_name="test_db",
        columns=[
            make_col(name="columnA"),
            make_col(name="columnB"),
            make_col(name="columnC"),
        ],
        fully_qualified_name="test_db.test_schema.test_table",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=False,
        origin=Origin.TARGET,
        platform=Platform.SNOWFLAKE,
        run_id="test_run_id",
        run_start_time="test_run_start_time",
        schema_name="test_schema",
        sql_generator=None,
        table_name="test_table",
        templates_loader_manager=None,
        user_index_column_collection=["columnB"],
        where_clause="",
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    table_context.index_column_collection = ["columnA"]


def test_index_column_collection_default():
    table_context = TableContext(
        column_selection_list=[],
        database_name="test_db",
        columns=[
            make_col(name="columnA", is_primary_key=True),
            make_col(name="columnB"),
            make_col(name="columnC"),
        ],
        fully_qualified_name="test_db.test_schema.test_table",
        has_where_clause=False,
        is_case_sensitive=False,
        is_exclusion_mode=False,
        origin=Origin.TARGET,
        platform=Platform.SNOWFLAKE,
        run_id="test_run_id",
        run_start_time="test_run_start_time",
        schema_name="test_schema",
        sql_generator=None,
        table_name="test_table",
        templates_loader_manager=None,
        user_index_column_collection=["columnA"],
        where_clause="",
        chunk_number=1,
        row_count=10,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    table_context.index_column_collection = ["columnA"]


def test_column_selection_list_case_sensitivity():
    """Test that column_selection_list is handled correctly based on case sensitivity setting"""
    cols = [make_col("columnA"), make_col("columnB")]
    mixed_case_column_list = ["columnA", "columnB"]

    # Test case insensitive mode - column_selection_list should be uppercase
    case_insensitive_context = TableContext(
        platform=Platform.SNOWFLAKE,
        origin=Origin.TARGET,
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_exclusion_mode=False,
        is_case_sensitive=False,
        column_selection_list=mixed_case_column_list,
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time="test_run_start_time",
        user_index_column_collection=[],
        chunk_number=3,
        row_count=30,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    # Column_selection_list should maintain the original case
    assert case_insensitive_context.column_selection_list == ["columnA", "columnB"]

    # Test case sensitive mode - column_selection_list should remain as-is
    case_sensitive_context = TableContext(
        platform=Platform.SNOWFLAKE,
        origin=Origin.TARGET,
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        is_exclusion_mode=False,
        is_case_sensitive=True,
        column_selection_list=mixed_case_column_list,
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time="test_run_start_time",
        user_index_column_collection=[],
        chunk_number=3,
        row_count=30,
        max_failed_rows_number=100,
        id=1,
        exclude_metrics=False,
    )

    # When case sensitive, column_selection_list should remain unchanged
    assert case_sensitive_context.column_selection_list == ["columnA", "columnB"]
