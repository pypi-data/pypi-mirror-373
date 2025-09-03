import pytest
from unittest.mock import MagicMock, patch, Mock
import typer

from snowflake.snowflake_data_validation.sqlserver.sqlserver_arguments_manager import (
    SqlServerArgumentsManager,
)
from snowflake.snowflake_data_validation.configuration.model.connections import (
    SqlServerCredentialsConnection,
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


class TestSqlServerArgumentsManager:
    def setup_method(self):
        self.args_manager = SqlServerArgumentsManager()

    def test_init_and_properties(self):
        """Test initialization and properties."""
        assert self.args_manager.source_platform == Platform.SQLSERVER
        assert self.args_manager.target_platform == Platform.SNOWFLAKE
        assert self.args_manager.is_snowflake_to_snowflake is False

    @patch.object(SqlServerArgumentsManager, "setup_validation_environment")
    def test_create_validation_environment_from_config_success(self, mock_setup_env):
        """Test successful creation of validation environment from config."""
        mock_config = MagicMock()
        mock_config.output_directory_path = "/tmp/output"
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = CREDENTIALS_CONNECTION_MODE
        mock_config.source_connection.host = "localhost"
        mock_config.source_connection.port = 1433
        mock_config.source_connection.username = "test_user"
        mock_config.source_connection.password = "test_password"
        mock_config.source_connection.database = "test_db"
        mock_config.source_connection.trust_server_certificate = "yes"
        mock_config.source_connection.encrypt = "no"
        mock_config.target_connection = MagicMock()
        mock_config.target_connection.mode = NAME_CONNECTION_MODE
        mock_config.target_connection.name = "test_connection"
        mock_config.target_platform = "Snowflake"

        result = self.args_manager.create_validation_environment_from_config(
            config_model=mock_config,
            data_validation_config_file="test_config.yaml",
            execution_mode=ExecutionMode.SYNC_VALIDATION,
        )

        mock_setup_env.assert_called_once()

    def test_setup_source_connection_config_success(self):
        """Test successful setup of source connection configuration."""
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = CREDENTIALS_CONNECTION_MODE
        mock_config.source_connection.host = "localhost"
        mock_config.source_connection.port = 1433
        mock_config.source_connection.username = "test_user"
        mock_config.source_connection.password = "test_password"
        mock_config.source_connection.database = "test_db"
        mock_config.source_connection.trust_server_certificate = "yes"
        mock_config.source_connection.encrypt = "no"

        result = self.args_manager._setup_source_connection_config_from_config(
            mock_config
        )

        assert isinstance(result, SqlServerCredentialsConnection)
        assert result.host == "localhost"
        assert result.port == 1433
        assert result.username == "test_user"
        assert result.password == "test_password"
        assert result.database == "test_db"
        assert result.trust_server_certificate == "yes"
        assert result.encrypt == "no"

    def test_setup_source_connection_config_missing_connection(self):
        """Test source connection setup with missing credentials."""
        mock_config = MagicMock()
        mock_config.source_connection = None

        with pytest.raises(typer.BadParameter, match="No source connection configured"):
            self.args_manager._setup_source_connection_config_from_config(mock_config)

    def test_setup_source_connection_config_unsupported_mode(self):
        """Test source connection setup with unsupported mode."""
        mock_config = MagicMock()
        mock_config.source_connection = MagicMock()
        mock_config.source_connection.mode = "unsupported_mode"

        with pytest.raises(
            typer.BadParameter, match="Unsupported source connection mode"
        ):
            self.args_manager._setup_source_connection_config_from_config(mock_config)

    def test_setup_target_connection_config_missing_connection(self):
        """Test setup from config with missing connections."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_config.target_connection = None

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_target_connection_config_from_config(mock_config)

        assert "No target connection configured" in str(exc_info.value)

    def test_setup_target_connection_config_unsupported_platform(self):
        """Test target setup with unsupported platform."""
        mock_config = Mock(spec=ConfigurationModel)
        mock_config.target_connection = Mock()
        mock_config.target_platform = "Oracle"

        with pytest.raises(typer.BadParameter) as exc_info:
            self.args_manager._setup_target_connection_config_from_config(mock_config)

        assert (
            "SqlServer arguments manager only supports Snowflake as target platform"
            in str(exc_info.value)
        )

    def test_get_source_templates_path(self):
        """Test getting source templates path."""
        path = self.args_manager.get_source_templates_path()
        assert "sqlserver" in path
        assert "extractor" in path
        assert "templates" in path

    def test_get_target_templates_path(self):
        """Test getting target templates path."""
        path = self.args_manager.get_target_templates_path()
        assert "snowflake" in path
        assert "extractor" in path
        assert "templates" in path
