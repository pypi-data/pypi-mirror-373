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

from pathlib import Path

import pandas as pd
import yaml

from snowflake.snowflake_data_validation.utils.constants import (
    COL_NAME_QUOTES_PLACEHOLDER,
    EDITABLE_YAML_FILE_FORMAT_ERROR,
    METRIC_COLUMN_KEY,
    METRIC_NORMALIZATION_KEY,
    METRIC_QUERY_KEY,
    METRIC_QUERY_PLACEHOLDER,
    METRIC_RETURN_DATATYPE_KEY,
    NORMALIZATION_COLUMN_KEY,
    TEMPLATE_COLUMN_KEY,
    TYPE_COLUMN_KEY,
)


class HelperTemplates:

    """Helper class for loading and processing templates from YAML files."""

    @staticmethod
    def load_metrics_templates_from_yaml(
        yaml_path: Path, datatypes_normalization_templates: dict[str, str]
    ) -> pd.DataFrame:
        """Load metrics templates from a YAML file into a pandas DataFrame.

        Args:
            yaml_path (Path): The file path to the YAML file.
            datatypes_normalization_templates (dict[str, str]): A dictionary containing
            normalization templates for data types.

        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
            KeyError: If a required key is missing in the YAML data.
            RuntimeError: If there is an error in the format of the YAML file.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the YAML file.

        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Template file not found at: {yaml_path}")

        try:
            file_content = yaml_path.read_text()
            yaml_data = yaml.safe_load(file_content)
            yaml_data_reformatted = HelperTemplates._reformat_metrics_yaml_data(
                yaml_data=yaml_data,
                datatypes_normalization_templates=datatypes_normalization_templates,
            )
            df = pd.DataFrame.from_dict(yaml_data_reformatted)

        except KeyError as e:
            error_message = (
                f"Missing {e.args[0]} datatype in datatypes normalization file."
            )
            raise RuntimeError(error_message) from e

        except Exception as e:
            error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(
                file_name=yaml_path.name
            )
            raise RuntimeError(error_message) from e

        return df

    @staticmethod
    def load_datatypes_templates_from_yaml(
        yaml_path: Path, platform: str
    ) -> pd.DataFrame:
        """Load datatypes templates from a YAML file into a pandas DataFrame.

        Args:
            yaml_path (Path): The file path to the YAML file.
            platform (str): The platform identifier to use.

        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
            RuntimeError: If there is an error in the format of the YAML file.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the YAML file.

        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Template file not found at: {yaml_path}")

        try:
            file_content = yaml_path.read_text()
            yaml_data = yaml.safe_load(file_content)
            yaml_data_reformatted = HelperTemplates._reformat_datatypes_yaml_data(
                yaml_data, platform
            )
            df = pd.DataFrame.from_dict(yaml_data_reformatted)

        except Exception as e:
            error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(
                file_name=yaml_path.name
            )
            raise RuntimeError(error_message) from e

        return df

    @staticmethod
    def load_datatypes_normalization_templates_from_yaml(
        yaml_path: Path,
    ) -> dict[str, str]:
        """Load datatypes normalization templates from a YAML file into a pandas DataFrame.

        Args:
            yaml_path (Path): The file path to the YAML file.

        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
            RuntimeError: If there is an error in the format of the YAML file.

        Returns:
            dict[str, str]: A dictionary containing the data from the YAML file.

        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Template file not found at: {yaml_path}")

        try:
            file_content = yaml_path.read_text()
            yaml_data = yaml.safe_load(file_content)
            yaml_data_reformatted = {
                key.upper(): yaml_data[key] for key in yaml_data.keys()
            }

        except Exception as e:
            error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(
                file_name=yaml_path.name
            )
            raise RuntimeError(error_message) from e

        return yaml_data_reformatted

    @staticmethod
    def _reformat_datatypes_yaml_data(
        yaml_data: dict, platform: str
    ) -> dict[str, list[str]]:
        """Reformat YAML data to ensure it is in a consistent format.

        Args:
            yaml_data (dict): The original YAML data.
            platform (str): The platform identifier to use.

        Raises:
            ValueError: If the YAML data does not contain the expected structure.

        Returns:
            dict: The reformatted YAML data.

        """
        source_platform_data_types_collection = list(yaml_data.keys())
        platform_data_types_dict_collection = {
            str.lower(platform): source_platform_data_types_collection
        }
        temporal_platform_data_types_dict_collection = {}
        for source_data_type in source_platform_data_types_collection:
            for target_data_type in yaml_data[source_data_type]:
                if (
                    temporal_platform_data_types_dict_collection.get(target_data_type)
                    is None
                ):
                    temporal_platform_data_types_dict_collection[target_data_type] = []
                current_data_type = yaml_data[source_data_type][target_data_type]
                temporal_platform_data_types_dict_collection[target_data_type].append(
                    current_data_type
                )

        platform_data_types_dict_collection.update(
            temporal_platform_data_types_dict_collection
        )
        return platform_data_types_dict_collection

    @staticmethod
    def _reformat_metrics_yaml_data(
        yaml_data: dict, datatypes_normalization_templates: dict[str, str]
    ) -> dict[str, list[str]]:
        """Reformat YAML data to ensure it is in a consistent format.

        Args:
            yaml_data (dict): The original YAML data.
            datatypes_normalization_templates (dict[str, str]): A dictionary containing
            normalization templates for data types.

        Raises:
            ValueError: If the YAML data does not contain the expected structure.

        Returns:
            dict: The reformatted YAML data.

        """
        type_column = []
        metric_column = []
        metric_template_column = []
        metric_normalization_template_column = []

        data_type_collection = list(yaml_data.keys())
        for data_type in data_type_collection:
            metric_name_collection = list(yaml_data[data_type].keys())
            template_collection = list(yaml_data[data_type].values())
            for metric_name, templates in zip(
                metric_name_collection, template_collection
            ):
                type_column.append(data_type.upper())
                metric_column.append(metric_name)
                metric_template_column.append(templates[METRIC_QUERY_KEY])

                if templates.get(METRIC_NORMALIZATION_KEY, None) is not None:
                    metric_normalization_template_column.append(
                        templates[METRIC_NORMALIZATION_KEY]
                    )
                else:
                    metric_return_datatype = templates[METRIC_RETURN_DATATYPE_KEY]
                    normalization_template = datatypes_normalization_templates[
                        metric_return_datatype.upper()
                    ]
                    normalization_template_normalized = normalization_template.replace(
                        COL_NAME_QUOTES_PLACEHOLDER, METRIC_QUERY_PLACEHOLDER
                    )
                    metric_normalization_template_column.append(
                        normalization_template_normalized
                    )

        type_metric_dict_collection = {
            TYPE_COLUMN_KEY: type_column,
            METRIC_COLUMN_KEY: metric_column,
            TEMPLATE_COLUMN_KEY: metric_template_column,
            NORMALIZATION_COLUMN_KEY: metric_normalization_template_column,
        }

        return type_metric_dict_collection

    @staticmethod
    def load_datatypes_mapping_templates_from_yaml(yaml_path: Path) -> dict[str, str]:
        """Load datatypes mapping templates from a YAML file into a dictionary.

        Args:
            yaml_path (Path): The file path to the YAML file.

        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
            RuntimeError: If there is an error in the format of the YAML file.

        Returns:
            dict[str, str]: A dictionary containing the data from the YAML file.

        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Template file not found at: {yaml_path}")

        try:
            file_content = yaml_path.read_text()
            if len(file_content) == 0:
                return {}

            yaml_data = yaml.safe_load(file_content)

        except Exception as e:
            error_message = EDITABLE_YAML_FILE_FORMAT_ERROR.format(
                file_name=yaml_path.name
            )
            raise RuntimeError(error_message) from e

        return yaml_data
