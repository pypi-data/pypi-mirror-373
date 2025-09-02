from django.apps import AppConfig as BaseAppConfig

class AppConfig(BaseAppConfig):
    name = 'amabase.ipam'
    label = 'ipam'
    verbose_name = "IPAM"
    subtitle = "IP Address Management"
