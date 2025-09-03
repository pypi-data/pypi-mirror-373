"""Custom exceptions for the dataflow secrets manager."""

from dataflow.utils.logger import CustomLogger
from typing import Optional


class SecretsManagerException(Exception):
    """Base exception for all secrets manager errors."""
    
    def __init__(self, message: str, details: Optional[str] = None, operation: Optional[str] = None):
        self.message = message
        self.details = details
        self.operation = operation
        self.logger = CustomLogger().get_logger(__name__)
        
        # Log detailed error information
        log_msg = f"SecretsManager Error"
        if operation:
            log_msg += f" in {operation}"
        log_msg += f": {message}"
        if details:
            log_msg += f" | Details: {details}"
            
        self.logger.error(log_msg)
        super().__init__(message)


class SecretNotFoundException(SecretsManagerException):
    """Raised when a requested secret is not found."""
    
    def __init__(self, secret_type: str, key: str, context: Optional[str] = None, original_error: Optional[str] = None):
        message = f"{secret_type.capitalize()} not found"
        
        details = f"Secret type: {secret_type}, Key: {key}"
        if context:
            details += f", Context: {context}"
        if original_error:
            details += f", Original error: {original_error}"
            
        super().__init__(message, details, f"get_{secret_type}")


class SecretAlreadyExistsException(SecretsManagerException):
    """Raised when trying to create a secret that already exists."""
    
    def __init__(self, secret_type: str, key: str, context: Optional[str] = None, original_error: Optional[str] = None, is_scheduled_for_deletion: bool = False):
        if is_scheduled_for_deletion:
            message = f"{secret_type.capitalize()} is in recovery mode. Please use another key name"
        else:
            message = f"{secret_type.capitalize()} already exists. Please use another key name"
        
        details = f"Secret type: {secret_type}, Key: {key}"
        if context:
            details += f", Context: {context}"
        if is_scheduled_for_deletion:
            details += ", Status: Scheduled for deletion"
        if original_error:
            details += f", Original error: {original_error}"
            
        super().__init__(message, details, f"create_{secret_type}")


class SecretValidationException(SecretsManagerException):
    """Raised when secret data validation fails."""
    
    def __init__(self, secret_type: str, validation_error: str, original_error: Optional[str] = None):
        message = f"Invalid {secret_type} data. Please check your input"
        
        details = f"Secret type: {secret_type}, Validation error: {validation_error}"
        if original_error:
            details += f", Original error: {original_error}"
            
        super().__init__(message, details, f"validate_{secret_type}")


class SecretManagerAuthException(SecretsManagerException):
    """Raised when authentication or authorization fails."""
    
    def __init__(self, operation: str, original_error: Optional[str] = None):
        message = "Access denied. Please check your permissions"
        
        details = f"Operation: {operation}"
        if original_error:
            details += f", Original error: {original_error}"
            
        super().__init__(message, details, operation)


class SecretManagerServiceException(SecretsManagerException):
    """Raised when the secret manager service is unavailable or fails."""
    
    def __init__(self, operation: str, original_error: Optional[str] = None):
        message = "We're experiencing some issues. Our best minds are working on it!"
        
        details = f"Operation: {operation}"
        if original_error:
            details += f", Original error: {original_error}"
            
        super().__init__(message, details, operation)


class SecretManagerConfigException(SecretsManagerException):
    """Raised when there's a configuration error."""
    
    def __init__(self, config_issue: str, original_error: Optional[str] = None):
        message = "Configuration issue detected. Please contact support"
        
        details = f"Config issue: {config_issue}"
        if original_error:
            details += f", Original error: {original_error}"
            
        super().__init__(message, details, "configuration")
