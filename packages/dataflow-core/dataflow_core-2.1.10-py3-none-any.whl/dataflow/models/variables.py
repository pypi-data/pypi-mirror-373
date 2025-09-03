from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func, UniqueConstraint, CheckConstraint, Boolean
from dataflow.db import Base

class Variable(Base):
    """
    Unified VARIABLE table to support both Studio and Runtime environments.
    """

    __tablename__ = 'VARIABLE'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    runtime = Column(String, nullable=True)
    slug = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, ForeignKey('USER.user_name'), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


    __table_args__ = (
        CheckConstraint(type.in_(['variable', 'secret']), name='check_variable_type'),
        UniqueConstraint('key', 'runtime', 'slug', 'created_by', name='unique_key'),
    )