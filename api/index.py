import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tatoo.settings')

# Direct import and assignment at top level for Vercel
from django.core.wsgi import get_wsgi_application

# Initialize application
try:
    application = get_wsgi_application()
    
    # Run migrations once on start
    from django.db import connection
    from django.core.management import call_command
    tables = connection.introspection.table_names()
    if 'tedapp_artist' not in tables:
        call_command('migrate', interactive=False)
        try:
            call_command('add_sample_data', interactive=False)
        except:
            pass
except Exception as e:
    print(f"Django startup error: {e}")
    # Define a fallback if Django fails to load
    def application(environ, start_response):
        start_response('500 Internal Server Error', [('Content-type', 'text/plain')])
        return [f"Error: {e}".encode('utf-8')]

# Vercel looks for 'app' or 'application' or 'handler'
app = application
handler = application