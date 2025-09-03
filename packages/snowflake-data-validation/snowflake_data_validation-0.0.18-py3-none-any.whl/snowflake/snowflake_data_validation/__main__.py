#!/usr/bin/env python3
"""Main entry point for the Snowflake Data Validation CLI when run as a module.

This allows the package to be run with: python -m snowflake.snowflake_data_validation
"""

import sys

import typer

from snowflake.snowflake_data_validation.main_cli import data_validation_app


def main():
    """Provide main entry point with error handling."""
    try:
        data_validation_app()
    except KeyboardInterrupt:
        typer.secho("\nOperation cancelled by user", fg=typer.colors.YELLOW, err=True)
        sys.exit(1)
    except ImportError as e:
        typer.secho(f"Import error: {e}", fg=typer.colors.RED, err=True)
        typer.secho(
            "Please ensure all dependencies are installed correctly.",
            fg=typer.colors.RED,
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        typer.secho(f"Unexpected error: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
