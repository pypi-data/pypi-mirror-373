from .interface import SecretManager
from ..schemas.connection import ConnectionSave, ConnectionUpdate, ConnectionRead
from ..schemas.secret import SecretSave, SecretUpdate, SecretRead
from ..schemas.git_ssh import SSHSave, SSHRead
from abc import ABC, abstractmethod
from typing import List

# --------------------------------------------------------------------------
# BASE ACCESSOR
# This contains all the methods for CRUD operations on secrets, connections, and SSH keys.
# --------------------------------------------------------------------------
class _BaseAccessor(ABC):
    def __init__(self, secret_manager: SecretManager):
        self.secret_manager = secret_manager

    @abstractmethod
    def _get_vault_path(self, secret_type: str, key: str) -> str:
        """This must be implemented by each specific context."""
        pass

    # --------------------------------------------------------------------------
    # CONNECTION CRUD OPERATIONS
    # --------------------------------------------------------------------------
    def create_connection(self, connection_data: ConnectionSave) -> str:
        """Create a new connection."""
        vault_path = self._get_vault_path("connections", connection_data.conn_id)
        # Convert schema to dict and then to JSON string for storage
        connection_dict = connection_data.model_dump()
        return self.secret_manager.create_secret(vault_path, connection_dict)

    def get_connection(self, key: str) -> ConnectionRead:
        """Get a connection by key."""
        vault_path = self._get_vault_path("connections", key)
        raw_data = self.secret_manager.get_secret_by_key(vault_path)
        # Convert stored dict back to schema
        return ConnectionRead(**raw_data)

    def update_connection(self, key: str, connection_data: ConnectionUpdate) -> str:
        """Update an existing connection."""
        vault_path = self._get_vault_path("connections", key)
        
        # First, get the existing connection data
        existing_data: dict = self.secret_manager.get_secret_by_key(vault_path)
        
        # Convert update schema to dict, only include non-None values
        update_dict: dict = connection_data.model_dump(exclude_none=True)

        # Merge existing data with update data
        existing_data.update(update_dict)
        
        # Send the complete merged data back to storage
        return self.secret_manager.update_secret(vault_path, existing_data)

    def delete_connection(self, key: str) -> str:
        """Delete a connection."""
        vault_path = self._get_vault_path("connections", key)
        return self.secret_manager.delete_secret(vault_path)

    def test_connection(self, key: str):
        """Test a connection."""
        vault_path = self._get_vault_path("connections", key)
        return self.secret_manager.test_connection(vault_path)

    # --------------------------------------------------------------------------
    # SSH CRUD OPERATIONS
    # --------------------------------------------------------------------------
    def create_ssh(self, ssh_data: SSHSave) -> str:
        """Create a new SSH key."""
        vault_path = self._get_vault_path("git-ssh", ssh_data.key_name)
        # Convert schema to dict for storage
        ssh_dict = ssh_data.model_dump()
        return self.secret_manager.create_secret(vault_path, ssh_dict)

    def get_ssh(self, key: str) -> SSHRead:
        """Get an SSH key by key."""
        vault_path = self._get_vault_path("git-ssh", key)
        raw_data = self.secret_manager.get_secret_by_key(vault_path)
        # Convert stored dict back to schema
        return SSHRead(**raw_data)

    def delete_ssh(self, key: str) -> str:
        """Delete an SSH key."""
        vault_path = self._get_vault_path("git-ssh", key)
        return self.secret_manager.delete_secret(vault_path)

    # --------------------------------------------------------------------------
    # SECRET CRUD OPERATIONS
    # --------------------------------------------------------------------------
    def create_secret(self, secret_data: SecretSave) -> str:
        """Create a new secret."""
        vault_path = self._get_vault_path("secrets", secret_data.key)
        # Convert schema to dict for storage
        secret_dict = secret_data.model_dump()
        return self.secret_manager.create_secret(vault_path, secret_dict)

    def get_secret(self, key: str) -> SecretRead:
        """Get a secret by key."""
        vault_path = self._get_vault_path("secrets", key)
        raw_data = self.secret_manager.get_secret_by_key(vault_path)
        # Convert stored dict back to schema
        return SecretRead(**raw_data)

    def update_secret(self, key: str, secret_data: SecretUpdate) -> str:
        """Update an existing secret."""
        vault_path = self._get_vault_path("secrets", key)
        # Convert schema to dict, only include non-None values
        update_dict = secret_data.model_dump(exclude_none=True)
        return self.secret_manager.update_secret(vault_path, update_dict)

    def delete_secret(self, key: str) -> str:
        """Delete a secret."""
        vault_path = self._get_vault_path("secrets", key)
        return self.secret_manager.delete_secret(vault_path)

# --------------------------------------------------------------------------
# CONTEXT-SPECIFIC ACCESSORS
# These classes implement the logic for building the vault path based on the context.
# --------------------------------------------------------------------------
class _RuntimeAccessor(_BaseAccessor):
    def __init__(self, secret_manager: SecretManager, runtime_env: str, slug: str = None):
        super().__init__(secret_manager)
        self.runtime_env = runtime_env
        self.slug = slug

    def _get_vault_path(self, secret_type: str, key: str) -> str:
        # Special case for git-ssh in runtime context
        if secret_type == "git-ssh":
            return f"{self.runtime_env}-{secret_type}-{self.slug}"

        # Standard format for all other secret types
        context = self.slug if self.slug else "global"
        return f"{self.runtime_env}-{context}-{secret_type}-{key}"

class _StudioAccessor(_BaseAccessor):
    def __init__(self, secret_manager: SecretManager, user_name: str):
        super().__init__(secret_manager)
        self.user_name = user_name

    def _get_vault_path(self, secret_type: str, key: str) -> str:
        return f"{self.user_name}-{secret_type}-{key}"

# --------------------------------------------------------------------------
# PUBLIC INTERFACE CLASS
# This is the class external systems will interact with.
# --------------------------------------------------------------------------
class SecretsService:
    def __init__(self, secret_manager: SecretManager):
        self._secret_manager = secret_manager

    def runtime(self, env: str, slug: str = None) -> _RuntimeAccessor:
        """Sets the context to RUNTIME and returns the appropriate accessor."""
        return _RuntimeAccessor(self._secret_manager, env, slug)

    def studio(self, user: str) -> _StudioAccessor:
        """Sets the context to STUDIO and returns the appropriate accessor."""
        return _StudioAccessor(self._secret_manager, user)