from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from shared_kernel.interfaces import KeyVaultInterface
import logging


class AzureKeyVault(KeyVaultInterface):
    _instance = None

    def __new__(cls, config: dict = None):
        """
        Create or return the singleton instance of AzureKeyVault.

        Args:
            config (dict, optional): Configuration dictionary containing 'vault_url', 'tenant_id', 'client_id', and 'client_secret'.

        Returns:
            AzureKeyVault: The singleton instance of the class.
        """
        if cls._instance is None:
            if config is None:
                raise ValueError("Configuration must be provided for the first instance creation.")
            cls._instance = super(AzureKeyVault, cls).__new__(cls)
            cls._instance.__initialize(config)
        return cls._instance

    def __initialize(self, config: dict):
        """
        Initialize the Azure Key Vault connection with the given configuration.

        Args:
            config (dict): Configuration dictionary containing 'vault_url', 'tenant_id', 'client_id', and 'client_secret'.
        """
        self._vault_url = config.get('vault_url')
        self._credential = ClientSecretCredential(
            tenant_id=config.get('tenant_id'),
            client_id=config.get('client_id'),
            client_secret=config.get('client_secret')
        )
        self._client = SecretClient(vault_url=self._vault_url, credential=self._credential)
        logging.info(f"Connected to Azure Key Vault at: {self._vault_url}")

    def store_secret(self, name: str, secret: str) -> None:
        """
        Store a secret in Azure Key Vault.

        Args:
            name (str): The name of the secret.
            secret (str): The value of the secret.
        """
        self._client.set_secret(name, secret)
        logging.info(f"Stored secret '{name}'")

    def retrieve_secret(self, name: str) -> str:
        """
        Retrieve a secret from Azure Key Vault.

        Args:
            name (str): The name of the secret.

        Returns:
            str: The value of the retrieved secret.
        """
        retrieved_secret = self._client.get_secret(name)
        return retrieved_secret.value

    def delete_secret(self, name: str) -> None:
        """
        Delete a secret from Azure Key Vault.

        Args:
            name (str): The name of the secret.
        """
        self._client.begin_delete_secret(name)
        logging.info(f"Deleted secret '{name}'")

    def list_secrets(self) -> list:
        """
        List all secrets in Azure Key Vault.

        Returns:
            list: A list of secret names.
        """
        secrets = self._client.list_properties_of_secrets()
        return [secret.name for secret in secrets]
