"""
Test parts access from a Generator
"""
from models import storage
from models.generator import Generator
from models.part import Part

"""
Objects creations
"""

#Create a generator
generator = Generator()
generator.name = "Generator 1"
generator.save()

#create a part
part = Part()
part.name = "Part 1"
part.save()

#Associate the part with the generator
generator.parts = part
generator.save()

#Retrieve the associated parts for the generator
generator_parts = generator.parts
for part in generator_parts:
    print(part.name)
