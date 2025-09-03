from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from dataflow.db import Base

class RoleZone(Base):
    __tablename__ = 'ROLE_ZONE'

    role_id = Column(Integer, ForeignKey('ROLE.id', ondelete="CASCADE"), primary_key=True)
    zone_id = Column(Integer, ForeignKey('DATAFLOW_ZONE.id', ondelete="CASCADE"), primary_key=True)
    is_default = Column(Boolean, default=False, nullable=False)

    role = relationship("Role", back_populates="role_zone_assocs")
    zone = relationship("DataflowZone", back_populates="role_zone_assocs")

    def __repr__(self):
        return f"<RoleZone(role_id={self.role_id}, zone_id={self.zone_id}, is_default={self.is_default})>"