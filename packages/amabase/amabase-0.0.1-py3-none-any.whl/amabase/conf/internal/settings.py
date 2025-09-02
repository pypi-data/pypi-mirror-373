from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

from amabase import __prog__
from amabase.conf import default as default_settings_module
from amabase.conf.internal.db import Db
from amabase.conf.exceptions import SettingsNotFound
from amabase.utils import configure_logging, ensure_pip_dependency, get_data_dir, get_random_string, load_dotenv


class Settings:
    APP_NAME: str
    """ Name of the application. """

    DATA_DIR: Path
    """ Directory for all application data (SQLite database, media, collected static files, etc) """

    INVOKED_AS: str
    """ The command-line invokation name. """
    
    DEBUG: bool
    """ Indicate whether Django is run in debug mode. """
    
    YES: bool
    """ Do not ask confirmation when performing sensible actions (e.g. auto install dependencies). """
    
    DOMAIN_NAME: str|None
    """ The primary domain name to use in production. """
    
    APPS: list[str]
    """ List of enabled user applications (in addition to `amabase.base`). """

    USE_GIS: bool
    """ Indicate whether GeoDjango (`django.contrib.gis`) is enabled. """

    USE_DJANGO_CONNECTION_FOR_CONF_DB: bool
    """ Indicate that Django uses the configuration SQLite database for as its default database. """

    FAVICON_URL: str

    SITE_TITLE: str
    """ Above the login form, in each page's <h1> and at the end of each page's <title> """

    SITE_INDEX_HEADER: str
    """ Top of the admin index page """
    
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Settings()
        return cls._instance
    

    def __init__(self):
        if self.__class__._instance is not None:
            raise ValueError(f"Already instanciated: {self.__class__}")
        self.__class__._instance = self

        self._configured = False
        self._django_configured = False

    
    def __getattribute__(self, name: str):
        if name.startswith('_') or name in {'values', 'configure', 'configure_django'}:
            return super().__getattribute__(name)

        try:
            return self._values[name]
        except KeyError:
            raise SettingsNotFound(name) from None


    def __setattr__(self, name: str, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
       
        raise AttributeError(f"Cannot set attributes (tried '{name}')")


    @property
    def values(self) -> dict[str,Any]:
        if not self._configured:
            raise ValueError("Settings not configured yet")
        return self._values
 

    def configure(self, settings_module: ModuleType|str|None = None, *, invoked_as: str|None = None, data_dir: str|os.PathLike|None = None, debug: bool|None = None, yes: bool|None = None, log_level: str|None = None, log_names: bool|None = None):
        if self._configured:
            raise ValueError("Already configured")
        
        load_dotenv()

        if not settings_module:
            settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        os.environ.pop('DJANGO_SETTINGS_MODULE', None)

        if settings_module:
            if isinstance(settings_module, str):
                settings_module = import_module(settings_module)

            parts = settings_module.__name__.split('.')

            if not settings_module.__file__:
                raise ValueError(f"Cannot configure with settings '{settings_module.__name__}': cannot determine base directory because the module has no '__file__' attribute")            
            file = Path(settings_module.__file__).resolve()
            
            if file.name == '__init__.py':
                file = file.parent
            file_depth = len(parts)
            for _ in range(file_depth):
                file = file.parent
                
            app_name = parts[0]
            base_dir = file
        else:
            app_name = __prog__
            base_dir = Path(__file__).resolve().parent.parent.parent.parent

        self._values = {}

        self._values['APP_NAME'] = app_name

        if data_dir is None:
            data_dir = get_data_dir(app_name, base_dir, system=True)
        self._values['DATA_DIR'] = data_dir
        
        self._values['INVOKED_AS'] = invoked_as if invoked_as else __prog__
        
        if debug is None:
            if value := os.environ.get('DEBUG'):
                debug = value.lower() in ('1', 'true', 'yes', 'on')
        self._values['DEBUG'] = debug
        
        if yes is None:
            yes = False
        self._values['YES'] = yes

        self._import_settings_module(default_settings_module, DATA_DIR=data_dir, DEBUG=debug, YES=yes)
        if settings_module:
            self._import_settings_module(settings_module, DATA_DIR=data_dir, DEBUG=debug, YES=yes)

        if self._values['DEBUG'] is None:
            try:
                self.DATA_DIR.relative_to(Path.home())
                debug = True
            except ValueError:
                debug = False
            self._values['DEBUG'] = debug

        configure_logging(self._values.get('LOGGING'), level=log_level, names=log_names)

        db = Db.instance()
        db.configure(path=self.DATA_DIR.joinpath(f'{app_name}.db'))

        if not self._values.get('SECRET_KEY'):
            value = db.get_prop('settings.secret_key')
            if not value:
                value = get_random_string(50)
                db.set_prop('settings.secret_key', value)
            self._values['SECRET_KEY'] = value

        target = []
        if current := self._values.get('ALLOWED_HOSTS'):
            for value in current:
                if value == '__domain_name__':
                    if self.DOMAIN_NAME:
                        target.append(self.DOMAIN_NAME)
                else:
                    target.append(value)
        self._values['ALLOWED_HOSTS'] = target

        if not self._values.get('CSRF_TRUSTED_ORIGINS'):
            self._values['CSRF_TRUSTED_ORIGINS'] = [f"http{'' if host in {'127.0.0.1', 'localhost'} or host.endswith('.localhost') else 's'}://{host}" for host in self._values['ALLOWED_HOSTS']]
        
        if not self._values.get('APPS'):
            self._values['APPS'] = []
        
        if self._values.get('DATABASES') is None:
            self._values['DATABASES'] = {}
        
        if 'default' in self._values['DATABASES']:
            default_database = self._values['DATABASES']['default']

            if self._values.get('USE_GIS') is None:
                self._values['USE_GIS'] = True if '.gis.' in default_database['ENGINE'] else ''
            
            self._values['USE_DJANGO_CONNECTION_FOR_CONF_DB'] = Path(default_database['NAME']).resolve().as_posix() == db.path.resolve().as_posix()

        else:
            if (use_gis := self._values.get('USE_GIS')) is None:
                use_gis = True if db.spatialite_version is not None else False
                self._values['USE_GIS'] = use_gis
            
            default_database = {
                'ENGINE': 'django.contrib.gis.db.backends.spatialite' if use_gis else 'django.db.backends.sqlite3',
                'NAME': str(db.path),
            }
            self._values['DATABASES']['default'] = default_database
            self._values['USE_DJANGO_CONNECTION_FOR_CONF_DB'] = True

        if current := self._values.get('INSTALLED_APPS'):
            target = []
            for value in current:
                if value == '__gis__':
                    if self.USE_GIS:
                        target.append('django.contrib.gis')
                elif value == '__apps__':
                    for app in self.APPS:
                        target.append(app)
                else:
                    target.append(value)
            self._values['INSTALLED_APPS'] = target

        if not (value := self._values.get('SITE_TITLE')):
            self._values['SITE_TITLE'] = app_name.capitalize()

        self._configured = True


    def configure_django(self):
        if self._django_configured:
            raise ValueError("Django already configured")
        
        dependencies = {
            'django': None,
            'channels': None,
            'daphne': None,
            'debug_toolbar': 'django-debug-toolbar',
            'import_export': 'django-import-export',
            'django_filters': 'django-filter',
        }

        db_engine = self.values['DATABASES']['default']['ENGINE']
        if 'postgres' in db_engine or 'postgis' in db_engine:
            dependencies['psycopg'] = 'psycopg[binary]'
        
        ensure_pip_dependency(dependencies, yes=self.YES)
        
        from django.conf import settings as django_settings
        django_settings.configure(**self._values)
        
        for attr in sorted(dir(django_settings)):
            if attr[1].isupper():
                self._values[attr] = getattr(django_settings, attr)

        if self.USE_DJANGO_CONNECTION_FOR_CONF_DB:
            db = Db.instance()
            db.close()
            db.configure(path=self.DATA_DIR.joinpath(f'{self.APP_NAME}.db'), reconfigure=True)

        self._django_configured = True


    def _import_settings_module(self, module: ModuleType|str, **overrides):
        if not isinstance(module, ModuleType):
            module = import_module(module)
        
        for attr in dir(module):
            if not attr[1].isupper():
                continue

            if attr in overrides and overrides[attr] is not None:
                continue

            value = getattr(module, attr)
            if isinstance(value, str) and '{' in value:
                value = value.format(DATA_DIR=self._values['DATA_DIR'])
            self._values[attr] = value
