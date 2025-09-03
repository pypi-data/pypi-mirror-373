"""models.py"""
from sqlalchemy import Column, Integer, String, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from dataflow.db import Base

class User(Base):
    """
    Table USER
    """

    __tablename__='USER'

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_name = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    role_id = Column(Integer, ForeignKey('ROLE.id'), nullable=False)
    image = Column(LargeBinary)
    image_url = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    password = Column(String, nullable=False)
    active_env = Column(String)
    active_env_type = Column(String, nullable=True)
    current_server = Column(String)
    show_server_page = Column(Boolean, default = True)

    role_details = relationship("Role")

    user_team_assocs = relationship("UserTeam", back_populates="user")