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

from functools import wraps
from typing import Optional


class HelperMisc:

    """A collection of miscellaneous helper functions for Snowflake Data Validation."""

    @staticmethod
    def get_decomposed_fully_qualified_name(
        fully_qualified_name: str,
    ) -> tuple[Optional[str], str, str]:
        """Decomposes a fully qualified name into its database, schema, and table components.

        Args:
            fully_qualified_name (str): The fully qualified name in the format
                'database.schema.table' or 'schema.table'.

        Returns:
            tuple: A tuple containing (database, schema, table). For 2-part names, database will be None.

        Raises:
            ValueError: If the fully qualified name does not have two or three parts separated by dots.

        """
        parts = fully_qualified_name.split(".")
        if len(parts) == 3:
            database, schema, table = parts
            return database, schema, table
        elif len(parts) == 2:
            schema, table = parts
            return None, schema, table
        else:
            raise ValueError(
                f"Invalid fully qualified name: {fully_qualified_name}. "
                "Expected format: 'database.schema.table' or 'schema.table'"
            )

    @staticmethod
    def import_dependencies(package: str = None, helper_text: str = ""):
        """Import a helper function from a package.

        Args:
            package (str): The name of the package to import from.
            helper_text (str): The name of the helper function to import.

        Returns:
            Any: The imported helper function or None if not found.

        """

        def decorator(func):
            @wraps(func)
            def _wrapper():
                try:
                    return func()
                except ModuleNotFoundError as e:
                    help = helper_text
                    if package:
                        help += f"Please install the missing depencies. \
                        Run pip install snowflake-data-validation[{package}]"
                    raise ModuleNotFoundError(f"{e}\n\n{help}") from e

            return _wrapper

        return decorator

    @staticmethod
    def create_uppercase_set(values) -> set:
        """Create a set of uppercase values from an iterable.

        This utility function directly creates an uppercase set from the given values,
        avoiding the need for an intermediate set creation.

        Args:
            values: An iterable containing string values to be converted to uppercase.

        Returns:
            set: A set containing all values converted to uppercase.

        """
        return {str(val).upper() for val in values}
