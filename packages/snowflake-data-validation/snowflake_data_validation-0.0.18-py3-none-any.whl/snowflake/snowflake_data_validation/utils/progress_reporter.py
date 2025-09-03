import json
import logging
import sys

from typing import Optional, TypedDict


class ProgressMetadata(TypedDict):

    """Interface for the metadata structure."""

    table: str
    columns: list[str]
    run_id: str
    run_start_time: str
    errorMessage: Optional[str]


def report_progress(metadata: ProgressMetadata) -> None:
    """Print a progress message to the standard output in the specified JSON structure.

    Args:
        metadata (dict): A dictionary containing metadata to include in the message.

    """
    message = {
        "channelName": "DataValidationMessage",
        "code": "TableDataValidationProgress",
        "metadata": metadata,
    }

    # Print the JSON message to standard output
    try:
        report = json.dumps(message)
        sys.stdout.write(report + "\n")
        sys.stdout.flush()  # Ensure the message is sent immediately
    except OSError as e:
        if (
            isinstance(e, BrokenPipeError) or e.errno == 32
        ):  # 32 is the error code for BrokenPipeError
            # Handle the case where stdout is closed
            # Suppress the error and continue with execution
            logger = logging.getLogger(__name__)
            logger.warning(
                "BrokenPipeError: Failed to write progress message to stdout for table: %s. "
                "This typically occurs when the parent process has closed the pipe. "
                "This is non-critical and validation will continue.",
                metadata.get("table", "unknown"),
            )
            try:
                sys.stderr.write("Warning: Broken pipe when writing to stdout\n")
                sys.stderr.flush()
            except Exception:
                pass  # Ignore if stderr is also closed
        else:
            logger = logging.getLogger(__name__)
            logger.warning(
                "OSError when writing to stdout for table: %s. Error: %s",
                metadata.get("table", "unknown"),
                str(e),
            )
