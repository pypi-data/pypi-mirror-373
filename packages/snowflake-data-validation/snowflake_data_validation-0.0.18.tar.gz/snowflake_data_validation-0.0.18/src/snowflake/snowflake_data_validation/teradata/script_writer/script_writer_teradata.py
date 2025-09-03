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

from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.script_writer.script_writer_base import (
    ScriptWriterBase,
)


class ScriptWriterTeradata(ScriptWriterBase):

    """Teradata-specific implementation for printing database queries.

    This class inherits all query printing functionality from ScriptWriterBase.
    No method overrides are needed as the base class provides complete implementations
    that work with Teradata's query generator.
    """

    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the Teradata script printer.

        Args:
            connector: Teradata database connector instance.
            query_generator: Query generator instance for generating Teradata SQL queries.
            report_path: Optional path for output reports.

        """
        super().__init__(connector, query_generator, report_path)
