"""models.py"""
from sqlalchemy import Column, Integer, String, ForeignKey
from dataflow.db import Base

class Session(Base):
    """
    Table SESSION
    """

    __tablename__='SESSION'

    id = Column(Integer, primary_key=True, index=True, unique=True, nullable=False, autoincrement=True)
    session_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('USER.user_id', ondelete="CASCADE"), nullable=False)    


    