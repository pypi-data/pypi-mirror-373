"""models.py"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from dataflow.db import Base

class EnvironmentStatus(Base):
    """
    Table ENVIRONMENT_STATUS
    """

    __tablename__='ENVIRONMENT_STATUS'

    id = Column(Integer, ForeignKey('ENVIRONMENT.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    status = Column(String, nullable=False)
    comment = Column(String)
    status_changed_date = Column(DateTime, server_default=func.now(), nullable=False)
    