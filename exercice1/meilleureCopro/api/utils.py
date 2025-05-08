from enum import Enum

class Choices(Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class PropertyTypes(Choices, Enum):
    APARTMENT = 'APARTMENT'
    OTHER = 'OTHER'
    
class MarketingTypes(Choices, Enum):
    LIFE_ANNUITY = 'LIFE_ANNUITY'
    SALE = 'SALE'
    
class HeatingModes(Choices, Enum):
    INDIVIDUAL = 'INDIVIDUAL'
    COLLECTIVE = 'COLLECTIVE'

class BuildingTypes(Choices, Enum):
    RECENT = 'RECENT'