import os

import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    CHUNK_ID_COLUMN_KEY,
    CHUNK_MD5_VALUE_COLUMN_KEY,
    NEWLINE,
    NOT_APPLY,
    RESULT_COLUMN_KEY,
    ROW_NUMBER_COLUMN_KEY,
    SOURCE_QUERY_COLUMN_KEY,
    TABLE_NAME_COLUMN_KEY,
    TARGET_QUERY_COLUMN_KEY,
    UNDERSCORE_MERGE_COLUMN_KEY,
    Platform,
    Result,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.validation.data_validator_base import (
    DataValidatorBase,
)


BOTH_PANDAS_INDICATOR = "both"
RIGHT_ONLY_PANDAS_INDICATOR = "right_only"
LEFT_ONLY_PANDAS_INDICATOR = "left_only"
SOURCE_SUFFIX = "_SOURCE"
TARGET_SUFFIX = "_TARGET"
ROW_MD5_KEY = "ROW_MD5"
ROW_VALIDATION_REPORT_NAME = (
    "{fully_qualified_name}_row_validation_report_{table_id}.csv"
)
ROW_VALIDATION_DIFF_QUERY_NAME = (
    "{fully_qualified_name}_{platform}_row_validation_diff_query_{table_id}.sql"
)
MD5_REPORT_QUERY_TEMPLATE = "SELECT * FROM {fully_qualified_name} WHERE {clause}"


class RowDataValidator(DataValidatorBase):
    def get_diff_md5_chunks(
        self,
        source_md5_df: pd.DataFrame,
        target_md5_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Get the differences in MD5 between source and target DataFrames.

        This function compares the MD5 of two DataFrames and returns a DataFrame containing
        the differences found, including chunk IDs and MD5 value.

        Args:
            source_md5_df (pd.DataFrame): The source DataFrame containing MD5.
            target_md5_df (pd.DataFrame): The target DataFrame containing MD5.

        Returns:
            pd.DataFrame: A DataFrame containing the differences in MD5.

        """
        source_intersection_target = pd.merge(
            source_md5_df,
            target_md5_df,
            on=[CHUNK_ID_COLUMN_KEY, CHUNK_MD5_VALUE_COLUMN_KEY],
            how="inner",
        )

        source_except_intersection = source_md5_df[
            ~source_md5_df[CHUNK_ID_COLUMN_KEY].isin(
                source_intersection_target[CHUNK_ID_COLUMN_KEY]
            )
        ]
        target_except_intersection = target_md5_df[
            ~target_md5_df[CHUNK_ID_COLUMN_KEY].isin(
                source_intersection_target[CHUNK_ID_COLUMN_KEY]
            )
        ]

        diff_df = pd.merge(
            source_except_intersection,
            target_except_intersection,
            on=[CHUNK_ID_COLUMN_KEY],
            how="left",
            suffixes=(SOURCE_SUFFIX, TARGET_SUFFIX),
        )

        return diff_df

    def get_diff_md5_rows_chunk(
        self,
        source_md5_rows_chunk: pd.DataFrame,
        target_md5_rows_chunk: pd.DataFrame,
        source_index_column_collection: list[str],
        target_index_column_collection: list[str],
        source_index_column_suffix_collection: list[str],
        target_index_column_suffix_collection: list[str],
    ) -> pd.DataFrame:
        """Get the differences in MD5 for a specific chunk row.

        Args:
            source_md5_rows_chunk (pd.DataFrame): The source DataFrame
            containing MD5 for a specific chunk row.
            target_md5_rows_chunk (pd.DataFrame): The target DataFrame
            containing MD5 for a specific chunk row.
            source_index_column_collection (list[str]): A list of index columns for the source DataFrame.
            target_index_column_collection (list[str]): A list of index columns for the target DataFrame.
            source_index_column_suffix_collection (list[str]): A list of index columns
            with suffix for the source DataFrame.
            target_index_column_suffix_collection (list[str]): A list of index columns
            with suffix for the target DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the differences in MD5 for the specified chunk row.

        """
        source_md5_rows_chunk_str = source_md5_rows_chunk.convert_dtypes()
        target_md5_rows_chunk_str = target_md5_rows_chunk.convert_dtypes()

        source_index_column_suffix_dict = dict(
            zip(source_index_column_collection, source_index_column_suffix_collection)
        )
        target_index_column_suffix_dict = dict(
            zip(target_index_column_collection, target_index_column_suffix_collection)
        )

        are_equal_index_columns = (
            source_index_column_collection == target_index_column_collection
        )

        if are_equal_index_columns:
            source_columns_to_rename_dict = {**source_index_column_suffix_dict}
            target_columns_to_rename_dict = {**target_index_column_suffix_dict}

            source_md5_rows_chunk_str = source_md5_rows_chunk_str.rename(
                columns=source_columns_to_rename_dict
            )

            target_md5_rows_chunk_str = target_md5_rows_chunk_str.rename(
                columns=target_columns_to_rename_dict
            )

        if not are_equal_index_columns:
            source_index = source_index_column_collection
            target_index = target_index_column_collection
        else:
            source_index = source_index_column_suffix_collection
            target_index = target_index_column_suffix_collection

        source_merge_target = pd.merge(
            source_md5_rows_chunk_str,
            target_md5_rows_chunk_str,
            left_on=source_index,
            right_on=target_index,
            how="outer",
            suffixes=(SOURCE_SUFFIX, TARGET_SUFFIX),
            indicator=True,
        )

        if not are_equal_index_columns:
            columns_to_rename_dict = {
                **source_index_column_suffix_dict,
                **target_index_column_suffix_dict,
            }
            source_merge_target = source_merge_target.rename(
                columns=columns_to_rename_dict
            )

        not_found_df = self._generate_not_found_df(source_merge_target)

        failed_df = self._generate_failed_df(source_merge_target)

        columns = (
            source_index_column_suffix_collection
            + target_index_column_suffix_collection
            + [RESULT_COLUMN_KEY]
        )

        diff_df = pd.concat([not_found_df, failed_df])[columns].convert_dtypes()

        diff_df_ordered = diff_df.sort_values(
            by=source_index_column_suffix_collection, ignore_index=True
        )

        return diff_df_ordered

    def _generate_not_found_df(self, source_merge_target: pd.DataFrame) -> pd.DataFrame:
        not_found_df = source_merge_target[
            source_merge_target[UNDERSCORE_MERGE_COLUMN_KEY] != BOTH_PANDAS_INDICATOR
        ]

        target_not_found_df = not_found_df[
            not_found_df[UNDERSCORE_MERGE_COLUMN_KEY] == LEFT_ONLY_PANDAS_INDICATOR
        ]
        target_not_found_df_copy = target_not_found_df.copy()
        target_not_found_df_copy[RESULT_COLUMN_KEY] = Result.NOT_FOUND_TARGET.value

        source_not_found_df = not_found_df[
            not_found_df[UNDERSCORE_MERGE_COLUMN_KEY] == RIGHT_ONLY_PANDAS_INDICATOR
        ]
        source_not_found_df_copy = source_not_found_df.copy()
        source_not_found_df_copy[RESULT_COLUMN_KEY] = Result.NOT_FOUND_SOURCE.value

        not_found_with_result_column_df = pd.concat(
            [target_not_found_df_copy, source_not_found_df_copy], ignore_index=True
        )

        return not_found_with_result_column_df

    def _generate_failed_df(self, source_merge_target: pd.DataFrame) -> pd.DataFrame:
        failed_df = source_merge_target[
            (source_merge_target[UNDERSCORE_MERGE_COLUMN_KEY] == BOTH_PANDAS_INDICATOR)
            & (
                source_merge_target[ROW_MD5_KEY + SOURCE_SUFFIX]
                != source_merge_target[ROW_MD5_KEY + TARGET_SUFFIX]
            )
        ]

        failed_df_copy = failed_df.copy()
        failed_df_copy[RESULT_COLUMN_KEY] = Result.FAILURE.value
        return failed_df_copy

    def generate_row_validation_report(
        self,
        compared_df: pd.DataFrame,
        fully_qualified_name: str,
        target_fully_qualified_name: str,
        source_index_column_suffix_collection: list[str],
        target_index_column_suffix_collection: list[str],
        table_id: int,
        context: Context,
    ) -> None:
        """Store a report for MD5 rows chunk validation.

        Args:
            compared_df (pd.DataFrame): The DataFrame containing the compared MD5 checksums.
            fully_qualified_name (str): The fully qualified name of the table being validated.
            target_fully_qualified_name (str): The fully qualified name of the target table being validated.
            source_index_column_suffix_collection (list[str]): A list of index columns
            with suffix for the source DataFrame.
            target_index_column_suffix_collection (list[str]): A list of index columns
            with suffix for the target DataFrame.
            table_id (int): The id of the table, used to avoid name collisions between reports.
            context (Context): The execution context containing relevant configuration and runtime information.

        """
        result_columns = (
            [
                ROW_NUMBER_COLUMN_KEY,
                TABLE_NAME_COLUMN_KEY,
                RESULT_COLUMN_KEY,
            ]
            + source_index_column_suffix_collection
            + target_index_column_suffix_collection
            + [
                SOURCE_QUERY_COLUMN_KEY,
                TARGET_QUERY_COLUMN_KEY,
            ]
        )

        result_df = pd.DataFrame(data=[], columns=result_columns)
        for _, row in compared_df.iterrows():
            values = []
            row_number = context.get_row_number()
            values.append(row_number)
            values.append(fully_qualified_name)

            result = Result(row[RESULT_COLUMN_KEY])
            values.append(row[RESULT_COLUMN_KEY])

            for index_column in source_index_column_suffix_collection:
                value = (
                    NOT_APPLY
                    if result == Result.NOT_FOUND_SOURCE
                    else row[index_column]
                )
                values.append(value)

            for index_column in target_index_column_suffix_collection:
                value = (
                    NOT_APPLY
                    if result == Result.NOT_FOUND_TARGET
                    else row[index_column]
                )
                values.append(value)

            if result != Result.NOT_FOUND_SOURCE:
                source_query = self._generate_select_all_columns_query(
                    fully_qualified_name=fully_qualified_name,
                    index_column_collection=source_index_column_suffix_collection,
                    df_row=row,
                    postfix=SOURCE_SUFFIX,
                )
                values.append(source_query)
            else:
                values.append(NOT_APPLY)

            if result != Result.NOT_FOUND_TARGET:
                target_query = self._generate_select_all_columns_query(
                    fully_qualified_name=target_fully_qualified_name,
                    index_column_collection=target_index_column_suffix_collection,
                    df_row=row,
                    postfix=TARGET_SUFFIX,
                )
                values.append(target_query)
            else:
                values.append(NOT_APPLY)

            result_df.loc[len(result_df)] = values

        report_name = ROW_VALIDATION_REPORT_NAME.format(
            fully_qualified_name=fully_qualified_name,
            table_id=table_id,
        )

        report_file = os.path.join(
            context.report_path, f"{context.run_start_time}_{report_name}"
        )

        result_df.to_csv(report_file, index=False)

    def generate_row_validation_queries(
        self,
        compared_df: pd.DataFrame,
        fully_qualified_name: str,
        target_fully_qualified_name: str,
        source_index_column_suffix_collection: list[str],
        target_index_column_suffix_collection: list[str],
        table_id: int,
        context: Context,
    ) -> None:
        """Generate SQL queries to validate MD5 checksums for a given DataFrame.

        This function constructs SQL queries to validate the MD5 checksums of the source and target DataFrames
        based on the provided compared DataFrame and index columns.

        Args:
            compared_df (pd.DataFrame): The DataFrame containing the compared MD5 checksums.
            fully_qualified_name (str): The fully qualified name of the source table being validated.
            target_fully_qualified_name (str): The fully qualified name of the target table being validated.
            source_index_column_suffix_collection (list[str]): A list of index columns
            with suffix for the source DataFrame.
            target_index_column_suffix_collection (list[str]): A list of index columns
            with suffix for the target DataFrame.
            table_id (int): The id of the table, used to avoid name collisions between reports.
            context (Context): The execution context containing relevant configuration and runtime information.

        """
        source_clause_collection = []
        target_clause_collection = []
        for _, row in compared_df.iterrows():

            result_value = Result(row[RESULT_COLUMN_KEY])
            if result_value != Result.NOT_FOUND_SOURCE:
                source_clause = self._generate_where_clause(
                    index_column_collection=source_index_column_suffix_collection,
                    df_row=row,
                    postfix=SOURCE_SUFFIX,
                )

                source_clause_newline = source_clause + NEWLINE
                source_clause_collection.append(source_clause_newline)

            if result_value != Result.NOT_FOUND_TARGET:
                target_clause = self._generate_where_clause(
                    index_column_collection=target_index_column_suffix_collection,
                    df_row=row,
                    postfix=TARGET_SUFFIX,
                )

                target_clause_newline = target_clause + NEWLINE
                target_clause_collection.append(target_clause_newline)

        self._generate_row_validation_query(
            clause_collection=source_clause_collection,
            fully_qualified_name=fully_qualified_name,
            platform=context.source_platform,
            report_path=context.report_path,
            run_start_time=context.run_start_time,
            table_id=table_id,
        )

        self._generate_row_validation_query(
            clause_collection=target_clause_collection,
            fully_qualified_name=target_fully_qualified_name,
            platform=context.target_platform,
            report_path=context.report_path,
            run_start_time=context.run_start_time,
            table_id=table_id,
        )

    def _generate_row_validation_query(
        self,
        clause_collection: list[str],
        fully_qualified_name: str,
        platform: Platform,
        report_path: str,
        run_start_time: str,
        table_id: int,
    ) -> None:

        joined_clause = " OR ".join(clause_collection)

        query = MD5_REPORT_QUERY_TEMPLATE.format(
            fully_qualified_name=fully_qualified_name, clause=joined_clause
        )

        report_name = ROW_VALIDATION_DIFF_QUERY_NAME.format(
            platform=platform,
            fully_qualified_name=fully_qualified_name,
            table_id=table_id,
        )

        report_file_path = os.path.join(
            report_path,
            f"{run_start_time}_{report_name}",
        )

        self._write_to_file(
            file_path=report_file_path,
            content=query,
        )

    def _generate_select_all_columns_query(
        self,
        fully_qualified_name: str,
        index_column_collection: list[str],
        df_row: pd.Series,
        postfix: str,
    ) -> str:
        where_clause = self._generate_where_clause(
            index_column_collection=index_column_collection,
            df_row=df_row,
            postfix=postfix,
        )

        query = MD5_REPORT_QUERY_TEMPLATE.format(
            fully_qualified_name=fully_qualified_name, clause=where_clause
        )

        return query

    def _generate_where_clause(
        self, index_column_collection: list[str], df_row: pd.Series, postfix: str
    ) -> str:
        clause = [
            self._generate_clause(
                column_name=index_column.replace(postfix, ""),
                value=df_row[index_column],
            )
            for index_column in index_column_collection
        ]

        joined_clause = " AND ".join(clause)

        return joined_clause

    def _generate_clause(
        self, column_name: str, value: any, operator: str = "="
    ) -> str:
        if self.is_numeric(value):
            return f""""{column_name}" {operator} {value}"""
        else:
            return f""""{column_name}" {operator} '{value}'"""

    def _write_to_file(self, file_path: str, content: str) -> None:
        """Write content to a file with UTF-8 encoding.

        Creates the directory if it doesn't exist.

        Args:
            file_path (str): The full path to the file including directory and filename.
            content (str): The content to write to the file.

        """
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
