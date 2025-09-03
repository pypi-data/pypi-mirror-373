# secrets_manager/factory.py
import os
from .interface import SecretManager
from .providers.aws_manager import AWSSecretsManager
from .providers.azure_manager import AzureKeyVault
from ..configuration import ConfigurationManager

# A custom exception for clear error messages
class SecretProviderError(Exception):
    pass

def get_secret_manager() -> SecretManager:
    """
    Factory function to get the configured secret manager instance.

    Reads the cloud provider configuration from dataflow_auth.cfg
    to determine which cloud provider's secret manager to instantiate.
    """
    try:
        # dataflow_config = None
        # if os.getenv('HOSTNAME'):
        #     dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
        # else:
        dataflow_config = ConfigurationManager('/dataflow/app/config/dataflow.cfg')
    except Exception as e:
        raise SecretProviderError(
            f"Failed to read cloud provider configuration: {str(e)}. "
            "Please check that the configuration file exists and contains the 'cloud' section."
        )

    provider = dataflow_config.get_config_value('cloudProvider', 'cloud')
    if not provider:
        raise SecretProviderError(
            "The cloud provider is not configured in config file. "
            "Please set the 'cloud' value in the 'cloud' section to 'aws' or 'azure'."
        )

    provider = provider.lower()
    print(f"Initializing secret manager for provider: {provider}")

    if provider == "aws":
        return AWSSecretsManager()

    elif provider == "azure":
        vault_url = dataflow_config.get_config_value('cloudProvider', 'key_vault')
        if not vault_url:
            raise SecretProviderError(
                "AZURE_VAULT_URL must be set when using the Azure provider."
            )
        return AzureKeyVault(vault_url=vault_url)

    # You can easily add more providers here in the future
    # elif provider == "gcp":
    #     return GCPSecretManager()

    else:
        raise SecretProviderError(
            f"Unsupported secret provider: '{provider}'. Supported providers are: aws, azure."
        )