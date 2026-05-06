from django.contrib import admin
from .models import Artist, Service, Booking, Review, UserProfile, Transaction, Notification

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'is_online', 'is_available_home', 'is_available_studio', 'is_active', 'is_verified']
    list_filter = ['city', 'is_online', 'is_available_home', 'is_available_studio', 'is_active', 'is_verified']
    search_fields = ['name', 'city', 'specializations']
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('name', 'nickname', 'phone', 'email', 'address', 'city', 'description', 'specializations', 'experience_years', 'photo')
        }),
        ('Lokasi', {
            'fields': ('latitude', 'longitude', 'current_latitude', 'current_longitude', 'service_radius_km')
        }),
        ('Layanan', {
            'fields': ('is_available_home', 'is_available_studio', 'home_service_fee', 'studio_name', 'studio_address')
        }),
        ('Nomor Pembayaran', {
            'fields': ('payment_gopay', 'payment_ovo', 'payment_dana', 'payment_shopeepay', 'payment_bank_name', 'payment_transfer')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'is_online')
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist', 'service_type', 'price_min', 'price_max', 'duration_minutes']
    list_filter = ['service_type', 'artist__city']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'artist', 'service_type', 'booking_date', 'status', 'total_price']
    list_filter = ['status', 'service_type', 'booking_date']
    search_fields = ['user__username', 'artist__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'artist', 'rating', 'created_at']
    list_filter = ['rating', 'artist__city']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city']
    search_fields = ['user__username', 'phone', 'city']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notif_type', 'title', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']