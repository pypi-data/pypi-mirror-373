from sqlalchemy import Column, String, Enum, DateTime, Integer, func, ForeignKey
from sqlalchemy.orm import relationship
from dataflow.db import Base

class ProjectDetails(Base):
    __tablename__ = "PROJECT_DETAIL"
    
    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String, nullable=False)
    git_url = Column(String)
    git_branch = Column(String, nullable=True)
    git_folder = Column(String, nullable=True)
    type = Column(String, ForeignKey('RUNTIME_APP_TYPE.name', ondelete="CASCADE"), nullable=False)
    slug = Column(String, nullable=False, unique=True)
    runtime = Column(String, nullable=False)
    py_env = Column(String, nullable=True)
    launch_url = Column(String, nullable=True)  
    status = Column(Enum("pending", "created" ,"deployed", "stopped", "failed", name="deployment_status"), default="created")
    last_deployed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    created_by = Column(String, nullable=False)

    app_type = relationship("AppType")