from django.contrib import admin
from .models import RealEstateListing

@admin.register(RealEstateListing)
class RealEstateListingAdmin(admin.ModelAdmin):
    list_display = (
        'reference_id', 'property_type', 'dept_code', 'postal_code', 'city',
        'latitude', 'longitude', 'marketing_type', 'price', 'surface',
        'condominium_expenses', 'heating_mode', 'elevator', 'floor',
        'floor_count', 'lot_count', 'construction_year'
    )
    search_fields = ('reference_id', 'city', 'dept_code', 'property_type')
    list_filter = ('property_type', 'dept_code', 'city')
    ordering = ('-id',)