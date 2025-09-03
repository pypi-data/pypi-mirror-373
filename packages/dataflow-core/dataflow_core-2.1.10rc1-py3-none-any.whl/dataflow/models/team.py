"""models.py"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from dataflow.db import Base

class Team(Base):
    """
    Table TEAM
    """

    __tablename__='TEAM'

    team_id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    team_name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    
    user_team_assocs = relationship("UserTeam", back_populates="team")