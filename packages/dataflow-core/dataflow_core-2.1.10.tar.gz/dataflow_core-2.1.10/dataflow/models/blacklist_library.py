# models/blacklist_library.py
from sqlalchemy import Column, Integer, String, UniqueConstraint
from dataflow.db import Base

class BlacklistedLibrary(Base):
    """
    BlacklistedLibrary model represents a table for storing blacklisted libraries with their versions.

    Attributes:
        id (int): Primary key of the table, auto-incremented.
        library_name (str): The name of the blacklisted library.
        version (str): The version of the blacklisted library.

    Unique constraint to ensure the combination of library_name and version is unique.
    """

    __tablename__ = "BLACKLISTED_LIBRARY"
    
    id = Column(Integer, primary_key=True, index=True, doc="Primary key for the library.")
    library_name = Column(String, index=True, doc="The name of the blacklisted library.")
    version = Column(String, doc="The version of the blacklisted library.")

    __table_args__ = (
        UniqueConstraint('library_name', 'version', name='uq_library_version'),
    )
    
