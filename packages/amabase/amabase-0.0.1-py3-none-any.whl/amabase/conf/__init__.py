from amabase.conf.internal.db import Db
from amabase.conf.internal.settings import Settings
from amabase.conf.exceptions import SettingsNotFound
from amabase.conf.main import main

settings = Settings.instance()

db = Db.instance()

__all__= ('SettingsNotFound', 'settings', 'db', 'main')
