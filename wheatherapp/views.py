from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Location, WeatherData
import random

# Simple in-memory weather data storage (for demo purposes)
weather_conditions = [
    'Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy', 
    'Thunderstorm', 'Snowy', 'Windy', 'Foggy'
]

def generate_weather_data(location):
    """Generate random weather data for a location"""
    return {
        'temperature': round(random.uniform(10, 35), 1),  # Temperature in Celsius
        'condition': random.choice(weather_conditions),
        'humidity': random.randint(30, 90),  # Humidity percentage
        'wind_speed': round(random.uniform(0.5, 15), 1),  # Wind speed in km/h
        'timestamp': timezone.now().isoformat(),
    }

def home(request):
    """Home page view that requires authentication"""
    if not request.user.is_authenticated:
        return redirect('weather:login')
    
    # Get user's saved locations or recent weather data
    recent_weather = WeatherData.objects.filter(location__isnull=False).order_by('-timestamp')[:5]
    
    return render(request, 'weather/home.html', {
        'recent_weather': recent_weather,
        'user': request.user
    })

def user_login(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('weather:home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('weather:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

def user_signup(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('weather:home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('weather:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@require_http_methods(["GET", "POST"])
def user_logout(request):
    """Handle user logout"""
    logout(request)
    return redirect('weather:login')  # Using namespaced URL

@login_required
@csrf_exempt
@require_http_methods(["GET"])
def weather_api(request):
    """
    Simple weather API endpoint
    
    GET Parameters:
    - city: City name (required)
    - country: Country code (optional)
    """
    city = request.GET.get('city')
    country = request.GET.get('country', '')
    
    if not city:
        return JsonResponse(
            {'error': 'City parameter is required'}, 
            status=400
        )
    
    try:
        # Try to get the location or create it if it doesn't exist
        location, created = Location.objects.get_or_create(
            city=city.capitalize(),
            country=country.upper() if country else '',
            defaults={
                'latitude': round(random.uniform(-90, 90), 6),
                'longitude': round(random.uniform(-180, 180), 6)
            }
        )
        
        # Generate weather data
        weather_data = generate_weather_data(location)
        
        # Save to database
        WeatherData.objects.create(
            location=location,
            temperature=weather_data['temperature'],
            weather_condition=weather_data['condition'],
            humidity=weather_data['humidity'],
            wind_speed=weather_data['wind_speed']
        )
        
        # Prepare response
        response_data = {
            'location': {
                'city': location.city,
                'country': location.country,
                'coordinates': {
                    'lat': float(location.latitude),
                    'lon': float(location.longitude)
                }
            },
            'weather': weather_data,
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse(
            {'error': f'An error occurred: {str(e)}'}, 
            status=500
        )
