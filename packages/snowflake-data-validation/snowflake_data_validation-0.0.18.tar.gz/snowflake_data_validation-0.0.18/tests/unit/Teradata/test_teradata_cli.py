"""Unit tests for Teradata CLI commands."""

import pytest
import typer
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch, call

from snowflake.snowflake_data_validation.teradata.teradata_cli import (
    teradata_app,
    validate_ipc_parameters,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    ExecutionMode,
)

# Initialize test runner
runner = CliRunner()

# Common test data
TEST_CONFIG_FILE = "test_config.yaml"
TEST_OUTPUT_DIR = "test_output"


@pytest.fixture
def mock_config_loader():
    """Mock configuration loader."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.ConfigurationLoader"
    ) as mock:
        config_model = MagicMock()
        config_model.output_directory_path = TEST_OUTPUT_DIR
        mock.return_value.get_configuration_model.return_value = config_model
        yield mock


@pytest.fixture
def mock_validation_env():
    """Mock validation environment."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.create_environment_from_config"
    ) as mock:
        mock_env = MagicMock()
        mock.return_value = mock_env
        yield mock_env


@pytest.fixture
def mock_orchestrator():
    """Mock comparison orchestrator."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.ComparisonOrchestrator"
    ) as mock:
        mock_instance = MagicMock()
        mock.from_validation_environment.return_value = mock_instance
        mock.run_sync_comparison = MagicMock()
        yield mock_instance


@pytest.fixture
def mock_path_exists():
    """Mock Path.exists() to return True for test config file."""
    with patch("pathlib.Path.exists") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_path_is_file():
    """Mock Path.is_file() to return True for test config file."""
    with patch("pathlib.Path.is_file") as mock:
        mock.return_value = True
        yield mock


def test_validate_ipc_parameters_success():
    """Test successful IPC parameter validation."""
    # Should not raise any exceptions
    validate_ipc_parameters(
        source_host="test-host",
        source_username="test-user",
        source_password="test-pass",
        source_database="test-db",
    )


def test_validate_ipc_parameters_missing_params():
    """Test IPC parameter validation with missing parameters."""
    with pytest.raises(typer.BadParameter) as exc:
        validate_ipc_parameters(
            source_host="",
            source_username="test-user",
            source_password="test-pass",
            source_database="test-db",
        )
    assert "Missing required Teradata connection parameters" in str(exc.value)


def test_validate_ipc_parameters_invalid_config_file():
    """Test IPC parameter validation with invalid config file."""
    with pytest.raises(typer.BadParameter) as exc:
        validate_ipc_parameters(
            source_host="test-host",
            source_username="test-user",
            source_password="test-pass",
            source_database="test-db",
            data_validation_config_file="nonexistent.yaml",
        )
    assert "Configuration file not found" in str(exc.value)


def test_run_validation_with_config_file(
    mock_config_loader,
    mock_validation_env,
    mock_orchestrator,
    mock_path_exists,
    mock_path_is_file,
):
    """Test run-validation command using config file."""
    result = runner.invoke(
        teradata_app,
        ["run-validation", "--data-validation-config-file", TEST_CONFIG_FILE],
    )

    assert result.exit_code == 0
    mock_orchestrator.run_sync_comparison.assert_called_once()
    assert "Validation completed successfully!" in result.stdout


def test_run_validation_with_credentials(
    mock_config_loader,
    mock_validation_env,
    mock_orchestrator,
    mock_path_exists,
    mock_path_is_file,
):
    """Test run-validation command using direct credentials."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.TeradataArgumentsManager"
    ) as mock_args_manager:
        mock_manager = MagicMock()
        mock_args_manager.return_value = mock_manager

        result = runner.invoke(
            teradata_app,
            [
                "run-validation",
                "--data-validation-config-file",
                TEST_CONFIG_FILE,
                "--teradata-host",
                "test-host",
                "--teradata-username",
                "test-user",
                "--teradata-password",
                "test-pass",
                "--teradata-database",
                "test-db",
            ],
        )

        assert result.exit_code == 0
        mock_manager.setup_validation_environment.assert_called_once()
        mock_orchestrator.run_sync_comparison.assert_called_once()


def test_generate_validation_scripts(
    mock_config_loader,
    mock_validation_env,
    mock_orchestrator,
    mock_path_exists,
    mock_path_is_file,
):
    """Test generate-validation-scripts command."""
    with runner.isolated_filesystem():
        # Create a dummy config file
        Path(TEST_CONFIG_FILE).touch()

        result = runner.invoke(
            teradata_app,
            [
                "generate-validation-scripts",
                TEST_CONFIG_FILE,
            ],
        )

        assert result.exit_code == 0
        mock_orchestrator.run_async_generation.assert_called_once()
        assert "Validation scripts generated successfully!" in result.stdout


def test_run_async_validation(
    mock_config_loader,
    mock_validation_env,
    mock_orchestrator,
    mock_path_exists,
    mock_path_is_file,
):
    """Test run-async-validation command."""
    with runner.isolated_filesystem():
        # Create a dummy config file
        Path(TEST_CONFIG_FILE).touch()

        result = runner.invoke(
            teradata_app,
            [
                "run-async-validation",
                TEST_CONFIG_FILE,
                "--output-directory",
                TEST_OUTPUT_DIR,
            ],
        )

        assert result.exit_code == 0
        mock_orchestrator.run_async_validation.assert_called_once()
        assert "Validation completed successfully!" in result.stdout


def test_run_validation_ipc(mock_config_loader, mock_validation_env, mock_orchestrator):
    """Test run-validation-ipc command."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.TeradataArgumentsManager"
    ) as mock_args_manager:
        mock_manager = MagicMock()
        mock_args_manager.return_value = mock_manager

        result = runner.invoke(
            teradata_app,
            [
                "run-validation-ipc",
                "--source-host",
                "test-host",
                "--source-username",
                "test-user",
                "--source-password",
                "test-pass",
                "--source-database",
                "test-db",
                "--snow-account",
                "snowaccount",
                "--snow_username",
                "snowuser",
                "--snow_database",
                "snowdb",
                "--snow_warehouse",
                "snowwarehouse",
                "--snow_password",
                "snowpass",
            ],
        )

        assert result.exit_code == 0
        mock_manager.setup_validation_environment.assert_called_once()
        mock_orchestrator.run_sync_comparison.assert_called_once()


def test_error_handling_bad_parameter():
    """Test error handling for bad parameters."""
    result = runner.invoke(
        teradata_app, ["run-validation"]  # Missing required parameter
    )

    assert result.exit_code == 2  # Typer's error code for missing required option
    assert "Missing option" in result.output  # Check output instead of stderr


def test_error_handling_connection_error(
    mock_config_loader, mock_path_exists, mock_path_is_file
):
    """Test error handling for connection errors."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.create_environment_from_config"
    ) as mock_env:
        mock_env.side_effect = ConnectionError("Failed to connect")

        result = runner.invoke(
            teradata_app,
            ["run-validation", "--data-validation-config-file", TEST_CONFIG_FILE],
            catch_exceptions=False,  # Let the error handler handle it
        )

        assert result.exit_code == 1
        assert "Failed to connect" in result.output  # Check output instead of stderr


def test_error_handling_unexpected_error(
    mock_config_loader, mock_path_exists, mock_path_is_file
):
    """Test error handling for unexpected errors."""
    with patch(
        "snowflake.snowflake_data_validation.teradata.teradata_cli.create_environment_from_config"
    ) as mock_env:
        mock_env.side_effect = Exception("Unexpected error")

        result = runner.invoke(
            teradata_app,
            ["run-validation", "--data-validation-config-file", TEST_CONFIG_FILE],
            catch_exceptions=False,  # Let the error handler handle it
        )

        assert result.exit_code == 1
        assert "Unexpected error" in result.output  # Check output instead of stderr
