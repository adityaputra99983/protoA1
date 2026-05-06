from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('artists/', views.artists, name='artists'),
    path('artist/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('book/<int:artist_id>/', views.book_artist, name='book_artist'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('invoice/<int:booking_id>/', views.invoice, name='invoice'),
    path('invoice/<int:booking_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('search/', views.search_artists, name='search_artists'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('notifications/', views.notifications, name='notifications'),
    
    # Artist routes
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('artist-bookings/', views.artist_bookings, name='artist_bookings'),
    path('artist-booking/<int:booking_id>/', views.artist_booking_detail, name='artist_booking_detail'),
    path('artist-update-location/', views.artist_update_location, name='artist_update_location'),
    path('artist-complete-booking/<int:booking_id>/', views.artist_complete_booking, name='artist_complete_booking'),
    path('artist-chat/<int:booking_id>/', views.chat_view, name='artist_chat'),
    path('artist-chat/<int:booking_id>/send/', views.chat_send, name='artist_chat_send'),
    
    # Chat routes
    path('chat/<int:booking_id>/', views.chat_view, name='chat'),
    path('chat/<int:booking_id>/send/', views.chat_send, name='chat_send'),
    path('api/chat/<int:booking_id>/messages/', views.chat_api_messages, name='chat_api_messages'),
    
    # API routes
    path('api/artists/', views.api_nearby_artists, name='api_artists'),
    path('api/book/', views.api_book, name='api_book'),
    path('api/location/', views.api_update_location, name='api_location'),
    path('api/booking/<int:booking_id>/status/', views.api_booking_status, name='api_booking_status'),
    path('api/booking/<int:booking_id>/update/', views.api_update_booking_status, name='api_update_booking_status'),
    path('api/booking/<int:booking_id>/track/', views.api_track_booking, name='api_track_booking'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/artist/bookings/', views.api_artist_bookings, name='api_artist_bookings'),
    path('api/artist/location/', views.api_artist_update_location, name='api_artist_location'),
    path('api/owner/dashboard/', views.api_owner_dashboard, name='api_owner_dashboard'),
    
    # Owner routes
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/app/', views.owner_app_dashboard, name='owner_app_dashboard'),
    path('owner/artists/', views.owner_artists, name='owner_artists'),
    path('owner/artist/add/', views.owner_add_artist, name='owner_add_artist'),
    path('owner/artist/<int:artist_id>/edit/', views.owner_edit_artist, name='owner_edit_artist'),
    path('owner/artist/<int:artist_id>/detail/', views.owner_artist_detail, name='owner_artist_detail'),
    path('owner/artist/<int:artist_id>/delete/', views.owner_delete_artist, name='owner_delete_artist'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    path('owner/users/', views.owner_users, name='owner_users'),
]