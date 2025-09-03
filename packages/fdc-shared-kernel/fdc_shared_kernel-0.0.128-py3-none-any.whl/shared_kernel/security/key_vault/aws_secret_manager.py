import boto3
import logging
from botocore.exceptions import ClientError
from shared_kernel.interfaces import KeyVaultInterface


class AWSSecretsManager(KeyVaultInterface):
    _instance = None

    def __new__(cls, config: dict = None):
        if cls._instance is None:
            if config is None:
                raise ValueError("Configuration must be provided for the first initialization.")
            cls._instance = super(AWSSecretsManager, cls).__new__(cls)
            cls._instance._initialize(config)
        return cls._instance

    def _initialize(self, config: dict):
        """
        Initialize the AWS Secrets Manager connection with the given configuration.

        Args:
            config (dict): Configuration dictionary containing region_name, aws_access_key_id, aws_secret_access_key
        """
        self._region_name = config.get('region_name')
        self._aws_access_key_id = config.get('AWS_SERVER_PUBLIC_KEY')
        self._aws_secret_access_key = config.get('AWS_SERVER_SECRET_KEY')
        self._client = boto3.client('secretsmanager',
                                    aws_access_key_id=self._aws_access_key_id,
                                    aws_secret_access_key=self._aws_secret_access_key,
                                    region_name=self._region_name)
        logging.info(f"Connected to AWS Secrets Manager in region: {self._region_name}")

    def store_secret(self, name: str, secret: str) -> None:
        """
        Store a secret in AWS Secrets Manager.

        Args:
            name (str): The name of the secret.
            secret (str): The value of the secret.

        Raises:
            ClientError: If storing the secret fails.
        """
        try:
            self._client.create_secret(Name=name, SecretString=secret)
            logging.info(f"Stored secret '{name}'")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                self._client.update_secret(SecretId=name, SecretString=secret)
                logging.info(f"Updated secret '{name}'")
            else:
                logging.error(f"Failed to update secret '{name}' | Error: '{e}'")
                raise e

    def retrieve_secret(self, name: str) -> str:
        """
        Retrieve a secret from AWS Secrets Manager.

        Args:
            name (str): The name of the secret.

        Returns:
            str: The value of the retrieved secret, or None if retrieval fails.

        Raises:
            ClientError: If retrieving the secret fails.
        """
        try:
            response = self._client.get_secret_value(SecretId=name)
            return response['SecretString']
        except ClientError as e:
            logging.error(f"Error retrieving secret '{name}': {e}")
            return None

    def delete_secret(self, name: str) -> None:
        """
        Delete a secret from AWS Secrets Manager.

        Args:
            name (str): The name of the secret.

        Raises:
            ClientError: If deleting the secret fails.
        """
        try:
            self._client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
            logging.info(f"Deleted secret '{name}'")
        except ClientError as e:
            logging.error(f"Error deleting secret '{name}': {e}")

    def list_secrets(self) -> list:
        """
        List all secrets in AWS Secrets Manager.

        Returns:
            list: A list of secret names.

        Raises:
            ClientError: If listing the secrets fails.
        """
        try:
            response = self._client.list_secrets()
            return [secret['Name'] for secret in response['SecretList']]
        except ClientError as e:
            logging.error(f"Error listing secrets: {e}")
            return []
