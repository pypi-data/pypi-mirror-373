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

"""Snowflake named connection configuration model."""

from pydantic import BaseModel, Field

from snowflake.snowflake_data_validation.utils.constants import (
    CONNECTION_NAME_DESC,
)


# Snowflake-specific connection mode description
SNOWFLAKE_NAMED_CONNECTION_MODE_DESC = "Connection mode - named connection"


class SnowflakeNamedConnection(BaseModel):

    """Snowflake named connection configuration model.

    Args:
        BaseModel: pydantic BaseModel

    """

    mode: str = Field(..., description=SNOWFLAKE_NAMED_CONNECTION_MODE_DESC)
    name: str = Field(..., description=CONNECTION_NAME_DESC)
