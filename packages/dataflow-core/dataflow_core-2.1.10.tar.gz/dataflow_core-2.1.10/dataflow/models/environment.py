from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from dataflow.db import Base, Local_Base

class EnvironmentAttributes(Base):
    """
    Shared columns between Environment and ArchivedEnvironment.
    """
    __abstract__ = True 

    name = Column(String)
    url = Column(String)
    enabled = Column(Boolean, default=True)
    version = Column(String, default=0)
    is_latest = Column(Boolean, default=True)
    base_env_id = Column(Integer, default=None)
    short_name = Column(String(5))
    status = Column(String, default="Saved")
    icon = Column(String)
    py_version = Column(String)
    r_version = Column(String)
    pip_libraries = Column(Text)
    conda_libraries = Column(Text)
    r_requirements = Column(Text)
    created_date = Column(DateTime, server_default=func.now())
    created_by = Column(String)



class Environment(EnvironmentAttributes): 
    __tablename__ = 'ENVIRONMENT'

    id = Column(Integer, primary_key=True, autoincrement=True)
    short_name = Column(String(5), unique=True)

    # Relationship with ArchivedEnvironment
    archived_versions = relationship("ArchivedEnvironment", back_populates="original_environment")

class ArchivedEnvironment(EnvironmentAttributes):
    __tablename__ = 'ARCHIVED_ENVIRONMENT'

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_env_id = Column(Integer, ForeignKey('ENVIRONMENT.id', ondelete='CASCADE'))
    is_latest = Column(Boolean, default=False) 

    # Relationship with Environment
    original_environment = relationship("Environment", back_populates="archived_versions")



class JobLogs(Base):
    __tablename__ = "JOB_LOG"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    log_file_name = Column(String, unique=True, nullable=False)
    log_file_location = Column(String, nullable=False)
    status = Column(String)
    created_by = Column(String)


class LocalEnvironment(Local_Base):
    __tablename__ = "LOCAL_ENVIRONMENT"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    py_version = Column(String)
    pip_libraries = Column(Text)
    conda_libraries = Column(Text)
    status = Column(String, default="Created")
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    need_refresh = Column(Boolean, default=False)
