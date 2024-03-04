#!/usr/bin/env python3
"""Generator Module"""
from models.base_model import BaseModel, Base
from models import storage_type
from models.part import Part
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.sql.schema import Table
from sqlalchemy.orm import relationship

if storage_type == 'db':
  generator_part = Table('generator_part', Base.metadata,
                         Column('generator_id', String(60),
                                ForeignKey('generators.id'),
                                primary_key=True,
                                nullable=False),
                         Column('part_id', String(60),
                                ForeignKey('parts.id'),
                                primary_key=True,
                                nullable=False)
                         )


class Generator(BaseModel, Base):
  """Generator class / table model """
  __tablename__ = 'generators'
  if storage_type == 'db':
    name = Column(String(128), nullable=False)
    manufacturer_id = Column(String(60), ForeignKey('manufacturers.id'), nullable=False)
    partids = []
    parts = relationship(Part, secondary='generator_part', viewonly=False, overlaps="generator_parts, generators")

  else:
    name = ""
    manufacturer_id = ""
    part_ids = []

    @property
    def parts(self):
      '''returns the list of part instances with generator_id
         equals the current Generator.id
         FileStorage relationship between Generator and Part
      '''
      from models import storage
      parts = storage.all(Part)
      return [part for part in parts.values() if self.id in part.generator_ids]


    @parts.setter
    def parts(self, obj):
      '''method for adding a Part.id to the 
         atrribute parts_ids, accepts only 
         Part objects
      '''
      if obj is not None and isinstance(obj, Part):
        if obj.id not in self.part_ids:
          self.part_ids.append(obj.id)
  
