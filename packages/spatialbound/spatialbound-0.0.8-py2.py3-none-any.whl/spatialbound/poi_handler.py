# spatialbound/poi_handler.py
import math
from shapely.geometry import Polygon, Point

class POIHandler:
    """
    Handler for Points of Interest (POI) related operations.
    """
    def __init__(self, api_handler):
        """
        Initialize the POI handler with the API handler.
        
        Args:
            api_handler: The API handler for making authorized requests.
        """
        self.api_handler = api_handler
    
    def fetch_pois_from_polygon(self, coordinates, poi_types=None):
        """
        Fetch POIs within a polygon defined by coordinates.
        
        Args:
            coordinates (list): List of coordinate tuples [(lon, lat), ...] defining a polygon.
            poi_types (list, optional): List of POI types to filter by.
            
        Returns:
            dict: Dictionary containing POIs found within the polygon.
        """
        endpoint = "/api/fetch_pois"
        
        # Ensure coordinates are in the right format (list of lists of tuples)
        formatted_coordinates = [[(float(lon), float(lat)) for lon, lat in coordinates]]
        
        payload = {
            "type": "Polygon",
            "coordinates": formatted_coordinates,
            "poi_types": poi_types if poi_types else None
        }
        
        try:
            response = self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
            
            # If poi_types is provided, filter the results
            if poi_types and 'pois' in response:
                filtered_pois = []
                for poi in response['pois']:
                    poi_type = poi.get('type', '').lower()
                    if any(pt.lower() in poi_type for pt in poi_types):
                        filtered_pois.append(poi)
                response['pois'] = filtered_pois
                
            return response
        except Exception as e:
            return {'error': f"Failed to fetch POIs: {str(e)}"}
    
    def fetch_pois_from_buffer(self, center_point, radius_meters, poi_types=None):
        """
        Fetch POIs within a circular buffer around a point.
        
        Args:
            center_point (tuple): Center point (lon, lat) of the buffer.
            radius_meters (float): Radius of the buffer in meters.
            poi_types (list, optional): List of POI types to filter by.
            
        Returns:
            dict: Dictionary containing POIs found within the buffer.
        """
        # Create a circular polygon approximation
        lon, lat = center_point
        
        # Convert radius from meters to approximate degrees
        # 1 degree latitude is approximately 111,000 meters
        radius_degrees = radius_meters / 111000
        
        # Generate points for a circular polygon (32 points)
        coordinates = []
        for i in range(33):  # 32 points + closing point
            angle = 2 * math.pi * i / 32
            x = lon + radius_degrees * math.cos(angle)
            y = lat + radius_degrees * math.sin(angle)
            coordinates.append((x, y))
        
        # Use the polygon method
        return self.fetch_pois_from_polygon(coordinates, poi_types)