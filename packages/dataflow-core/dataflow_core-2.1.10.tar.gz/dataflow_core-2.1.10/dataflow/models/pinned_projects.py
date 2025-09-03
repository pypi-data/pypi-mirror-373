from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from dataflow.db import Base
from datetime import datetime

class PinnedProject(Base):
    __tablename__ = "PINNED_PROJECT"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('USER.user_id', ondelete="CASCADE"), index=True)
    project_id = Column(Integer, ForeignKey('PROJECT_DETAIL.project_id', ondelete="CASCADE"), index=True)
    pinned_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uix_user_project"),
    )