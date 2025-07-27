"""
ASGI config for wheather project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wheather.settings')

# This application object is used by any ASGI server to start the application.
django_application = get_asgi_application()

# Import channels routing after Django setup to avoid AppRegistryNotReady exception
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import wheatherapp.routing

# Initialize Django before importing models that depend on the ORM
django.setup()

application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            wheatherapp.routing.websocket_urlpatterns
        )
    ),
})
