#!/usr/bin/env python3
"""Part Module"""
from models.base_model import BaseModel, Base
from models import storage_type
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

class Part(BaseModel, Base):
  """This Part Class, contains Generator ID, price and name """
  __tablename__ = 'parts'
  if storage_type == 'db':
    name = Column(String(128), nullable=False)
    price = Column(String(60), nullable=False)
    generator_parts = relationship('Generator', 
                                   secondary="generator_part",
                                   backref='generators',
                                   overlaps="generator_parts, generators")

  else:
    name = ""
    price = ""
    generator_ids = []

    @property
    def generators(self):
      """Get all generators assocaited with this part"""
      from models import storage
      generators = storage.all(Generator)
      return [generator for generator in generator.values() if self.id in generator.part_ids]
    
    @generators.setter
    def generators(self, obj):
      """Add a generator to this part"""
      if obj is not None and isinstance(obj, Generator):
        if obj.id not in self.generator_ids:
          self.generator_ids.append(obj.id)
