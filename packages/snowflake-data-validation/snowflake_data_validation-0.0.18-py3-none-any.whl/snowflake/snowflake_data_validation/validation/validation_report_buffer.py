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

import logging
import os
import queue

import pandas as pd

from snowflake.snowflake_data_validation.utils.thread_safe_singleton import (
    ThreadSafeSingleton,
)


LOGGER = logging.getLogger(__name__)
VALIDATION_REPORT_NAME = "data_validation_report.csv"


class ValidationReportBuffer(metaclass=ThreadSafeSingleton):

    """Thread-safe singleton class for buffering validation report data before writing to file.

    This class implements the producer-consumer pattern where validation threads produce
    DataFrames and add them to a queue, and a single write operation consumes all
    queued data to write to the report file.
    """

    def __init__(self):
        """Initialize the buffer with a thread-safe queue.

        Note: This method may be called multiple times due to the metaclass implementation,
        but initialization is protected to ensure it only happens once.
        """
        if not hasattr(self, "_initialized"):
            self.data_queue = queue.Queue()
            self._initialized = True
            LOGGER.debug("ValidationReportBuffer singleton initialized")

    def add_data(self, dataframe: pd.DataFrame) -> None:
        """Add a DataFrame to the buffer queue.

        Args:
            dataframe (pd.DataFrame): The validation data to buffer

        """
        if not dataframe.empty:
            self.data_queue.put(dataframe.copy())
            LOGGER.debug("Added DataFrame with %d rows to buffer queue", len(dataframe))

    def flush_to_file(self, context) -> str:
        """Flush all buffered validation data to the report file.

        Args:
            context: The execution context containing report path and run start time.

        Returns:
            str: The path to the written report file.

        """
        report_file_path = self._get_report_file_path(context)
        LOGGER.info("Flushing validation report buffer to file: %s", report_file_path)
        self.write_all_to_file(report_file_path)
        return report_file_path

    def write_all_to_file(self, report_file_path: str) -> None:
        """Write all buffered data to the report file.

        This method consumes all DataFrames from the queue, concatenates them,
        and writes them to the specified file path in a single operation.

        Args:
            report_file_path (str): Path to the report file

        """
        if self.data_queue.empty():
            LOGGER.debug("No data in buffer queue to write")
            return

        # Collect all DataFrames from the queue
        dataframes = []
        while not self.data_queue.empty():
            try:
                df = self.data_queue.get_nowait()
                dataframes.append(df)
            except queue.Empty:
                break

        if not dataframes:
            LOGGER.debug("No DataFrames collected from queue")
            return

        # Concatenate all DataFrames
        combined_data = pd.concat(dataframes, ignore_index=True)
        LOGGER.info(
            "Combined %d DataFrames with total %d rows",
            len(dataframes),
            len(combined_data),
        )

        # Write all data to file
        combined_data.to_csv(report_file_path, index=False)
        LOGGER.info(
            "Successfully wrote %d rows to report file: %s",
            len(combined_data),
            report_file_path,
        )

    def clear_buffer(self) -> None:
        """Clear all data from the buffer queue.

        This method can be called to clear the buffer queue, typically used
        for cleanup or when starting a fresh validation run.
        """
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except queue.Empty:
                break
        LOGGER.info("Validation report buffer cleared")

    def get_queue_size(self) -> int:
        """Get the current size of the buffer queue.

        Returns:
            int: Number of DataFrames currently in the queue

        """
        return self.data_queue.qsize()

    def has_data(self) -> bool:
        """Check if the buffer has any data.

        Returns:
            bool: True if the buffer contains data, False otherwise

        """
        return not self.data_queue.empty()

    def _get_report_file_path(self, context) -> str:
        """Get the full path for the validation report file.

        Args:
            context: The execution context containing report path and run start time.

        Returns:
            str: The full path to the validation report file

        """
        return os.path.join(
            context.report_path, f"{context.run_start_time}_{VALIDATION_REPORT_NAME}"
        )
