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

"""Validation executors package.

This package contains different validation execution strategies:
- BaseValidationExecutor: Abstract base class defining the interface
- SyncValidationExecutor: For synchronous validation operations
- AsyncGenerationExecutor: For asynchronous query generation
- ExecutorFactory: Factory for creating appropriate executors
"""

from snowflake.snowflake_data_validation.executer.async_generation_executor import (
    AsyncGenerationExecutor,
)
from snowflake.snowflake_data_validation.executer.base_validation_executor import (
    BaseValidationExecutor,
)
from snowflake.snowflake_data_validation.utils.constants import ExecutionMode
from snowflake.snowflake_data_validation.executer.executor_factory import (
    ExecutorFactory,
)
from snowflake.snowflake_data_validation.executer.sync_validation_executor import (
    SyncValidationExecutor,
)

__all__ = [
    "BaseValidationExecutor",
    "SyncValidationExecutor",
    "AsyncGenerationExecutor",
    "ExecutorFactory",
    "ExecutionMode",
]
