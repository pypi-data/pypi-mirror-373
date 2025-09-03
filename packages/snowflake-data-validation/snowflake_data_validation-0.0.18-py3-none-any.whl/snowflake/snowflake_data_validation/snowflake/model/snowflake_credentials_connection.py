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

"""Snowflake credentials connection configuration model."""

from typing import Optional

from pydantic import BaseModel, Field

from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
)


# Snowflake-specific connection descriptions
SNOWFLAKE_CREDENTIALS_CONNECTION_MODE_DESC = "Connection mode - credentials"
SNOWFLAKE_ACCOUNT_DESC = "Snowflake account name"
SNOWFLAKE_USERNAME_DESC = "Snowflake username"
SNOWFLAKE_DATABASE_DESC = "Snowflake database name"
SNOWFLAKE_SCHEMA_DESC = "Snowflake schema name"
SNOWFLAKE_WAREHOUSE_DESC = "Snowflake warehouse name"
SNOWFLAKE_ROLE_DESC = "Snowflake role"
SNOWFLAKE_AUTHENTICATOR_DESC = "Snowflake authenticator method"
SNOWFLAKE_PASSWORD_DESC = "Snowflake password"
SNOWFLAKE_PRIVATE_KEY_DESC = "Snowflake private key file path"
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_DESC = "Snowflake private key passphrase (if required)"


class SnowflakeCredentialsConnection(BaseModel):

    """Snowflake credentials connection configuration model.

    Args:
        BaseModel: pydantic BaseModel

    """

    mode: str = Field(
        default=CREDENTIALS_CONNECTION_MODE,
        description=SNOWFLAKE_CREDENTIALS_CONNECTION_MODE_DESC,
    )
    account: str = Field(..., description=SNOWFLAKE_ACCOUNT_DESC)
    username: str = Field(..., description=SNOWFLAKE_USERNAME_DESC)
    database: str = Field(..., description=SNOWFLAKE_DATABASE_DESC)
    warehouse: str = Field(..., description=SNOWFLAKE_WAREHOUSE_DESC)
    schema: Optional[str] = Field(None, description=SNOWFLAKE_SCHEMA_DESC)
    role: Optional[str] = Field(None, description=SNOWFLAKE_ROLE_DESC)
    authenticator: Optional[str] = Field(None, description=SNOWFLAKE_AUTHENTICATOR_DESC)
    password: Optional[str] = Field(None, description=SNOWFLAKE_PASSWORD_DESC)
    private_key_file: Optional[str] = Field(
        None, description=SNOWFLAKE_PRIVATE_KEY_DESC
    )
    private_key_passphrase: Optional[str] = Field(
        None, description=SNOWFLAKE_PRIVATE_KEY_PASSPHRASE_DESC
    )
