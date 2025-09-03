# models/user_team.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from dataflow.db import Base

class RoleServer(Base):
    __tablename__ = 'ROLE_SERVER'
    __table_args__ = (UniqueConstraint('role_id', 'server_id', name='_role_server_uc'),)

    role_id = Column(Integer, ForeignKey('ROLE.id', ondelete="CASCADE"), nullable=False, primary_key=True)
    server_id = Column(Integer, ForeignKey('CUSTOM_SERVER.id', ondelete="CASCADE"), nullable=False, primary_key=True)

    role = relationship("Role", back_populates="role_server_assocs")
    server = relationship("CustomServerConfig", back_populates="role_server_assocs")
