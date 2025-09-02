import os, sys, django
from django.core.management import execute_from_command_line

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_checker.settings')
    django.setup()
    if len(sys.argv) == 1:
        sys.argv.extend(['runserver', '127.0.0.1:8080'])
    execute_from_command_line(sys.argv)