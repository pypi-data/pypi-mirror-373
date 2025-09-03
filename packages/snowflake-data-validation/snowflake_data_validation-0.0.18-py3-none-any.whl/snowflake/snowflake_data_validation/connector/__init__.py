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


# Description: This file is used to expose the ConnectorBase class to the outside world.
# The ConnectorBase class is used to define the interface for the Snowflake connector.
# It is used to define the methods that the connector must implement.
# The methods defined in the ConnectorBase class are connect
# execute_query, and close.
# The connect method is used to establish a connection to the Snowflake database.

__all__ = ["ConnectorBase", "NullConnector", "ConnectorFactoryBase"]

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
    NullConnector,
)
from snowflake.snowflake_data_validation.connector.connector_factory_base import (
    ConnectorFactoryBase,
)
