from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='artist_profile')
    name = models.CharField(max_length=200)
    nickname = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='artists/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Lokasi saat ini (mobile tracking)')
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text='Lokasi saat ini (mobile tracking)')
    description = models.TextField()
    specializations = models.CharField(max_length=300)
    experience_years = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    is_available_home = models.BooleanField(default=True)
    is_available_studio = models.BooleanField(default=True)
    home_service_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    studio_name = models.CharField(max_length=200, blank=True)
    studio_address = models.CharField(max_length=300, blank=True)
    service_radius_km = models.DecimalField(max_digits=5, decimal_places=2, default=20, help_text='Radius layanan dalam km')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False, help_text='Artist sedang online/menerima order')
    payment_gopay = models.CharField(max_length=30, blank=True, help_text='Nomor GoPay')
    payment_ovo = models.CharField(max_length=30, blank=True, help_text='Nomor OVO')
    payment_dana = models.CharField(max_length=30, blank=True, help_text='Nomor DANA')
    payment_shopeepay = models.CharField(max_length=30, blank=True, help_text='Nomor ShopeePay')
    payment_transfer = models.CharField(max_length=50, blank=True, help_text='Nomor Rekening Transfer Bank')
    payment_bank_name = models.CharField(max_length=50, blank=True, help_text='Nama Bank')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def has_location(self):
        return bool(self.latitude and self.longitude)
    
    @property
    def location_status(self):
        if self.current_latitude and self.current_longitude:
            return 'current'
        elif self.latitude and self.longitude:
            return 'saved'
        return 'none'
    
    def distance_to_user(self, user_lat, user_lng):
        import math
        lat = self.current_latitude if self.current_latitude else self.latitude
        lng = self.current_longitude if self.current_longitude else self.longitude
        if not lat or not lng:
            return None
        R = 6371
        lat1 = math.radians(float(lat))
        lat2 = math.radians(float(user_lat))
        dlat = math.radians(float(user_lat) - float(lat))
        dlon = math.radians(float(user_lng) - float(lng))
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def can_reach_user(self, user_lat, user_lng):
        dist = self.distance_to_user(user_lat, user_lng)
        if dist is None:
            return False
        return dist <= float(self.service_radius_km)

class Service(models.Model):
    SERVICE_TYPES = [
        ('tattoo', 'Tattoo'),
        ('piercing', 'Piercing'),
        ('removal', 'Tattoo Removal'),
        ('touchup', 'Touch Up'),
    ]
    
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    price_min = models.DecimalField(max_digits=10, decimal_places=0)
    price_max = models.DecimalField(max_digits=10, decimal_places=0)
    duration_minutes = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} - {self.artist.name}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('confirmed', 'Dikonfirmasi'),
        ('on_the_way', 'Dalam Perjalanan'),
        ('arrived', 'Tiba'),
        ('started', 'Sedang Dikerjakan'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('studio', 'Ke Studio'),
        ('home', 'Ke Rumah'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Tunai'),
        ('gopay', 'GoPay'),
        ('ovo', 'OVO'),
        ('dana', 'DANA'),
        ('shopeepay', 'ShopeePay'),
        ('transfer', 'Transfer Bank'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('paid', 'Lunas'),
        ('failed', 'Gagal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    user_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    user_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    estimated_arrival = models.IntegerField(default=0, help_text='Estimasi waktu arrival dalam menit')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.artist.name}"
    
    def calculate_distance(self):
        import math
        if not self.user_latitude or not self.user_longitude or not self.artist.current_latitude:
            return None
        R = 6371
        lat1 = math.radians(float(self.user_latitude))
        lat2 = math.radians(float(self.artist.current_latitude))
        dlat = math.radians(float(self.artist.current_latitude) - float(self.user_latitude))
        dlon = math.radians(float(self.artist.current_longitude) - float(self.user_longitude))
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.artist.name}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('artist', 'Artist'),
        ('owner', 'Owner'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    notification_token = models.CharField(max_length=255, blank=True, help_text='FCM token untuk push notification')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    def __str__(self):
        return self.user.username

class Transaction(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Tunai'),
        ('gopay', 'GoPay'),
        ('ovo', 'OVO'),
        ('dana', 'DANA'),
        ('shopeepay', 'ShopeePay'),
        ('transfer', 'Transfer Bank'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Menunggu'),
        ('paid', 'Lunas'),
        ('failed', 'Gagal'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Transaction {self.id} - Booking {self.booking.id}"

class Notification(models.Model):
    NOTIF_TYPES = [
        ('booking_new', 'Pesanan Baru'),
        ('booking_confirmed', 'Pesanan Dikonfirmasi'),
        ('booking_cancelled', 'Pesanan Dibatalkan'),
        ('artist_arrived', 'Seniman Tiba'),
        ('promo', 'Promosi'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class ChatMessage(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Chat #{self.id} - Booking {self.booking.id}"