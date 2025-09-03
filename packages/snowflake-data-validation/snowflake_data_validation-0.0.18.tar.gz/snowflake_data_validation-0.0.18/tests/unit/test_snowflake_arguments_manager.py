import pytest
from unittest.mock import MagicMock, patch, Mock
import typer

from snowflake.snowflake_data_validation.snowflake.snowflake_arguments_manager import (
    SnowflakeArgumentsManager,
)
from snowflake.snowflake_data_validation.configuration.model.connections import (
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
    ExecutionMode,
)


class TestSnowflakeArgumentsManager:
    def setup_method(self):
        self.args_manager = SnowflakeArgumentsManager()

    def test_init_and_properties(self):
        """Test initialization and properties."""
        assert self.args_manager.source_platform == Platform.SNOWFLAKE
        assert self.args_manager.target_platform == Platform.SNOWFLAKE
        assert self.args_manager.is_snowflake_to_snowflake is True

    @patch.object(SnowflakeArgumentsManager, "setup_validation_environment")
    def test_create_validation_environment_from_config_success(self, mock_setup_env):
        """Test successful creation of validation environment from config."""
        mock_config = MagicMock()
        mock_config.output_directory_path = "/tmp/output"
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = NAME_CONNECTION_MODE
        mock_config.source_connection.name = "source_connection"
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = DEFAULT_CONNECTION_MODE
        mock_config.target_platform = "Snowflake"

        result = self.args_manager.create_validation_environment_from_config(
            config_model=mock_config,
            data_validation_config_file="test_config.yaml",
            execution_mode=ExecutionMode.SYNC_VALIDATION,
        )

        mock_setup_env.assert_called_once()

    def test_setup_snowflake_connection_toml_mode_error(self):
        """Test that TOML mode raises appropriate error."""
        # This test confirms that credentials mode is not supported in config files
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = CREDENTIALS_CONNECTION_MODE

        with pytest.raises(
            typer.BadParameter, match="Unsupported source connection mode"
        ):
            self.args_manager._setup_source_connection_config_from_config(mock_config)

    def test_setup_source_connection_config_name_mode(self):
        """Test successful setup of source connection with name mode."""
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = NAME_CONNECTION_MODE
        mock_config.source_connection.name = "test_connection"

        result = self.args_manager._setup_source_connection_config_from_config(
            mock_config
        )

        assert isinstance(result, SnowflakeNamedConnection)
        assert result.name == "test_connection"

    def test_setup_source_connection_config_default_mode(self):
        """Test successful setup of source connection with default mode."""
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = DEFAULT_CONNECTION_MODE

        result = self.args_manager._setup_source_connection_config_from_config(
            mock_config
        )

        assert isinstance(result, SnowflakeDefaultConnection)

    def test_setup_source_connection_config_missing_connection(self):
        """Test setup from config with missing connections."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_config.source_connection = None

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_source_connection_config_from_config(mock_config)

        assert "No source connection configured" in str(exc_info.value)

    def test_setup_source_connection_config_unsupported_mode(self):
        """Test setup from config with unsupported connection mode."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_source_conn = Mock()
        mock_source_conn.mode = "unsupported_mode"
        mock_config.source_connection = mock_source_conn

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_source_connection_config_from_config(mock_config)

        assert "Unsupported source connection mode" in str(exc_info.value)

    def test_setup_target_connection_config_name_mode(self):
        """Test successful setup of target connection with name mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = NAME_CONNECTION_MODE
        mock_config.target_connection.name = "target_connection"
        mock_config.target_platform = "Snowflake"

        result = self.args_manager._setup_target_connection_config_from_config(
            mock_config
        )

        assert isinstance(result, SnowflakeNamedConnection)
        assert result.name == "target_connection"

    def test_setup_target_connection_config_default_mode(self):
        """Test successful setup of target connection with default mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = DEFAULT_CONNECTION_MODE
        mock_config.target_platform = "Snowflake"

        result = self.args_manager._setup_target_connection_config_from_config(
            mock_config
        )

        assert isinstance(result, SnowflakeDefaultConnection)

    def test_setup_target_connection_config_missing_connection(self):
        """Test setup target connection config with missing connection."""
        mock_config = MagicMock()
        mock_config.target_connection = None

        with pytest.raises(typer.BadParameter, match="No target connection configured"):
            self.args_manager._setup_target_connection_config_from_config(mock_config)

    def test_setup_target_connection_config_unsupported_mode(self):
        """Test setup target connection config with unsupported mode."""
        mock_config = MagicMock()
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = "unsupported_mode"
        mock_config.target_platform = "Snowflake"

        with pytest.raises(
            typer.BadParameter, match="Unsupported target connection mode"
        ):
            self.args_manager._setup_target_connection_config_from_config(mock_config)

    def test_get_source_templates_path(self):
        """Test getting source templates path."""
        path = self.args_manager.get_source_templates_path()
        assert "snowflake" in path
        assert "extractor" in path
        assert "templates" in path

    def test_get_target_templates_path(self):
        """Test getting target templates path."""
        path = self.args_manager.get_target_templates_path()
        assert "snowflake" in path
        assert "extractor" in path
        assert "templates" in path
