import os
import pytest
from unittest.mock import MagicMock, patch, Mock
import typer

from snowflake.snowflake_data_validation.redshift.redshift_arguments_manager import (
    RedshiftArgumentsManager,
)
from snowflake.snowflake_data_validation.configuration.model.connections import (
    RedshiftCredentialsConnection,
    SnowflakeNamedConnection,
    SnowflakeDefaultConnection,
)
from snowflake.snowflake_data_validation.configuration.model.configuration_model import (
    ConfigurationModel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CREDENTIALS_CONNECTION_MODE,
    DEFAULT_CONNECTION_MODE,
    NAME_CONNECTION_MODE,
    Platform,
    MISSING_SOURCE_CONNECTION_ERROR,
    MISSING_TARGET_CONNECTION_ERROR,
    ExecutionMode,
)


class TestRedshiftArgumentsManager:
    def setup_method(self):
        self.manager = RedshiftArgumentsManager()

    def test_init(self):
        assert self.manager.source_platform == Platform.REDSHIFT
        assert self.manager.target_platform == Platform.SNOWFLAKE

    def test_is_snowflake_to_snowflake_property(self):
        assert self.manager.is_snowflake_to_snowflake is False

    @patch.object(RedshiftArgumentsManager, "setup_validation_environment")
    def test_create_validation_environment_from_config_success(self, mock_setup_env):
        """Test successful creation of validation environment from config."""
        mock_config = MagicMock()
        mock_config.output_directory_path = "/tmp/output"
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = CREDENTIALS_CONNECTION_MODE
        mock_config.source_connection.host = "test-host"
        mock_config.source_connection.port = 5439
        mock_config.source_connection.username = "test-user"
        mock_config.source_connection.password = "test-pass"
        mock_config.source_connection.database = "test-db"
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = NAME_CONNECTION_MODE
        mock_config.target_connection.name = "test_connection"
        mock_config.target_platform = "Snowflake"

        result = self.manager.create_validation_environment_from_config(
            config_model=mock_config,
            data_validation_config_file="test_config.yaml",
            execution_mode=ExecutionMode.SYNC_VALIDATION,
        )

        mock_setup_env.assert_called_once()

    def test_setup_source_connection_config_from_config_success(self):
        """Test successful setup of source connection configuration."""
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = CREDENTIALS_CONNECTION_MODE
        mock_config.source_connection.host = "test-host"
        mock_config.source_connection.port = 5439
        mock_config.source_connection.username = "test-user"
        mock_config.source_connection.password = "test-pass"
        mock_config.source_connection.database = "test-db"

        result = self.manager._setup_source_connection_config_from_config(mock_config)

        assert isinstance(result, RedshiftCredentialsConnection)
        assert result.host == "test-host"
        assert result.port == 5439
        assert result.username == "test-user"
        assert result.password == "test-pass"
        assert result.database == "test-db"

    def test_setup_source_connection_config_missing_connection(self):
        """Test setup source connection config with missing connection."""
        mock_config = MagicMock()
        mock_config.source_connection = None

        with pytest.raises(typer.BadParameter, match=MISSING_SOURCE_CONNECTION_ERROR):
            self.manager._setup_source_connection_config_from_config(mock_config)

    def test_setup_source_connection_config_unsupported_mode(self):
        """Test setup source connection config with unsupported mode."""
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = "unsupported_mode"

        with pytest.raises(
            typer.BadParameter, match="Unsupported source connection mode"
        ):
            self.manager._setup_source_connection_config_from_config(mock_config)

    def test_setup_target_connection_config_name_mode(self):
        """Test setup target connection config with name mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = NAME_CONNECTION_MODE
        mock_config.target_connection.name = "test_connection"
        mock_config.target_platform = "Snowflake"

        result = self.manager._setup_target_connection_config_from_config(mock_config)

        assert isinstance(result, SnowflakeNamedConnection)
        assert result.name == "test_connection"

    def test_setup_target_connection_config_default_mode(self):
        """Test setup target connection config with default mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = DEFAULT_CONNECTION_MODE
        mock_config.target_platform = "Snowflake"

        result = self.manager._setup_target_connection_config_from_config(mock_config)

        assert isinstance(result, SnowflakeDefaultConnection)

    def test_setup_target_connection_config_missing_connection(self):
        """Test setup target connection config with missing connection."""
        mock_config = MagicMock()
        mock_config.target_connection = None

        with pytest.raises(typer.BadParameter, match=MISSING_TARGET_CONNECTION_ERROR):
            self.manager._setup_target_connection_config_from_config(mock_config)

    def test_setup_target_connection_config_unsupported_platform(self):
        """Test setup target connection config with unsupported platform."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_platform = "Oracle"

        with pytest.raises(
            typer.BadParameter, match="only supports Snowflake as target platform"
        ):
            self.manager._setup_target_connection_config_from_config(mock_config)

    def test_setup_target_connection_config_unsupported_mode(self):
        """Test setup target connection config with unsupported mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = "unsupported_mode"
        mock_config.target_platform = "Snowflake"

        with pytest.raises(
            typer.BadParameter, match="Unsupported target connection mode"
        ):
            self.manager._setup_target_connection_config_from_config(mock_config)

    def test_get_source_templates_path(self):
        """Test getting source templates path."""
        path = self.manager.get_source_templates_path()
        assert "redshift" in path
        assert "extractor" in path
        assert "templates" in path

    def test_get_target_templates_path(self):
        """Test getting target templates path."""
        path = self.manager.get_target_templates_path()
        assert "snowflake" in path
        assert "extractor" in path
        assert "templates" in path
