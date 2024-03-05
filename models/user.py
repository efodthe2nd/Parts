"""User module"""
from models.base_model import BaseModel, Base
from models import storage_type
from models.part import Part
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class User(BaseModel, Base):
    """This class initializes User instances"""
    __tablename__ = 'users'
    if storage_type == 'db':
        name = Column(String(128), nullable=False)
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        parts = relationship('Part', backref='user', cascade='all, delete, delete-orphan')
    else:
        name: str = ""