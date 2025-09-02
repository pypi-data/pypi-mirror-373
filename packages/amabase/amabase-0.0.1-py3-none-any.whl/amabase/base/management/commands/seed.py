import logging
from argparse import ArgumentParser
from importlib import import_module

from django.apps import AppConfig, apps
from django.core.management.base import BaseCommand

_logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Ensure initial data are created in the database.

    This command calls the `seed()` function (with optional boolean argument `demo`) located in the `management.seed` submodule, for each application.
    """

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--demo', action='store_true', help="Populate the database with demo data")
    

    def handle(self, **options):
        ordered_apps: list[AppConfig] = []
            
        for app in sorted(apps.get_app_configs(), key=lambda app: app.name):
            if app.name == 'amabase.base':
                ordered_apps.insert(0, app)
            else:
                ordered_apps.append(app)
            
        for app in ordered_apps:
            self.for_app(app)


    def for_app(self, app: AppConfig):
        feature_name = 'seed'

        # Load module
        module_name = f'{app.name}.management.{feature_name}'
        try:
            module = import_module(module_name)
        except ModuleNotFoundError as err:
            if str(err) in [f"No module named '{module_name}'", f"No module named '{app.name}.management'"]:
                return
            raise
            
        # Find function to call
        feature_func = getattr(module, feature_name, None)
        if feature_func is None:
            _logger.error(f"Cannot run management.{feature_name} for app {app.name}: no function named '{feature_name}'")
            return
            
        _logger.debug(f"Seed app {app.name}")
        feature_func()
