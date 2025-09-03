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

from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd


class OutputMessageLevel(Enum):

    """Enum to represent mesage level constants."""

    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    ERROR = "ERROR"
    TARGET_RESULT = "TARGET_RESULT"
    SOURCE_RESULT = "SOURCE_RESULT"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class OutputHandlerBase(ABC):

    """Abstract base class for handling output from the core module."""

    def __init__(self, enable_console_output: bool = True):
        self.console_output_enabled = enable_console_output

    @abstractmethod
    def handle_message(
        self,
        level: OutputMessageLevel,
        message: str = "",
        header: str = "",
        dataframe: pd.DataFrame = None,
    ):
        """Handle the output message with a specified level and optional header.

        Args:
            message (str): The message to be handled.
            level (OutputMessageLevel): The severity level of the message.
            header (str, optional): An optional header for the message. Defaults to an empty string.
            dataframe (pd.DataFrame, optional): A pandas DataFrame to be included in the message. Defaults to None.

        """
        pass
