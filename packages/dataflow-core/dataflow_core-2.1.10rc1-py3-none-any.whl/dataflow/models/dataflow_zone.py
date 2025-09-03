from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from dataflow.db import Base

class DataflowZone(Base):
    __tablename__ = "DATAFLOW_ZONE"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    is_runtime = Column(Boolean, default=False)
    subdomain = Column(String)
    spark_enabled = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    role_zone_assocs = relationship("RoleZone", back_populates="zone")

    def __repr__(self):
        return f"<DataflowZone(id={self.id}, slug='{self.slug}', display_name='{self.display_name}', display_order={self.display_order})>"