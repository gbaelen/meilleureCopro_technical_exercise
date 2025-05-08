import logging
import requests
import pandas as pd

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from .models import RealEstateListing
from .serializer import StatisticsQuerySerializer, StatisticsResponseSerializer, RealEstateListingSerializer, BienIciImportSerializer

logger = logging.getLogger(__name__)

def index(request):
    return redirect(reverse('api:stats_form'))

def form_view(request):
    return render(request, 'listings/form.html')

class StatisticsView(APIView):
    def get(self, request):
        serializer = StatisticsQuerySerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query_type = serializer.validated_data['query_type']
        query_value = serializer.validated_data['query_value']

        if query_type == 'department':
            listings = RealEstateListing.objects.filter(dept_code=query_value)
        elif query_type == 'city':
            listings = RealEstateListing.objects.filter(city__iexact=query_value)
        elif query_type == 'postal_code':
            listings = RealEstateListing.objects.filter(postal_code=query_value)

        listings_data = list(listings.values('condominium_expenses', 'surface', 'price'))

        if not listings_data:
            return Response(
                {"error": f"No data found for {query_type}: {query_value}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        df = pd.DataFrame(listings_data)

        def calculate_fees_per_sqm(row):
            try:
                if pd.notna(row['condominium_expenses']) and pd.notna(row['surface']):
                    # Get the first surface value from the list if it exists
                    surface = row['surface'][0] if isinstance(row['surface'], list) and row['surface'] else None
                    if surface and surface > 0:
                        return row['condominium_expenses'] / surface
                return None
            except Exception as e:
                logger.error(f"Error calculating fees per sqm: {str(e)}")
                return None

        df['fees_per_sqm'] = df.apply(calculate_fees_per_sqm, axis=1)

        def safe_stat(series):
            try:
                if series.empty:
                    return 0.0

                clean_series = series.dropna()
                if clean_series.empty:
                    return 0.0
                
                value = clean_series.mean()
                return 0.0 if pd.isna(value) else float(value)
            except Exception as e:
                logger.error(f"Error in safe_stat: {str(e)}")
                return 0.0

        def safe_quantile(series, q):
            try:
                if series.empty:
                    return 0.0

                clean_series = series.dropna()
                if clean_series.empty:
                    return 0.0
                value = clean_series.quantile(q)
                return 0.0 if pd.isna(value) else float(value)
            except Exception as e:
                logger.error(f"Error in safe_quantile: {str(e)}")
                return 0.0

        df['surface_float'] = df['surface'].apply(
            lambda x: float(x[0]) if isinstance(x, list) and x and not pd.isna(x[0]) else None
        )

        stats = {
            'mean_price': safe_stat(df['price']),
            'mean_surface': safe_stat(df['surface'].apply(lambda x: x[0] if isinstance(x, list) and x else None)),
            'mean_fees': safe_stat(df['condominium_expenses']),
            'mean_fees_per_sqm': safe_stat(df['fees_per_sqm']),
            'quantile_10_price': safe_quantile(df['price'], 0.1),
            'quantile_90_price': safe_quantile(df['price'], 0.9),
            'quantile_10_surface': safe_quantile(df['surface'].apply(lambda x: x[0] if isinstance(x, list) and x else None), 0.1),
            'quantile_90_surface': safe_quantile(df['surface'].apply(lambda x: x[0] if isinstance(x, list) and x else None), 0.9),
            'quantile_10_fees': safe_quantile(df['condominium_expenses'], 0.1),
            'quantile_90_fees': safe_quantile(df['condominium_expenses'], 0.9),
            'quantile_10_fees_per_sqm': safe_quantile(df['fees_per_sqm'], 0.1),
            'quantile_90_fees_per_sqm': safe_quantile(df['fees_per_sqm'], 0.9),
        }

        stats = {k: float(v) if not pd.isna(v) else 0.0 for k, v in stats.items()}
        logger.info(f"Calculated stats: {stats}")

        response_serializer = StatisticsResponseSerializer(data=stats)
        if not response_serializer.is_valid():
            logger.error(f"Serializer validation errors: {response_serializer.errors}")
            return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"Response data: {response_serializer.data}")
        return Response({
            'query_type': query_type,
            'query_value': query_value,
            'count': len(listings_data),
            'statistics': response_serializer.data
        })
    
class AddBienIciListingView(APIView):
    """API view for adding a new listing from BienIci."""
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'listings/stats_form.html'
    
    def get(self, request):
        serializer = BienIciImportSerializer()
        return Response({'serializer': serializer})
    
    def post(self, request):
        serializer = BienIciImportSerializer(data=request.data)
        
        if not serializer.is_valid():
            if request.accepted_renderer.format == 'html':
                messages.error(request, "Invalid URL format")
                return redirect(reverse('api:stats_form'))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        url = serializer.validated_data['url']
        
        try:
            listing_id = url.split('/')[-1]
            
            api_url = f"https://www.bienici.com/realEstateAd.json?id={listing_id}"
            response = requests.get(api_url)
            response.raise_for_status()
            
            listing_data = response.json()
            
            listing = self._process_bienici_data(listing_data, url)
            
            if request.accepted_renderer.format == 'html':
                messages.success(request, f"Successfully added listing: {listing.reference_id}")
                return redirect(reverse('api:stats_form'))
            
            return Response({
                'message': 'Listing added successfully',
                'listing': RealEstateListingSerializer(listing).data
            }, status=status.HTTP_201_CREATED)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching data from BienIci: {str(e)}"
            if request.accepted_renderer.format == 'html':
                messages.error(request, error_msg)
                return redirect(reverse('api:stats_form'))
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            error_msg = f"Error processing listing: {str(e)}"
            if request.accepted_renderer.format == 'html':
                messages.error(request, error_msg)
                return redirect(reverse('api:stats_form'))
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_bienici_data(self, data, url):
        """Process the data from BienIci API and save it to the database."""
        postal_code = data.get('postalCode', '')
        dept_code = None
        
        try:
            postal_code = int(postal_code)
            dept_code = postal_code // 1000
        except (ValueError, TypeError):
            postal_code = None
        
        print(data.get('reference'))
        existing = RealEstateListing.objects.filter(reference_id=data.get('reference', '')).first()
        if existing:
            existing.ad_url = url
            existing.postal_code = postal_code
            existing.DEPT_CODE = dept_code
            existing.city = data.get('city', '')
            existing.price = data.get('price', 0)
            existing.surface = data.get('surfaceArea', 0)
            existing.condominium_expenses = data.get('fees', {}).get('yearly', 0)
            existing.description = data.get('description', '')
            
            existing.floor = data.get('floor', None)
            existing.construction_year = data.get('constructionYear', None)
            existing.property_type = self._map_property_type(data.get('propertyType', ''))
            
            if 'coordinates' in data:
                existing.latitude = data['coordinates'].get('lat', None)
                existing.longitude = data['coordinates'].get('lng', None)
            
            existing.save()
            return existing
        
        listing = RealEstateListing(
            reference_id=data.get('reference', ''),
            ad_url=url,
            postal_code=postal_code,
            dept_code=dept_code,
            city=data.get('city', ''),
            price=data.get('price', 0),
            surface=data.get('surfaceArea', 0),
            condominium_expenses=data.get('fees', {}).get('yearly', 0),
            description=data.get('description', ''),
            floor=data.get('floor', None),
            construction_year=data.get('constructionYear', None),
            property_type=self._map_property_type(data.get('propertyType', '')),
        )
        
        if 'coordinates' in data:
            listing.latitude = data['coordinates'].get('lat', None)
            listing.longitude = data['coordinates'].get('lng', None)
            
        listing.save()
        return listing
    
    def _map_property_type(self, bienici_type):
        """Map BienIci property type to our model choices."""
        # This is a simplified mapping
        mapping = {
            'APARTMENT': 'APARTMENT',
        }
        return mapping.get(bienici_type, 'OTHER')