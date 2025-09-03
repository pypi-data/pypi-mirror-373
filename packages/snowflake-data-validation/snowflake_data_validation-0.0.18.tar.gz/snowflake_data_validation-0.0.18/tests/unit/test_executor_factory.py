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

import pytest
from unittest.mock import MagicMock

from snowflake.snowflake_data_validation.executer.executor_factory import (
    ExecutorFactory,
    PlatformConfig,
)
from snowflake.snowflake_data_validation.utils.constants import (
    ExecutionMode,
    Platform,
)
from snowflake.snowflake_data_validation.executer.extractor_types import (
    ExtractorType,
)


def test_executor_factory_default_initialization():
    """Test that ExecutorFactory initializes with default platform configurations."""
    factory = ExecutorFactory()

    # Should have default platform configs
    assert Platform.SNOWFLAKE in factory._platform_configs
    assert Platform.SQLSERVER in factory._platform_configs
    assert Platform.TERADATA in factory._platform_configs


def test_executor_factory_custom_initialization():
    """Test that ExecutorFactory can be initialized with custom platform configurations."""
    custom_configs = {
        Platform.SNOWFLAKE: PlatformConfig(
            query_generator=MagicMock,
            metadata_extractor=MagicMock,
            script_writer=MagicMock,
        )
    }

    factory = ExecutorFactory(platform_configs=custom_configs)

    # Should use custom configs
    assert factory._platform_configs == custom_configs
    assert Platform.SQLSERVER not in factory._platform_configs


def test_create_executor_sync_validation():
    """Test creating a sync validation executor."""
    factory = ExecutorFactory()

    source_extractor = MagicMock()
    target_extractor = MagicMock()
    context = MagicMock()

    executor = factory.create_executor(
        ExecutionMode.SYNC_VALIDATION,
        source_extractor=source_extractor,
        target_extractor=target_extractor,
        context=context,
    )

    # Should return a SyncValidationExecutor
    from snowflake.snowflake_data_validation.executer.sync_validation_executor import (
        SyncValidationExecutor,
    )

    assert isinstance(executor, SyncValidationExecutor)


def test_create_executor_invalid_mode():
    """Test that invalid execution mode raises ValueError."""
    factory = ExecutorFactory()

    with pytest.raises(ValueError, match="Unsupported execution mode"):
        factory.create_executor(
            "invalid_mode",  # Invalid mode
            source_extractor=MagicMock(),
            target_extractor=MagicMock(),
            context=MagicMock(),
        )


def test_create_extractor_from_connector_invalid_platform():
    """Test that invalid platform raises ValueError."""
    factory = ExecutorFactory()

    with pytest.raises(ValueError, match="Unsupported platform"):
        factory.create_extractor_from_connector(
            connector=MagicMock(),
            extractor_type=ExtractorType.METADATA_EXTRACTOR,
            platform="invalid_platform",  # Invalid platform
        )


def test_create_extractor_from_connector_invalid_type():
    """Test that invalid extractor type raises ValueError."""
    factory = ExecutorFactory()

    with pytest.raises(ValueError, match="Unsupported extractor type"):
        factory.create_extractor_from_connector(
            connector=MagicMock(),
            extractor_type="invalid_type",  # Invalid type
            platform=Platform.SNOWFLAKE,
        )
