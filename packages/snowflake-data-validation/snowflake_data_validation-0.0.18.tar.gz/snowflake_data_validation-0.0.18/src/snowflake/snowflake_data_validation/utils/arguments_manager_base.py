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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from snowflake.snowflake_data_validation.configuration.configuration_loader import (
    ConfigurationLoader,
)
from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.configuration.model.connection_types import (
    Connection,
)
from snowflake.snowflake_data_validation.configuration.model.connections import (
    SnowflakeDefaultConnection,
    SnowflakeNamedConnection,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.connection_pool import (
    create_connection_pool_manager,
)
from snowflake.snowflake_data_validation.utils.console_output_handler import (
    ConsoleOutputHandler,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COLUMN_DATATYPES_MAPPING_NAME_FORMAT,
    COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT,
    COLUMN_METRICS_TEMPLATE_NAME_FORMAT,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    ExecutionMode,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.helper import Helper
from snowflake.snowflake_data_validation.utils.logging_config import (
    relocate_log_file,
)
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)
from snowflake.snowflake_data_validation.utils.run_context import RunContext


@dataclass
class ValidationEnvironmentObject:

    """Container for all components needed by the orchestrator."""

    source_connection_config: Connection
    target_connection_config: Connection
    context: Context

    def create_connection_pool_manager(self, pool_size: int = 1):
        """Create a connection pool manager for threaded processing.

        Args:
            pool_size: Number of connection pairs to maintain in the pool

        Returns:
            ConnectionPoolManager: Configured connection pool manager

        """
        return create_connection_pool_manager(
            source_platform=self.context.source_platform,
            target_platform=self.context.target_platform,
            source_connection_config=self.source_connection_config,
            target_connection_config=self.target_connection_config,
            pool_size=pool_size,
        )


class ArgumentsManagerBase(ABC):

    """Abstract base class for dialect-specific argument managers."""

    def __init__(self, source_platform: Platform, target_platform: Platform):
        """Initialize the arguments manager with source and target platform identifiers.

        Args:
            source_platform (Platform): The source platform enum (e.g., Platform.SNOWFLAKE, Platform.SQLSERVER).
            target_platform (Platform): The target platform enum (e.g., Platform.SNOWFLAKE, Platform.SQLSERVER).

        """
        self.source_platform = source_platform
        self.target_platform = target_platform

    @abstractmethod
    def create_validation_environment_from_config(
        self,
        config_model: ConfigurationModel,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_handler: Optional[ConsoleOutputHandler] = None,
    ) -> ValidationEnvironmentObject:
        """Create a complete validation environment from configuration model.

        Args:
            config_model: The loaded configuration model
            data_validation_config_file: Path to the config file
            execution_mode: Execution mode for the validation process
            output_handler: Optional output handler

        Returns:
            ValidationEnvironmentObject: Validation environment ready to run

        Raises:
            typer.BadParameter: If configuration is invalid
            ValueError: If required connections are missing

        """
        pass

    @abstractmethod
    def get_source_templates_path(self) -> str:
        """Get the path to dialect-specific templates.

        Returns:
            str: Path to source templates directory

        """
        pass

    @abstractmethod
    def get_target_templates_path(self) -> str:
        """Get the path to target dialect-specific templates.

        Returns:
            str: Path to target templates directory

        """
        pass

    @property
    @abstractmethod
    def is_snowflake_to_snowflake(self) -> bool:
        """Check if this is a Snowflake-to-Snowflake validation scenario.

        Returns:
            bool: True if both source and target are Snowflake

        """
        pass

    def setup_validation_environment(
        self,
        source_connection_config: Connection,
        target_connection_config: Connection,
        data_validation_config_file: str,
        execution_mode: ExecutionMode,
        output_directory_path: Optional[str] = None,
        output_handler: Optional[OutputHandlerBase] = None,
    ) -> ValidationEnvironmentObject:
        """Set up the validation environment with context and all necessary components.

        Args:
            source_connection_config: Source connection configuration
            target_connection_config: Target connection configuration
            data_validation_config_file: Path to validation configuration
            execution_mode: Execution mode for the validation process
            output_directory_path: Optional path for output directory (reports, logs, etc.)
            output_handler: Optional custom output handler

        Returns:
            ValidationEnvironmentObject: Complete environment ready for orchestrator

        """
        # Load configuration model
        configuration = self.load_configuration(data_validation_config_file)

        # Set up temporary directories for execution
        execution_temp_dir = Helper.create_temp_dir()

        if output_directory_path is not None:
            output_directory_path_ = output_directory_path
        elif configuration.output_directory_path:
            output_directory_path_ = configuration.output_directory_path
        else:
            output_directory_path_ = os.path.join(execution_temp_dir, "reports")

        templates_temp_dir_path = os.path.join(execution_temp_dir, "templates")

        for directory in [output_directory_path_, templates_temp_dir_path]:
            os.makedirs(directory, exist_ok=True)

        # Relocate log file to the configured output directory
        relocate_log_file(output_directory_path_)

        # Get templates paths
        source_templates_path = self.get_source_templates_path()
        target_templates_path = self.get_target_templates_path()

        Helper.copy_templates_to_temp_dir(
            source_templates_path, target_templates_path, templates_temp_dir_path
        )

        # Set up output handler
        if not output_handler:
            output_handler = ConsoleOutputHandler()

        # Initialize run context
        run_context = RunContext()
        run_context.initialize_run()
        run_id = run_context.run_id
        run_start_time = run_context.run_start_time

        source_template_loader_manager = TemplatesLoaderManager(
            templates_directory_path=Path(self.get_source_templates_path()),
            platform=self.source_platform,
            custom_templates_directory_path=configuration.validation_configuration.custom_templates_path,
        )

        target_template_loader_manager = TemplatesLoaderManager(
            templates_directory_path=Path(self.get_target_templates_path()),
            platform=self.target_platform,
            custom_templates_directory_path=configuration.validation_configuration.custom_templates_path,
        )

        source_templates_dir_path = Path(self.get_source_templates_path())
        # Load datatypes mapping template from the appropriate location
        datatypes_file_name = COLUMN_DATATYPES_MAPPING_NAME_FORMAT.format(
            source_platform=self.source_platform.value,
            target_platform=self.target_platform.value,
        )

        # Determine the correct path for the datatypes mapping file
        datatypes_file_path = self._resolve_datatypes_mapping_path(
            custom_templates_path=configuration.validation_configuration.custom_templates_path,
            default_templates_path=source_templates_dir_path,
            file_name=datatypes_file_name,
        )

        # Load the datatypes mappings from the resolved path
        datatypes_mappings = Helper.load_datatypes_mapping_templates_from_yaml(
            yaml_path=datatypes_file_path
        )

        context = Context(
            configuration=configuration,
            report_path=output_directory_path_,
            templates_dir_path=templates_temp_dir_path,
            source_platform=self.source_platform,
            target_platform=self.target_platform,
            custom_output_handler=output_handler,
            run_id=run_id,
            run_start_time=run_start_time,
            source_templates=source_template_loader_manager,
            target_templates=target_template_loader_manager,
            execution_mode=execution_mode,
            datatypes_mappings=datatypes_mappings,
        )

        return ValidationEnvironmentObject(
            source_connection_config=source_connection_config,
            target_connection_config=target_connection_config,
            context=context,
        )

    def load_configuration(
        self, data_validation_config_file: str
    ) -> ConfigurationModel:
        """Load the configuration model from the specified YAML file.

        Args:
            data_validation_config_file (str): Path to the configuration YAML file.

        Returns:
            ConfigurationModel: Loaded configuration model.

        """
        config_loader = ConfigurationLoader(Path(data_validation_config_file))
        return config_loader.get_configuration_model()

    def dump_and_write_yaml_templates(
        self, source: str, templates_directory: str
    ) -> None:
        """Dump and write YAML templates to specified output files.

        This function iterates over the list of template paths,
        dumps their content, and writes it to the specified output files.

        Args:
            source (str): The source platform identifier (e.g., 'snowflake', 'sqlserver').
            templates_directory (str): The directory where the templates will be written.

        """
        templates_path = self.get_source_templates_path()
        target_templates_path = self.get_target_templates_path()
        templates = []
        # dump from source
        # Collect templates from source if not Snowflake
        if source != Platform.SNOWFLAKE.value:
            templates += [
                os.path.join(
                    templates_path,
                    COLUMN_DATATYPES_MAPPING_NAME_FORMAT.format(
                        source_platform=source, target_platform=Platform.SNOWFLAKE.value
                    ),
                ),
                os.path.join(
                    templates_path,
                    COLUMN_METRICS_TEMPLATE_NAME_FORMAT.format(platform=source),
                ),
                os.path.join(
                    templates_path,
                    COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT.format(
                        platform=source
                    ),
                ),
            ]
        # Always collect Snowflake templates from target
        templates += [
            os.path.join(
                target_templates_path,
                COLUMN_METRICS_TEMPLATE_NAME_FORMAT.format(
                    platform=Platform.SNOWFLAKE.value
                ),
            ),
            os.path.join(
                target_templates_path,
                COLUMN_DATATYPES_NORMALIZATION_TEMPLATES_NAME_FORMAT.format(
                    platform=Platform.SNOWFLAKE.value
                ),
            ),
        ]

        for template in templates:
            self._dump_and_write_yaml_template(
                template, output_directory=templates_directory
            )

    @staticmethod
    def _dump_and_write_yaml_template(template_path: str, output_directory: str) -> str:
        """Dump the content of a YAML template file to a new file.

        Args:
            template_path (str): The path to the YAML template file.
            output_directory (str): The directory where the output file will be written.

        Returns:
            str: The path to the output file where the content was written.

        """
        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)
        with open(template_path, encoding="utf-8") as f:
            content = yaml.safe_load(f)
        output_file = os.path.join(output_directory, os.path.basename(template_path))
        with open(output_file, "w", encoding="utf-8") as out_f:
            yaml.dump(content, out_f, default_flow_style=False)
        return str(output_file)

    def _resolve_datatypes_mapping_path(
        self,
        custom_templates_path: Optional[Path],
        default_templates_path: Path,
        file_name: str,
    ) -> Path:
        """Resolve the correct path for a datatypes mapping file, checking custom directory first if available.

        Args:
            custom_templates_path (Optional[Path]): Path to custom templates directory, if specified.
            default_templates_path (Path): Path to default templates directory.
            file_name (str): Name of the file to resolve.

        Returns:
            Path: The resolved path to the mapping file, prioritizing custom templates when available.

        """
        # Use default path if no custom path is specified
        if not custom_templates_path:
            return default_templates_path.joinpath(file_name)

        # Check if the file exists in the custom templates directory
        custom_file_path = custom_templates_path.joinpath(file_name)
        if custom_file_path.exists():
            return custom_file_path

        # Fall back to default path if not found in custom directory
        return default_templates_path.joinpath(file_name)

    def _setup_target_connection_config_from_config(
        self, config_model: ConfigurationModel
    ):
        """Consolidated method to setup target connection configuration from config model.

        This method handles the common logic for all platforms.
        """
        if not config_model.target_connection:
            raise ValueError(
                "No target connection configured in YAML file. "
                "Please add a target_connection section to your configuration file."
            )

        target_conn = config_model.target_connection
        target_platform = config_model.target_platform or "Snowflake"

        if target_platform.lower() != "snowflake":
            platform_name = self.__class__.__name__.replace("ArgumentsManager", "")
            raise ValueError(
                f"{platform_name} arguments manager only supports Snowflake as target platform, got: {target_platform}"
            )

        mode = getattr(target_conn, "mode", NAME_CONNECTION_MODE)
        if mode == NAME_CONNECTION_MODE:
            return SnowflakeNamedConnection(
                mode=NAME_CONNECTION_MODE,
                name=getattr(target_conn, "name", None),
            )
        elif mode == DEFAULT_CONNECTION_MODE:
            return SnowflakeDefaultConnection(
                mode=DEFAULT_CONNECTION_MODE,
            )
        else:
            raise ValueError(
                f"Unsupported target connection mode for Snowflake: {mode}. "
                "Supported modes are 'name' and 'default'. Use IPC commands for credentials mode."
            )
