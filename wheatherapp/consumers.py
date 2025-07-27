import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import UserPreferences, Location, WeatherData

logger = logging.getLogger(__name__)

class WeatherConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        logger.info(f"WebSocket connection attempt - User: {self.user}")
        
        if not self.user.is_authenticated:
            logger.warning("WebSocket connection rejected: User not authenticated")
            await self.close()
            return
            
        # Get user's preferred location
        self.location = await self.get_user_location()
        if not self.location:
            logger.warning(f"WebSocket connection rejected: No location found for user {self.user}")
            await self.close()
            return
            
        # Create a unique group name for this location
        self.room_group_name = f'weather_{self.location.city.lower().replace(" ", "_")}'
        logger.info(f"WebSocket connected - User: {self.user}, Location: {self.location.city}, Group: {self.room_group_name}")
        
        # Join room group
        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"WebSocket accepted for user {self.user}")
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            await self.close()
        
        # Send current weather data immediately upon connection
        current_weather = await self.get_current_weather()
        if current_weather:
            await self.send(text_data=json.dumps({
                'type': 'weather_update',
                'data': current_weather
            }))

    async def disconnect(self, close_code):
        # Leave room group if we have a location
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass  # We don't expect any messages from the client

    # Receive message from room group
    async def weather_update(self, event):
        try:
            logger.info(f"Sending weather update to {self.user}: {event['data']}")
            await self.send(text_data=json.dumps({
                'type': 'weather_update',
                'data': event['data']
            }))
        except Exception as e:
            logger.error(f"Error sending weather update: {str(e)}")
            raise

    @database_sync_to_async
    def get_user_location(self):
        try:
            preferences = UserPreferences.objects.get(user=self.user)
            return preferences.default_location
        except UserPreferences.DoesNotExist:
            return None

    @database_sync_to_async
    def get_current_weather(self):
        try:
            latest_weather = WeatherData.objects.filter(
                location=self.location
            ).latest('timestamp')
            
            return {
                'temperature': latest_weather.temperature,
                'feels_like': latest_weather.feels_like,
                'humidity': latest_weather.humidity,
                'wind_speed': latest_weather.wind_speed,
                'condition': latest_weather.weather_condition,
                'description': latest_weather.weather_description,
                'timestamp': latest_weather.timestamp.isoformat(),
                'location': f"{self.location.city}, {self.location.country}"
            }
        except WeatherData.DoesNotExist:
            return None
