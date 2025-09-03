import unittest
from unittest.mock import patch
import os

from snowflake.snowflake_data_validation.utils.cpu_optimizer import CpuOptimizer
from snowflake.snowflake_data_validation.utils.constants import (
    DEFAULT_THREAD_COUNT_OPTION,
)


class TestCpuOptimizer(unittest.TestCase):
    """Test cases for CPU optimization functionality."""

    def test_get_optimal_thread_count_with_explicit_max_threads(self):
        """Test get_optimal_thread_count with user-specified max_threads."""
        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, 6)

        # Should return min(6, 10) = 6
        self.assertEqual(result, 6)

    def test_get_optimal_thread_count_limited_by_tables(self):
        """Test get_optimal_thread_count when max_threads exceeds table count."""
        # Execute
        result = CpuOptimizer.get_optimal_thread_count(3, 10)

        # Should return min(10, 3) = 3
        self.assertEqual(result, 3)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_auto_detection(self, mock_cpu_count):
        """Test get_optimal_thread_count with auto-detection (max_threads='auto')."""
        # Setup
        mock_cpu_count.return_value = 4

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, DEFAULT_THREAD_COUNT_OPTION)

        # Should calculate based on CPU count: 4 * 3.0 = 12, min(12, 10) = 10
        self.assertEqual(result, 10)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_auto_detection_with_auto_string(
        self, mock_cpu_count
    ):
        """Test get_optimal_thread_count with auto-detection using 'auto' string."""
        # Setup
        mock_cpu_count.return_value = 4

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, DEFAULT_THREAD_COUNT_OPTION)

        # Should calculate based on CPU count: 4 * 3.0 = 12, min(12, 10) = 10
        self.assertEqual(result, 10)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_fallback(self, mock_cpu_count):
        """Test get_optimal_thread_count with CPU count fallback."""
        # Setup
        mock_cpu_count.return_value = None

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, DEFAULT_THREAD_COUNT_OPTION)

        # Should use fallback: 4 * 3.0 = 12, min(12, 10) = 10
        self.assertEqual(result, 10)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_minimum_threads(self, mock_cpu_count):
        """Test get_optimal_thread_count respects minimum thread requirement."""
        # Setup
        mock_cpu_count.return_value = 1

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, DEFAULT_THREAD_COUNT_OPTION)

        # Should respect minimum: max(2, 1 * 3.0) = 3
        self.assertEqual(result, 3)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_max_limit(self, mock_cpu_count):
        """Test get_optimal_thread_count respects maximum thread limit."""
        # Setup
        mock_cpu_count.return_value = 20

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(50, DEFAULT_THREAD_COUNT_OPTION)

        # Should respect max limit: min(20 * 3.0, 50, 32) = 32
        self.assertEqual(result, 32)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_invalid_max_threads_negative(
        self, mock_cpu_count
    ):
        """Test get_optimal_thread_count with invalid negative max_threads."""
        # Setup
        mock_cpu_count.return_value = 4

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, -5)

        # Should use auto-detection: 4 * 3.0 = 12, min(12, 10) = 10
        self.assertEqual(result, 10)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_invalid_max_threads_zero(self, mock_cpu_count):
        """Test get_optimal_thread_count with invalid zero max_threads."""
        # Setup
        mock_cpu_count.return_value = 4

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, 0)

        # Should use auto-detection: 4 * 3.0 = 12, min(12, 10) = 10
        self.assertEqual(result, 10)

    @patch("snowflake.snowflake_data_validation.utils.cpu_optimizer.os.cpu_count")
    def test_get_optimal_thread_count_invalid_max_threads_string(self, mock_cpu_count):
        """Test get_optimal_thread_count with invalid string max_threads."""
        # Setup
        mock_cpu_count.return_value = 4

        # Execute
        result = CpuOptimizer.get_optimal_thread_count(10, "invalid")

        # Should use auto-detection: 4 * 3.0 = 12, min(12, 10) = 10
        self.assertEqual(result, 10)


if __name__ == "__main__":
    unittest.main()
