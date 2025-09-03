from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.expression import func
from dataflow.db import Base

class UserEnvironment(Base):
    """
    Table USER_ENVIRONMENT
    """

    __tablename__ = 'USER_ENVIRONMENT'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('USER.user_id', ondelete="CASCADE"), nullable=False)
    env_name = Column(String)
    timestamp = Column(DateTime, server_default=func.now(), onupdate=func.now())
