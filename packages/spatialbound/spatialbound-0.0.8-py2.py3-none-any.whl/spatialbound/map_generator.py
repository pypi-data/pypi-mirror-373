# spatialbound/map_generator.py
import logging
import json

logger = logging.getLogger(__name__)

class MapGenerator:
    """
    Handler for map generation operations.
    """
    def __init__(self, api_handler):
        """
        Initialize the map generator with the API handler.
        
        Args:
            api_handler: The API handler for making authorized requests.
        """
        self.api_handler = api_handler
    
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
        endpoint = "/api/create_map"
        
        # Validate required inputs
        if not map_id:
            return {"error": "Map ID is required"}
        
        if not layers or not isinstance(layers, list):
            return {"error": "Layers must be provided as a list"}
        
        if not boundary_details:
            return {"error": "Boundary details are required"}
        
        # Prepare request payload
        payload = {
            "map_id": map_id,
            "layers": layers,
            "grid_or_vector": grid_or_vector,
            "boundary_type": boundary_type,
            "boundary_details": boundary_details,
            "operation": operation
        }
        
        # Add grid-specific parameters if relevant
        if grid_or_vector == "grid":
            payload["grid_type"] = grid_type
            payload["resolution"] = resolution
        
        # Add layer group if specified for vector maps
        if grid_or_vector == "vector" and layer_group:
            payload["layer_group"] = layer_group
        
        try:
            response = self.api_handler.make_authorised_request(endpoint, method='POST', json=payload)
            return response
        except Exception as e:
            logger.error(f"Failed to create map: {e}")
            return {'error': str(e)}
    
    def get_vector_layer_names(self):
        """
        Retrieves all available vector layer names.
        
        Returns:
            dict: Available vector layer names.
        """
        endpoint = "/api/vector_layer_names"
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='GET')
        except Exception as e:
            logger.error(f"Failed to retrieve vector layer names: {e}")
            return {'error': str(e)}
    
    def get_grid_layer_names(self):
        """
        Retrieves all available grid layer names.
        
        Returns:
            dict: Available grid layer names.
        """
        endpoint = "/api/grid_layer_names"
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='GET')
        except Exception as e:
            logger.error(f"Failed to retrieve grid layer names: {e}")
            return {'error': str(e)}
    
    def get_vector_layer_groups(self):
        """
        Retrieves all available vector layer groups.
        
        Returns:
            dict: Available vector layer groups.
        """
        endpoint = "/api/vector_layer_groups"
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='GET')
        except Exception as e:
            logger.error(f"Failed to retrieve vector layer groups: {e}")
            return {'error': str(e)}
    
    def generate_map_id(self):
        """
        Generates a unique map ID.
        
        Returns:
            dict: Object containing the generated map ID.
        """
        endpoint = "/api/generate_map_id"
        
        try:
            return self.api_handler.make_authorised_request(endpoint, method='GET')
        except Exception as e:
            logger.error(f"Failed to generate map ID: {e}")
            return {'error': str(e)}