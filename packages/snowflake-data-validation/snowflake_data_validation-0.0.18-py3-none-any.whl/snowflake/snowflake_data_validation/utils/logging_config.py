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

"""Logging configuration for Snowflake Data Validation CLI."""

import logging.config
import os
import shutil

from datetime import datetime
from typing import Optional


class LoggingManager:

    """Manages logging configuration and log file relocation."""

    def __init__(self):
        """Initialize the logging manager."""
        self._log_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._current_log_file: Optional[str] = None

    def setup_logging(self) -> str:
        """Set up logging configuration.

        Returns:
            str: Path to the initial log file

        """
        # Create initial log file in current directory
        log_filename = f"data_validation_{self._log_timestamp}.log"
        self._current_log_file = log_filename

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": "{asctime} - {name} - {levelname} - {message}",
                        "style": "{",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "standard",
                        "level": "WARNING",
                    },
                    "file": {
                        "class": "logging.FileHandler",
                        "formatter": "standard",
                        "filename": log_filename,
                        "level": "INFO",
                        "encoding": "utf-8",
                    },
                },
                "loggers": {
                    "snowflake.snowflake_data_validation": {
                        "handlers": ["file"],
                        "level": "INFO",
                        "propagate": False,
                    },
                },
                "root": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                },
            }
        )

        return log_filename

    def relocate_log_file(self, output_directory_path: str) -> bool:
        """Move the log file to the output directory.

        Args:
            output_directory_path: Target directory for the log file

        Returns:
            bool: True if successful, False otherwise

        """
        if not self._current_log_file or not output_directory_path:
            return False

        try:
            os.makedirs(output_directory_path, exist_ok=True)
            new_log_path = os.path.join(
                output_directory_path, f"data_validation_{self._log_timestamp}.log"
            )
            if os.path.exists(self._current_log_file):
                shutil.move(self._current_log_file, new_log_path)
                self._current_log_file = new_log_path

                self._update_file_handler(new_log_path)

                logging.getLogger(__name__).info(
                    f"Log file relocated to: {new_log_path}"
                )
                return True

        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to relocate log file: {e}")

        return False

    def get_current_log_file(self) -> str:
        """Get the current log file path."""
        return self._current_log_file or ""

    def _update_file_handler(self, new_log_path: str):
        """Update file handlers to use the new log file path."""
        for logger_name in ["", "snowflake.snowflake_data_validation"]:
            logger = logging.getLogger(logger_name)
            # Iterate over a shallow copy of the logger's handlers list.
            # This allows us to safely modify (remove) handlers from the original list during iteration.
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.FileHandler):
                    new_handler = logging.FileHandler(new_log_path, encoding="utf-8")
                    new_handler.setLevel(handler.level)
                    new_handler.setFormatter(handler.formatter)

                    # Replace old handler
                    logger.removeHandler(handler)
                    logger.addHandler(new_handler)
                    handler.close()


# Singleton instance
_logging_manager = LoggingManager()


def setup_logging() -> str:
    """Set up logging configuration."""
    return _logging_manager.setup_logging()


def relocate_log_file(output_directory_path: str) -> bool:
    """Relocate the log file to the output directory."""
    return _logging_manager.relocate_log_file(output_directory_path)


def get_current_log_file() -> str:
    """Get the current log file path."""
    return _logging_manager.get_current_log_file()
