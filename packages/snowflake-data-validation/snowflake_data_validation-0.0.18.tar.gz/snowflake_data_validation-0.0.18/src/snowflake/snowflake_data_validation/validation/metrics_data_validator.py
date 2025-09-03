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


class MetricsDataValidator(DataValidatorBase):
    @log
    def validate_column_metadata(
        self,
        object_name: str,
        target_df: pd.DataFrame,
        source_df: pd.DataFrame,
        context: Context,
        columns_mappings: dict[str, str],
        tolerance: float = 0.001,
    ) -> bool:
        """Validate that the column metadata of the target DataFrame matches the source DataFrame.

        This method normalizes both the target and source DataFrames and then compares their
        column metadata cell by cell to ensure they are equivalent within a given tolerance.

        Args:
            object_name (str): The name of the object (e.g., table) being validated.
            target_df (pd.DataFrame): The target DataFrame whose column metadata is to be validated.
            source_df (pd.DataFrame): The source DataFrame to compare against.
            context (Context): The execution context containing relevant configuration and runtime information.
            columns_mappings (dict[str, str]): A dictionary mapping source column names to target column names.
            tolerance (float, optional): The tolerance level for numerical differences. Defaults to 0.001.

        Returns:
            bool: True if the column metadata of both DataFrames are equal within the tolerance, False otherwise.

        """
        LOGGER.info(
            "Starting column metadata validation for: %s with tolerance: %f",
            object_name,
            tolerance,
        )
        context.output_handler.handle_message(
            message=f"Running Metrics Validation for {object_name}",
            level=OutputMessageLevel.INFO,
        )

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
        if normalized_target.empty or COLUMN_VALIDATED not in normalized_target.columns:
            LOGGER.warning(
                "Target table metrics metadata is empty or missing COLUMN_VALIDATED column for table: %s",
                object_name,
            )
            uppercase_target_validated_set = set()
        else:
            uppercase_target_validated_set = HelperMisc.create_uppercase_set(
                normalized_target[COLUMN_VALIDATED].values
            )

        has_differences = False

        for _, source_row in normalized_source.iterrows():
            column_name = source_row[COLUMN_VALIDATED]
            source_validated_value = source_row[COLUMN_VALIDATED]
            source_validated_value = columns_mappings.get(
                source_validated_value, source_validated_value
            )

            if source_validated_value not in uppercase_target_validated_set:
                new_row = self.create_validation_row(
                    validation_type=ValidationLevel.METRICS_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=NOT_EXIST_TARGET,
                    status=Result.FAILURE.value,
                    comments="The column does not exist in the target table.",
                )
                differences_data = pd.concat(
                    [differences_data, new_row], ignore_index=True
                )
                has_differences = True
            else:
                target_row = normalized_target[
                    normalized_target[COLUMN_VALIDATED].str.upper()
                    == source_validated_value
                ]

                column_has_differences = False

                for col in normalized_source.columns:
                    if col == COLUMN_VALIDATED:
                        continue

                    source_value = source_row[col]
                    target_value = target_row[col].values[0]

                    # Skip if both values are NaN or identical
                    if pd.isna(source_value) and pd.isna(target_value):
                        # Record successful validation for NaN values
                        success_row = self.create_validation_row(
                            validation_type=ValidationLevel.METRICS_VALIDATION.value,
                            table_name=object_name,
                            column_validated=column_name,
                            evaluation_criteria=col,
                            source_value="NULL",
                            snowflake_value="NULL",
                            status=Result.SUCCESS.value,
                            comments="Both values are NULL/NaN - validation passed",
                        )
                        differences_data = pd.concat(
                            [differences_data, success_row], ignore_index=True
                        )
                        continue
                    if source_value == target_value:
                        # Record successful validation for exact matches
                        success_row = self.create_validation_row(
                            validation_type=ValidationLevel.METRICS_VALIDATION.value,
                            table_name=object_name,
                            column_validated=column_name,
                            evaluation_criteria=col,
                            source_value=str(source_value),
                            snowflake_value=str(target_value),
                            status=Result.SUCCESS.value,
                            comments=f"Values match exactly: {source_value}",
                        )
                        differences_data = pd.concat(
                            [differences_data, success_row], ignore_index=True
                        )
                        continue

                    # Check numeric values with tolerance
                    if self.is_numeric(source_value) and self.is_numeric(target_value):
                        source_num = float(source_value)
                        target_num = float(target_value)
                        if abs(source_num - target_num) <= tolerance:
                            # Record successful validation within tolerance
                            success_row = self.create_validation_row(
                                validation_type=ValidationLevel.METRICS_VALIDATION.value,
                                table_name=object_name,
                                column_validated=column_name,
                                evaluation_criteria=col,
                                source_value=str(source_value),
                                snowflake_value=str(target_value),
                                status=Result.SUCCESS.value,
                                comments=(
                                    f"Values within tolerance ({tolerance}): "
                                    f"source({source_value}), target({target_value})"
                                ),
                            )
                            differences_data = pd.concat(
                                [differences_data, success_row], ignore_index=True
                            )
                            continue
                        comment = (
                            f"Values differ beyond tolerance of {tolerance}: "
                            f"source({source_value}), target({target_value})"
                        )
                    else:
                        comment = f"Values differ: source({source_value}), target({target_value})"

                    column_has_differences = True
                    has_differences = True
                    new_row = self.create_validation_row(
                        validation_type=ValidationLevel.METRICS_VALIDATION.value,
                        table_name=object_name,
                        column_validated=column_name,
                        evaluation_criteria=col,
                        source_value=str(source_value),
                        snowflake_value=str(target_value),
                        status=Result.FAILURE.value,
                        comments=comment,
                    )
                    differences_data = pd.concat(
                        [differences_data, new_row], ignore_index=True
                    )

                # If the column exists and had no differences, record overall column success
                if not column_has_differences:
                    success_row = self.create_validation_row(
                        validation_type=ValidationLevel.METRICS_VALIDATION.value,
                        table_name=object_name,
                        column_validated=column_name,
                        evaluation_criteria=COLUMN_VALIDATED,
                        source_value=source_validated_value,
                        snowflake_value=source_validated_value,
                        status=Result.SUCCESS.value,
                        comments="Column exists in target table and all metrics match.",
                    )
                    differences_data = pd.concat(
                        [differences_data, success_row], ignore_index=True
                    )

        # Process and output validation results
        self.process_validation_results(
            validation_type=ValidationLevel.METRICS_VALIDATION.value,
            differences_data=differences_data,
            object_name=object_name,
            header="Metrics validation results:",
            has_differences=has_differences,
            context=context,
        )

        return not has_differences
