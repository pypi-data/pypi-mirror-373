from __future__ import annotations

import argparse
import sys
from argparse import ArgumentParser


class DjangoCommand:
    help = "Run a Django administrative task."
    
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('args', nargs=argparse.REMAINDER)

    def handle(self, args: str|list[str] = []):
        if isinstance(args, str):
            args = [args]

        from amabase.conf import settings
        if not settings._django_configured:
            settings.configure_django()
        
        from django.core.management import execute_from_command_line
        execute_from_command_line([f'{settings.INVOKED_AS} django', *args])


class LsDjangoCommand:
    help = "List available Django administrative tasks."
    
    def handle(self):
        try:
            import django
        except ModuleNotFoundError:
            print("Django is not available.")
            return
        
        django = DjangoCommand()        
        django.handle('help')


class WebCommand:
    help = "Apply pending database migrations and launch the Django website server."
    
    def handle(self):        
        django = DjangoCommand()
        
        django.handle('migrate')

        # Avoid running the 'migrate' command again when reloading
        sys.argv = [sys.argv[0], 'django', 'runserver']
        django.handle('runserver')
