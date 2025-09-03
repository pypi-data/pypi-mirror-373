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

import pandas as pd
import typer

from rich.console import Console
from rich.table import Table

from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import NEWLINE


class ConsoleOutputHandler(OutputHandlerBase):

    """Concrete implementation of OutputHandlerBase that outputs messages to the console."""

    def __init__(self, enable_console_output: bool = True):
        super().__init__(enable_console_output)

    def handle_message(
        self,
        level: OutputMessageLevel,
        message: str = None,
        header: str = "",
        dataframe: pd.DataFrame = None,
    ):
        """Handle the display of messages with different levels of importance and formatting.

        Args:
            message (str): The message to be displayed.
            level (OutputMessageLevel): The importance level of the message, which determines
                the formatting and color of the output.
            header (str, optional): An optional header to prepend to the message. Defaults to an empty string.
            dataframe (pd.DataFrame, optional): An optional pandas DataFrame to display as a table. Defaults to None.

        """
        if not self.console_output_enabled:
            return

        color_map = {
            OutputMessageLevel.ERROR: typer.colors.RED,
            OutputMessageLevel.WARNING: typer.colors.YELLOW,
            OutputMessageLevel.INFO: typer.colors.BLUE,
            OutputMessageLevel.DEBUG: typer.colors.WHITE,
            OutputMessageLevel.TARGET_RESULT: typer.colors.CYAN,
            OutputMessageLevel.SOURCE_RESULT: typer.colors.MAGENTA,
            OutputMessageLevel.SUCCESS: typer.colors.GREEN,
            OutputMessageLevel.FAILURE: typer.colors.RED,
        }
        color = color_map.get(level)
        message_header = f"[{level.name}] {header}" if header else f"[{level.name}]"
        typer.secho(f"\n{message_header}", fg=color)

        if message is not None and (not hasattr(message, "empty") or not message.empty):
            typer.secho(f"{message}")

        if dataframe is not None:
            table_border_color = "grey30"
            table = Table(show_lines=True, border_style=table_border_color)
            for column in dataframe.columns:
                table.add_column(
                    column,
                    justify="center",
                    header_style=color,
                    no_wrap=True,
                )
            for _, row in dataframe.iterrows():
                table.add_row(
                    *map(str, row),
                )
            console = Console()
            console.print(NEWLINE, table)
