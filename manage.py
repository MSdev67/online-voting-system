#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voteindia.settings")
    
    # SSL modification starts here
    if 'runssl' in sys.argv:
        import ssl
        from django.core.servers.basehttp import WSGIServer
        WSGIServer.socket_type = ssl.SSLSocket
        WSGIServer.server_side = True
        WSGIServer.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        WSGIServer.ssl_context.load_cert_chain('cert.pem', 'key.pem')
        sys.argv.remove('runssl')
        sys.argv.append('runserver')
    # SSL modification ends here
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()