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

from enum import Enum


# ----- PLATFORM ENUMS -----


class Platform(Enum):

    """Enumeration of supported database platforms."""

    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"
    TERADATA = "teradata"


class ExecutionMode(Enum):

    """Enumeration of available execution modes."""

    SYNC_VALIDATION = "sync_validation"
    ASYNC_GENERATION = "async_generation"
    ASYNC_VALIDATION = "async_validation"


class ValidationLevel(Enum):

    """Enumeration of validation level names for the validation report."""

    SCHEMA_VALIDATION = "SCHEMA VALIDATION"
    METRICS_VALIDATION = "METRICS VALIDATION"
    ROW_VALIDATION = "ROW VALIDATION"


class Origin(Enum):

    """Enumeration of data origin types."""

    SOURCE = "source"
    TARGET = "target"


class Result(Enum):

    """Enumeration of result types for validation."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"
    NOT_FOUND_SOURCE = "NOT_FOUND_SOURCE"
    NOT_FOUND_TARGET = "NOT_FOUND_TARGET"


# ----- COLLECTION CONSTANTS -----

METRICS_TO_EXCLUDE = {"avg", "sum", "stddev", "variance"}


# ----- CORE CONSTANTS -----

# Character constants
NEWLINE = "\n"
NOT_APPLY = "N/A"

# Magic Number Constants
ROW_NUMBER_DEFAULT_CHUNK = 100000
MAX_FAILED_ROWS_NUMBER_DEFAULT_VALUE = 100

# Jinja templates names

# Template files
TABLE_METADATA_QUERY = "{platform}_table_metadata_query.sql.j2"

# Exception messages
TEMPLATE_NOT_FOUND = (
    "Template not found for platform: {platform}. Please create {template_file} "
    "in the {template_dir} directory."
)
ERROR_GENERATING_TEMPLATE = "Error generating template: {exception}"
CONNECTION_NOT_ESTABLISHED = "Connection is not established. Call connect() first."
FAILED_TO_EXECUTE_QUERY = "An error occurred while executing the query"
FAILED_TO_EXECUTE_STATEMENT = (
    "An error occurred while executing the statement: {statement}"
)
INVALID_CONNECTION_MODE = "Invalid connection mode or missing configuration."

EDITABLE_YAML_FILE_FORMAT_ERROR = """Error in the format of {file_name}. Please check the following:
Incorrect indentation: YAML relies heavily on consistent indentation using spaces (not tabs).
Invalid characters: Certain characters might need to be quoted.
Syntax errors in lists or dictionaries: Incorrect use of hyphens for list items or nested structures.
Special characters not quoted: If a string contains special characters it might need to be enclosed in quotes."""

COLUMN_VALUES_CONCATENATED_ERROR = """The concatenated of your column values is longer than the limit
for a string column.
To avoid this error, you can either:
1. Exclude large object columns type from the table validation {}.
2. Exclude one or more columns from the table validation.
3. Split the table validation by columns."""

COLUMN_VALUES_CONCATENATED_ERROR_REDSHIFT = COLUMN_VALUES_CONCATENATED_ERROR.format(
    "VARCHAR(65535) and VARBYTE(65535)"
)

COLUMN_VALUES_CONCATENATED_ERROR_SQL_SERVER = COLUMN_VALUES_CONCATENATED_ERROR.format(
    "VARCHAR(MAX), NVARCHAR(MAX), VARBINARY(MAX) and XML"
)

COLUMN_VALUES_CONCATENATED_ERROR_SNOWFLAKE = COLUMN_VALUES_CONCATENATED_ERROR.format("")

COLUMN_VALUES_CONCATENATED_ERROR_TERADATA = COLUMN_VALUES_CONCATENATED_ERROR.format(
    "BLOB AND CLOB"
)

# Error code for exceeding the maximum allowed string column length
EXCEED_MAX_STRING_LENGHT_SQL_SERVER_ERROR_CODE = "Msg 511"
EXCEED_MAX_STRING_LENGHT_SNOWFLAKE_ERROR_CODE = "100078 (22000)"
EXCEED_MAX_STRING_LENGHT_REDSHIFT_ERROR_CODE = "code: 25101"


# Temporary constant for data parameters validation
DATA_PARAMETERS = (
    "tables_validate"  # TODO: Remove once Pydantic model implementation is complete
)
FULLY_QUALIFIED_NAME = "fully_qualified_name"
DATA_VALIDATION_CLI = "Data validation CLI"
COLUMN_VALIDATED = "COLUMN_VALIDATED"
COLUMNS_USED_DATA_CONF_FILE = "columns_validate"
COLUMN_DATATYPE = "DATA_TYPE"
DATATYPES_MAPPING_CONF_FILE = "datatype_maping"

# MESSAGES
NOT_EXIST_TARGET = "Not exist in the target"

# Validation criteria constants
NOT_APPLICABLE_CRITERIA_VALUE = "N/A"

# CPU optimization constants
CPU_MULTIPLIER = (
    3.0  # Multiplier for CPU cores (3.0 = 3x cores for I/O bound database workloads)
)
TEMPORARY_DEFAULT_OPTIMAL_LIMIT = 1
MAX_THREAD_LIMIT = 32  # Maximum allowed threads regardless of other factors
MIN_THREADS = 2  # Minimum threads for effective parallelization
DEFAULT_CPU_COUNT = 4  # Fallback CPU count when system detection fails
DEFAULT_THREAD_COUNT_OPTION = "auto"  # Default option for thread count configuration

# Files names
DIFFERENCES_FILE_NAME = "differencesL1.csv"
DIFFERENCES_FILE_NAME2 = "differencesL2.csv"
DATA_VALIDATION_OUTPUT_FOLDER = "output"

COLUMN_METRICS_TEMPLATE_NAME_FORMAT = "{platform}_column_metrics_templates.yaml"
TABLE_METADATA_QUERIES_FILENAME = "table_metadata_queries_{timestamp}.sql"
COLUMN_METADATA_QUERIES_FILENAME = "column_metadata_queries_{timestamp}.sql"
COLUMN_NORMALIZARION_TEMPLATE_NAME_FORMAT = (
    "{platform}_column_normalization_templates.yaml"
)
COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT = (
    "{platform}_datatypes_normalization_templates.yaml"
)
COLUMN_DATATYPES_MAPPING_NAME_FORMAT = (
    "{source_platform}_to_{target_platform}_datatypes_mapping_template.yaml"
)
CHUNK_ID_FORMAT = "CHUNK_{source_name}_{other_table_name}_{id}"

# Connection option
DEFAULT_CONNECTION_MODE = "default"
NAME_CONNECTION_MODE = "name"
CREDENTIALS_CONNECTION_MODE = "credentials"
TOML_CONNECTION_MODE = "toml"

# Connection pool configuration constants
DEFAULT_MAX_CONNECTION_AGE = 3600.0  # 1 hour in seconds
DEFAULT_CONNECTION_TIMEOUT = 30.0  # 30 seconds

# File configuration model constants
SCHEMA_VALIDATION_KEY = "schema_validation"
METRICS_VALIDATION_KEY = "metrics_validation"
ROW_VALIDATION_KEY = "row_validation"
TOLERANCE_KEY = "tolerance"
TYPE_MAPPING_FILE_PATH_KEY = "type_mapping_file_path"
MAX_FAILED_ROWS_KEY = "max_failed_rows"
EXCLUDE_METRICS_KEY = "exclude_metrics"

VALIDATION_CONFIGURATION_DEFAULT_VALUE = {
    SCHEMA_VALIDATION_KEY: True,
    METRICS_VALIDATION_KEY: True,
    ROW_VALIDATION_KEY: True,
    MAX_FAILED_ROWS_KEY: MAX_FAILED_ROWS_NUMBER_DEFAULT_VALUE,
    EXCLUDE_METRICS_KEY: False,
}

# Column Table Metadata Keys
CALCULATED_COLUMN_SIZE_IN_BYTES_KEY = "CALCULATED_COLUMN_SIZE_IN_BYTES"
CHARACTER_LENGTH_KEY = "CHARACTER_LENGTH"
COLUMN_NAME_KEY = "COLUMN_NAME"
DATA_TYPE_KEY = "DATA_TYPE"
DATABASE_NAME_KEY = "DATABASE_NAME"
IS_DATA_TYPE_SUPPORTED_KEY = "IS_DATA_TYPE_SUPPORTED"
IS_PRIMARY_KEY_KEY = "IS_PRIMARY_KEY"
NULLABLE_KEY = "NULLABLE"
PRECISION_KEY = "PRECISION"
SCALE_KEY = "SCALE"
SCHEMA_NAME_KEY = "SCHEMA_NAME"
TABLE_NAME_KEY = "TABLE_NAME"
ROW_COUNT_KEY = "ROW_COUNT"


# Column Validation DataFrame Keys
VALIDATION_TYPE_KEY = "VALIDATION_TYPE"
TABLE_KEY = "TABLE"
COLUMN_VALIDATED_KEY = "COLUMN_VALIDATED"
EVALUATION_CRITERIA_KEY = "EVALUATION_CRITERIA"
SOURCE_VALUE_KEY = "SOURCE_VALUE"
SNOWFLAKE_VALUE_KEY = "SNOWFLAKE_VALUE"
STATUS_KEY = "STATUS"
COMMENTS_KEY = "COMMENTS"
DIFFERENCES_KEY = "DIFFERENCES"
COLUMN_DIFFERENT_KEY = "COLUMN_DIFFERENT"
METRIC_DIFFERENT_KEY = "METRIC_DIFFERENT"

# DataFrames Column Names
TYPE_COLUMN_KEY = "type"
METRIC_COLUMN_KEY = "metric"
TEMPLATE_COLUMN_KEY = "template"
NORMALIZATION_COLUMN_KEY = "normalization"
ROW_NUMBER_COLUMN_KEY = "ROW_NUMBER"
TABLE_NAME_COLUMN_KEY = "TABLE_NAME"
RESULT_COLUMN_KEY = "RESULT"
SOURCE_QUERY_COLUMN_KEY = "SOURCE_QUERY"
TARGET_QUERY_COLUMN_KEY = "TARGET_QUERY"
CHUNK_ID_COLUMN_KEY = "CHUNK_ID"
CHUNK_MD5_VALUE_COLUMN_KEY = "CHUNK_MD5_VALUE"
UNDERSCORE_MERGE_COLUMN_KEY = "_merge"


# YAML Configurable Keys
METRIC_QUERY_KEY = "metric_query"
METRIC_NORMALIZATION_KEY = "metric_normalization"
METRIC_RETURN_DATATYPE_KEY = "metric_return_datatype"

# YAML placeholders
COL_NAME_NO_QUOTES_PLACEHOLDER = "{{ col_name }}"
COL_NAME_QUOTES_PLACEHOLDER = '"{{ col_name }}"'
METRIC_QUERY_PLACEHOLDER = "{{ metric_query }}"

# YAML errors
MISSING_SOURCE_CONNECTION_ERROR = (
    "No source connection configured in YAML file. "
    "Please add a source_connection section to your configuration file."
)

MISSING_TARGET_CONNECTION_ERROR = (
    "No target connection configured in YAML file. "
    "Please add a target_connection section to your configuration file."
)

# ----- TELEMETRY CONSTANTS -----

# Constants for telemetry events
VALIDATION_STARTED = "Validation_Started"
VALIDATION_FAILED = "Validation_Failed"
CONNECTION_ESTABLISHED = "Connection_Established"
CONNECTION_FAILED = "Connection_Failed"
SCHEMA_VALIDATION = "Schema_Validation"
METRICS_VALIDATION = "Metrics_Validation"
DATA_VALIDATION = "Data_Validation"
SYNC_COMPARISON_EXECUTED = "Sync_Comparison_Executed"
ASYNC_GENERATION_EXECUTED = "Async_Generation_Executed"
ASYNC_COMPARISON_EXECUTED = "Async_Comparison_Executed"
FUNCTION_EXECUTED = "Function_Executed"

# Telemetry data keys for table context
SOURCE_TABLE_CONTEXT = "source_table_context"
TARGET_TABLE_CONTEXT = "target_table_context"

# Constants for telemetry data keys
FUNCTION_KEY = "function"
SOURCE_PLATFORM_KEY = "source_platform"
TARGET_PLATFORM_KEY = "target_platform"
CONNECTION_MODE_KEY = "connection_mode"
TABLE_COUNT_KEY = "table_count"
DURATION_KEY = "duration"
SUCCESS_KEY = "success"
ERROR_MESSAGE_KEY = "error_message"
RUN_ID_KEY = "run_id"

# Table configuration keys
TABLE_CONTEXT_KEY = "table_context"
FULLY_QUALIFIED_NAME_KEY = "fully_qualified_name"
HAS_WHERE_CLAUSE_KEY = "has_where_clause"
COLUMN_SELECTION_USED_AS_EXCLUDED_KEY = "use_column_selection_as_exclude_list"
MODULE_NAME_KEY = "module_name"

# Configuration model keys
CONFIG_MODEL_KEY = "config_model"
IS_DATABASE_MAPPING_USED_KEY = "is_database_mapping_used"
IS_SCHEMA_MAPPING_USED_KEY = "is_schema_mapping_used"
PARALLELIZATION_KEY = "parallelization"
DATA_VALIDATION_CONFIG_FILE_KEY = "data_validation_config_file"

# Platform constants for telemetry
SQL_SERVER_PLATFORM = "SQL_SERVER"

# Connection mode constants
IPC_CONNECTION_MODE = "ipc"
CONFIG_FILE_CONNECTION_MODE = "config_file"

# Module name patterns for platform detection
SQLSERVER_MODULE_PATTERNS = ["sqlserver", "sql_server"]

# ----- GENERAL CONNECTION FIELD DESCRIPTIONS -----

# General field descriptions that can be reused across different database connections
CONNECTION_NAME_DESC = "The name of the saved connection"
HOST_DESC = "The hostname or IP address of the server"
PORT_DESC = "The port number on which the server is listening"
USERNAME_DESC = "The username for authentication"
PASSWORD_DESC = "The password for authentication"
DATABASE_DESC = "The name of the database to connect to"

# Error message templates
ERROR_MESSAGE_TEMPLATE = "[{platform}] {operation} for table: {table_name}."
