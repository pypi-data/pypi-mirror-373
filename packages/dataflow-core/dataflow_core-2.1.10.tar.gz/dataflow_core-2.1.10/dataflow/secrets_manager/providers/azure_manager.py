
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import (
    ResourceNotFoundError,
    ResourceExistsError,
    HttpResponseError,
    ClientAuthenticationError,
    ServiceRequestError
)
from ..interface import SecretManager
from ...utils.exceptions import (
    SecretNotFoundException,
    SecretAlreadyExistsException,
    SecretManagerAuthException,
    SecretManagerServiceException
)
import json

class AzureKeyVault(SecretManager):
    def __init__(self, vault_url: str):
        try:
            credential = DefaultAzureCredential(additionally_allowed_tenants=["*"])
            self.client = SecretClient(vault_url=vault_url, credential=credential)
        except ClientAuthenticationError as e:
            raise SecretManagerAuthException("initialize_azure_client", original_error=str(e))
        except ServiceRequestError as e:
            raise SecretManagerServiceException("initialize_azure_client", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("initialize_azure_client", original_error=str(e))

    def create_secret(self, vault_path: str, secret_data: dict) -> str:
        try:
            # Convert dictionary to JSON string before saving
            secret_string = json.dumps(secret_data)
            
            self.client.set_secret(
                name=vault_path,
                value=secret_string,
                content_type="application/json",
                tags={"description": secret_data.get("description", "Created by AzureKeyVault")}
            )
            return "Secret created successfully"
        except ResourceExistsError as e:
            raise SecretAlreadyExistsException("secret", vault_path, original_error=str(e))
        except ClientAuthenticationError as e:
            raise SecretManagerAuthException("create_secret", original_error=str(e))
        except HttpResponseError as e:
            if e.status_code == 403:
                raise SecretManagerAuthException("create_secret", original_error=str(e))
            elif e.status_code == 409:
                # Check if it's a scheduled deletion case
                if "deleted but not purged" in str(e) or "being recovered" in str(e):
                    raise SecretAlreadyExistsException("secret", vault_path, original_error=str(e), is_scheduled_for_deletion=True)
                else:
                    raise SecretAlreadyExistsException("secret", vault_path, original_error=str(e))
            elif e.status_code == 429:
                raise SecretManagerServiceException("create_secret", original_error=str(e))
            elif e.status_code >= 500:
                raise SecretManagerServiceException("create_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("create_secret", original_error=str(e))
        except ServiceRequestError as e:
            raise SecretManagerServiceException("create_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("create_secret", original_error=str(e))

    def get_secret_by_key(self, vault_path: str) -> dict:
        try:
            secret = self.client.get_secret(vault_path)
            secret_string = secret.value
            
            # Convert JSON string back to dictionary before returning
            secret_data = json.loads(secret_string)
            return secret_data
        except ResourceNotFoundError as e:
            raise SecretNotFoundException("secret", vault_path, original_error=str(e))
        except ClientAuthenticationError as e:
            raise SecretManagerAuthException("get_secret", original_error=str(e))
        except HttpResponseError as e:
            if e.status_code == 403:
                raise SecretManagerAuthException("get_secret", original_error=str(e))
            elif e.status_code == 404:
                raise SecretNotFoundException("secret", vault_path, original_error=str(e))
            elif e.status_code >= 500:
                raise SecretManagerServiceException("get_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("get_secret", original_error=str(e))
        except json.JSONDecodeError as e:
            raise SecretManagerServiceException("get_secret", original_error=str(e))
        except ServiceRequestError as e:
            raise SecretManagerServiceException("get_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("get_secret", original_error=str(e))

    def update_secret(self, vault_path: str, update_data: dict) -> str:
        try:
            # Get current secret data
            current_secret = self.client.get_secret(vault_path)
            current_string = current_secret.value
            
            # Convert current JSON string to dictionary
            current_data = json.loads(current_string)
            
            # Update with new data
            current_data.update(update_data)
            
            # Convert updated dictionary back to JSON string
            updated_string = json.dumps(current_data)
            
            self.client.set_secret(
                name=vault_path,
                value=updated_string,
                content_type="application/json",
                tags={"description": current_data.get("description", "")}
            )
            return "Secret updated successfully"
        except ResourceNotFoundError as e:
            raise SecretNotFoundException("secret", vault_path, original_error=str(e))
        except ClientAuthenticationError as e:
            raise SecretManagerAuthException("update_secret", original_error=str(e))
        except HttpResponseError as e:
            if e.status_code == 403:
                raise SecretManagerAuthException("update_secret", original_error=str(e))
            elif e.status_code == 404:
                raise SecretNotFoundException("secret", vault_path, original_error=str(e))
            elif e.status_code >= 500:
                raise SecretManagerServiceException("update_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("update_secret", original_error=str(e))
        except json.JSONDecodeError as e:
            raise SecretManagerServiceException("update_secret", original_error=str(e))
        except ServiceRequestError as e:
            raise SecretManagerServiceException("update_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("update_secret", original_error=str(e))

    def delete_secret(self, vault_path: str) -> str:
        try:
            if "git-ssh" in vault_path:
                # For SSH keys, try to purge immediately after deletion
                delete_poller = self.client.begin_delete_secret(vault_path)
                delete_poller.wait()  # Wait for deletion to complete
                try:
                    # Try to purge immediately (only works if soft-delete is enabled and allows purging)
                    self.client.purge_deleted_secret(vault_path)
                except (ResourceNotFoundError, HttpResponseError):
                    # Purge may fail if soft-delete is disabled or purging is not allowed - that's ok
                    pass
            else:
                # For other secrets, just delete (respects soft-delete settings)
                delete_poller = self.client.begin_delete_secret(vault_path)
                delete_poller.wait()  # Wait for deletion to complete
            return "Secret deleted successfully"
        except ResourceNotFoundError as e:
            raise SecretNotFoundException("secret", vault_path, original_error=str(e))
        except ClientAuthenticationError as e:
            raise SecretManagerAuthException("delete_secret", original_error=str(e))
        except HttpResponseError as e:
            if e.status_code == 403:
                raise SecretManagerAuthException("delete_secret", original_error=str(e))
            elif e.status_code == 404:
                raise SecretNotFoundException("secret", vault_path, original_error=str(e))
            elif e.status_code == 409:
                # Can occur if secret is already being deleted or in invalid state
                raise SecretManagerServiceException("delete_secret", original_error=str(e))
            elif e.status_code >= 500:
                raise SecretManagerServiceException("delete_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("delete_secret", original_error=str(e))
        except ServiceRequestError as e:
            raise SecretManagerServiceException("delete_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("delete_secret", original_error=str(e))

    def test_connection(self, vault_path: str) -> str:
        try:
            secret = self.get_secret_by_key(vault_path)
            return secret.get('status', 'Unknown')
        except SecretNotFoundException:
            raise
        except (SecretManagerAuthException, SecretManagerServiceException):
            raise
        except Exception as e:
            raise SecretManagerServiceException("test_connection", original_error=str(e))