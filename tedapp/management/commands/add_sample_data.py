from django.core.management.base import BaseCommand
from tedapp.models import Artist, Service
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add sample artists and services'

    def handle(self, *args, **options):
        artists_data = [
            {
                'name': 'Rizky Pratama',
                'nickname': 'Kiky Ink',
                'phone': '081234567890',
                'email': 'kiky@studio.com',
                'address': 'Jl. Sudirman No. 123',
                'city': 'Jakarta',
                'latitude': Decimal('-6.208764'),
                'longitude': Decimal('106.845599'),
                'description': 'Seniman tato profesional dengan pengalaman lebih dari 10 tahun. Spesialisasi dalam realisme dan neo-tradisional.',
                'specializations': 'Realism,Neo-Traditional,Blackwork',
                'experience_years': 10,
                'rating': Decimal('4.9'),
                'total_reviews': 156,
                'is_available_home': True,
                'is_available_studio': True,
                'home_service_fee': Decimal('200000'),
                'studio_name': 'Black Ink Studio',
                'studio_address': 'Jl. Sudirman No. 123, Jakarta',
                'is_verified': True,
            },
            {
                'name': 'Sarah Wijaya',
                'nickname': 'Sarah Tattoo',
                'phone': '081234567891',
                'email': 'sarah@inkart.com',
                'address': 'Jl. Pahlawan No. 45',
                'city': 'Bandung',
                'latitude': Decimal('-6.917464'),
                'longitude': Decimal('107.619125'),
                'description': 'Female tattoo artist yang fokus pada minimalis dan fine line tattoo. Gaya clean dan aesthetic.',
                'specializations': 'Minimalist,Fine Line,Floral',
                'experience_years': 5,
                'rating': Decimal('4.8'),
                'total_reviews': 89,
                'is_available_home': True,
                'is_available_studio': True,
                'home_service_fee': Decimal('150000'),
                'studio_name': 'Ink Art Studio',
                'studio_address': 'Jl. Pahlawan No. 45, Bandung',
                'is_verified': True,
            },
            {
                'name': 'Budi Santoso',
                'nickname': 'Budi Dragon',
                'phone': '081234567892',
                'email': 'budi@dragontattoo.com',
                'address': 'Jl. Malioboro No. 78',
                'city': 'Yogyakarta',
                'latitude': Decimal('-7.575492'),
                'longitude': Decimal('110.824367'),
                'description': 'Master dalam traditional dan Japanese style. Portofolio lengkap dengan berbagai proyek besar.',
                'specializations': 'Japanese,Traditional,Irezumi',
                'experience_years': 15,
                'rating': Decimal('4.95'),
                'total_reviews': 234,
                'is_available_home': False,
                'is_available_studio': True,
                'home_service_fee': Decimal('0'),
                'studio_name': 'Dragon Tattoo Studio',
                'studio_address': 'Jl. Malioboro No. 78, Yogyakarta',
                'is_verified': True,
            },
            {
                'name': 'Andi Wijaya',
                'nickname': 'Andi Ink',
                'phone': '081234567893',
                'email': 'andi@tedapp.com',
                'address': 'Jl. Pemuda No. 90',
                'city': 'Surabaya',
                'latitude': Decimal('-7.257471'),
                'longitude': Decimal('112.752099'),
                'description': 'Artist modern dengan sentuhan geometric dan dotwork. Terkenal dengan detail yang presisi.',
                'specializations': 'Geometric,Dotwork,Script',
                'experience_years': 7,
                'rating': Decimal('4.7'),
                'total_reviews': 67,
                'is_available_home': True,
                'is_available_studio': True,
                'home_service_fee': Decimal('250000'),
                'studio_name': 'Modern Ink Studio',
                'studio_address': 'Jl. Pemuda No. 90, Surabaya',
                'is_verified': False,
            },
            {
                'name': 'Maya Putri',
                'nickname': 'Maya Art',
                'phone': '081234567894',
                'email': 'maya@colorart.com',
                'address': 'Jl. Braga No. 56',
                'city': 'Bandung',
                'latitude': Decimal('-6.919862'),
                'longitude': Decimal('107.608639'),
                'description': 'Color specialist dengan teknik shading yang luar biasa. Fokus pada realism berwarna dan portrait.',
                'specializations': 'Color Realism,Portrait,Watercolor',
                'experience_years': 8,
                'rating': Decimal('4.85'),
                'total_reviews': 112,
                'is_available_home': True,
                'is_available_studio': True,
                'home_service_fee': Decimal('180000'),
                'studio_name': 'Color Art Studio',
                'studio_address': 'Jl. Braga No. 56, Bandung',
                'is_verified': True,
            },
            {
                'name': 'Fajar Nugroho',
                'nickname': 'Fajar Tribal',
                'phone': '081234567895',
                'email': 'fajar@tribalink.com',
                'address': 'Jl. Pandegiling No. 34',
                'city': 'Surabaya',
                'latitude': Decimal('-7.265869'),
                'longitude': Decimal('112.738286'),
                'description': 'Tribal dan blackwork expert. Desain bold dan statement yang kuat.',
                'specializations': 'Tribal,Blackwork,Old School',
                'experience_years': 12,
                'rating': Decimal('4.75'),
                'total_reviews': 98,
                'is_available_home': True,
                'is_available_studio': True,
                'home_service_fee': Decimal('200000'),
                'studio_name': 'Tribal Ink Studio',
                'studio_address': 'Jl. Pandegiling No. 34, Surabaya',
                'is_verified': True,
            },
        ]

        services_data = [
            {'name': 'Small Tattoo', 'description': 'Ukuran kecil (max 5x5cm)', 'service_type': 'tattoo', 'price_min': Decimal('300000'), 'price_max': Decimal('500000'), 'duration_minutes': 60},
            {'name': 'Medium Tattoo', 'description': 'Ukuran sedang (5x5cm - 10x10cm)', 'service_type': 'tattoo', 'price_min': Decimal('500000'), 'price_max': Decimal('1000000'), 'duration_minutes': 120},
            {'name': 'Large Tattoo', 'description': 'Ukuran besar (>10x10cm)', 'service_type': 'tattoo', 'price_min': Decimal('1000000'), 'price_max': Decimal('3000000'), 'duration_minutes': 240},
            {'name': 'Piercing', 'description': 'Body piercing service', 'service_type': 'piercing', 'price_min': Decimal('100000'), 'price_max': Decimal('300000'), 'duration_minutes': 30},
            {'name': 'Touch Up', 'description': 'Perbaikan tato existing', 'service_type': 'touchup', 'price_min': Decimal('200000'), 'price_max': Decimal('500000'), 'duration_minutes': 60},
        ]

        for artist_data in artists_data:
            artist, created = Artist.objects.get_or_create(
                name=artist_data['name'],
                defaults=artist_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created artist: {artist.name}'))
                for service_data in services_data:
                    service_data['artist'] = artist
                    Service.objects.create(**service_data)
                self.stdout.write(self.style.SUCCESS(f'Added services for {artist.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Artist already exists: {artist.name}'))

        self.stdout.write(self.style.SUCCESS('Sample data added successfully!'))