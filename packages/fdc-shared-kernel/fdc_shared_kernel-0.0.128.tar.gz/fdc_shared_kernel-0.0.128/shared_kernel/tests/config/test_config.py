import os
import logging
import pytest
from unittest.mock import patch, mock_open
from shared_kernel.config import Config
from shared_kernel.exceptions import InvalidConfiguration, MissingConfiguration
from shared_kernel.exceptions.configuration_exceptions import EnvFileNotFound


@pytest.fixture(autouse=True)
def configure_logging():
    logging.getLogger().setLevel(logging.DEBUG)


@patch("shared_kernel.config.find_dotenv", return_value=".env")
def test_validate_env_sample_file_not_found(mock_file):
    if os.path.exists(".env.sample"):
        os.remove(".env.sample")
    with pytest.raises(EnvFileNotFound) as excinfo:
        Config()
    assert str(excinfo.value) == "EnvFileNotFound: .env.sample file not found"


@patch("shared_kernel.config.find_dotenv", return_value=".env")
@patch("builtins.open", new_callable=mock_open, read_data="REQUIRED_KEY=\n")
def test_validate_env_sample_missing_keys(mock_file, mock_find_dotenv):
    with patch("shared_kernel.config.load_dotenv"), patch.dict(
        os.environ, {}, clear=True
    ):
        with pytest.raises(MissingConfiguration) as excinfo:
            Config().get("KEY1")
        assert "MissingConfiguration: KEY1 (Config Key: )" in str(excinfo.value)


@patch("shared_kernel.config.find_dotenv", return_value=".env")
@patch("builtins.open", new_callable=mock_open, read_data="REQUIRED_KEY=value\n")
def test_validate_env_sample_all_keys_present(mock_file, mock_find_dotenv):
    with patch("shared_kernel.config.load_dotenv"), patch.dict(
        os.environ, {"REQUIRED_KEY": "value"}, clear=True
    ):
        config = Config()
        assert config.get("REQUIRED_KEY") == "value"


@patch("shared_kernel.config.find_dotenv", return_value=".env")
def test_get_existing_variable(mock_find_dotenv):
    with patch.dict(os.environ, {"KEY": "VALUE"}), patch(
        "shared_kernel.config.load_dotenv"
    ):
        config = Config()
        assert config.get("KEY") == "VALUE"


if __name__ == "__main__":
    pytest.main(["-s", "test/config/test_config.py"])


