from sqlalchemy import Column, Integer, ForeignKey
from dataflow.db import Base

class RecentProjects(Base):
    __tablename__ = "RECENT_PROJECT"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('PROJECT_DETAIL.project_id', ondelete="CASCADE"), nullable=False)

