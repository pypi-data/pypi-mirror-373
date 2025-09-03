# models/user_team.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from dataflow.db import Base

class UserTeam(Base):
    __tablename__ = 'USER_TEAM'
    __table_args__ = (UniqueConstraint('user_id', 'team_id', name='_user_team_uc'),)

    user_id = Column(Integer, ForeignKey('USER.user_id', ondelete="CASCADE"), nullable=False, primary_key=True)
    team_id = Column(Integer, ForeignKey('TEAM.team_id', ondelete="CASCADE"), nullable=False, primary_key=True)

    user = relationship("User", back_populates="user_team_assocs")
    team = relationship("Team", back_populates="user_team_assocs")