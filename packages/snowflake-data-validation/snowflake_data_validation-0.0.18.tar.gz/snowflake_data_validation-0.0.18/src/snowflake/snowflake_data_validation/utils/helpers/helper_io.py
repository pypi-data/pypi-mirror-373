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

import os
import tempfile


class HelperIO:

    """Helper class for input/output operations in Snowflake Data Validation."""

    # WIP We should evaluate the need for a directory manager class, it could exist in the Context class
    # and potentially move this functionality to a more appropriate location inside it
    @staticmethod
    def copy_templates_to_temp_dir(
        source_templates_path: str,
        core_templates_path: str,
        templates_temp_dir_path: str,
    ) -> None:
        """Copy template files from source and core template directories to a temporary directory.

        This function ensures that the temporary directory exists, and then copies all files
        and directories from the specified source and core template paths into the temporary
        directory. If the temporary directory cannot be created or the files cannot be copied,
        an appropriate exception is raised.

        Args:
            source_templates_path (str): The path to the source templates directory.
            core_templates_path (str): The path to the core templates directory.
            templates_temp_dir_path (str): The path to the temporary directory where templates
                                        will be copied.

        Raises:
            RuntimeError: If the temporary directory cannot be created or if an error occurs
                        during the copying of templates.

        """
        try:
            for path in [core_templates_path, source_templates_path]:
                if os.path.exists(path):
                    for item in os.listdir(path):
                        source_item = os.path.join(path, item)
                        dest_item = os.path.join(templates_temp_dir_path, item)
                        if os.path.isdir(source_item):
                            os.makedirs(dest_item, exist_ok=True)
                        else:
                            with open(source_item, "rb") as src, open(
                                dest_item, "wb"
                            ) as dst:
                                dst.write(src.read())
        except Exception as e:
            raise RuntimeError(
                f"Failed to copy templates from {core_templates_path} or "
                f"{source_templates_path} to {templates_temp_dir_path}: {e}"
            ) from e

    @staticmethod
    def create_temp_dir(prefix="sdv_") -> str:
        """Create a temporary directory with a specified prefix.

        This function generates a temporary directory in the system's default
        temporary file location. The directory name will start with the given
        prefix, followed by a unique identifier.

        Args:
            prefix (str): The prefix for the temporary directory name. Defaults to "sdv_".

        Returns:
            str: The path to the created temporary directory.

        """
        temp_dir_path = tempfile.mkdtemp(prefix=prefix)
        return temp_dir_path
