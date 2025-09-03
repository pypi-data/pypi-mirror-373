from abc import ABC, abstractmethod


class KeyVaultInterface(ABC):
    """
    An abstract base class for a key vault interface that defines methods for interacting
    with a key vault service. Subclasses must implement these methods to manage secrets.

    Methods
    -------
    __init__(config: dict):
        Initializes the key vault connection with the given configuration dictionary.

    store_secret(name: str, secret: str) -> None:
        Stores a secret in the key vault.

    retrieve_secret(name: str) -> str:
        Retrieves a secret from the key vault by its name.

    delete_secret(name: str) -> None:
        Deletes a secret from the key vault by its name.

    list_secrets() -> list:
        Lists all secrets currently stored in the key vault.
    """

    @abstractmethod
    def __init__(self, config: dict):
        """
        Initialize the key vault connection with the given configuration dictionary.

        Parameters:
        - config (dict): A dictionary containing configuration settings for connecting to the key vault.
        """
        pass

    @abstractmethod
    def store_secret(self, name: str, secret: str) -> None:
        """
        Store a secret in the key vault.

        Parameters:
        - name (str): The name of the secret to be stored.
        - secret (str): The value of the secret to be stored.
        """
        pass

    @abstractmethod
    def retrieve_secret(self, name: str) -> str:
        """
        Retrieve a secret from the key vault.

        Parameters:
        - name (str): The name of the secret to be retrieved.

        Returns:
        - str: The value of the retrieved secret.
        """
        pass

    @abstractmethod
    def delete_secret(self, name: str) -> None:
        """
        Delete a secret from the key vault.

        Parameters:
        - name (str): The name of the secret to be deleted.
        """
        pass

    @abstractmethod
    def list_secrets(self) -> list:
        """
        List all secrets in the key vault.

        Returns:
        - list: A list of names of all the secrets stored in the key vault.
        """
        pass
