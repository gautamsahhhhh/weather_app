from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'weather'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    
    # API endpoint for weather data
    path('api/weather/', views.weather_api, name='weather_api'),
]
