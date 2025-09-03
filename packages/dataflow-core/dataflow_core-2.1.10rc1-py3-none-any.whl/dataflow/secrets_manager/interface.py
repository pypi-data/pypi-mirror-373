from abc import ABC, abstractmethod

class SecretManager(ABC):
    @abstractmethod
    def create_secret(self, vault_path: str, secret_data: dict) -> str:
        pass

    @abstractmethod
    def get_secret_by_key(self, vault_path: str):
        pass

    @abstractmethod
    def update_secret(self, vault_path: str, update_data):
        pass

    @abstractmethod
    def delete_secret(self, vault_path: str):
        pass

    @abstractmethod
    def test_connection(self, vault_path: str):
        pass