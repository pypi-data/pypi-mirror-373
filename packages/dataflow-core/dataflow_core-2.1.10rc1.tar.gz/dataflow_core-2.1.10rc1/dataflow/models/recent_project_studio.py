"""models.py"""
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Boolean
from sqlalchemy.sql import func
from dataflow.db import Local_Base as Base

class RecentProjectStudio(Base):
    __tablename__ = 'RECENT_PROJECT_STUDIO'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, nullable=False, index=True)
    app_name = Column(String, nullable=False, index=True)
    project_name = Column(String, nullable=False)
    project_path = Column(String, nullable=False)
    last_opened_date = Column(DateTime, server_default=func.now(), nullable=False)
    remember = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint(user_name, project_path, app_name, name='user_name_project_path_app_name_unique'),
    )