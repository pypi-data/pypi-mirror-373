from __future__ import annotations

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to ensure the AppRegistry is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
})
