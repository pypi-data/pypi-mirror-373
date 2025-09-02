#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Add path to generated proto files
here = os.path.abspath(os.path.dirname(__file__))
path_proto = os.path.abspath(os.path.join(here, 'api_grpc', 'api1', 'proto'))
sys.path.insert(0, path_proto)
                             
# Patch djangogrpcframework if installed
import patch_djangogrpcframework  # @UnusedImport

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_grpc.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
