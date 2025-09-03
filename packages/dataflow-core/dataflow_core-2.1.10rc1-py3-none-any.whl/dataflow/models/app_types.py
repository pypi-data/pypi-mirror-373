from sqlalchemy import Column, Integer, String, Boolean
from dataflow.db import Base

class AppType(Base):
    __tablename__ = "RUNTIME_APP_TYPE"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, unique=True, nullable=True)
    display_name = Column(String, nullable=False)
    code_based = Column(Boolean, nullable=False)