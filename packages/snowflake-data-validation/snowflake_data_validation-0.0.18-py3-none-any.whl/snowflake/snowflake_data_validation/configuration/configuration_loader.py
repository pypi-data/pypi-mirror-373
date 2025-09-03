from pathlib import Path

from pydantic_yaml import parse_yaml_raw_as

from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.configuration.singleton import Singleton


class ConfigurationLoader(metaclass=Singleton):

    """ConfigurationLoader class.

    This is a singleton class that reads the configuration.yaml file
    and provides an interface to get the configuration settings model.

    Args:
        metaclass (Singleton, optional): Defaults to Singleton.

    """

    def __init__(self, file_path: Path) -> None:
        self.configuration_model: ConfigurationModel = ConfigurationModel(
            source_platform="",
            target_platform="",
            output_directory_path="",
        )

        if file_path is None:
            raise ValueError("The configuration file path cannot be None value")

        if not (file_path.suffix == ".yaml" or file_path.suffix == ".yml"):
            raise Exception(
                "The configuration file must have a .yaml or .yml extension"
            )

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found in {file_path}")

        try:
            file_content = file_path.read_text()
            self.configuration_model = parse_yaml_raw_as(
                ConfigurationModel, file_content
            )

        except Exception as exception:
            error_msg = "An error occurred while loading the configuration file:"
            raise Exception(f"{error_msg}\n{exception}") from None

    def get_configuration_model(self) -> ConfigurationModel:
        """Get the configuration model.

        Returns:
            ConfigurationModel: The configuration model instance.

        """
        return self.configuration_model
