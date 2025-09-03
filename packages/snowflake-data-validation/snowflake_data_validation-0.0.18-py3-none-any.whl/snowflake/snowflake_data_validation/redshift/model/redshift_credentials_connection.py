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

from pydantic import BaseModel, Field

from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DATABASE_DESC,
    HOST_DESC,
    PASSWORD_DESC,
    PORT_DESC,
    USERNAME_DESC,
)


REDSHIFT_CREDENTIALS_CONNECTION_MODE_DESCRIPTION = (
    "Redshift Standard Authentication mode."
)

class RedshiftCredentialsConnection(BaseModel):

    """RedshiftCredentialsConnection model for storing Redshift connection credentials.

    Args:
        BaseModel (pydantic.BaseModel): Base model for data validation and serialization.

    """

    mode: str = Field(
        default=CREDENTIALS_CONNECTION_MODE,
        description=REDSHIFT_CREDENTIALS_CONNECTION_MODE_DESCRIPTION,
    )

    host: str = Field(
        ...,
        description=HOST_DESC,
    )

    database: str = Field(
        ...,
        description=DATABASE_DESC,
    )

    username: str = Field(
        ...,
        description=USERNAME_DESC
    )

    password: str = Field(
        ...,
        description=PASSWORD_DESC
    )

    port: int = Field(
        default=5439,
        description=PORT_DESC,
    )
