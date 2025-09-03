"""schemas/secret.py"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class SecretBase(BaseModel):
    """Base secret model with common fields."""
    key: str
    value: str
    description: Optional[str] = None

    @field_validator("key")
    def validate_key(cls, v) -> str:
        import re
        if not isinstance(v, str):
            raise ValueError("Secret key must be a string.")
        if len(v) > 20:
            raise ValueError("Secret key must be at most 20 characters long.")
        if not re.fullmatch(r"[A-Za-z0-9-]+", v):
            raise ValueError(
                "Secret key can only contain letters, numbers, and hyphens (-)!"
            )
        return v


class SecretSave(SecretBase):
    """Model for creating a new secret."""
    pass


class SecretUpdate(BaseModel):
    """Model for updating an existing secret."""
    value: Optional[str] = None
    description: Optional[str] = None


class SecretRead(SecretBase):
    """Model for reading/displaying secret data."""
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True
