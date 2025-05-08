from rest_framework import serializers
from .models import RealEstateListing

class RealEstateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealEstateListing
        fields = '__all__'

class BienIciImportSerializer(serializers.Serializer):
    url = serializers.URLField(
        help_text="BienIci listing URL (e.g. https://www.bienici.com/annonce/orpi-1-099934E0KUR9)"
    )

class StatisticsQuerySerializer(serializers.Serializer):
    QUERY_TYPES = (
        ('department', 'Department'),
        ('city', 'City'),
        ('postal_code', 'Postal Code'),
    )
    
    query_type = serializers.ChoiceField(choices=QUERY_TYPES)
    query_value = serializers.CharField(max_length=255)

class StatisticsResponseSerializer(serializers.Serializer):
    mean_price = serializers.FloatField()
    mean_surface = serializers.FloatField()
    mean_fees = serializers.FloatField()
    mean_fees_per_sqm = serializers.FloatField()
    quantile_10_price = serializers.FloatField()
    quantile_90_price = serializers.FloatField()
    quantile_10_surface = serializers.FloatField()
    quantile_90_surface = serializers.FloatField()
    quantile_10_fees = serializers.FloatField()
    quantile_90_fees = serializers.FloatField()
    quantile_10_fees_per_sqm = serializers.FloatField()
    quantile_90_fees_per_sqm = serializers.FloatField()