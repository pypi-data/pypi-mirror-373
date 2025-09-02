from __future__ import annotations

from django.apps import AppConfig as BaseAppConfig

class AppConfig(BaseAppConfig):
    name = 'amabase.cmdb'
    label = 'cmdb'
    verbose_name = "CMDB"
    subtitle = "Configuration Management DataBase"
