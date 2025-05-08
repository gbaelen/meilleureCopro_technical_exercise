from django.db import models
from .utils import PropertyTypes, MarketingTypes, HeatingModes, BuildingTypes

class RealEstateListing(models.Model):
    """Model for real estate listings data."""

    reference_id = models.CharField(max_length=255, unique=True)
    ad_url = models.CharField(max_length=255, null=True, blank=True)

    property_type = models.CharField(max_length=255, choices=PropertyTypes.choices(), default=PropertyTypes.OTHER)
    dept_code = models.IntegerField(null=True, blank=True, db_index=True )
    postal_code = models.IntegerField(null=True, blank=True, db_index=True)
    city = models.CharField(max_length=255, db_index=True)

    insee_code = models.IntegerField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    blur_radius = models.IntegerField(null=True, blank=True)
    marketing_type = models.CharField(max_length=255, choices=MarketingTypes.choices())
                                      
    price = models.FloatField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    surface = models.JSONField(null=True, blank=True) #planned in m²
    condominium_expenses = models.FloatField(null=True, blank=True)
    caretaker = models.BooleanField(null=True, blank=True)
    heating_mode = models.CharField(max_length=255, choices=HeatingModes.choices())
    water_heating_mode = models.CharField(max_length=255, null=True, blank=True)

    elevator = models.BooleanField(null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    floor_count = models.IntegerField(null=True, blank=True)
    lot_count = models.IntegerField(null=True, blank=True)
    construction_year = models.IntegerField(null=True, blank=True)
    
    building_type = models.CharField(max_length=255, choices=BuildingTypes.choices(), null=True, blank=True)
    parking = models.BooleanField(null=True, blank=True)
    parking_count = models.IntegerField(null=True, blank=True)
    terrace = models.BooleanField(null=True, blank=True)
    terrace_surface = models.FloatField(null=True, blank=True)
    swimming_pool = models.BooleanField(null=True, blank=True)
    garden = models.BooleanField(null=True, blank=True)
    standing = models.BooleanField(null=True, blank=True)
    new_build = models.BooleanField(null=True, blank=True)
    small_building = models.BooleanField(null=True, blank=True)
    corner_building = models.BooleanField(null=True, blank=True)
    publication_start_date = models.CharField(max_length=255, null=True, blank=True)
    dealer_name = models.CharField(max_length=255, null=True, blank=True)
    dealer_type = models.CharField(max_length=255, null=True, blank=True)
    energy_classification = models.CharField(max_length=3, null=True, blank=True)