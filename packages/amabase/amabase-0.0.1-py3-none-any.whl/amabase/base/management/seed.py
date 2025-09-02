import logging
import os

from django.contrib.auth import get_user_model
from django.core.management import call_command

from amabase.conf import settings
from amabase.base.models import UserId

_logger = logging.getLogger(__name__)


def seed():
    seed_known_user_ids()

    if settings.DEBUG:
        seed_debug_superuser()


def seed_debug_superuser():
    User = get_user_model()

    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    if not username:
        if User.objects.filter(is_superuser=True).exists():
            return
        else:
            username = os.environ.get('USER')
            if username:
                os.environ['DJANGO_SUPERUSER_USERNAME'] = username
            else:
                return
    
    if User.objects.filter(username=username).exists():
        return
    
    os.environ.setdefault('DJANGO_SUPERUSER_PASSWORD', "Debug123")
    os.environ.setdefault('DJANGO_SUPERUSER_EMAIL', f"{username}@example.org")

    _logger.info("Create superuser %s", username)
    call_command('createsuperuser', interactive=False)


def seed_known_user_ids():
    User = get_user_model()

    for literal in UserId:
        username = f'({literal.name.lower()})'
        user, created = User.objects.get_or_create(id=literal.value, defaults={'username': username})
        if created:
            _logger.info("Created user with id %s: %s", user.pk, user.username)
        elif user.username != username:
            _logger.error("User with id %s has username '%s' (expected '%d')", user.pk, user.username, username)
