"""models.py"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from dataflow.db import Base

class GitSSH(Base):
    __tablename__ = 'GIT_SSH'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, ForeignKey('USER.user_name', ondelete="CASCADE"), nullable=False)
    description = Column(String)
    key_name = Column(String, nullable=False)
    created_date = Column(DateTime, server_default=func.now(), nullable=False)
    last_used_date = Column(DateTime)

    __table_args__ = (
        UniqueConstraint(user_name, key_name, name='user_name_key_name_unique'),
    )