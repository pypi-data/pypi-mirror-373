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

import logging

from dataclasses import dataclass
from typing import Union

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.executer.async_generation_executor import (
    AsyncGenerationExecutor,
)
from snowflake.snowflake_data_validation.executer.async_validation_executor import (
    AsyncValidationExecutor,
)
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
)
from snowflake.snowflake_data_validation.executer.extractor_types import (
    ExtractorType,
)
from snowflake.snowflake_data_validation.executer.sync_validation_executor import (
    SyncValidationExecutor,
)
from snowflake.snowflake_data_validation.extractor.metadata_extractor_base import (
    MetadataExtractorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.redshift.extractor.metadata_extractor_redshift import MetadataExtractorRedshift
from snowflake.snowflake_data_validation.redshift.query.query_generator_redshift import QueryGeneratorRedshift
from snowflake.snowflake_data_validation.redshift.script_writer.script_writer_redshift import ScriptWriterRedshift
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)
from snowflake.snowflake_data_validation.snowflake.extractor.metadata_extractor_snowflake import (
    MetadataExtractorSnowflake,
)
from snowflake.snowflake_data_validation.snowflake.query.query_generator_snowflake import (
    QueryGeneratorSnowflake,
)
from snowflake.snowflake_data_validation.snowflake.script_writer.script_writer_snowflake import (
    ScriptWriterSnowflake,
)
from snowflake.snowflake_data_validation.sqlserver.extractor.metadata_extractor_sqlserver import (
    MetadataExtractorSQLServer,
)
from snowflake.snowflake_data_validation.sqlserver.query.query_generator_sqlserver import (
    QueryGeneratorSqlServer,
)
from snowflake.snowflake_data_validation.sqlserver.script_writer.script_writer_sqlserver import (
    ScriptWriterSQLServer,
)
from snowflake.snowflake_data_validation.teradata.extractor.metadata_extractor_teradata import (
    MetadataExtractorTeradata,
)
from snowflake.snowflake_data_validation.teradata.query.query_generator_teradata import (
    QueryGeneratorTeradata,
)
from snowflake.snowflake_data_validation.teradata.script_writer.script_writer_teradata import (
    ScriptWriterTeradata,
)
from snowflake.snowflake_data_validation.utils.constants import (
    ExecutionMode,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log


LOGGER = logging.getLogger(__name__)


@dataclass
class PlatformConfig:

    """Configuration for platform-specific components."""

    query_generator: type[QueryGeneratorBase]
    metadata_extractor: type[MetadataExtractorBase]
    script_writer: type[ScriptWriterBase]


class ExecutorFactory:

    """Factory for creating validation executors based on execution mode."""

    @log
    def __init__(self, platform_configs: dict[Platform, PlatformConfig] = None):
        """Initialize the factory with platform configurations.

        Args:
            platform_configs: Optional custom platform configurations.
                             If None, default configurations will be used.

        """
        LOGGER.debug("Initializing ExecutorFactory")
        self._platform_configs = (
            platform_configs or self._get_default_platform_configs()
        )
        LOGGER.debug("ExecutorFactory initialized with platform configurations")

    @log
    def _get_default_platform_configs(self) -> dict[Platform, PlatformConfig]:
        """Get the default platform configurations.

        Returns:
            dict[Platform, PlatformConfig]: Default platform configurations

        """
        LOGGER.debug("Getting default platform configurations")
        return {
            Platform.SNOWFLAKE: PlatformConfig(
                query_generator=QueryGeneratorSnowflake,
                metadata_extractor=MetadataExtractorSnowflake,
                script_writer=ScriptWriterSnowflake,
            ),
            Platform.SQLSERVER: PlatformConfig(
                query_generator=QueryGeneratorSqlServer,
                metadata_extractor=MetadataExtractorSQLServer,
                script_writer=ScriptWriterSQLServer,
            ),
            Platform.TERADATA: PlatformConfig(
                query_generator=QueryGeneratorTeradata,
                metadata_extractor=MetadataExtractorTeradata,
                script_writer=ScriptWriterTeradata,
            ),
            Platform.REDSHIFT: PlatformConfig(
                query_generator=QueryGeneratorRedshift,
                metadata_extractor=MetadataExtractorRedshift,
                script_writer=ScriptWriterRedshift,
            )
        }

    @log
    def create_executor(
        self,
        execution_mode: ExecutionMode,
        source_extractor: Union[MetadataExtractorBase, ScriptWriterBase],
        target_extractor: Union[MetadataExtractorBase, ScriptWriterBase],
        context: Context,
    ) -> BaseValidationExecutor:
        """Create a validation executor based on the execution mode.

        Args:
            execution_mode: The execution mode for the validation
            source_extractor: Source extractor or script writer
            target_extractor: Target extractor or script writer
            context: Validation context containing configuration and runtime info

        Returns:
            BaseValidationExecutor: The appropriate executor for the execution mode

        Raises:
            ValueError: If execution mode is not supported

        """
        LOGGER.debug("Creating executor for execution mode: %s", execution_mode)

        if execution_mode == ExecutionMode.SYNC_VALIDATION:
            LOGGER.debug("Creating SyncValidationExecutor")
            return SyncValidationExecutor(
                source_extractor=source_extractor,
                target_extractor=target_extractor,
                context=context,
            )
        elif execution_mode == ExecutionMode.ASYNC_GENERATION:
            LOGGER.debug("Creating AsyncValidationExecutor")
            return AsyncGenerationExecutor(
                source_extractor=source_extractor,
                target_extractor=target_extractor,
                context=context,
            )
        elif execution_mode == ExecutionMode.ASYNC_VALIDATION:
            LOGGER.debug("Creating AsyncGenerationExecutor")
            return AsyncValidationExecutor(
                source_extractor=source_extractor,
                target_extractor=target_extractor,
                context=context,
            )
        else:
            error_msg = f"Unsupported execution mode: {execution_mode}"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)

    @log
    def create_extractor_from_connector(
        self,
        connector: ConnectorBase,
        extractor_type: ExtractorType,
        platform: Platform,
        report_path: str = "",
    ) -> Union[MetadataExtractorBase, ScriptWriterBase]:
        """Create an extractor instance from a connector based on the type and platform.

        Args:
            connector: Database connector instance
            extractor_type: Type of extractor to create
            platform: Platform enum (e.g., Platform.SNOWFLAKE, Platform.SQLSERVER)
            report_path: Optional path for output reports

        Returns:
            Union[MetadataExtractorBase, ScriptWriterBase]: Appropriate extractor instance

        Raises:
            ValueError: If the platform or extractor type is not supported

        """
        LOGGER.debug("Creating %s extractor for platform: %s", extractor_type, platform)

        if platform not in self._platform_configs:
            error_msg = f"Unsupported platform: {platform}"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)

        config = self._platform_configs[platform]
        query_generator = config.query_generator()
        LOGGER.debug("Created query generator for platform: %s", platform)

        # Select the appropriate extractor class based on type
        if extractor_type == ExtractorType.METADATA_EXTRACTOR:
            extractor_class = config.metadata_extractor
        elif extractor_type == ExtractorType.SCRIPT_WRITER:
            extractor_class = config.script_writer
        else:
            error_msg = f"Unsupported extractor type: {extractor_type}"
            LOGGER.error(error_msg)
            raise ValueError(error_msg)

        LOGGER.debug(
            "Creating %s instance for platform: %s", extractor_class.__name__, platform
        )
        return extractor_class(connector, query_generator, report_path)
