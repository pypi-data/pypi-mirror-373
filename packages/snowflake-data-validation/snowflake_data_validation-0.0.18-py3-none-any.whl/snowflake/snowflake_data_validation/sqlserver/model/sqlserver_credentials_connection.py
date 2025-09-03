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

"""SQL Server credentials connection configuration model."""

from pydantic import BaseModel, Field

from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DATABASE_DESC,
    HOST_DESC,
    PASSWORD_DESC,
    PORT_DESC,
    USERNAME_DESC,
)


# SQL Server-specific connection mode description
SQLSERVER_CREDENTIALS_CONNECTION_MODE_DESC = "Connection mode - credentials"

# SSL/TLS connection parameter descriptions
TRUST_SERVER_CERTIFICATE_DESC = (
    "Whether to trust the server certificate (yes/no). Defaults to 'no'."
)
ENCRYPT_DESC = "Whether to encrypt the connection (yes/no/optional). Defaults to 'yes'."


class SqlServerCredentialsConnection(BaseModel):

    """SQL Server credentials connection configuration model.

    Args:
        BaseModel: pydantic BaseModel

    """

    mode: str = Field(
        default=CREDENTIALS_CONNECTION_MODE,
        description=SQLSERVER_CREDENTIALS_CONNECTION_MODE_DESC,
    )
    host: str = Field(..., description=HOST_DESC)
    port: int = Field(..., description=PORT_DESC)
    username: str = Field(..., description=USERNAME_DESC)
    password: str = Field(..., description=PASSWORD_DESC)
    database: str = Field(..., description=DATABASE_DESC)
    trust_server_certificate: str = Field(
        default="no",
        description=TRUST_SERVER_CERTIFICATE_DESC,
    )
    encrypt: str = Field(
        default="yes",
        description=ENCRYPT_DESC,
    )
