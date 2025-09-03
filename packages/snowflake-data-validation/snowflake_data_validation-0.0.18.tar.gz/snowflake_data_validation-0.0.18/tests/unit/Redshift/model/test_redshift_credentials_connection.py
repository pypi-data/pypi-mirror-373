from deepdiff import DeepDiff

from snowflake.snowflake_data_validation.redshift.model.redshift_credentials_connection import RedshiftCredentialsConnection
from snowflake.snowflake_data_validation.utils.constants import CREDENTIALS_CONNECTION_MODE

class TestRedshiftCredentialsConnectionModel:

    def test_valid_instantiation_with_all_fields(self):
        connection = RedshiftCredentialsConnection(
            mode="credentials",
            host="redshift.example.com",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        expected_data = {
            "mode": "credentials",
            "host": "redshift.example.com",
            "database": "testdb",
            "username": "testuser",
            "password": "testpass",
            "port": 5439
        }
        
        diff = DeepDiff(expected_data, connection.model_dump(), ignore_order=True)
        assert diff == {}

    def test_default_mode_value(self):
        connection = RedshiftCredentialsConnection(
            mode="some_mode",
            host="redshift.example.com",
            database="testdb",
            username="testuser",
            password="testpass"
        )

        expected_data = {
            "mode": "some_mode",
            "host": "redshift.example.com",
            "database": "testdb",
            "username": "testuser",
            "password": "testpass",
            "port": 5439
        }
        
        diff = DeepDiff(expected_data, connection.model_dump(), ignore_order=True)
        assert diff == {}

    def test_default_port_value(self):
        connection = RedshiftCredentialsConnection(
            host="redshift.example.com",
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        assert connection.port == 5439

    def test_custom_port_value(self):
        connection = RedshiftCredentialsConnection(
            host="redshift.example.com",
            database="testdb",
            username="testuser",
            password="testpass",
            port=5555
        )

        expected_data = {
            "mode": "credentials",
            "host": "redshift.example.com",
            "database": "testdb",
            "username": "testuser",
            "password": "testpass",
            "port": 5555
        }
        
        diff = DeepDiff(expected_data, connection.model_dump(), ignore_order=True)
        assert diff == {}

  