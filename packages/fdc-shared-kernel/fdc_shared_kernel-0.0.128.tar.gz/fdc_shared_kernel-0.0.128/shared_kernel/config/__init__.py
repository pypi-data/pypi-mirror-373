import os
import logging
from typing import Any
from dotenv import load_dotenv, find_dotenv
from shared_kernel.exceptions import MissingConfiguration, InvalidConfiguration, EnvFileNotFound


class Config:

    _instance = None

    def __new__(cls, env_path=".env"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize(env_path)
        return cls._instance

    def _initialize(self, env_path=None):
        """
        Initializes the Config class with an optional path to the .env file.

        :param env_path: Optional path to the .env file. Defaults to finding the .env file in the current directory.
        """
        if env_path is None:
            dotenv_path = find_dotenv()
            if not dotenv_path:
                logging.error(".env file not found")
                raise EnvFileNotFound(".env file not found")
        else:
            dotenv_path = env_path

        logging.info(f"Loading environment variables from {dotenv_path}")
        load_dotenv(dotenv_path)
        self._validate_env_sample()

    def _validate_env_sample(self):
        # Read the .env.sample file
        sample_env_path = ".env.sample"
        if not os.path.exists(sample_env_path):
            raise EnvFileNotFound(".env.sample file not found")

        with open(sample_env_path, "r") as file:
            required_keys = {
                line.strip().split("=")[0]
                for line in file
                if line.strip() and not line.startswith("#")
            }

        # Populate config with environment variables
        missing_keys = []
        for key in required_keys:
            value = os.getenv(key)
            if value is None:
                missing_keys.append(key)

        if missing_keys:
            raise InvalidConfiguration(f"Missing keys in the env file : {missing_keys}")

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Retrieves the value of an environment variable.

        :param key: The name of the environment variable.
        :param default: Default value to return if the environment variable is not set.
        :return: The value of the environment variable.
        """
        value = os.getenv(key, default)
        if value is None:
            raise MissingConfiguration(key)
        return value
