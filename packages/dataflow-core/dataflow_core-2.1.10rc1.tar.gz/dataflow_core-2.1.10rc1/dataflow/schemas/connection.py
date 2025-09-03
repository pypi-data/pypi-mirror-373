"""schemas/connection.py"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ConnectionType(str, Enum):
    """Enum for supported connection types."""
    POSTGRESQL = "PostgreSQL"
    MYSQL = "MySQL"


class ConnectionBase(BaseModel):
    """Base connection model with common fields."""
    conn_id: str
    conn_type: ConnectionType
    description: Optional[str] = None
    host: str
    schemas: Optional[str] = None
    password: str
    login: str
    port: int
    extra: Optional[str] = None

    @field_validator("conn_id")
    def validate_conn_id(cls, v) -> str:
        import re
        if not isinstance(v, str):
            raise ValueError("Connection ID must be a string.")
        if len(v) > 20:
            raise ValueError("Connection ID must be at most 20 characters long.")
        if not re.fullmatch(r"[A-Za-z0-9-]+", v):
            raise ValueError(
                "Connection ID can only contain letters, numbers, and hyphens (-)!"
            )
        return v

    @field_validator("conn_type")
    def validate_conn_type(cls, v) -> ConnectionType:
        if isinstance(v, str):
            try:
                return ConnectionType(v)
            except ValueError:
                raise ValueError(f'conn_type must be one of {[e.value for e in ConnectionType]}')
        return v


class ConnectionSave(ConnectionBase):
    """Model for creating a new connection."""
    pass


class ConnectionUpdate(BaseModel):
    """Model for updating an existing connection."""
    conn_type: Optional[ConnectionType] = None
    description: Optional[str] = None
    host: Optional[str] = None
    schemas: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    port: Optional[int] = None
    extra: Optional[str] = None

    @field_validator("conn_type")
    def validate_conn_type(cls, v) -> Optional[ConnectionType]:
        if v is None:
            return v
        if isinstance(v, str):
            # Convert string to enum if needed
            try:
                return ConnectionType(v)
            except ValueError:
                raise ValueError(f'conn_type must be one of {[e.value for e in ConnectionType]}')
        return v


class ConnectionRead(ConnectionBase):
    """Model for reading/displaying connection data."""
    pass

    class Config:
        from_attributes = True
