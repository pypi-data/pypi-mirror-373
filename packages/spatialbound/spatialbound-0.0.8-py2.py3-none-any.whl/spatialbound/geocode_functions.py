# spatialbound/geocode_functions.py
import logging

logger = logging.getLogger(__name__)

class GeocodeFunctions:
    def __init__(self, api_handler):
        self.api_handler = api_handler
    
    def address_to_latlon(self, address: str):
        """
        Convert an address to latitude and longitude.
        
        Args:
            address (str): The address to convert.
            
        Returns:
            dict: Dictionary containing the latitude and longitude.
        """
        endpoint = "/api/address_to_latlon"  
        payload = {"address": address}
        
        try:
            response = self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
            return response
        except Exception as e:
            logger.error(f"Error converting address to coordinates: {e}")
            return {"error": str(e)}
    
    
    def latlon_to_address(self, lat: float, lon: float):
        """
        Convert latitude and longitude to an address.
        
        Args:
            lat (float): The latitude.
            lon (float): The longitude.
            
        Returns:
            dict: Dictionary containing the address.
        """
        endpoint = "/api/latlon_to_address"  
        payload = {"lat": lat, "lon": lon}
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
        except Exception as e:
            logger.error(f"Error converting coordinates to address: {e}")
            return {"error": str(e)}
    
    def latlon_to_admin_boundary(self, lat: float, lon: float):
        """
        Convert latitude and longitude to administrative boundaries.
        
        Args:
            lat (float): The latitude.
            lon (float): The longitude.
            
        Returns:
            dict: Dictionary containing administrative boundary information.
        """
        endpoint = "/api/latlon_to_admin_boundary"  
        payload = {"lat": lat, "lon": lon}
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
        except Exception as e:
            logger.error(f"Error converting coordinates to admin boundary: {e}")
            return {"error": str(e)}
    
    def latlon_to_city_country(self, lat: float, lon: float):
        """
        Convert latitude and longitude to city and country.
        
        Args:
            lat (float): The latitude.
            lon (float): The longitude.
            
        Returns:
            dict: Dictionary containing city and country information.
        """
        endpoint = "/api/latlon_to_city_country"  
        payload = {"lat": lat, "lon": lon}
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
        except Exception as e:
            logger.error(f"Error converting coordinates to city/country: {e}")
            return {"error": str(e)}