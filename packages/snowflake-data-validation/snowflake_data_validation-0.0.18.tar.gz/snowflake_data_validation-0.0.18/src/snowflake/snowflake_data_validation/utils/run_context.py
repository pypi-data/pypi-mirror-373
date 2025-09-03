# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

"""Run context singleton for managing run-level variables."""

import uuid

from datetime import datetime, timezone

from snowflake.snowflake_data_validation.configuration.singleton import Singleton


class RunContext(metaclass=Singleton): # pragma: no cover

    """Singleton class for managing run-level variables.

    This class provides a centralized way to access run-level variables
    like run_id and run_start_time across the application.
    Exclude from coverage as it is a model.
    """

    def __init__(self):
        """Initialize the RunContext with default values."""
        self._run_id = None
        self._run_start_time = None

    def initialize_run(self):
        """Initialize a new run with a new run_id and start time."""
        self._run_id = str(uuid.uuid4())
        self._run_start_time = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    @property
    def run_id(self) -> str:
        """Get the current run ID.

        Returns:
            str: The current run ID. If not initialized, initializes a new run.

        """
        if self._run_id is None:
            self.initialize_run()
        return self._run_id

    @property
    def run_start_time(self) -> str:
        """Get the current run start time.

        Returns:
            str: The current run start time. If not initialized, initializes a new run.

        """
        if self._run_start_time is None:
            self.initialize_run()
        return self._run_start_time

    def reset(self):
        """Reset the run context, clearing run_id and run_start_time."""
        self._run_id = None
        self._run_start_time = None
