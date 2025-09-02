from django.apps import AppConfig as BaseAppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate


class AppConfig(BaseAppConfig):
    name = 'amabase.base'
    label = 'base'
    verbose_name = "Base"

    def ready(self):
        post_migrate.connect(on_post_migrate, sender=self)
        
def on_post_migrate(*args, **kwargs):
    call_command('seed')
