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
        # Get list of tables
        tables = connection.introspection.table_names()
        
        # If the main table doesn't exist, we need to migrate
        if 'tedapp_artist' not in tables:
            print("System: Tables not found. Running migrations...")
            call_command('migrate', interactive=False)
            
            # Load sample data if migration was performed
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