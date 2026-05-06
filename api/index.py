import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tatoo.settings')

# Import Django
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
from django.db import connection

# Initialize WSGI application
application = get_wsgi_application()

def run_setup():
    """Ensure database is ready and has sample data."""
    try:
        # Check if DB file exists in /tmp
        db_path = '/tmp/db.sqlite3'
        from django.conf import settings
        
        # If the main table doesn't exist, we need to migrate
        tables = connection.introspection.table_names()
        if 'tedapp_artist' not in tables:
            print(f"System: Tables not found in {db_path}. Running migrations...")
            call_command('migrate', interactive=False)
            
            # Load sample data
            try:
                print("System: Loading sample data...")
                call_command('add_sample_data', interactive=False)
            except Exception as e:
                print(f"System: Error loading data: {e}")
        else:
            print("System: Database already setup.")
    except Exception as e:
        print(f"System: Setup failed: {e}")

# Run setup during cold start
run_setup()

# Define the app entry point
app = application
handler = application