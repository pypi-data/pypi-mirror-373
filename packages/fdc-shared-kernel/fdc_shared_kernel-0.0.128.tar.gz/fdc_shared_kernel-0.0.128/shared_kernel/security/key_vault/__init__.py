from shared_kernel.interfaces import KeyVaultInterface
from shared_kernel.security.key_vault.aws_secret_manager import AWSSecretsManager
from shared_kernel.security.key_vault.azure_keyvault import AzureKeyVault


class KeyVaultManager:

    keyvault_classes = {"AZURE": AzureKeyVault, "AWS": AWSSecretsManager}

    @staticmethod
    def create_data_bus(vault_type: str, config: dict) -> KeyVaultInterface:
        keyvault_class = KeyVaultManager.keyvault_classes.get(vault_type)
        if keyvault_class is None:
            raise ValueError(f"Unknown vault type: {vault_type}")
        return keyvault_class(config)
