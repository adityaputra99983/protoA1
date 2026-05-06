"""
WSGI config for tatoo project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tatoo.settings')

if os.environ.get('VERCEL') == '1':
    os.environ['DEBUG'] = 'False'
    os.environ['ALLOWED_HOSTS'] = '*'

application = get_wsgi_application()
