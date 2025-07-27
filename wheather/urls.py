"""
URL configuration for wheather project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import wheatherapp.routing

# HTTP URL patterns
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Authentication URLs (if using Django's built-in auth)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Weather app URLs
    path('', include('wheatherapp.urls')),
]

# WebSocket URL patterns - directly include the WebSocket patterns
websocket_urlpatterns = wheatherapp.routing.websocket_urlpatterns

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This is needed for Django Channels
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
