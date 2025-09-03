from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from dataflow.db import Base

class ServerConfig(Base):
    __tablename__ = "SERVER_CONFIG"

    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String, nullable=False, unique=True)
    slug = Column(String, unique=True, nullable=False)
    price = Column(String, nullable=False)
    ram = Column(String, nullable=False)
    cpu = Column(String, nullable=False)
    gpu = Column(String)
    default = Column(Boolean, default=False)
    tags = Column(JSONB, default=func.json([]))
    description = Column(Text, nullable=True)
    kubespawner_override = Column(JSONB, default=func.json({}))


class CustomServerConfig(Base):
    __tablename__ = "CUSTOM_SERVER"

    id = Column(Integer, primary_key=True, autoincrement=True)
    base_server_id = Column(Integer, ForeignKey(ServerConfig.id, ondelete="CASCADE"), nullable=False)
    display_name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Relationship to the server_config table
    server_config = relationship(ServerConfig)
    role_server_assocs = relationship("RoleServer", back_populates="server", cascade="all, delete-orphan")
