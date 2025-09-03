
import boto3
import json
from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError, NoCredentialsError
from ..interface import SecretManager
from ...utils.exceptions import (
    SecretNotFoundException,
    SecretAlreadyExistsException,
    SecretManagerAuthException,
    SecretManagerServiceException
)

class AWSSecretsManager(SecretManager):
    def __init__(self):
        try:
            self.client = boto3.client('secretsmanager')
        except EndpointConnectionError as e:
            raise SecretManagerServiceException("initialize_aws_client", original_error=str(e))
        except NoCredentialsError as e:
            raise SecretManagerAuthException("initialize_aws_client", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("initialize_aws_client", original_error=str(e))

    def create_secret(self, vault_path: str, secret_data: dict) -> str:
        try:
            # Convert dictionary to JSON string before saving
            secret_string = json.dumps(secret_data)
            
            self.client.create_secret(
                Name=vault_path,
                SecretString=secret_string,
                Description=secret_data.get("description", "Created by AWSSecretsManager")
            )
            return "Secret created successfully"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ResourceExistsException':
                raise SecretAlreadyExistsException("secret", vault_path, original_error=str(e))
            elif error_code == 'InvalidRequestException' and 'scheduled for deletion' in error_message:
                # Special case for secrets in recovery period
                raise SecretAlreadyExistsException("secret", vault_path, original_error=str(e), is_scheduled_for_deletion=True)
            elif error_code in ['AccessDeniedException', 'UnauthorizedOperation', 'UnrecognizedClientException']:
                raise SecretManagerAuthException("create_secret", original_error=str(e))
            elif error_code in ['InvalidRequestException', 'LimitExceededException']:
                raise SecretManagerServiceException("create_secret", original_error=str(e))
            elif error_code == 'InternalServiceErrorException':
                raise SecretManagerServiceException("create_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("create_secret", original_error=str(e))
        except BotoCoreError as e:
            raise SecretManagerServiceException("create_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("create_secret", original_error=str(e))

    def get_secret_by_key(self, vault_path: str) -> dict:
        try:
            response = self.client.get_secret_value(SecretId=vault_path)
            secret_string = response.get('SecretString')
            
            # Convert JSON string back to dictionary before returning
            secret_data = json.loads(secret_string)
            return secret_data
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundException("secret", vault_path, original_error=str(e))
            elif error_code in ['AccessDeniedException', 'UnauthorizedOperation', 'UnrecognizedClientException']:
                raise SecretManagerAuthException("get_secret", original_error=str(e))
            elif error_code in ['InvalidRequestException', 'DecryptionFailureException']:
                raise SecretManagerServiceException("get_secret", original_error=str(e))
            elif error_code == 'InternalServiceErrorException':
                raise SecretManagerServiceException("get_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("get_secret", original_error=str(e))
        except json.JSONDecodeError as e:
            raise SecretManagerServiceException("get_secret", original_error=str(e))
        except BotoCoreError as e:
            raise SecretManagerServiceException("get_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("get_secret", original_error=str(e))

    def update_secret(self, vault_path: str, update_data: dict) -> str:
        try:
            # Get current secret data
            current = self.client.get_secret_value(SecretId=vault_path)
            current_string = current['SecretString']
            
            # Convert current JSON string to dictionary
            current_data = json.loads(current_string)
            
            # Update with new data
            current_data.update(update_data)
            
            # Convert updated dictionary back to JSON string
            updated_string = json.dumps(current_data)
            
            self.client.update_secret(
                SecretId=vault_path,
                SecretString=updated_string,
                Description=current_data.get('description', '')
            )
            return "Secret updated successfully"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundException("secret", vault_path, original_error=str(e))
            elif error_code in ['AccessDeniedException', 'UnauthorizedOperation', 'UnrecognizedClientException']:
                raise SecretManagerAuthException("update_secret", original_error=str(e))
            elif error_code in ['InvalidRequestException', 'DecryptionFailureException']:
                raise SecretManagerServiceException("update_secret", original_error=str(e))
            elif error_code == 'InternalServiceErrorException':
                raise SecretManagerServiceException("update_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("update_secret", original_error=str(e))
        except json.JSONDecodeError as e:
            raise SecretManagerServiceException("update_secret", original_error=str(e))
        except BotoCoreError as e:
            raise SecretManagerServiceException("update_secret", original_error=str(e))
        except Exception as e:
            raise SecretManagerServiceException("update_secret", original_error=str(e))

    def delete_secret(self, vault_path: str) -> str:
        try:
            if "git-ssh" in vault_path:
                self.client.delete_secret(
                    SecretId=vault_path,
                    ForceDeleteWithoutRecovery=True
                )
            else:
                self.client.delete_secret(
                    SecretId=vault_path,
                    RecoveryWindowInDays=7
                )
            return "Secret deleted successfully"
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                raise SecretNotFoundException("secret", vault_path, original_error=str(e))
            elif error_code in ['AccessDeniedException', 'UnauthorizedOperation', 'UnrecognizedClientException']:
                raise SecretManagerAuthException("delete_secret", original_error=str(e))
            elif error_code == 'InvalidRequestException':
                # Can occur if secret is already scheduled for deletion or in invalid state
                raise SecretManagerServiceException("delete_secret", original_error=str(e))
            elif error_code == 'InternalServiceErrorException':
                raise SecretManagerServiceException("delete_secret", original_error=str(e))
            else:
                raise SecretManagerServiceException("delete_secret", original_error=str(e))
        except BotoCoreError as e:
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