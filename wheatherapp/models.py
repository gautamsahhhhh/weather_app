from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Location(models.Model):
    """
    Model to store location information
    """
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('city', 'country')
        ordering = ['city']

    def __str__(self):
        return f"{self.city}, {self.country}"


class WeatherData(models.Model):
    """
    Model to store weather data for locations
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_data')
    timestamp = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField(help_text="Temperature in Celsius")
    feels_like = models.FloatField(
        help_text="Feels like temperature in Celsius",
        null=True,
        blank=True,
        default=None
    )
    humidity = models.IntegerField(
        help_text="Humidity percentage",
        null=True,
        blank=True
    )
    pressure = models.IntegerField(
        help_text="Atmospheric pressure in hPa",
        null=True,
        blank=True
    )
    wind_speed = models.FloatField(
        help_text="Wind speed in meter/sec",
        null=True,
        blank=True
    )
    wind_degree = models.IntegerField(
        help_text="Wind direction in degrees",
        null=True,
        blank=True
    )
    weather_condition = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    weather_description = models.TextField(
        null=True,
        blank=True
    )
    visibility = models.IntegerField(
        help_text="Visibility in meters",
        null=True,
        blank=True
    )
    cloudiness = models.IntegerField(
        help_text="Cloudiness percentage",
        null=True,
        blank=True
    )
    sunrise = models.DateTimeField(
        null=True,
        blank=True
    )
    sunset = models.DateTimeField(
        null=True,
        blank=True
    )
    timezone_offset = models.IntegerField(
        help_text="Shift in seconds from UTC",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Weather Data'
        get_latest_by = 'timestamp'

    def __str__(self):
        return f"{self.location} - {self.temperature}°C - {self.weather_condition}"


class UserPreferences(models.Model):
    """
    Model to store user preferences for the weather app
    """
    TEMPERATURE_UNITS = [
        ('C', 'Celsius'),
        ('F', 'Fahrenheit'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='weather_preferences')
    default_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    temperature_unit = models.CharField(max_length=1, choices=TEMPERATURE_UNITS, default='C')
    show_humidity = models.BooleanField(default=True)
    show_wind = models.BooleanField(default=True)
    show_pressure = models.BooleanField(default=False)
    refresh_interval = models.PositiveIntegerField(
        default=30,
        help_text="Auto-refresh interval in minutes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
