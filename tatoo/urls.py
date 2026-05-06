from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tedapp.urls')),
] + static(settings.STATIC_URL, document_root=os.path.join(BASE_DIR, 'static')) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'TED Admin'
admin.site.site_title = 'TED Management'
admin.site.index_title = 'Kelola Aplikasi TED'