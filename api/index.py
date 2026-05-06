import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tatoo.settings')

# Export WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    app = application
    
    # Optimize startup: Only migrate if specific tables are missing
    try:
        from django.db import connection
        from django.core.management import call_command
        
        tables = connection.introspection.table_names()
        if 'tedapp_artist' not in tables:
            print("DB tables missing. Running migrations...")
            call_command('migrate', interactive=False)
            
            # Load sample data ONLY if migration was needed
            try:
                print("Loading sample data...")
                call_command('add_sample_data', interactive=False)
            except Exception as e:
                print(f"Sample data error (can be ignored): {e}")
    except Exception as db_error:
        print(f"DB Startup Check error: {db_error}")

except Exception as e:
    print(f"Error loading Django: {e}")
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [f"Django startup error: {e}".encode('utf-8')]