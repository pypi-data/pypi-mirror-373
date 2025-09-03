from pathlib import Path
from typing import Union

import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT,
    COLUMN_METRICS_TEMPLATE_NAME_FORMAT,
    Platform,
)
from snowflake.snowflake_data_validation.utils.helper import Helper


class TemplatesLoaderManager:

    """A class to manage the loading of templates from a specified directory."""

    def __init__(
        self,
        templates_directory_path: Path,
        platform: Platform,
        custom_templates_directory_path: Union[Path, None] = None,
    ):
        """Initialize the TemplatesLoaderManager with the directory path and platform.

        Args:
            templates_directory_path (Path): The path to the directory containing the templates.
            platform (Platform): The source platform for which the templates are being loaded.
            custom_templates_directory_path (Union[Path, None]): Optional path to a custom directory
                containing templates. If provided, it will be checked first for templates.

        """
        self.templates_directory_path: Path = templates_directory_path
        self.platform: Platform = platform
        self.custom_templates_directory_path: Union[
            Path, None
        ] = custom_templates_directory_path

        if self.templates_directory_path is not None and self.platform is not None:
            self.datatypes_normalization_templates: dict[
                str, str
            ] = self._load_datatypes_normalization_templates()
            self.metrics_templates: pd.DataFrame = self._load_metrics_templates()
        else:
            self.datatypes_normalization_templates = {}
            self.metrics_templates = pd.DataFrame()

    def _get_template_path(self, template_name_format: str) -> Path:
        """Get the template path, checking custom directory first if available.

        Args:
            template_name_format (str): Format string for the template file name.

        Returns:
            Path: The path to the template file to use.

        """
        file_name = template_name_format.format(platform=self.platform.value)
        default_path = self.templates_directory_path.joinpath(file_name)

        # If no custom directory is specified, use default
        if not self.custom_templates_directory_path:
            return default_path

        # Check if template exists in custom directory
        custom_path = self.custom_templates_directory_path.joinpath(file_name)
        return custom_path if custom_path.exists() else default_path

    def _load_datatypes_normalization_templates(self) -> dict[str, str]:
        """Load the datatypes normalization templates from the specified directory.

        Returns:
            dict[str, str]: A dictionary containing the datatypes normalization templates.

        """
        template_path = self._get_template_path(
            COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT
        )
        return Helper.load_datatypes_normalization_templates_from_yaml(
            yaml_path=template_path
        )

    def _load_metrics_templates(self) -> pd.DataFrame:
        """Load the metrics templates from the specified directory.

        Returns:
            pd.DataFrame: A DataFrame containing the metrics templates.

        """
        template_path = self._get_template_path(COLUMN_METRICS_TEMPLATE_NAME_FORMAT)

        return Helper.load_metrics_templates_from_yaml(
            yaml_path=template_path,
            datatypes_normalization_templates=self.datatypes_normalization_templates,
        )
