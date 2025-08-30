# spatialbound/weather_handler.py
import logging
import pandas as pd
import requests

logger = logging.getLogger(__name__)

class WeatherHandler:
    """
    Handler for weather and air quality data.
    """
    def __init__(self, api_handler):
        """
        Initialize the weather handler with the API handler.
        
        Args:
            api_handler: The API handler for making authorized requests.
        """
        self.api_handler = api_handler
    
    def get_weather(self, lat, lon):
        """
        Get current weather and air quality data for a specific location.
        
        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            
        Returns:
            dict: Weather and air quality data for the specified location
        """
        # Construct the endpoint with query parameters
        endpoint = f"/api/weather?lat={lat}&lon={lon}"
        
        try:
            # Call the API handler with the existing method parameters it accepts
            response = self.api_handler.make_authorised_request(endpoint, method='GET')
            return response
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            return {'error': str(e)}
    
    def get_air_quality(self, lat, lon):
        """
        Get current air quality data for a specific location.
        
        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            
        Returns:
            dict: Air quality data for the specified location
        """
        # Construct the endpoint with query parameters
        endpoint = f"/api/air_quality?lat={lat}&lon={lon}"
        
        try:
            # Call the API handler with the existing method parameters it accepts
            response = self.api_handler.make_authorised_request(endpoint, method='GET')
            return response
        except Exception as e:
            logger.error(f"Failed to get air quality data: {e}")
            return {'error': str(e)}