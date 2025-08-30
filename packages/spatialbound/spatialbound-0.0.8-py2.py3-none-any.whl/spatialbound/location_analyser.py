# spatialbound/location_analyser.py
import logging

logger = logging.getLogger(__name__)

class LocationAnalyser:
    def __init__(self, api_handler):
        self.api_handler = api_handler
        # Import geocode functions to use for address conversion
        from .geocode_functions import GeocodeFunctions
        self.geocode_functions = GeocodeFunctions(api_handler)
    
    def analyse_location(self, location_type, address=None, postcode=None, location=None,
                         transaction_type=None, business_type=None, radius=500):
        """
        Analyses the location based on the provided parameters.
        
        Args:
            location_type (str): The type of the location ("home" or "business").
            address (str, optional): The address of the location.
            postcode (str, optional): The postcode of the location.
            location (dict, optional): The latitude and longitude of the location.
            transaction_type (str, optional): The transaction type (e.g., "buy", "rent").
            business_type (str, optional): The business type for commercial locations.
            radius (int, optional): Radius in meters for analysis (default is 500).
            
        Returns:
            dict: Location analysis details.
        """
        endpoint = "/api/analyse-location"
        
        # Validate location_type
        if location_type not in ["home", "business"]:
            logger.warning(f"Invalid location_type: {location_type}. Must be 'home' or 'business'.")
            return {"error": "Invalid location_type. Must be 'home' or 'business'."}
        
        # If address is provided and no coordinates, convert address to coordinates first
        if address is not None and not location and not postcode:
            try:
                # Use the geocode functions to convert address to coordinates
                geocode_result = self.geocode_functions.address_to_latlon(address)
                if "error" not in geocode_result and "lat" in geocode_result and "lng" in geocode_result:
                    location = {"lat": geocode_result["lat"], "lng": geocode_result["lng"]}
                    address = None  # Clear the address to use coordinates instead
                    logger.info(f"Converted address to coordinates: {location}")
                else:
                    logger.warning(f"Failed to geocode address: {geocode_result}")
            except Exception as e:
                logger.warning(f"Geocoding failed, will let API handle it: {e}")
        
        # Start building the request payload
        location_data = {
            "locationType": location_type,
            "radius": radius
        }
        
        # Add optional parameters only if they are not None
        if transaction_type is not None:
            location_data["transactionType"] = transaction_type
        
        if business_type is not None:
            location_data["businessType"] = business_type
        
        if address is not None:
            location_data["address"] = address
        
        if postcode is not None:
            location_data["postcode"] = postcode
        
        # Handle location coordinates
        if location is not None:
            # Format location coordinates correctly
            if isinstance(location, dict) and 'lat' in location and 'lng' in location:
                location_data["location"] = {
                    "lat": float(location['lat']),
                    "lng": float(location['lng'])
                }
            elif isinstance(location, (list, tuple)) and len(location) >= 2:
                location_data["location"] = {
                    "lat": float(location[0]),
                    "lng": float(location[1])
                }
            else:
                logger.warning(f"Invalid location format: {location}")
                return {"error": "Location must be a dict with 'lat' and 'lng' keys or a (lat, lng) tuple"}
        
        # Require at least one location method
        if "address" not in location_data and "postcode" not in location_data and "location" not in location_data:
            logger.error("No address, postcode, or location provided.")
            return {"error": "Address, postcode, or location coordinates must be provided"}
        
        # Log the request details for debugging
        logger.info(f"Sending location analysis request: locationType={location_type}, radius={radius}m")
        
        try:
            # Make the API request
            response = self.api_handler.make_authorised_request(endpoint, method='POST', json=location_data)
            
            # Log the result summary
            if isinstance(response, dict):
                if "error" in response:
                    logger.error(f"API returned error: {response['error']}")
                else:
                    logger.info(f"Location analysis successful for {location_type} location")
            
            return response
        except Exception as e:
            logger.error(f"Error analyzing location: {str(e)}")
            return {"error": f"Error analyzing location: {str(e)}"}