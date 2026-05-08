from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, F, Sum, DecimalField
from .models import Artist, Service, Booking, Review, UserProfile, Transaction, Notification, ChatMessage
from decimal import Decimal
from reportlab.lib.pagesizes import A4, mm
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import json, math

def home(request):
    featured_artists = Artist.objects.filter(is_active=True, is_online=True)[:6]
    active_orders = []
    if request.user.is_authenticated:
        active_orders = Booking.objects.filter(
            user=request.user
        ).exclude(
            status__in=['completed', 'cancelled']
        )[:3]
    
    # Prepare artists JSON for map fallback
    all_artists = Artist.objects.filter(is_active=True)
    artists_data = []
    for a in all_artists:
        lat_val = a.current_latitude if a.current_latitude else a.latitude
        lng_val = a.current_longitude if a.current_longitude else a.longitude
        if lat_val and lng_val:
            artists_data.append({
                'id': a.id,
                'name': a.name,
                'city': a.city,
                'specializations': a.specializations,
                'latitude': float(lat_val),
                'longitude': float(lng_val),
            })
    
    context = {
        'featured_artists': featured_artists,
        'active_orders': active_orders,
        'artists_json': json.dumps(artists_data),
    }
    return render(request, 'tedapp/home.html', context)

def artists(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = request.GET.get('radius', 20)
    city = request.GET.get('city', '')
    specialty = request.GET.get('specialty', '')
    service_type = request.GET.get('service_type', '')
    
    artists_list = Artist.objects.filter(is_active=True, is_online=True)
    
    if city:
        artists_list = artists_list.filter(city__icontains=city)
    if specialty:
        artists_list = artists_list.filter(specializations__icontains=specialty)
    
    if lat and lng:
        artists_list = artists_list.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        artists_list = list(artists_list)
        for artist in artists_list:
            artist.distance_to_user_val = artist.distance_to_user(Decimal(lat), Decimal(lng))
    
    context = {
        'artists': artists_list,
        'cities': Artist.objects.filter(is_active=True).values_list('city', flat=True).distinct(),
        'user_lat': lat,
        'user_lng': lng,
    }
    return render(request, 'tedapp/artists.html', context)

def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    services = artist.services.all()
    reviews = artist.reviews.all()[:5]
    
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    distance = None
    
    if user_lat and user_lng and (artist.current_latitude or artist.latitude):
        distance = artist.distance_to_user(Decimal(user_lat), Decimal(user_lng))
    
    context = {
        'artist': artist,
        'services': services,
        'reviews': reviews,
        'distance': distance,
    }
    return render(request, 'tedapp/artist_detail.html', context)

@login_required
def book_artist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    services = artist.services.all()
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    min_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        service_type = request.POST.get('service_type')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        address = request.POST.get('address', user_profile.address or '')
        city = request.POST.get('city', user_profile.city or '')
        user_lat = request.POST.get('user_lat', user_profile.latitude)
        user_lng = request.POST.get('user_lng', user_profile.longitude)
        description = request.POST.get('description', '')
        
        service = get_object_or_404(Service, id=service_id)
        
        total_price = service.price_min
        if service_type == 'home':
            total_price += artist.home_service_fee
        
        try:
            booking_date_obj = datetime.strptime(booking_date, '%Y-%m-%d').date()
            booking_time_obj = datetime.strptime(booking_time, '%H:%M').time()
        except ValueError:
            messages.error(request, 'Format tanggal atau waktu tidak valid. Gunakan format YYYY-MM-DD untuk tanggal dan HH:MM untuk waktu.')
            return redirect('book_artist', artist_id=artist_id)
        
        booking = Booking.objects.create(
            user=request.user,
            artist=artist,
            service=service,
            service_type=service_type,
            booking_date=booking_date_obj,
            booking_time=booking_time_obj,
            address=address,
            city=city,
            user_latitude=Decimal(user_lat) if user_lat else None,
            user_longitude=Decimal(user_lng) if user_lng else None,
            description=description,
            total_price=total_price,
        )
        
        Notification.objects.create(
            user=request.user,
            notif_type='booking_new',
            title='Pesanan Terkirim',
            message=f'Pesanan #{booking.id} dikirim ke {artist.name}. Total: Rp {int(total_price):,}. Silakan lakukan pembayaran.',
        )
        
        if artist.user:
            Notification.objects.create(
                user=artist.user,
                notif_type='booking_new',
                title='Pesanan Baru',
                message=f'Booking #{booking.id} dari {request.user.username}. Layanan: {service.name}. Total: Rp {int(total_price):,}. Jadwal: {booking_date} {booking_time}.',
            )
        
        messages.success(request, 'Pemesanan berhasil! Silakan pilih metode pembayaran.')
        return redirect('payment', booking_id=booking.id)
    
    user_lat = request.GET.get('lat') or user_profile.latitude
    user_lng = request.GET.get('lng') or user_profile.longitude
    distance = None
    if user_lat and user_lng:
        distance = artist.distance_to_user(Decimal(str(user_lat)), Decimal(str(user_lng)))
    
    context = {
        'artist': artist,
        'services': services,
        'user_profile': user_profile,
        'min_date': min_date,
        'distance': distance,
        'user_lat': user_lat,
        'user_lng': user_lng,
    }
    return render(request, 'tedapp/book_artist.html', context)

@login_required
def my_bookings(request):
    active_bookings = Booking.objects.filter(user=request.user).exclude(
        status__in=['completed', 'cancelled']
    ).order_by('-created_at')
    past_bookings = Booking.objects.filter(user=request.user, status__in=['completed', 'cancelled']).order_by('-created_at')[:10]
    
    context = {
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'tedapp/my_bookings.html', context)

@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.user != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke booking ini.')
        return redirect('my_bookings')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        booking.payment_method = payment_method
        booking.payment_status = 'paid'
        booking.save()
        
        invoice_msg = (
            f"Booking #{booking.id} telah LUNAS.\n"
            f"Layanan: {booking.service.name}\n"
            f"Artist: {booking.artist.name}\n"
            f"Total: Rp {int(booking.total_price):,}\n"
            f"Metode: {booking.get_payment_method_display()}\n"
            f"Jadwal: {booking.booking_date} {booking.booking_time}"
        ).replace(',', '.')
        
        Notification.objects.create(
            user=request.user,
            notif_type='booking_confirmed',
            title='Pembayaran Berhasil - LUNAS',
            message=invoice_msg,
        )
        
        if booking.artist.user:
            artist_msg = (
                f"Booking #{booking.id} sudah dibayar.\n"
                f"User: {booking.user.username}\n"
                f"Layanan: {booking.service.name}\n"
                f"Total: Rp {int(booking.total_price):,}\n"
                f"Metode: {booking.get_payment_method_display()}\n"
                f"Jadwal: {booking.booking_date} {booking.booking_time}"
            ).replace(',', '.')
            
            Notification.objects.create(
                user=booking.artist.user,
                notif_type='booking_new',
                title='Pembayaran Diterima',
                message=artist_msg,
            )
        
        messages.success(request, 'Pembayaran berhasil! Menunggu konfirmasi dari seniman.')
        return redirect('invoice', booking_id=booking.id)
    
    return render(request, 'tedapp/payment.html', {
        'booking': booking,
        'artist': booking.artist,
    })

@login_required
def invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.user != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke booking ini.')
        return redirect('my_bookings')
    
    return render(request, 'tedapp/invoice.html', {'booking': booking})

@login_required
def invoice_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.user != request.user:
        messages.error(request, 'Anda tidak memiliki akses ke booking ini.')
        return redirect('my_bookings')
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=(80*mm, 220*mm))
    
    y_pos = 205
    
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(colors.HexColor('#6B21A8'))
    p.drawString(28*mm, y_pos*mm, "TED")
    y_pos -= 8
    
    p.setFont("Helvetica", 7)
    p.setFillColor(colors.black)
    p.drawString(22*mm, y_pos*mm, "Tattoo on Demand")
    y_pos -= 5
    p.drawString(24*mm, y_pos*mm, "Layanan Tato Online")
    y_pos -= 8
    
    p.setFont("Helvetica-Bold", 9)
    p.drawString(28*mm, y_pos*mm, f"INV-{booking.id}")
    y_pos -= 10
    
    p.line(8*mm, y_pos*mm, 72*mm, y_pos*mm)
    y_pos -= 8
    
    p.setFont("Helvetica", 6)
    p.setFillColor(colors.gray)
    p.drawString(8*mm, y_pos*mm, f"Tgl: {booking.created_at.strftime('%d/%m/%Y')}")
    p.drawString(45*mm, y_pos*mm, f"Jam: {booking.created_at.strftime('%H:%M')}")
    y_pos -= 7
    
    p.setFillColor(colors.black)
    p.drawString(8*mm, y_pos*mm, "Customer:")
    p.drawString(28*mm, y_pos*mm, str(booking.user.username)[:15])
    y_pos -= 7
    
    p.drawString(8*mm, y_pos*mm, "Artist:")
    p.drawString(28*mm, y_pos*mm, str(booking.artist.name)[:15])
    y_pos -= 7
    
    p.drawString(8*mm, y_pos*mm, "Layanan:")
    p.drawString(28*mm, y_pos*mm, str(booking.service.name)[:15])
    y_pos -= 8
    
    p.line(8*mm, y_pos*mm, 72*mm, y_pos*mm)
    y_pos -= 8
    
    p.setFont("Helvetica", 7)
    service_name = str(booking.service.name)[:20]
    price_str = f"Rp {int(booking.service.price_min):,}".replace(',', '.')
    p.drawString(8*mm, y_pos*mm, service_name)
    p.drawRightString(72*mm, y_pos*mm, price_str)
    y_pos -= 7
    
    if booking.service_type == 'home':
        p.drawString(8*mm, y_pos*mm, "Biaya Rumah")
        p.drawRightString(72*mm, y_pos*mm, f"Rp {int(booking.artist.home_service_fee):,}".replace(',', '.'))
        y_pos -= 7
    
    p.line(8*mm, y_pos*mm, 72*mm, y_pos*mm)
    y_pos -= 7
    
    p.setFont("Helvetica-Bold", 8)
    p.drawString(8*mm, y_pos*mm, "TOTAL")
    total_str = f"Rp {int(booking.total_price):,}".replace(',', '.')
    p.drawRightString(72*mm, y_pos*mm, total_str)
    y_pos -= 10
    
    p.setFillColor(colors.black)
    p.rect(8*mm, y_pos*mm, 64*mm, 7*mm, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 7)
    p.drawString(32*mm, (y_pos+2)*mm, "LUNAS")
    y_pos -= 10
    
    p.setFont("Helvetica", 6)
    p.setFillColor(colors.gray)
    p.drawCentredString(40*mm, y_pos*mm, str(booking.get_payment_method_display()))
    y_pos -= 8
    
    p.line(8*mm, y_pos*mm, 72*mm, y_pos*mm)
    y_pos -= 7
    
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 6)
    p.drawString(8*mm, y_pos*mm, f"Tgl Tato: {booking.booking_date.strftime('%d/%m/%Y')}")
    y_pos -= 5
    p.drawString(45*mm, y_pos*mm, f"Jam: {booking.booking_time}")
    y_pos -= 5
    p.drawString(8*mm, y_pos*mm, "Tipe:")
    p.drawString(22*mm, y_pos*mm, "Studio" if booking.service_type == 'studio' else "Rumah")
    y_pos -= 8
    
    p.line(8*mm, y_pos*mm, 72*mm, y_pos*mm)
    y_pos -= 7
    
    p.setFont("Helvetica", 5)
    p.setFillColor(colors.gray)
    p.drawCentredString(40*mm, y_pos*mm, "Terima Kasih")
    y_pos -= 4
    p.drawCentredString(40*mm, y_pos*mm, "Simpan bukti ini")
    y_pos -= 4
    p.drawCentredString(40*mm, y_pos*mm, "sebagai pembayaran")
    y_pos -= 7
    
    p.setFont("Courier-Bold", 8)
    p.drawCentredString(40*mm, y_pos*mm, f"*{booking.id}{booking.created_at.strftime('%y%m%d')}*")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice-TED-{booking.id}.pdf"'
    
    return response

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Allow if user is the booking owner OR user is owner
    is_owner = False
    if hasattr(request.user, 'profile') and request.user.profile.role == 'owner':
        is_owner = True
    
    if booking.user != request.user and not is_owner:
        messages.error(request, 'Anda tidak memiliki akses ke booking ini.')
        return redirect('my_bookings')
    
    distance = booking.calculate_distance()
    return render(request, 'tedapp/booking_detail.html', {'booking': booking, 'distance': distance})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.cancellation_reason = request.POST.get('reason', 'Dibatalkan oleh pengguna')
        booking.save()
        messages.success(request, 'Pemesanan berhasil dibatalkan.')
    return redirect('my_bookings')

def search_artists(request):
    query = request.GET.get('q', '')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    artists_list = Artist.objects.filter(is_active=True)
    
    if query:
        artists_list = artists_list.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(specializations__icontains=query)
        )
    
    if lat and lng:
        artists_list = list(artists_list)
        for artist in artists_list:
            artist.distance_to_user_val = artist.distance_to_user(Decimal(lat), Decimal(lng))
    
    # Prepare artists JSON for map fallback
    all_artists = Artist.objects.filter(is_active=True)
    artists_data = []
    for a in all_artists:
        lat_val = a.current_latitude if a.current_latitude else a.latitude
        lng_val = a.current_longitude if a.current_longitude else a.longitude
        if lat_val and lng_val:
            artists_data.append({
                'id': a.id,
                'name': a.name,
                'city': a.city,
                'specializations': a.specializations,
                'latitude': float(lat_val),
                'longitude': float(lng_val),
            })
    
    context = {
        'artists': artists_list,
        'query': query,
        'user_lat': lat,
        'user_lng': lng,
        'artists_json': json.dumps(artists_data),
    }
    return render(request, 'tedapp/search.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, phone=phone)
        login(request, user)
        messages.success(request, 'Registrasi berhasil! Selamat datang di TED.')
        return redirect('home')
    
    return render(request, 'tedapp/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login berhasil!')
            return redirect('home')
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'tedapp/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logout berhasil!')
    return redirect('home')

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.city = request.POST.get('city', profile.city)
        profile.latitude = Decimal(request.POST.get('latitude')) if request.POST.get('latitude') else profile.latitude
        profile.longitude = Decimal(request.POST.get('longitude')) if request.POST.get('longitude') else profile.longitude
        profile.save()
        messages.success(request, 'Profil berhasil diupdate.')
        return redirect('my_bookings')
    return redirect('my_bookings')

# Artist Dashboard
@login_required
def artist_dashboard(request):
    try:
        artist = Artist.objects.get(userprofile__user=request.user)
    except Artist.DoesNotExist:
        messages.error(request, 'Anda bukan seniman.')
        return redirect('home')
    
    active_bookings = Booking.objects.filter(artist=artist).exclude(status__in=['completed', 'cancelled']).order_by('-created_at')
    
    context = {
        'artist': artist,
        'active_bookings': active_bookings,
    }
    return render(request, 'tedapp/artist_dashboard.html', context)

@login_required
def artist_bookings(request):
    try:
        artist = Artist.objects.get(userprofile__user=request.user)
    except Artist.DoesNotExist:
        return redirect('home')
    
    bookings = Booking.objects.filter(artist=artist).order_by('-created_at')
    context = {
        'bookings': bookings,
    }
    return render(request, 'tedapp/artist_bookings.html', context)

@login_required
def artist_booking_detail(request, booking_id):
    try:
        artist = Artist.objects.get(userprofile__user=request.user)
        booking = get_object_or_404(Booking, id=booking_id, artist=artist)
    except Artist.DoesNotExist:
        return redirect('home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            booking.status = 'confirmed'
            Notification.objects.create(
                user=booking.user,
                notif_type='booking_confirmed',
                title='Pesanan Dikonfirmasi',
                message=f'Seniman {artist.name} telah mengkonfirmasi pesanan #{booking.id}.',
            )
        elif action == 'start':
            booking.status = 'on_the_way'
            Notification.objects.create(
                user=booking.user,
                notif_type='booking_new',
                title='Seniman Dalam Perjalanan',
                message=f'Seniman {artist.name} sedang dalam perjalanan ke lokasi Anda.',
            )
        elif action == 'arrive':
            booking.status = 'arrived'
            Notification.objects.create(
                user=booking.user,
                notif_type='artist_arrived',
                title='Seniman Tiba',
                message=f'Seniman {artist.name} telah tiba di lokasi Anda!',
            )
        elif action == 'complete':
            booking.status = 'completed'
            Notification.objects.create(
                user=booking.user,
                notif_type='booking_new',
                title='Tattoo Selesai',
                message=f'Tattoo oleh {artist.name} telah selesai!',
            )
        booking.save()
        messages.success(request, 'Status pesanan diupdate.')
        return redirect('artist_booking_detail', booking_id=booking.id)
    
    distance = booking.calculate_distance()
    context = {
        'booking': booking,
        'artist': artist,
        'distance': distance,
    }
    return render(request, 'tedapp/artist_booking_detail.html', context)

@login_required
def artist_update_location(request):
    if request.method == 'POST':
        try:
            artist = Artist.objects.get(userprofile__user=request.user)
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                artist.current_latitude = Decimal(lat)
                artist.current_longitude = Decimal(lng)
                artist.save()
                return JsonResponse({'success': True})
        except Artist.DoesNotExist:
            pass
    return JsonResponse({'error': 'Invalid'}, status=400)

@login_required
def artist_complete_booking(request, booking_id):
    try:
        artist = Artist.objects.get(userprofile__user=request.user)
        booking = get_object_or_404(Booking, id=booking_id, artist=artist)
        booking.status = 'completed'
        booking.save()
        Notification.objects.create(
            user=booking.user,
            notif_type='booking_new',
            title='Tattoo Selesai',
            message=f'Tattoo oleh {artist.name} telah selesai!',
        )
        messages.success(request, 'Pesanan ditandai selesai.')
    except Artist.DoesNotExist:
        pass
    return redirect('artist_bookings')

@login_required
def notifications(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'tedapp/notifications.html', {'notifications': notifs})

@csrf_exempt
def api_nearby_artists(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = float(request.GET.get('radius', 50))
    
    # Get all active artists
    artists = list(Artist.objects.filter(is_active=True))
    
    # Demo artists fallback
    demo_artists = [
        {'id': 1, 'name': 'Budi Tattoo Artist', 'nickname': 'Budi', 'city': 'Jakarta', 'address': 'Jakarta Pusat', 'latitude': -6.2088, 'longitude': 106.8456, 'specializations': 'Tribal, Blackwork', 'rating': 4.8, 'total_reviews': 120, 'is_online': True, 'is_available_home': True, 'is_available_studio': True, 'home_service_fee': 150000},
        {'id': 2, 'name': 'Ari Ink Studio', 'nickname': 'Ari', 'city': 'Bandung', 'address': 'Bandung', 'latitude': -6.9175, 'longitude': 107.6191, 'specializations': 'Realism, Portrait', 'rating': 4.9, 'total_reviews': 85, 'is_online': True, 'is_available_home': False, 'is_available_studio': True, 'home_service_fee': 0},
        {'id': 3, 'name': 'Doni Art Design', 'nickname': 'Doni', 'city': 'Surabaya', 'address': 'Surabaya', 'latitude': -7.2575, 'longitude': 112.7521, 'specializations': 'Neo Traditional', 'rating': 4.7, 'total_reviews': 95, 'is_online': True, 'is_available_home': True, 'is_available_studio': True, 'home_service_fee': 200000},
        {'id': 4, 'name': 'Sarah Ink Art', 'nickname': 'Sarah', 'city': 'Bali', 'address': 'Denpasar, Bali', 'latitude': -8.4095, 'longitude': 115.1889, 'specializations': 'Watercolor, Floral', 'rating': 4.9, 'total_reviews': 150, 'is_online': True, 'is_available_home': True, 'is_available_studio': True, 'home_service_fee': 180000},
        {'id': 5, 'name': 'Joko Traditional', 'nickname': 'Joko', 'city': 'Yogyakarta', 'address': 'Yogyakarta', 'latitude': -7.7956, 'longitude': 110.3695, 'specializations': 'Traditional, Japanese', 'rating': 4.6, 'total_reviews': 70, 'is_online': True, 'is_available_home': True, 'is_available_studio': False, 'home_service_fee': 120000},
        {'id': 6, 'name': 'Roni Blackwork', 'nickname': 'Roni', 'city': 'Medan', 'address': 'Medan', 'latitude': 3.5881, 'longitude': 98.6730, 'specializations': 'Blackwork, Geometric', 'rating': 4.5, 'total_reviews': 45, 'is_online': False, 'is_available_home': True, 'is_available_studio': True, 'home_service_fee': 100000},
    ]
    
    # If no database artists, use demo
    if len(artists) == 0:
        return JsonResponse({'artists': demo_artists}, safe=False)
    
    if lat and lng:
        nearby = []
        for artist in artists:
            lat_val = artist.current_latitude if artist.current_latitude else artist.latitude
            lng_val = artist.current_longitude if artist.current_longitude else artist.longitude
            
            if lat_val and lng_val:
                dist = artist.distance_to_user(Decimal(lat), Decimal(lng))
                nearby.append({
                    'id': artist.id,
                    'name': artist.name,
                    'nickname': artist.nickname,
                    'photo': request.build_absolute_uri(artist.photo.url) if artist.photo else None,
                    'phone': artist.phone,
                    'email': artist.email,
                    'address': artist.address,
                    'city': artist.city,
                    'latitude': float(lat_val) if lat_val else None,
                    'longitude': float(lng_val) if lng_val else None,
                    'has_location': artist.has_location,
                    'location_status': artist.location_status,
                    'specializations': artist.specializations,
                    'description': artist.description,
                    'experience_years': artist.experience_years,
                    'rating': float(artist.rating) if artist.rating else 0,
                    'total_reviews': int(artist.total_reviews) if artist.total_reviews else 0,
                    'distance_km': round(dist, 1) if dist else None,
                    'is_available_home': artist.is_available_home,
                    'is_available_studio': artist.is_available_studio,
                    'home_service_fee': int(artist.home_service_fee) if artist.home_service_fee else 0,
                    'studio_name': artist.studio_name or '',
                    'studio_address': artist.studio_address or '',
                    'service_radius_km': float(artist.service_radius_km) if artist.service_radius_km else 20,
                    'is_verified': artist.is_verified,
                    'is_online': artist.is_online,
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'] if x['distance_km'] else 9999)
        return JsonResponse({'artists': nearby}, safe=False)
    else:
        # Return all artists without distance
        data = []
        for a in artists:
            lat_val = a.current_latitude if a.current_latitude else a.latitude
            lng_val = a.current_longitude if a.current_longitude else a.longitude
            
            data.append({
                'id': a.id,
                'name': a.name,
                'nickname': a.nickname,
                'photo': request.build_absolute_uri(a.photo.url) if a.photo else None,
                'phone': a.phone,
                'email': a.email,
                'address': a.address,
                'city': a.city,
                'latitude': float(lat_val) if lat_val else None,
                'longitude': float(lng_val) if lng_val else None,
                'has_location': a.has_location,
                'location_status': a.location_status,
                'specializations': a.specializations,
                'description': a.description,
                'experience_years': a.experience_years,
                'rating': float(a.rating) if a.rating else 0,
                'total_reviews': int(a.total_reviews) if a.total_reviews else 0,
                'distance_km': None,
                'is_available_home': a.is_available_home,
                'is_available_studio': a.is_available_studio,
                'home_service_fee': int(a.home_service_fee) if a.home_service_fee else 0,
                'studio_name': a.studio_name or '',
                'studio_address': a.studio_address or '',
                'service_radius_km': float(a.service_radius_km) if a.service_radius_km else 20,
                'is_verified': a.is_verified,
                'is_online': a.is_online,
            })
        
        # If no artists with location, return demo data
        if len(data) == 0:
            return JsonResponse({'artists': demo_artists, 'message': 'Using demo data'}, safe=False)
        
        return JsonResponse({'artists': data}, safe=False)

@csrf_exempt
def api_book(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        
        data = json.loads(request.body)
        artist_id = data.get('artist_id')
        service_id = data.get('service_id')
        service_type = data.get('service_type')
        booking_date = data.get('booking_date')
        booking_time = data.get('booking_time')
        address = data.get('address', '')
        city = data.get('city', '')
        user_lat = data.get('latitude')
        user_lng = data.get('longitude')
        
        try:
            artist = Artist.objects.get(id=artist_id)
            service = Service.objects.get(id=service_id)
            
            total_price = service.price_min
            if service_type == 'home':
                total_price += artist.home_service_fee
            
            booking = Booking.objects.create(
                user=request.user,
                artist=artist,
                service=service,
                service_type=service_type,
                booking_date=booking_date,
                booking_time=booking_time,
                address=address,
                city=city,
                user_latitude=Decimal(user_lat) if user_lat else None,
                user_longitude=Decimal(user_lng) if user_lng else None,
                total_price=total_price,
            )
            
            return JsonResponse({'success': True, 'booking_id': booking.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def api_update_location(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        try:
            artist = Artist.objects.get(userprofile__user=request.user)
            artist.current_latitude = Decimal(lat)
            artist.current_longitude = Decimal(lng)
            artist.save()
            return JsonResponse({'success': True})
        except Artist.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Not an artist'}, status=400)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def api_booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        return JsonResponse({
            'id': booking.id,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'artist_lat': float(booking.artist.current_latitude) if booking.artist.current_latitude else None,
            'artist_lng': float(booking.artist.current_longitude) if booking.artist.current_longitude else None,
            'user_lat': float(booking.user_latitude) if booking.user_latitude else None,
            'user_lng': float(booking.user_longitude) if booking.user_longitude else None,
            'distance_km': booking.calculate_distance(),
        })
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

@csrf_exempt
def api_track_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        
        return JsonResponse({
            'id': booking.id,
            'status': booking.status,
            'status_display': booking.get_status_display(),
            'artist_lat': float(booking.artist.current_latitude) if booking.artist.current_latitude else float(booking.artist.latitude) if booking.artist.latitude else None,
            'artist_lng': float(booking.artist.current_longitude) if booking.artist.current_longitude else float(booking.artist.longitude) if booking.artist.longitude else None,
            'user_lat': float(booking.user_latitude) if booking.user_latitude else None,
            'user_lng': float(booking.user_longitude) if booking.user_longitude else None,
            'distance_km': booking.calculate_distance(),
            'artist_name': booking.artist.name,
            'artist_phone': booking.artist.phone,
            'booking_date': booking.booking_date.strftime('%d %b %Y'),
            'booking_time': booking.booking_time.strftime('%H:%M'),
            'address': booking.address,
        })
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Booking not found'}, status=404)

@csrf_exempt
def api_update_booking_status(request, booking_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        
        try:
            booking = Booking.objects.get(artist__userprofile__user=request.user, id=booking_id)
            data = json.loads(request.body)
            booking.status = data.get('status', booking.status)
            booking.save()
            return JsonResponse({'success': True})
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Not authorized'}, status=403)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def api_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    notifs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    return JsonResponse({'count': notifs.count()})

@csrf_exempt
def api_artist_bookings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    try:
        artist = Artist.objects.get(userprofile__user=request.user)
        bookings = Booking.objects.filter(artist=artist).exclude(status__in=['completed', 'cancelled']).order_by('-created_at')
        
        data = [{
            'id': b.id,
            'user_name': b.user.username,
            'service_name': b.service.name,
            'service_type': b.service_type,
            'status': b.status,
            'status_display': b.get_status_display(),
            'date': b.booking_date.strftime('%d %b %Y'),
            'time': b.booking_time.strftime('%H:%M'),
            'address': b.address,
            'user_lat': float(b.user_latitude) if b.user_latitude else None,
            'user_lng': float(b.user_longitude) if b.user_longitude else None,
        } for b in bookings]
        
        return JsonResponse({'bookings': data}, safe=False)
    except Artist.DoesNotExist:
        return JsonResponse({'error': 'Not an artist'}, status=400)

@csrf_exempt
def api_artist_update_location(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        try:
            artist = Artist.objects.get(userprofile__user=request.user)
            artist.current_latitude = Decimal(lat)
            artist.current_longitude = Decimal(lng)
            artist.save()
            return JsonResponse({'success': True})
        except Artist.DoesNotExist:
            return JsonResponse({'error': 'Not an artist'}, status=400)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def api_owner_dashboard(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid method'}, status=400)
    
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            return JsonResponse({'error': 'Access denied'}, status=403)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    total_artists = Artist.objects.count()
    online_artists = Artist.objects.filter(is_online=True).count()
    active_artists = Artist.objects.filter(is_active=True).count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_users = User.objects.count()
    total_revenue = Transaction.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_bookings = Booking.objects.order_by('-created_at')[:5]
    recent_artists = Artist.objects.order_by('-created_at')[:5]
    
    return JsonResponse({
        'total_artists': total_artists,
        'online_artists': online_artists,
        'active_artists': active_artists,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_users': total_users,
        'total_revenue': int(total_revenue),
        'recent_bookings': [{
            'id': b.id,
            'user': b.user.username,
            'artist': b.artist.name,
            'status': b.status,
            'status_display': b.get_status_display(),
            'total_price': int(b.total_price),
            'date': b.booking_date.strftime('%Y-%m-%d'),
        } for b in recent_bookings],
        'recent_artists': [{
            'id': a.id,
            'name': a.name,
            'nickname': a.nickname,
            'city': a.city,
            'is_online': a.is_online,
            'has_location': a.has_location,
            'rating': float(a.rating),
        } for a in recent_artists],
    })

# ===== OWNER VIEWS =====

@login_required
def owner_dashboard(request):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user, role='user')
        return redirect('home')
    
    total_artists = Artist.objects.count()
    active_artists = Artist.objects.filter(is_active=True).count()
    online_artists = Artist.objects.filter(is_online=True).count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_users = User.objects.count()
    total_revenue = Transaction.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_bookings = Booking.objects.order_by('-created_at')[:10]
    recent_artists = Artist.objects.order_by('-created_at')[:5]
    
    context = {
        'total_artists': total_artists,
        'active_artists': active_artists,
        'online_artists': online_artists,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_artists': recent_artists,
    }
    return render(request, 'tedapp/owner_dashboard.html', context)

@login_required
def owner_app_dashboard(request):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=request.user, role='user')
        return redirect('home')
    
    total_artists = Artist.objects.count()
    online_artists = Artist.objects.filter(is_online=True).count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_users = User.objects.count()
    total_revenue = Transaction.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_bookings = Booking.objects.order_by('-created_at')[:5]
    recent_artists = Artist.objects.order_by('-created_at')[:5]
    
    context = {
        'total_artists': total_artists,
        'online_artists': online_artists,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_users': total_users,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_artists': recent_artists,
    }
    return render(request, 'tedapp/owner_app.html', context)

@login_required
def owner_artists(request):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    search = request.GET.get('q', '')
    artists_list = Artist.objects.all().order_by('-created_at')
    if search:
        artists_list = artists_list.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search) |
            Q(nickname__icontains=search)
        )
    
    context = {
        'artists': artists_list,
        'search': search,
    }
    return render(request, 'tedapp/owner_artists.html', context)

@login_required
def owner_artist_detail(request, artist_id):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    artist = get_object_or_404(Artist, id=artist_id)

    total_bookings = Booking.objects.filter(artist=artist).count()
    completed_bookings = Booking.objects.filter(artist=artist, status='completed').count()

    total_earnings = Booking.objects.filter(artist=artist, status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0

    recent_bookings = Booking.objects.filter(artist=artist).order_by('-created_at')[:10]
    
    context = {
        'artist': artist,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'total_earnings': total_earnings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'tedapp/owner_artist_detail.html', context)

@login_required
def owner_add_artist(request):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    if request.method == 'POST':
        import logging
        logger = logging.getLogger(__name__)
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', 'password123')
        name = request.POST.get('name')
        nickname = request.POST.get('nickname')
        phone = request.POST.get('phone')
        artist_email = request.POST.get('artist_email', email)
        address = request.POST.get('address')
        city = request.POST.get('city')
        description = request.POST.get('description')
        specializations = request.POST.get('specializations')
        experience_years = request.POST.get('experience_years', 0) or 0
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        
        logger.error(f"DEBUG: lat='{lat}', lng='{lng}'")
        logger.error(f"DEBUG POST keys: {list(request.POST.keys())}")

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            artist = Artist.objects.create(
                user=user,
                name=name,
                nickname=nickname,
                phone=phone,
                email=artist_email,
                address=address,
                city=city,
                description=description,
                specializations=specializations,
                experience_years=int(experience_years or 0),
                latitude=Decimal(lat) if lat else None,
                longitude=Decimal(lng) if lng else None,
                is_online=True,
                is_active=True,
                payment_gopay=request.POST.get('payment_gopay', ''),
                payment_ovo=request.POST.get('payment_ovo', ''),
                payment_dana=request.POST.get('payment_dana', ''),
                payment_shopeepay=request.POST.get('payment_shopeepay', ''),
                payment_transfer=request.POST.get('payment_transfer', ''),
                payment_bank_name=request.POST.get('payment_bank_name', ''),
            )
            UserProfile.objects.update_or_create(
                user=user,
                defaults={'phone': phone, 'role': 'artist'}
            )
            
            service_names = request.POST.getlist('service_name')
            service_price_mins = request.POST.getlist('service_price_min')
            service_price_maxs = request.POST.getlist('service_price_max')
            service_types = request.POST.getlist('service_type')
            
            for i, svc_name in enumerate(service_names):
                if svc_name:
                    price_min = int(service_price_mins[i]) if i < len(service_price_mins) and service_price_mins[i] else 0
                    price_max = int(service_price_maxs[i]) if i < len(service_price_maxs) and service_price_maxs[i] else price_min
                    svc_type = service_types[i] if i < len(service_types) and service_types[i] else 'tattoo'
                    
                    Service.objects.create(
                        artist=artist,
                        name=svc_name,
                        description=f'Layanan {svc_name}',
                        service_type=svc_type,
                        price_min=price_min,
                        price_max=price_max,
                        duration_minutes=60,
                    )
            
            if not lat or not lng:
                messages.warning(request, f'Artist {name} berhasil ditambahkan, tetapi lokasi belum di-set. Silakan edit untuk menambahkan lokasi.')
            else:
                messages.success(request, f'Artist {name} berhasil ditambahkan!')
            return redirect('owner_artists')
    
    return render(request, 'tedapp/owner_artist_form.html', {'artist': None})

@login_required
def owner_edit_artist(request, artist_id):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    artist = get_object_or_404(Artist, id=artist_id)
    
    if request.method == 'POST':
        artist.name = request.POST.get('name')
        artist.nickname = request.POST.get('nickname')
        artist.phone = request.POST.get('phone')
        artist.email = request.POST.get('artist_email', artist.email)
        artist.address = request.POST.get('address')
        artist.city = request.POST.get('city')
        artist.description = request.POST.get('description')
        artist.specializations = request.POST.get('specializations')
        artist.experience_years = int(request.POST.get('experience_years', 0) or 0)
        artist.is_available_home = 'is_available_home' in request.POST
        artist.is_available_studio = 'is_available_studio' in request.POST

        try:
            artist.home_service_fee = Decimal(request.POST.get('home_service_fee', 0) or 0)
        except:
            artist.home_service_fee = Decimal(0)
        
        artist.studio_name = request.POST.get('studio_name', '')
        artist.studio_address = request.POST.get('studio_address', '')
        
        try:
            artist.service_radius_km = Decimal(request.POST.get('service_radius_km', 20) or 20)
        except:
            artist.service_radius_km = Decimal(20)
        
        try:
            artist.latitude = Decimal(request.POST.get('latitude')) if request.POST.get('latitude') else None
            artist.longitude = Decimal(request.POST.get('longitude')) if request.POST.get('longitude') else None
        except:
            artist.latitude = None
            artist.longitude = None
        
        artist.is_verified = 'is_verified' in request.POST
        artist.is_active = 'is_active' in request.POST
        artist.is_online = 'is_online' in request.POST
        artist.payment_gopay = request.POST.get('payment_gopay', '')
        artist.payment_ovo = request.POST.get('payment_ovo', '')
        artist.payment_dana = request.POST.get('payment_dana', '')
        artist.payment_shopeepay = request.POST.get('payment_shopeepay', '')
        artist.payment_transfer = request.POST.get('payment_transfer', '')
        artist.payment_bank_name = request.POST.get('payment_bank_name', '')
        artist.save()
        
        service_ids = request.POST.getlist('service_id')
        service_names = request.POST.getlist('service_name')
        service_price_mins = request.POST.getlist('service_price_min')
        service_price_maxs = request.POST.getlist('service_price_max')
        service_types = request.POST.getlist('service_type')
        
        existing_ids = set()
        for i, svc_name in enumerate(service_names):
            if svc_name:
                price_min = int(service_price_mins[i]) if i < len(service_price_mins) and service_price_mins[i] else 0
                price_max = int(service_price_maxs[i]) if i < len(service_price_maxs) and service_price_maxs[i] else price_min
                svc_type = service_types[i] if i < len(service_types) and service_types[i] else 'tattoo'
                
                if i < len(service_ids) and service_ids[i]:
                    svc = Service.objects.get(id=service_ids[i])
                    svc.name = svc_name
                    svc.service_type = svc_type
                    svc.price_min = price_min
                    svc.price_max = price_max
                    svc.save()
                    existing_ids.add(svc.id)
                else:
                    svc = Service.objects.create(
                        artist=artist,
                        name=svc_name,
                        description=f'Layanan {svc_name}',
                        service_type=svc_type,
                        price_min=price_min,
                        price_max=price_max,
                        duration_minutes=60,
                    )
                    existing_ids.add(svc.id)
        
        artist.services.exclude(id__in=existing_ids).delete()
        
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        if not lat or not lng:
            messages.warning(request, f'Artist {artist.name} berhasil diupdate, tetapi lokasi belum di-set.')
        else:
            messages.success(request, f'Artist {artist.name} berhasil diupdate!')
        return redirect('owner_artists')
    
    return render(request, 'tedapp/owner_artist_form.html', {'artist': artist})

@login_required
def owner_delete_artist(request, artist_id):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    artist = get_object_or_404(Artist, id=artist_id)
    artist_name = artist.name
    artist.delete()
    messages.success(request, f'Artist {artist_name} berhasil dihapus!')
    return redirect('owner_artists')

@login_required
def owner_bookings(request):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    status_filter = request.GET.get('status', '')
    bookings_list = Booking.objects.all().order_by('-created_at')
    if status_filter:
        bookings_list = bookings_list.filter(status=status_filter)
    
    context = {
        'bookings': bookings_list,
        'status_filter': status_filter,
    }
    return render(request, 'tedapp/owner_bookings.html', context)

@login_required
def owner_users(request):
    try:
        profile = request.user.profile
        if profile.role != 'owner':
            messages.error(request, 'Anda tidak memiliki akses ke halaman owner.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        return redirect('home')
    
    search = request.GET.get('q', '')
    users_list = User.objects.filter(is_active=True).order_by('-date_joined')
    if search:
        users_list = users_list.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'users': users_list,
        'search': search,
    }
    return render(request, 'tedapp/owner_users.html', context)

@login_required
def chat_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    is_user = booking.user == request.user
    is_artist = hasattr(request.user, 'profile') and request.user.profile.role == 'artist' and hasattr(request.user, 'artist_profile') and booking.artist == request.user.artist_profile
    
    if not is_user and not is_artist:
        messages.error(request, 'Anda tidak memiliki akses ke chat ini.')
        return redirect('home')
    
    messages_list = booking.chat_messages.all()
    
    booking.chat_messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    other_user = booking.user if is_artist else booking.artist.user
    other_name = booking.artist.name if is_user else booking.user.username
    
    context = {
        'booking': booking,
        'chat_messages': messages_list,
        'other_user': other_user,
        'other_name': other_name,
        'is_artist_chat': is_artist,
    }
    return render(request, 'tedapp/chat.html', context)

@login_required
def chat_send(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        
        is_user = booking.user == request.user
        is_artist = hasattr(request.user, 'profile') and request.user.profile.role == 'artist' and hasattr(request.user, 'artist_profile') and booking.artist == request.user.artist_profile
        
        if not is_user and not is_artist:
            return JsonResponse({'error': 'Akses ditolak'}, status=403)
        
        message_text = request.POST.get('message', '').strip()
        if message_text:
            chat_message = ChatMessage.objects.create(
                booking=booking,
                sender=request.user,
                message=message_text
            )
            
            other_user = booking.artist.user if is_user else booking.user
            if other_user:
                Notification.objects.create(
                    user=other_user,
                    notif_type='booking_new',
                    title='Pesan Baru',
                    message=f'Ada pesan baru dari {request.user.username} di booking #{booking.id}',
                )
            
            messages.success(request, 'Pesan terkirim!')
        
        if is_user:
            return redirect('chat', booking_id=booking.id)
        else:
            return redirect('artist_chat', booking_id=booking.id)
    
    return redirect('home')

@login_required
def chat_api_messages(request, booking_id):
    if request.method == 'GET':
        booking = get_object_or_404(Booking, id=booking_id)
        
        is_user = booking.user == request.user
        is_artist = hasattr(request.user, 'profile') and request.user.profile.role == 'artist' and hasattr(request.user, 'artist_profile') and booking.artist == request.user.artist_profile
        
        if not is_user and not is_artist:
            return JsonResponse({'error': 'Akses ditolak'}, status=403)
        
        messages_list = booking.chat_messages.all().order_by('created_at')
        
        booking.chat_messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        data = [{
            'id': m.id,
            'sender': m.sender.username,
            'is_me': m.sender == request.user,
            'message': m.message,
            'time': m.created_at.strftime('%H:%M'),
            'date': m.created_at.strftime('%d %b'),
        } for m in messages_list]
        
        return JsonResponse({'messages': data}, safe=False)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)