import os
import tarfile
from django.db import IntegrityError
import pandas as pd

from django.core.management.base import BaseCommand
from api.models import RealEstateListing

from tqdm import tqdm

class Command(BaseCommand):
    help='Import real estate listings from the provided CSV dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='dataset_annonces.csv.tar.gz',
            help='Path to the dataset file (default: dataset_annonces.csv.tar.gz)'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not os.path.exists(file_path):
            url = "https://storage.googleapis.com/data.meilleurecopro.com/stage/dataset_annonces.csv.tar.gz"
            self.stdout.write(self.style.WARNING(
                f"File {file_path} not found! Please download it from {url}"
            ))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Importing data from {file_path}"))

        try:
            if file_path.endswith('tar.gz'):
                extract_dir = os.path.dirname(file_path) or '.'
                with tarfile.open(file_path, 'r:gz') as tar:
                    csv_members = [m for m in tar.getmembers() if m.name.endswith('.csv')]
                    if not csv_members:
                        self.stdout.write(self.style.ERROR("No CSV file found in the tarball!"))
                        return
                    
                    csv_member = csv_members[0]
                    tar.extract(csv_member, path=extract_dir)
                    csv_path = os.path.join(extract_dir, csv_member.name)
                    self.stdout.write(self.style.SUCCESS(f"Extracted {csv_member.name}"))
            else:
                csv_path = file_path

            self.stdout.write(self.style.SUCCESS(f"Reading data from {csv_path}"))

            total_rows = sum(1 for _ in open(csv_path)) - 1 
            chunk_size = 50000
            total_imported = 0

            pbar = tqdm(total=total_rows, desc="Importing listings", unit="rows")

            for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
                self._process_chunk(chunk)
                total_imported += len(chunk)
                pbar.update(len(chunk))

                import gc
                gc.collect()

            pbar.close()
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {total_imported} listings."))
            self.stdout.write(self.style.SUCCESS("Import completed."))

            if file_path.endswith('.tar.gz') and os.path.exists(csv_path):
                os.remove(csv_path)
                self.stdout.write(self.style.SUCCESS(f"Cleaned up temporary file {csv_path}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {str(e)}"))

    def _process_chunk(self, df):
        batch_size = 5000
        listings_to_create = []
        chunk_imported = 0
            
        for _, row in df.iterrows():
            if chunk_imported == 0 and len(listings_to_create) == 0:
                self.stdout.write(self.style.SUCCESS("Sample row data:"))
                for col in df.columns:
                    self.stdout.write(f"{col}: {row.get(col)}")

            surface_value = self.handle_surface_value(row)

            listing = RealEstateListing(
                reference_id=str(row.get('REFERENCE_NUMBER', '')),
                ad_url=str(row.get('AD_URLS', '')),
                property_type=str(row.get('PROPERTY_TYPE', '')),
                dept_code=self.safe_int(row.get('DEPT_CODE', '')),
                postal_code=self.safe_int(row.get('ZIP_CODE', '')),
                city=str(row.get('CITY', '')),
                insee_code=self.safe_int(row.get('INSEE_CODE', None)),
                latitude=self.safe_float(row.get('LATITUDE', None)),
                longitude=self.safe_float(row.get('LONGITUDE', None)),
                blur_radius=self.safe_int(row.get('BLUR_RADIUS', None)),
                marketing_type=str(row.get('MARKETING_TYPE', '')),              
                price=self.safe_float(row.get('PRICE', None)),
                description=str(row.get('DESCRIPTION', None)),
                surface=surface_value,
                condominium_expenses=self.safe_float(row.get('CONDOMINIUM_EXPENSES', None)),
                caretaker=bool(row.get('CARETAKER', None)),
                heating_mode=str(row.get('HEATING_MODE', None)),
                water_heating_mode=str(row.get('WATER_HEATING_MODE', '')),
                elevator=bool(row.get('ELEVATOR', '')),
                floor=self.safe_int(row.get('FLOOR', None)),
                floor_count=self.safe_int(row.get('FLOOR_COUNT', None)),
                lot_count=self.safe_int(row.get('LOT_COUNT', None)),
                construction_year=self.safe_int(row.get('CONSTRUCTION_YEAR', None)),
                building_type=str(row.get('BUILDING_TYPE', '')),
                parking=bool(row.get('PARKING', None)),
                parking_count=self.safe_int(row.get('PARKING_COUNT', None)),
                terrace=bool(row.get('TERRACE', None)),
                terrace_surface=self.safe_float(row.get('TERRACE_SURFACE', None)),
                swimming_pool=bool(row.get('SWIMMING_POOL', None)),
                garden=bool(row.get('GARDEN', None)),
                standing=bool(row.get('STANDING', None)),
                new_build=bool(row.get('NEW_BUILD', None)),
                small_building=bool(row.get('SMALL_BUILDING', None)),
                corner_building=bool(row.get('CORNER_BUILDING', None)),
                publication_start_date=str(row.get('PUBLICATION_START_DATE', '')),
                dealer_name=str(row.get('DEALER_NAME', '')),
                dealer_type=str(row.get('DEALER_TYPE', '')),
                energy_classification=str(row.get('ENERGY_CLASSIFICATION', '')),
            )

            if chunk_imported == 0 and len(listings_to_create) == 0:
                self.stdout.write(self.style.SUCCESS("Sample listing data:"))
                self.stdout.write(f"reference_id: {listing.reference_id}")
                self.stdout.write(f"dept_code: {listing.dept_code}")
                self.stdout.write(f"surface: {listing.surface}")

            listings_to_create.append(listing)

            if len(listings_to_create) >= batch_size:
                try:
                    RealEstateListing.objects.bulk_create(
                        listings_to_create,
                        batch_size=batch_size,
                        ignore_conflicts=True
                    )
                    chunk_imported += len(listings_to_create)
                    listings_to_create = []
                except IntegrityError as e:
                    self.stdout.write(self.style.ERROR(f"Integrity error: {str(e)}"))
                    listings_to_create = []
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error in bulk_create: {str(e)}"))
                    listings_to_create = []

        if listings_to_create:
            RealEstateListing.objects.bulk_create(
                listings_to_create,
                batch_size=batch_size,
                ignore_conflicts=True
            )
            chunk_imported += len(listings_to_create)

    def handle_surface_value(self, row):
        surface_value = row.get('SURFACE', None)
        if isinstance(surface_value, str) and surface_value.startswith('[') and surface_value.endswith(']'):
            try:
                # Convert string representation of list to actual list of floats
                return [self.safe_float(x) for x in eval(surface_value)]
            except (ValueError, SyntaxError):
                return None
        else:
            try:
                # If it's a single value, convert it to a list with one element
                return [float(surface_value)] if pd.notna(surface_value) else None
            except (ValueError, TypeError):
                return None

    def safe_float(self, value):
        try:
            return float(value) if pd.notna(value) else None
        except (ValueError, TypeError):
            return None

    def safe_int(self, value):
        try:
            return int(value) if pd.notna(value) else None
        except (ValueError, TypeError):
            return None