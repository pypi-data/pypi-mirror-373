"""models.py"""
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from dataflow.db import Base
import enum

class BaseRoleField(enum.Enum):
    admin = "admin"
    user = "user"
    applicant = "applicant"

class Role(Base):
    """
    Table Role
    """

    __tablename__='ROLE'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    base_role = Column(Enum(BaseRoleField), nullable=False, default=BaseRoleField.user)

    users = relationship("User", back_populates="role_details", cascade="all, delete-orphan")
    role_server_assocs = relationship("RoleServer", back_populates="role")
    role_zone_assocs = relationship("RoleZone", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', base_role='{self.base_role}')>"