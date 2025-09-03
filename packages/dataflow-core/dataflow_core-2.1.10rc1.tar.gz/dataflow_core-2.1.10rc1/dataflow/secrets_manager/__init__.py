# secrets_manager/__init__.py

from .factory import get_secret_manager
from .service import SecretsService

# 1. Call the factory to get the configured low-level secret manager
#    (e.g., an instance of AWSSecretsManager or AzureKeyVault).
#    This happens only once when the package is first imported.
secret_manager_instance = get_secret_manager()

# 2. Create the single, high-level service instance that the rest of
#    your application will use. It wraps the low-level instance.
secrets_service = SecretsService(secret_manager=secret_manager_instance)