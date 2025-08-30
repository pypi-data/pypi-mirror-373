from spatialbound.api_handler import APIHandler
from spatialbound.route_calculator import RouteCalculator
from spatialbound.location_analyser import LocationAnalyser
from spatialbound.video_analyser import VideoAnalyser
from spatialbound.geocode_functions import GeocodeFunctions
from spatialbound.poi_handler import POIHandler
from spatialbound.chat_handler import ChatHandler
from spatialbound.map_generator import MapGenerator
from spatialbound.weather_handler import WeatherHandler
from spatialbound.live_events_handler import LiveEventsHandler
from spatialbound.status import Status
from spatialbound.version import __version__
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Spatialbound:
    """
    Spatialbound class that serves as an API client to access various functionalities such as route calculation,
    location analysis, video analysis, geocoding functions, POI retrieval, LLM chat, map generation,
    and weather data.

    Attributes:
        api_handler (APIHandler): The API handler for making authorised requests.
        login_response (dict): The response received after logging in with the API key.
        route_calculator (RouteCalculator): An instance of the RouteCalculator class.
        location_analyser (LocationAnalyser): An instance of the LocationAnalyser class.
        video_analyser (VideoAnalyser): An instance of the VideoAnalyser class.
        geocode_functions (GeocodeFunctions): An instance of the GeocodeFunctions class.
        poi_handler (POIHandler): An instance of the POIHandler class.
        chat_handler (ChatHandler): An instance of the ChatHandler class.
        map_generator (MapGenerator): An instance of the MapGenerator class.
        weather_handler (WeatherHandler): An instance of the WeatherHandler class.
    """
    # Add version as a class attribute
    __version__ = __version__
    
    def __init__(self, api_key):
        """
        Initializes the Spatialbound class with the provided API key and sets up the necessary instances.
        
        Args:
            api_key (str): The API key to authenticate requests.
        """
        # Validate API key
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("Invalid API key. Please provide a valid SpatialBound API key.")
        
        self.api_handler = APIHandler(api_key)
        self.login_response = self.api_handler.login_response
        
        # Add version to login response
        if isinstance(self.login_response, dict):
            self.login_response["client_version"] = self.__class__.__version__
        
        # Initialize status monitoring system
        self.status = Status(api_key, enabled=True)
        
        # Track successful login and update account info
        if self.login_response and "access_token" in self.login_response:
            # Extract account information from login response
            account_info = {
                "user_email": self.login_response.get("user_email"),
                "user_type": self.login_response.get("user_type"),
                "subscription_type": self.login_response.get("subscription_type")
            }
            # Update status monitoring with account information
            self.status.update_account_info(account_info)
            self.status.track_feature_usage("login", success=True)
        else:
            self.status.track_feature_usage("login", success=False)
            
        self.route_calculator = RouteCalculator(self.api_handler)
        self.location_analyser = LocationAnalyser(self.api_handler)
        self.video_analyser = VideoAnalyser(self.api_handler)
        self.geocode_functions = GeocodeFunctions(self.api_handler)
        self.poi_handler = POIHandler(self.api_handler)
        self.chat_handler = ChatHandler(self.api_handler)
        self.map_generator = MapGenerator(self.api_handler)
        self.weather_handler = WeatherHandler(self.api_handler)
        self.live_events_handler = LiveEventsHandler(self.api_handler, self)
        
        # Try to get server version
        self.server_version = self._get_server_version()

    def _get_server_version(self):
        """
        Get the version of the server API
        
        Returns:
            str: The server version or None
        """
        try:
            response = self.api_handler.make_authorised_request("/api/version", method='GET')
            
            if response and isinstance(response, dict) and 'version' in response:
                server_version = response['version']
                logger.info(f"Server API version: {server_version}")
                
                # Add to login response
                if isinstance(self.login_response, dict):
                    self.login_response["server_version"] = server_version
                    
                return server_version
            return None
        except Exception as e:
            logger.warning(f"Failed to get server version: {e}")
            return None

    def get_version(self):
        """
        Get version information for the client and server.
        
        Returns:
            dict: Dictionary containing version information
        """
        version_info = {
            "client_version": self.__class__.__version__,
        }
        
        if hasattr(self, 'server_version') and self.server_version:
            version_info["server_version"] = self.server_version
            
        return version_info

    def get_weather(self, lat, lon):
        """
        Get current weather and air quality data for a specific location.
        
        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            
        Returns:
            dict: Weather and air quality data for the specified location
        """
        try:
            result = self.weather_handler.get_weather(lat, lon)
            
            # Track status
            success = "error" not in result
            metadata = {"lat": lat, "lon": lon}
            
            self.status.track_location_usage(lat, lon, "weather", success, metadata)
            self.status.track_feature_usage("weather", success, metadata)
            return result
            
        except Exception as e:
            self.status.track_feature_usage("weather", False, {"error": str(e)})
            raise
    
    def get_air_quality(self, lat, lon):
        """
        Get current air quality data for a specific location.
        
        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            
        Returns:
            dict: Air quality data for the specified location
        """
        try:
            result = self.weather_handler.get_air_quality(lat, lon)
            
            # Track status
            success = "error" not in result
            metadata = {"lat": lat, "lon": lon}
            
            self.status.track_location_usage(lat, lon, "air_quality", success, metadata)
            self.status.track_feature_usage("air_quality", success, metadata)
            return result
            
        except Exception as e:
            self.status.track_feature_usage("air_quality", False, {"error": str(e)})
            raise

    def live_events(self, category: str = "all", timeframe: str = "1h") -> Dict[str, Any]:
        """
        Get live events and real-time disaster data from the GlobalEvents system.
        
        Args:
            category (str): Event category filter. Options: "all", "natural_disaster", 
                          "human_conflict", "health_emergency", "infrastructure_failure", 
                          "environmental_crisis", "security_threat", "other_critical"
            timeframe (str): Time range to look back. Options: "1h", "2h", "6h", "12h", 
                           "24h", "48h", "72h" (72h only available for ultra/enterprise accounts)
        
        Returns:
            Dict[str, Any]: Live events data with metadata and account limits information.
            
        Raises:
            ValueError: If invalid category or timeframe is provided.
            Exception: If API request fails or quota is exceeded.
        """
        return self.live_events_handler.live_events(category, timeframe)
    
    def get_live_events_categories(self) -> Dict[str, Any]:
        """
        Get detailed live events categories from the server.
        
        Returns:
            Dict[str, Any]: Categories with detailed information including codes, names, and descriptions.
            
        Raises:
            Exception: If API request fails.
        """
        return self.live_events_handler.get_live_events_categories()
    
    def disable_status_monitoring(self):
        """
        Disable status monitoring for this session.
        WARNING: This will invalidate your authentication token.
        """
        if hasattr(self, 'status'):
            self.status.disable()
            # Clear the token to force re-authentication
            if hasattr(self, 'api_handler'):
                self.api_handler.token = None
            logger.warning("Status monitoring disabled - authentication token invalidated")
    
    def enable_status_monitoring(self):
        """
        Enable status monitoring for this session.
        """
        if hasattr(self, 'status'):
            self.status.enable()
    
    def __del__(self):
        """
        Destructor to ensure status monitoring session is properly ended.
        """
        try:
            if hasattr(self, 'status'):
                self.status.track_session_end()
        except:
            pass  # Ignore errors during cleanup
    
    def get_user_location_info(self) -> Dict[str, Any]:
        """Get current user location information"""
        if hasattr(self, 'status'):
            return self.status.get_user_location_info()
        return {}
    
    def check_access_control(self, feature: str) -> Dict[str, Any]:
        """
        Check if current user has access to a specific feature based on location.
        
        Args:
            feature: Name of the feature to check access for
            
        Returns:
            dict: Access control information including allowed status and reason
        """
        if hasattr(self, 'status'):
            return self.status.check_access_control(feature)
        return {"allowed": True, "restricted": False, "reason": None}
    

    def navigate(self, route_type: str, origin, destinations: list, optimisation_type="shortest_path", mode_of_travel="walk"):
        """
        Calculates the route based on the provided parameters.

        Args:
            route_type (str): The type of the route (e.g., "address", "postcode", or "points").
            origin (str or list): The origin of the route.
            destinations (list): The list of destinations for the route.
            optimisation_type (str, optional): The optimisation type for the route calculation (default is "shortest_path").
            mode_of_travel (str, optional): The mode of travel for the route (default is "walk").

        Returns:
            dict: The calculated route details.
        """
        try:
            result = self.route_calculator.navigate(route_type, origin, destinations, optimisation_type, mode_of_travel)
            
            # Track status
            success = "error" not in result
            metadata = {
                "route_type": route_type,
                "optimisation_type": optimisation_type,
                "mode_of_travel": mode_of_travel,
                "destinations_count": len(destinations) if isinstance(destinations, list) else 1
            }
            
            # Track location usage if coordinates are provided
            if route_type == "points" and isinstance(origin, list) and len(origin) >= 2:
                self.status.track_location_usage(
                    origin[0], origin[1], "route_calculation", success, metadata
                )
            
            self.status.track_feature_usage("route_calculation", success, metadata)
            return result
            
        except Exception as e:
            self.status.track_feature_usage("route_calculation", False, {"error": str(e)})
            raise
    
    def get_optimization_types(self):
        """
        Get available optimization types from the server.
        
        Returns:
            List[Dict]: List of available optimization types with descriptions.
        """
        return self.route_calculator.get_optimization_types()
    
    def get_modes_of_travel(self):
        """
        Get available modes of travel from the server.
        
        Returns:
            List[Dict]: List of available modes of travel with descriptions.
        """
        return self.route_calculator.get_modes_of_travel()

    def analyse_location(self, location_type, address=None, postcode=None, location=None, transaction_type=None, business_type=None, radius=300):
  
        """
        Analyses the location based on the provided parameters.

        Args:
            location_type (str): The type of the location (e.g., "residential", "commercial").
            address (str, optional): The address of the location.
            postcode (str, optional): The postcode of the location.
            location (dict, optional): The latitude and longitude of the location as a dict with 'lat' and 'lng' keys.
            transaction_type (str, optional): The transaction type (e.g., "buy", "rent").
            business_type (str, optional): The business type for commercial locations.
            radius (int, optional): Radius in meters for analysis (default is 500).

        Returns:
            dict: The location analysis details.
        """
        
        try:
            result = self.location_analyser.analyse_location(
                location_type, address, postcode, location, transaction_type, business_type, radius
            )
            
            # Track status
            success = "error" not in result
            metadata = {
                "location_type": location_type,
                "transaction_type": transaction_type,
                "business_type": business_type,
                "radius": radius,
                "has_address": address is not None,
                "has_postcode": postcode is not None,
                "has_location": location is not None
            }
            
            # Track location usage if coordinates are provided
            if location and isinstance(location, dict) and 'lat' in location and 'lng' in location:
                self.status.track_location_usage(
                    location['lat'], location['lng'], "location_analysis", success, metadata)
            
            self.status.track_feature_usage("location_analysis", success, metadata)
            return result
            
        except Exception as e:
            self.status.track_feature_usage("location_analysis", False, {"error": str(e)})
            raise     

    def upload_video(self, file_path):
        """
        Upload a video file for analysis.

        Args:
            file_path (str): Path to the video file on the local system.

        Returns:
            dict: Response containing the uploaded video URL.
        """
        return self.video_analyser.upload_video(file_path)

    def analyse_video(self, video_url, user_prompt, fps):
        """
        Analyses the video based on the provided parameters.

        Args:
            video_url (str): The URL of the previously uploaded video to be analysed.
            user_prompt (str): The prompt for AI analysis.
            fps (int): The frames per second for video processing.

        Returns:
            dict: The video analysis details.
        """
        return self.video_analyser.analyse_video(video_url, user_prompt, fps)

    def search_video(self, query, video_url, limit=10, search_mode="semantic"):
        """
        Search for specific content within a video based on natural language queries.
        
        Args:
            query (str): Search query to find video moments.
            video_url (str): URL of the video to search.
            limit (int, optional): Maximum number of results to return (default 10).
            search_mode (str, optional): Search mode, "semantic" or "exact" (default "semantic").
            
        Returns:
            dict: Search results matching the query.
        """
        return self.video_analyser.search_video(query, video_url, limit, search_mode)

    def find_similarities(self, video_url, timestamp, limit=10, threshold=0.7):
        """
        Find moments in videos that are similar to a specific timestamp in a source video.
        
        Args:
            video_url (str): URL of the video to compare against database.
            timestamp (float): Timestamp in seconds to find similar moments.
            limit (int, optional): Maximum number of results to return (default 10).
            threshold (float, optional): Similarity threshold from 0.0 to 1.0 (default 0.7).
            
        Returns:
            dict: Similar moments found across videos.
        """
        return self.video_analyser.find_similarities(video_url, timestamp, limit, threshold)
    
    def find_image_in_video(self, image_path, video_url, threshold=0.7):
        """
        Find an uploaded image within frames of a video.
        
        Args:
            image_path (str): Path to the image file on the local system.
            video_url (str): URL of the video to search within.
            threshold (float, optional): Minimum similarity threshold (default 0.7).
            
        Returns:
            dict: Found timestamps and frames with similarity scores.
        """
        return self.video_analyser.find_image_in_video(image_path, video_url, threshold)
    
    def analyze_video_location(self, video_url, fps=2):
        """
        Analyze a video to determine its geographical location.
        
        Args:
            video_url (str): URL of the video to analyze.
            fps (int, optional): Frames per second to extract (default 2).
            
        Returns:
            dict: Geolocation analysis results.
        """
        return self.video_analyser.analyze_video_location(video_url, fps)

    def create_map(self, map_id, layers, grid_or_vector="grid", boundary_type="bbox", boundary_details=None, 
                  grid_type="h3", resolution="auto", operation="visualisation", layer_group=None):
        """
        Creates a map based on the provided parameters.

        Args:
            map_id (str): Unique identifier for the map.
            layers (list): List of layer names to include in the map.
            grid_or_vector (str, optional): Type of map, either "grid" or "vector" (default is "grid").
            boundary_type (str, optional): Type of boundary (address, postcode, latlon, bbox, etc.) (default is "bbox").
            boundary_details (str, optional): Details of the boundary in format appropriate for boundary_type.
            grid_type (str, optional): Type of grid, if grid_or_vector is "grid" (default is "h3").
            resolution (str or int, optional): Resolution of the grid (default is "auto").
            operation (str, optional): Operation to perform (default is "visualisation").
            layer_group (str, optional): Name of a predefined layer group, if using vector map.

        Returns:
            dict: The created map data.
        """
        return self.map_generator.create_map(
            map_id, layers, grid_or_vector, boundary_type, boundary_details,
            grid_type, resolution, operation, layer_group
        )

    def get_vector_layer_names(self):
        """
        Retrieves all available vector layer names.

        Returns:
            dict: Available vector layer names.
        """
        return self.map_generator.get_vector_layer_names()

    def get_grid_layer_names(self):
        """
        Retrieves all available grid layer names.

        Returns:
            dict: Available grid layer names.
        """
        return self.map_generator.get_grid_layer_names()

    def get_vector_layer_groups(self):
        """
        Retrieves all available vector layer groups.

        Returns:
            dict: Available vector layer groups.
        """
        return self.map_generator.get_vector_layer_groups()

    def generate_map_id(self):
        """
        Generates a unique map ID.

        Returns:
            dict: Object containing the generated map ID.
        """
        return self.map_generator.generate_map_id()
        
    def fetch_pois_from_polygon(self, coordinates, poi_types=None):
        """
        Fetches Points of Interest (POIs) within a polygon defined by coordinates.

        Args:
            coordinates (list): List of coordinate tuples [(lon, lat), ...] defining a polygon.
            poi_types (list, optional): List of POI types to filter by (e.g., ["restaurant", "school"])

        Returns:
            dict: Dictionary containing POIs found within the polygon.
        """
        return self.poi_handler.fetch_pois_from_polygon(coordinates, poi_types)

    def fetch_pois_from_buffer(self, center_point, radius_meters, poi_types=None):
        """
        Fetches POIs within a circular buffer around a point.

        Args:
            center_point (tuple): Center point (lon, lat) of the buffer.
            radius_meters (float): Radius of the buffer in meters.
            poi_types (list, optional): List of POI types to filter by.

        Returns:
            dict: Dictionary containing POIs found within the polygon.
        """
        return self.poi_handler.fetch_pois_from_buffer(center_point, radius_meters, poi_types)

    def chat(self, query):
        """
        Send a query to the LLM triage chat API.

        Args:
            query (str): The user's query or message.

        Returns:
            dict: The chat response.
        """
        return self.chat_handler.chat(query)

    def address_to_latlon(self, address: str):
        """
        Converts an address to latitude and longitude.

        Args:
            address (str): The address to be converted.

        Returns:
            dict: The latitude and longitude of the address.
        """
        return self.geocode_functions.address_to_latlon(address)

    def postcode_to_latlon(self, postcode: str):
        """
        Converts a postcode to latitude and longitude.

        Args:
            postcode (str): The postcode to be converted.

        Returns:
            dict: The latitude and longitude of the postcode.
        """
        return self.geocode_functions.postcode_to_latlon(postcode)

    def latlon_to_postcode(self, lat: float, lon: float):
        """
        Converts latitude and longitude to a postcode.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            str: The postcode for the given latitude and longitude.
        """
        return self.geocode_functions.latlon_to_postcode(lat, lon)

    def latlon_to_address(self, lat: float, lon: float):
        """
        Converts latitude and longitude to an address.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            str: The address for the given latitude and longitude.
        """
        return self.geocode_functions.latlon_to_address(lat, lon)

    def latlon_to_admin_boundary(self, lat: float, lon: float):
        """
        Converts latitude and longitude to administrative boundaries.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            dict: The administrative boundaries for the given latitude and longitude.
        """
        return self.geocode_functions.latlon_to_admin_boundary(lat, lon)

    def latlon_to_city_country(self, lat: float, lon: float):
        """
        Converts latitude and longitude to city and country.

        Args:
            lat (float): The latitude of the location.
            lon (float): The longitude of the location.

        Returns:
            dict: The city and country for the given latitude and longitude.
        """
        return self.geocode_functions.latlon_to_city_country(lat, lon)