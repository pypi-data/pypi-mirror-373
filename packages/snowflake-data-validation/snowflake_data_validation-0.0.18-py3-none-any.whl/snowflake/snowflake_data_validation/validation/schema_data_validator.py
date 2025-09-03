import logging

import pandas as pd

from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_VALIDATED,
    COLUMN_VALIDATED_KEY,
    COMMENTS_KEY,
    EVALUATION_CRITERIA_KEY,
    NOT_EXIST_TARGET,
    SNOWFLAKE_VALUE_KEY,
    SOURCE_VALUE_KEY,
    STATUS_KEY,
    TABLE_KEY,
    VALIDATION_TYPE_KEY,
    Result,
    ValidationLevel,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.helpers.helper_misc import HelperMisc
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.validation.data_validator_base import (
    DataValidatorBase,
)


LOGGER = logging.getLogger(__name__)


class SchemaDataValidator(DataValidatorBase):
    @log
    def validate_table_metadata(
        self,
        object_name: str,
        target_df: pd.DataFrame,
        source_df: pd.DataFrame,
        context: Context,
        columns_mappings: dict[str, str],
    ) -> bool:
        """Validate the metadata of two tables by normalizing and comparing their dataframes.

        Args:
            object_name (str): The name of the object (e.g., table) being validated.
            target_df (pd.DataFrame): The dataframe representing the target table's metadata.
            source_df (pd.DataFrame): The dataframe representing the source table's metadata.
            context (Context): The execution context containing relevant configuration and runtime information.
            columns_mappings (dict[str, str]): A dictionary mapping source column names to target column names.

        Returns:
            bool: True if the normalized dataframes are equal, False otherwise.

        """
        LOGGER.info("Starting table metadata validation for: %s", object_name)
        context.output_handler.handle_message(
            message=f"Running Schema Validation for {object_name}",
            level=OutputMessageLevel.INFO,
        )

        LOGGER.debug("Normalizing target and source DataFrames")
        normalized_target = self.normalize_dataframe(target_df)
        normalized_source = self.normalize_dataframe(source_df)

        differences_data = pd.DataFrame(
            columns=[
                VALIDATION_TYPE_KEY,
                TABLE_KEY,
                COLUMN_VALIDATED_KEY,
                EVALUATION_CRITERIA_KEY,
                SOURCE_VALUE_KEY,
                SNOWFLAKE_VALUE_KEY,
                STATUS_KEY,
                COMMENTS_KEY,
            ]
        )

        # Handle case where target DataFrame is empty (no metadata found)
        if normalized_target.empty or COLUMN_VALIDATED not in normalized_target.columns:
            LOGGER.warning(
                "Target table schema metadata is empty or missing COLUMN_VALIDATED column for table: %s",
                object_name,
            )
            uppercase_target_validated_set = set()
        else:
            uppercase_target_validated_set = HelperMisc.create_uppercase_set(
                normalized_target[COLUMN_VALIDATED].values
            )

        for _, source_row in normalized_source.iterrows():
            source_validated_value = source_row[COLUMN_VALIDATED]

            # Handle missing columns in target
            source_validated_value = columns_mappings.get(
                source_validated_value, source_validated_value
            )
            if source_validated_value not in uppercase_target_validated_set:
                LOGGER.debug(
                    "Column %s not found in target table", source_validated_value
                )
                new_row = self.create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=NOT_EXIST_TARGET,
                    status=Result.FAILURE.value,
                    comments="The column does not exist in the target table.",
                )
                differences_data = self.add_validation_row_to_data(
                    differences_data, new_row
                )
                continue

            # Validate existing columns
            if (
                normalized_target.empty
                or COLUMN_VALIDATED not in normalized_target.columns
            ):
                continue

            target_row = normalized_target[
                normalized_target[COLUMN_VALIDATED].str.upper()
                == source_validated_value
            ]
            column_has_differences = False

            for column in normalized_source.columns:
                # Skip irrelevant columns
                if column in {COLUMN_VALIDATED, TABLE_KEY}:
                    continue

                source_value = source_row[column]
                target_value = target_row[column].values[0]

                validation_row, field_success = self.validate_column_field(
                    column,
                    source_value,
                    target_value,
                    context,
                    object_name,
                    source_validated_value,
                )

                if not validation_row.empty:
                    differences_data = self.add_validation_row_to_data(
                        differences_data, validation_row
                    )

                if not field_success:
                    column_has_differences = True

            # Record overall column success if no field differences found
            if not column_has_differences:
                success_row = self.create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=source_validated_value,
                    status=Result.SUCCESS.value,
                    comments="Column exists in target table and all metadata matches.",
                )
                differences_data = self.add_validation_row_to_data(
                    differences_data, success_row
                )

        # Determine if there are actual failures (excluding WARNING status)
        failure_rows = differences_data[
            differences_data[STATUS_KEY] == Result.FAILURE.value
        ]
        has_failures = len(failure_rows) > 0

        # Process and output validation results
        self.process_validation_results(
            validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
            differences_data=differences_data,
            object_name=object_name,
            header="Schema validation results:",
            has_differences=has_failures,
            context=context,
        )

        return not has_failures
