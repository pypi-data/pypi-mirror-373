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


import os

import jinja2

from snowflake.snowflake_data_validation.utils.constants import (
    ERROR_GENERATING_TEMPLATE,
    TABLE_METADATA_QUERY,
    TEMPLATE_NOT_FOUND,
)
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)


class SQLQueriesTemplateGenerator:
    def __init__(self, jinja_templates_folder_path: str):
        """Initialize the SQLQueriesTemplateGenerator.

        Set up the template directory and initialize the Jinja2 environment
        with a file system loader pointing to the template directory.

        Attributes:
            template_dir (str): The directory where Jinja2 templates are stored.
            env (jinja2.Environment): The Jinja2 environment for loading templates.

        """
        self.template_dir = os.path.join(jinja_templates_folder_path)
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir))

    def generate_table_metadata_sql(
        self,
        platform: str,
        table_name: str,
        schema_name: str,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
        column_selection_list: list[ColumnMetadata],
    ):
        """Generate SQL query for table metadata based on the provided table configuration and platform.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value).
            table_name (str): The name of the table for which the SQL query is being generated.
            schema_name (str): The name of the schema containing the table.
            fully_qualified_name (str): The fully qualified name of the table.
            where_clause (str): Optional WHERE clause to filter results.
            has_where_clause (bool): Indicates if a WHERE clause is present.
            column_selection_list (list[ColumnMetadata]): List of ColumnMetadata objects to include in the query.

        Returns:
            str: The generated SQL query as a string.

        Raises:
            ValueError: If the template file for the specified platform is not found.
            Exception: If there is an error generating the template.

        """
        template_file = TABLE_METADATA_QUERY.format(platform=platform)
        try:
            template = self.env.get_template(template_file)
            column_names = [col.name for col in column_selection_list]
            sql = template.render(
                object_name=table_name,
                object_schema=schema_name,
                fully_qualified_name=fully_qualified_name,
                where_clause=where_clause,
                has_where_clause=has_where_clause,
                columns=column_names,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                TEMPLATE_NOT_FOUND.format(
                    platform=platform,
                    template_file=template_file,
                    template_dir=self.template_dir,
                )
            ) from None
        except Exception as e:
            raise Exception(ERROR_GENERATING_TEMPLATE.format(exception=e)) from e

    def generate_columns_metrics_metadata_sql(
        self, table_name: str, column_names: list[str], platform: str
    ):
        """Generate an SQL query for column metrics metadata using a Jinja2 template.

        Args:
            table_name (str): The name of the table for which the SQL query is being generated.
            column_names (list[str]): A list of column names to include in the query.
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)

        Returns:
            str: The rendered SQL query as a string.

        Raises:
            ValueError: If the template file for the specified platform is not found.
            Exception: If an error occurs during template rendering.

        """
        template_file = f"{platform}_columns_metrics_query.sql.j2"  # Naming convention: platform.sql.j2
        try:
            template = self.env.get_template(template_file)
            sql = template.render(table_name=table_name, column_names=column_names)
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def extract_table_column_metadata(
        self, database_name: str, schema_name: str, table_name: str, platform: str
    ) -> str:
        """Generate a SQL query to extract table column metadata.

        Args:
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            table_name (str): The name of the table for which metadata is to be extracted.
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)

        Returns:
            str: The SQL query string to extract table metadata.

        Raises:
            ValueError: If the template file for the specified platform is not found.
            Exception: If an error occurs during template rendering.

        """
        template_file = f"{platform}_get_columns_metadata.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                database_name=database_name,
                schema_name=schema_name,
                table_name=table_name,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def get_case_sensitive_columns(
        self, database_name: str, schema_name: str, table_name: str, platform: str
    ) -> str:
        """Generate a SQL query to check which columns are case-sensitive in Snowflake.

        Args:
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            table_name (str): The name of the table for which case-sensitive columns are to be checked.
            platform (str): The platform identifier (should be Platform.SNOWFLAKE.value)

        Returns:
            str: The SQL query string to extract case-sensitive column information.

        Raises:
            ValueError: If the template file is not found.
            Exception: If an error occurs during template rendering.

        """
        template_file = f"{platform}_get_case_sensitive_columns.sql.j2"
        # TODO this is a workaround, the real name should be in the YAML file as target_schema or target_name
        schema_name = schema_name.upper()
        table_name = table_name.upper()
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                schema_name=schema_name,
                table_name=table_name,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def generate_statement_table_chunks_md5(
        self,
        database_name: str,
        schema_name: str,
        normalized_fully_qualified_name: str,
        platform: str,
        table_id: int,
    ) -> str:
        """Generate the DDL statement to create a table for storing MD5 of data chunks.

        Args:
            normalized_fully_qualified_name (str): The normalized fully qualified name of the table.
            database_name (str): The name of the database where the table will be created.
            schema_name (str): The name of the schema where the table will be created.
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)
            table_id (int): The id of the table, used to avoid name collisions between temporal tables.

        Returns:
            str: SQL query string to create a table for storing MD5 of data chunks.

        """
        template_file = f"{platform}_chunks_md5_table_template.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                database_name=database_name,
                schema_name=schema_name,
                normalized_fully_qualified_name=normalized_fully_qualified_name,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found: {template_file}. Please create it in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def generate_compute_md5_query(
        self,
        platform: str,
        chunk_id: str,
        column_collection: list[ColumnMetadata],
        datatypes_normalization_renderer_templates: dict[str, str],
        index_column_collection: list[ColumnMetadata],
        column_names_separate_by_comma: str,
        fully_qualified_name: str,
        has_where_clause: bool,
        where_clause: str,
        source_table_name: str,
        normalized_fully_qualified_name: str,
        fetch: int,
        offset: int,
        database_name: str,
        schema_name: str,
        table_id: int,
    ) -> str:
        template_file = f"{platform}_compute_md5_sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                database_name=database_name,
                schema_name=schema_name,
                chunk_id=chunk_id,
                column_collection=column_collection,
                datatypes_normalization_renderer_templates=datatypes_normalization_renderer_templates,
                index_column_collection=index_column_collection,
                column_names_separate_by_comma=column_names_separate_by_comma,
                fully_qualified_name=fully_qualified_name,
                has_where_clause=has_where_clause,
                where_clause=where_clause,
                source_table_name=source_table_name,
                normalized_fully_qualified_name=normalized_fully_qualified_name,
                fetch=fetch,
                offset=offset,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def generate_extract_chunks_md5_query(
        self,
        platform: str,
        database_name: str,
        schema_name: str,
        normalized_fully_qualified_name: str,
        table_id: int,
    ) -> str:
        template_file = f"{platform}_extract_chunks_md5_table_template.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                database_name=database_name,
                schema_name=schema_name,
                normalized_fully_qualified_name=normalized_fully_qualified_name,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found for platform: {platform}. Please create {template_file} "
                f"in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def generate_extract_md5_rows_chunk_query(
        self,
        platform: str,
        chunk_id: str,
        database_name: str,
        schema_name: str,
        index_column_collection: list[ColumnMetadata],
        table_id: int,
    ) -> str:
        """Generate the SQL query to extract MD5 for a specific chunk of a table.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)
            chunk_id (str): The identifier for the data chunk.
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            index_column_collection (list[ColumnMetadata]): List of index columns metadata.
            table_id (int): The id of the table, used to avoid name collisions between temporal tables.

        Returns:
            str: SQL query string to extract MD5 for the specified chunk.

        """
        template_file = f"{platform}_extract_md5_rows_chunk.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                database_name=database_name,
                schema_name=schema_name,
                index_column_collection=index_column_collection,
                chunk_id=chunk_id,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found: {template_file}. Please create it in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    def generate_table_row_count_query(
        self,
        platform: str,
        fully_qualified_name: str,
        where_clause: str,
        has_where_clause: bool,
    ):
        """Generate the SQL query to count rows in a table.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)
            fully_qualified_name (str): The fully qualified name of the table.
            where_clause (str): Optional WHERE clause to filter results.
            has_where_clause (bool): Indicates if a WHERE clause is present.

        Returns:
            str: SQL query string to count rows in the specified table.

        """
        template_file = f"{platform}_row_count_query.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                fully_qualified_name=fully_qualified_name,
                where_clause=where_clause,
                has_where_clause=has_where_clause,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found: {template_file}. Please create it in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    # SNOWFLAKE ONLY
    def generate_chunk_row_concatenated_template_query(
        self,
        platform: str,
        chunk_id: str,
        index_column_collection: list[ColumnMetadata],
        column_names_separate_by_comma: str,
        column_collection: list[ColumnMetadata],
        datatypes_normalization_renderer_templates: dict[str, str],
        fully_qualified_name: str,
        has_where_clause: bool,
        where_clause: str,
        fetch: int,
        offset: int,
        database_name: str,
        schema_name: str,
        table_id: int,
    ) -> str:
        """Generate the SQL query to concatenate row values for MD5 calculation.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)
            chunk_id (str): The identifier for the data chunk.
            index_column_collection (list[ColumnMetadata]): List of index columns metadata.
            column_names_separate_by_comma (str): Comma-separated string of column names.
            column_collection (list[ColumnMetadata]): List of all columns metadata.
            datatypes_normalization_renderer_templates (dict[str, str]): Dictionary of
            normalization templates for data types.
            fully_qualified_name (str): The fully qualified name of the table.
            has_where_clause (bool): Indicates if a WHERE clause is present.
            where_clause (str): The WHERE clause to filter rows.
            fetch (int): The maximum number of rows to return.
            offset (int): The number of rows to skip before starting to return rows.
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            table_id (int): The id of the table, used to avoid name collisions between temporal tables.

        Returns:
            str: SQL query string to concatenate row values.

        """
        template_file = f"{platform}_chunk_row_concatenated_template.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                chunk_id=chunk_id,
                index_column_collection=index_column_collection,
                column_names_separate_by_comma=column_names_separate_by_comma,
                column_collection=column_collection,
                datatypes_normalization_renderer_templates=datatypes_normalization_renderer_templates,
                fully_qualified_name=fully_qualified_name,
                has_where_clause=has_where_clause,
                where_clause=where_clause,
                fetch=fetch,
                offset=offset,
                database_name=database_name,
                schema_name=schema_name,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found: {template_file}. Please create it in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    # SNOWFLAKE ONLY
    def generate_chunk_row_md5_template_query(
        self,
        platform: str,
        chunk_id: str,
        index_column_collection: list[ColumnMetadata],
        fetch: int,
        offset: int,
        database_name: str,
        schema_name: str,
        table_id: int,
    ) -> str:
        """Generate the SQL query to calculate MD5 for concatenated row values.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)
            chunk_id (str): The identifier for the data chunk.
            index_column_collection (list[ColumnMetadata]): List of index columns metadata.
            fetch (int): The maximum number of rows to return.
            offset (int): The number of rows to skip before starting to return rows.
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            table_id (int): The id of the table, used to avoid name collisions between temporal tables.

        Returns:
            str: SQL query string to calculate MD5.

        """
        template_file = f"{platform}_chunk_row_md5_template.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                chunk_id=chunk_id,
                index_column_collection=index_column_collection,
                fetch=fetch,
                offset=offset,
                database_name=database_name,
                schema_name=schema_name,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found: {template_file}. Please create it in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e

    # SNOWFLAKE ONLY
    def generate_insert_chunk_row_md5_template_query(
        self,
        platform: str,
        normalized_fully_qualified_name: str,
        chunk_id: str,
        database_name: str,
        schema_name: str,
        table_id: int,
    ) -> str:
        """Generate the SQL query to insert MD5 into the chunks table.

        Args:
            platform (str): The platform identifier (e.g., Platform.SNOWFLAKE.value, Platform.SQLSERVER.value)
            normalized_fully_qualified_name (str): The normalized fully qualified name of the table.
            chunk_id (str): The identifier for the data chunk.
            database_name (str): The name of the database containing the table.
            schema_name (str): The name of the schema containing the table.
            table_id (int): The id of the table, used to avoid name collisions between temporal tables.

        Returns:
            str: SQL query string to insert MD5.

        """
        template_file = f"{platform}_insert_chunk_row_md5_template.sql.j2"
        try:
            template = self.env.get_template(template_file)
            sql = template.render(
                normalized_fully_qualified_name=normalized_fully_qualified_name,
                chunk_id=chunk_id,
                database_name=database_name,
                schema_name=schema_name,
                table_id=table_id,
            )
            return sql
        except jinja2.exceptions.TemplateNotFound:
            raise ValueError(
                f"Template not found: {template_file}. Please create it in the {self.template_dir} directory."
            ) from None
        except Exception as e:
            raise Exception(f"Error generating template: {e}") from e
