# spatialbound/__init__.py
from .spatialbound import Spatialbound
from .version import __version__

__all__ = ['Spatialbound', '__version__']

# Create a callable class that wraps the module
class SpatialboundModule:
    def __init__(self):
        self.Spatialbound = Spatialbound
        self.__version__ = __version__
    
    def __call__(self, api_key: str) -> Spatialbound:
        """
        Allow direct calling of the module for instantiation.
        
        Args:
            api_key (str): Your API key for authentication
            
        Returns:
            Spatialbound: Configured Spatialbound instance
            
        Example:
            >>> import spatialbound
            >>> spatialbound = spatialbound("your-api-key")
            >>> result = spatialbound.navigate(route_type="address", origin="London", destinations=["Paris"])
        """
        return Spatialbound(api_key)

# Create the module instance
spatialbound = SpatialboundModule()

# Make the module callable by replacing the module with our callable instance
import sys
sys.modules[__name__] = spatialbound