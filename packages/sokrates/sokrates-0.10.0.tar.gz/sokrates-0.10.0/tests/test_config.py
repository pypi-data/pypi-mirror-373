"""
Test suite for the Config class.

This module contains unit tests for the Config class which manages application 
configuration settings. The tests cover singleton behavior, environment variable
loading, directory initialization, and configuration value retrieval.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from sokrates import Config

@pytest.fixture(autouse=True)
def after_each_test():
    # Reset the config singleton instance after each test
    # THIS NEEDS TO BE DONE TO INSURE PROPER WORKINGS OF THE Config testsuite
    Config._instance = None
        
class TestConfig:
    """Test cases for the Config class."""

    def test_singleton_pattern(self):
        """Test that only one instance of Config can be created."""
        config1 = Config()
        config2 = Config()
        
        # Both variables should reference the same object
        assert config1 is config2

    def test_config_initialization_with_defaults(self, tmp_path):
        """Test Config initialization with default values when no .env file exists."""
        # Create a temporary directory for testing
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Mock the home directory to use our temp dir
        with patch('src.sokrates.config.Path.home', return_value=home_dir):
            config = Config(verbose=False)
            
            # Check that default paths are set correctly
            assert config.home_path == str(home_dir / ".sokrates")
            assert config.config_path == str(home_dir / ".sokrates" / ".env")
            assert config.logs_path == str(home_dir / ".sokrates" / "logs")
            assert config.daemon_logfile_path == str(home_dir / ".sokrates" / "logs" / "daemon.log")
            assert config.database_path == str(home_dir / ".sokrates" / "sokrates_database.sqlite")

    def test_config_initialization_with_env_vars(self, tmp_path):
        """Test Config initialization with environment variable overrides."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Set up environment variables
        env_vars = {
            'SOKRATES_API_ENDPOINT': 'https://api.example.com',
            'SOKRATES_API_KEY': 'custom_api_key',
            'SOKRATES_DEFAULT_MODEL': 'gpt-4',
            'SOKRATES_DEFAULT_MODEL_TEMPERATURE': '0.9'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                # Check that environment variables override defaults
                assert config.api_endpoint == 'https://api.example.com'
                assert config.api_key == 'custom_api_key'
                assert config.default_model == 'gpt-4'
                assert config.default_model_temperature == 0.9

    def test_config_initialization_with_custom_config_path(self, tmp_path):
        """Test Config initialization with custom configuration file path."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Set up environment variable for custom config path
        env_vars = {
            'SOKRATES_CONFIG_FILEPATH': str(tmp_path / "custom.env")
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                  config = Config(verbose=False)
                  
                  # Check that custom path is used
                  assert config.config_path == str(tmp_path / "custom.env")

    def test_directory_initialization(self, tmp_path):
        """Test directory creation functionality."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        with patch('src.sokrates.config.Path.home', return_value=home_dir):
            config = Config(verbose=False)
            
            # Check that directories were created
            assert (home_dir / ".sokrates").exists()
            assert (home_dir / ".sokrates" / "logs").exists()

    def test_get_method_with_local_values(self):
        """Test the get method with local configuration values."""
        config = Config(verbose=False)
        
        # Test getting a value that exists locally
        api_endpoint = Config.get('api_endpoint')
        assert api_endpoint == config.api_endpoint

    def test_get_method_with_env_vars(self, tmp_path):
        """Test the get method with environment variable fallback."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Set up environment variables
        env_vars = {
            'SOKRATES_TEST_VAR': 'test_value'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                # Test getting a value from environment
                test_var = Config.get('SOKRATES_TEST_VAR')
                assert test_var == 'test_value'

    def test_get_method_with_default(self, tmp_path):
        """Test the get method with default fallback."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        with patch('src.sokrates.config.Path.home', return_value=home_dir):
            config = Config(verbose=False)
            
            # Test getting a non-existent value with default
            result = Config.get('non_existent_var', 'default_value')
            assert result == 'default_value'

    def test_get_method_with_none_default(self, tmp_path):
        """Test the get method with None as default."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        with patch('src.sokrates.config.Path.home', return_value=home_dir):
            config = Config(verbose=False)
            
            # Test getting a non-existent value with None default
            result = Config.get('non_existent_var')
            assert result is None

    def test_get_local_member_value(self):
        """Test internal _get_local_member_value method."""
        config = Config(verbose=False)
        
        # Test getting a valid key
        api_endpoint = Config._get_local_member_value('api_endpoint')
        assert api_endpoint == config.api_endpoint
        
        # Test getting an invalid key
        result = Config._get_local_member_value('invalid_key')
        assert result is None

    def test_get_local_member_value_api_key_bug(self, tmp_path):
        """Test that _get_local_member_value correctly returns api_key (there was a bug in original code)."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        with patch('src.sokrates.config.Path.home', return_value=home_dir):
            config = Config(verbose=False)
            
            # This should return the actual api_key, not api_endpoint (which was a bug in original code)
            api_key_result = Config._get_local_member_value('api_key')
            assert api_key_result == config.api_key

    def test__load_env_with_mocked_file(self, tmp_path):
        """Test _load_env method with mocked .env file content."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Create a mock .env file
        env_content = """
SOKRATES_API_ENDPOINT=https://api.example.com
SOKRATES_API_KEY=mock_api_key
SOKRATES_DEFAULT_MODEL=gpt-4-turbo
"""
        
        config_file_path = home_dir / ".sokrates" / ".env"
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file_path, 'w') as f:
            f.write(env_content)
            
        # Use the actual load_dotenv function but ensure it loads our test file
        # This approach uses real behavior while maintaining proper test isolation
        with patch('src.sokrates.config.Path.home', return_value=home_dir):
            config = Config(verbose=False)
            
            assert config.api_endpoint == 'https://api.example.com'
            assert config.api_key == 'mock_api_key'
            assert config.default_model == 'gpt-4-turbo'

    def test__setup_directories_with_verbose(self, tmp_path):
        """Test directory initialization with verbose output."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # Mock print function to capture calls
        with patch('src.sokrates.config.print') as mock_print:
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=True)
                
                # Check that print was called for directory creation messages
                assert mock_print.called

    def test_config_with_verbose_output(self, tmp_path):
        """Test configuration printing when verbose is enabled."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        with patch('src.sokrates.config.print') as mock_print:
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=True)
                
                # Check that print was called for configuration details
                assert mock_print.called

    def test_config_with_empty_env_vars(self, tmp_path):
        """Test behavior when environment variables are empty strings."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_API_ENDPOINT': '',
            'SOKRATES_API_KEY': ''
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                # Empty strings should override defaults
                assert config.api_endpoint == ''
                assert config.api_key == ''

    def test_config_with_none_env_vars(self, tmp_path):
        """Test behavior when environment variables are explicitly set to None."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        # This is a bit tricky since env vars can't actually be None,
        # but we can simulate by setting them to string 'None'
        env_vars = {
            'SOKRATES_API_ENDPOINT': 'None',
            'SOKRATES_API_KEY': 'None'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                # String 'None' should be treated as string value
                assert config.api_endpoint == 'None'
                assert config.api_key == 'None'

    def test_config_with_special_characters(self, tmp_path):
        """Test configuration with special characters in environment variables."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_API_ENDPOINT': 'https://api.example.com/path?param=value&other=123',
            'SOKRATES_DEFAULT_MODEL': 'gpt-4-turbo-with-special-chars-!@#$%^&*()'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                assert config.api_endpoint == 'https://api.example.com/path?param=value&other=123'
                assert config.default_model == 'gpt-4-turbo-with-special-chars-!@#$%^&*()'

    def test_config_with_unicode_characters(self, tmp_path):
        """Test configuration with Unicode characters."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_DEFAULT_MODEL': 'gpt-4-turbo-unicode-🚀🌟'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                assert config.default_model == 'gpt-4-turbo-unicode-🚀🌟'

    def test_config_with_large_numbers(self, tmp_path):
        """Test configuration with large numeric values."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_DEFAULT_MODEL_TEMPERATURE': '0.999999999'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                config = Config(verbose=False)
                
                assert config.default_model_temperature == 0.999999999

    def test_config_with_invalid_temperature(self, tmp_path):
        """Test configuration handling of invalid temperature values."""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_DEFAULT_MODEL_TEMPERATURE': 'invalid'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                try:
                    config = Config(verbose=False)
                    assert False, "Should have raised ValueError"
                except ValueError:
                    pass  # Expected behavior

    def test_config_with_negative_temperature(self, tmp_path):
        """Test configuration with negative temperature values. -> should raise an Exception"""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_DEFAULT_MODEL_TEMPERATURE': '-0.5'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                with pytest.raises(BaseException):
                    config = Config(verbose=False) 

    def test_config_with_zero_temperature(self, tmp_path):
        """Test configuration with zero temperature value. -> should raise an exception"""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_DEFAULT_MODEL_TEMPERATURE': '0'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                with pytest.raises(BaseException):
                    config = Config(verbose=False)

    def test_config_with_too_high_temperature(self, tmp_path):
        """Test configuration with too high temperature values. -> should raise an exception"""
        home_dir = tmp_path / "test_home"
        home_dir.mkdir()
        
        env_vars = {
            'SOKRATES_DEFAULT_MODEL_TEMPERATURE': '1000.5'
        }
        
        with patch.dict(os.environ, env_vars):
            with patch('src.sokrates.config.Path.home', return_value=home_dir):
                with pytest.raises(BaseException):
                    config = Config(verbose=False)