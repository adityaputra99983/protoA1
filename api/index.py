import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'tatoo'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tatoo.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

def handler(event, context):
    from io import BytesIO
    from urllib.parse import parse_qs

    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    headers = event.get('headers', {})
    query_string = event.get('queryStringParameters') or {}

    body = event.get('body', '')
    if body and event.get('isBase64Encoded', False):
        body = BytesIO(body.encode('utf-8'))
    else:
        body = BytesIO(body.encode('utf-8') if body else b'')

    body.seek(0)

    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': '&'.join(f'{k}={v}' for k, v in query_string.items()),
        'CONTENT_TYPE': headers.get('Content-Type', headers.get('content-type', '')),
        'CONTENT_LENGTH': str(len(body.getvalue())),
        'SERVER_NAME': headers.get('Host', 'localhost'),
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': body,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': True,
    }

    for key, value in headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value

    response_status = [200]
    response_headers = []

    def start_response(status, headers, exc_info=None):
        response_status[0] = int(status.split()[0])
        for name, value in headers:
            if name.lower() == 'content-type':
                response_headers.append(('Content-Type', value))
            elif name.lower() == 'location':
                response_headers.append(('Location', value))
            elif name.lower() != 'content-length':
                response_headers.append((name, value))
        return lambda x: x

    response = application(environ, start_response)
    response_body = b''.join(response)

    return {
        'statusCode': response_status[0],
        'headers': dict(response_headers),
        'body': response_body.decode('utf-8')
    }