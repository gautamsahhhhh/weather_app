import json
import random
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from wheatherapp.models import Location, WeatherData

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Simulate weather updates and send them via WebSocket'

    def handle(self, *args, **options):
        channel_layer = get_channel_layer()
        
        # Get all active locations
        locations = Location.objects.filter(is_active=True)
        
        if not locations.exists():
            self.stdout.write(self.style.WARNING('No active locations found. Please add some locations first.'))
            return
            
        self.stdout.write(self.style.SUCCESS(f'Starting weather simulation for {locations.count()} locations...'))
        
        try:
            while True:
                for location in locations:
                    # Generate random weather data
                    weather_data = {
                        'temperature': round(random.uniform(10, 35), 1),
                        'feels_like': round(random.uniform(5, 40), 1),
                        'humidity': random.randint(30, 90),
                        'wind_speed': round(random.uniform(0.5, 15), 1),
                        'wind_degree': random.randint(0, 359),
                        'weather_condition': random.choice([
                            'Clear', 'Clouds', 'Rain', 'Thunderstorm', 
                            'Drizzle', 'Snow', 'Mist', 'Fog'
                        ]),
                        'weather_description': 'Simulated weather data',
                        'visibility': random.randint(1000, 10000),
                        'cloudiness': random.randint(0, 100),
                        'sunrise': datetime.now().replace(hour=6, minute=0, second=0, microsecond=0),
                        'sunset': datetime.now().replace(hour=18, minute=0, second=0, microsecond=0),
                        'timezone_offset': 20700  # Nepal time (UTC+5:45)
                    }
                    
                    # Save to database
                    weather = WeatherData.objects.create(
                        location=location,
                        **weather_data
                    )
                    
                    # Prepare data for WebSocket
                    ws_data = {
                        'temperature': weather.temperature,
                        'feels_like': weather.feels_like,
                        'humidity': weather.humidity,
                        'wind_speed': weather.wind_speed,
                        'condition': weather.weather_condition,
                        'description': weather.weather_description,
                        'timestamp': weather.timestamp.isoformat(),
                        'location': f"{location.city}, {location.country}"
                    }
                    
                    # Send to WebSocket group
                    group_name = f'weather_{location.city.lower().replace(" ", "_")}'
                    try:
                        logger.info(f"Sending to group {group_name}: {ws_data}")
                        async_to_sync(channel_layer.group_send)(
                            group_name,
                            {
                                'type': 'weather_update',
                                'data': ws_data
                            }
                        )
                        self.stdout.write(self.style.SUCCESS(f'Sent update for {location.city} to group {group_name}'))
                    except Exception as e:
                        logger.error(f"Error sending to group {group_name}: {str(e)}")
                        self.stdout.write(self.style.ERROR(f'Error sending update for {location.city}: {str(e)}'))
                    
                # Wait for 30 seconds before next update
                import time
                time.sleep(30)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\nStopping weather simulation...'))
