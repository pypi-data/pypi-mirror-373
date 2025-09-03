# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

"""CPU optimization utilities for determining optimal thread counts."""

import logging
import os

from typing import Optional, Union

from snowflake.snowflake_data_validation.utils.constants import (
    CPU_MULTIPLIER,
    DEFAULT_CPU_COUNT,
    DEFAULT_THREAD_COUNT_OPTION,
    MAX_THREAD_LIMIT,
    MIN_THREADS,
)


logger = logging.getLogger(__name__)


class CpuOptimizer:

    """Utility class for CPU-aware thread optimization.

    This class provides methods to calculate optimal thread counts for database
    workloads based on system capabilities and configuration.
    """

    @staticmethod
    def get_optimal_thread_count(num_tables: int, max_threads: Union[str, int]) -> int:
        """Calculate optimal thread count based on system capabilities and configuration.

        Args:
            num_tables: Number of tables to process
            max_threads: Maximum threads configuration ("auto" or int)

        Returns:
            Optimal thread count for the workload

        """
        validated_max_threads = CpuOptimizer._validate_max_threads(max_threads)

        if validated_max_threads is not None:
            return CpuOptimizer._apply_configured_threads(
                validated_max_threads, num_tables
            )

        logging.info(
            "Using automatic thread count detection based on system capabilities."
        )
        return CpuOptimizer._calculate_auto_threads(num_tables)

    @staticmethod
    def _validate_max_threads(max_threads: Union[str, int]) -> Optional[int]:
        if max_threads == DEFAULT_THREAD_COUNT_OPTION:
            return None

        if isinstance(max_threads, str):
            logging.warning(
                f"Invalid max_threads value: '{max_threads}'. Using auto-detection."
            )
            return None

        if isinstance(max_threads, int):
            if max_threads <= 0:
                logging.warning(
                    f"Invalid max_threads value: {max_threads}. Using auto-detection."
                )
                return None

            if max_threads > MAX_THREAD_LIMIT:
                logging.warning(
                    f"Specified max_threads {max_threads} exceeds limit of "
                    f"{MAX_THREAD_LIMIT}. Using {MAX_THREAD_LIMIT}."
                )
                return MAX_THREAD_LIMIT

            return max_threads

        logging.warning(
            f"Unexpected max_threads type: {type(max_threads)}. Using auto-detection."
        )
        return None

    @staticmethod
    def _apply_configured_threads(configured_threads: int, num_tables: int) -> int:
        final_threads = min(configured_threads, num_tables)

        if final_threads < configured_threads:
            logging.info(
                f"Using {final_threads} threads (limited by number of tables) instead of "
                f"configured {configured_threads} threads."
            )
        else:
            logging.info(
                f"Using configured max_threads value: {configured_threads} threads."
            )

        return final_threads

    @staticmethod
    def _calculate_auto_threads(num_tables: int) -> int:
        cpu_count = CpuOptimizer._get_cpu_count()
        initial_threads = int(cpu_count * CPU_MULTIPLIER)

        logging.info(f"Automatic detected optimal threads: {initial_threads} threads")

        final_threads = CpuOptimizer._apply_thread_constraints(
            initial_threads, num_tables
        )

        logging.info(f"Final optimal thread count: {final_threads}")
        return final_threads

    @staticmethod
    def _get_cpu_count() -> int:
        detected_cpu_count = os.cpu_count()

        if detected_cpu_count is None:
            logging.info(
                f"Unable to detect system CPU count. Using default CPU count of {DEFAULT_CPU_COUNT} cores."
            )
            return DEFAULT_CPU_COUNT

        logging.info(f"Detected {detected_cpu_count} CPU cores on system.")
        return detected_cpu_count

    @staticmethod
    def _apply_thread_constraints(initial_threads: int, num_tables: int) -> int:
        constraints_applied = []
        final_threads = initial_threads

        if final_threads < MIN_THREADS:
            constraints_applied.append(
                f"minimum threads constraint (raised from {final_threads} to {MIN_THREADS})"
            )
            final_threads = MIN_THREADS

        if final_threads > MAX_THREAD_LIMIT:
            constraints_applied.append(
                f"maximum thread limit (reduced from {final_threads} to {MAX_THREAD_LIMIT})"
            )
            final_threads = MAX_THREAD_LIMIT

        if final_threads > num_tables:
            constraints_applied.append(
                f"table count limit (reduced to {num_tables} to match number of tables)"
            )
            final_threads = num_tables

        if constraints_applied:
            logging.info(f"Applied constraints: {', '.join(constraints_applied)}")

        return final_threads
