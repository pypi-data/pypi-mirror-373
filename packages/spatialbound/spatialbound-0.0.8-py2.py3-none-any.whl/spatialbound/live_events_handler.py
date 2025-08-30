import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LiveEventsHandler:
    """
    Handler for live events and real-time disaster data from the GlobalEvents system.
    Provides access to live events with account-based quota limits and filtering capabilities.
    """
    
    def __init__(self, api_handler, spatialbound_instance=None):
        """
        Initialize the LiveEventsHandler with an API handler.
        
        Args:
            api_handler: The API handler for making authorized requests.
            spatialbound_instance: The Spatialbound instance for status tracking.
        """
        self.api_handler = api_handler
        self.spatialbound = spatialbound_instance
        
        # Available categories from the GlobalEvents system
        self.available_categories = [
            "all",
            "natural_disaster",
            "human_conflict", 
            "health_emergency",
            "infrastructure_failure",
            "environmental_crisis",
            "security_threat",
            "other_critical"
        ]
        
        # Timeframe options with validation
        self.timeframe_options = {
            "1h": 1,
            "2h": 2,
            "6h": 6,
            "12h": 12,
            "24h": 24,
            "48h": 48,
            "72h": 72
        }
    
    def live_events(self, category: str = "all", timeframe: str = "1h") -> Dict[str, Any]:
        """
        Get live events from the GlobalEvents system with account-based quota limits.
        
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
        try:
            # Validate category
            if category not in self.available_categories:
                raise ValueError(f"Invalid category '{category}'. Available categories: {', '.join(self.available_categories)}")
            
            # Validate timeframe
            if timeframe not in self.timeframe_options:
                raise ValueError(f"Invalid timeframe '{timeframe}'. Available timeframes: {', '.join(self.timeframe_options.keys())}")
            
            # Convert timeframe to hours
            hours = self.timeframe_options[timeframe]
            
            # Track feature usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("live_events", success=True, metadata={
                    "category": category,
                    "timeframe": timeframe,
                    "hours": hours
                })
            
            # Build query parameters
            query_params = []
            query_params.append(f"hours={hours}")
            query_params.append("limit=1000")  # Let server apply account limits
            
            # Add category filter if not "all"
            if category != "all":
                query_params.append(f"category={category}")
            
            # Construct the endpoint with query parameters
            endpoint = f"/api/live-events/disasters?{'&'.join(query_params)}"
            
            # Make API request to live events endpoint
            response = self.api_handler.make_authorised_request(
                endpoint,
                method='GET'
            )
            
            if not response:
                raise Exception("Failed to retrieve live events data")
            
            # Return only the clean event data
            response = {
                'events': response.get('data', []),
                'total_count': response.get('filtered_count', 0),
                'category': category,
                'timeframe': timeframe
            }
            
            logger.info(f"Successfully retrieved {response['total_count']} live events for category '{category}' in timeframe '{timeframe}'")
            
            return response
            
        except ValueError as e:
            # Track failed usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("live_events", success=False, metadata={
                    "error": "validation_error",
                    "category": category,
                    "timeframe": timeframe
                })
            raise e
        except Exception as e:
            # Track failed usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("live_events", success=False, metadata={
                    "error": "api_error",
                    "category": category,
                    "timeframe": timeframe
                })
            logger.error(f"Error retrieving live events: {str(e)}")
            raise Exception(f"Failed to retrieve live events: {str(e)}")
    
    def get_events_summary(self, timeframe: str = "24h") -> Dict[str, Any]:
        """
        Get a summary of live events statistics.
        
        Args:
            timeframe (str): Time range to look back. Options: "1h", "2h", "6h", "12h", 
                           "24h", "48h", "72h" (72h only available for ultra/enterprise accounts)
        
        Returns:
            Dict[str, Any]: Events summary with statistics and account limits information.
        """
        try:
            # Validate timeframe
            if timeframe not in self.timeframe_options:
                raise ValueError(f"Invalid timeframe '{timeframe}'. Available timeframes: {', '.join(self.timeframe_options.keys())}")
            
            # Convert timeframe to hours
            hours = self.timeframe_options[timeframe]
            
            # Track feature usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("live_events_summary", success=True, metadata={
                    "timeframe": timeframe,
                    "hours": hours
                })
            
            # Construct the endpoint with query parameters
            endpoint = f"/api/live-events/summary?hours={hours}"
            
            # Make API request to summary endpoint
            response = self.api_handler.make_authorised_request(
                endpoint,
                method='GET'
            )
            
            if not response:
                raise Exception("Failed to retrieve events summary")
            
            # Return only the clean summary data
            response = {
                'summary': response.get('summary', {}),
                'timeframe': timeframe
            }
            
            logger.info(f"Successfully retrieved events summary for timeframe '{timeframe}'")
            
            return response
            
        except Exception as e:
            # Track failed usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("live_events_summary", success=False, metadata={
                    "error": "api_error",
                    "timeframe": timeframe
                })
            logger.error(f"Error retrieving events summary: {str(e)}")
            raise Exception(f"Failed to retrieve events summary: {str(e)}")
    
    def get_available_categories(self) -> List[str]:
        """
        Get list of available event categories.
        
        Returns:
            List[str]: List of available category codes.
        """
        return self.available_categories.copy()
    
    def get_live_events_categories(self) -> Dict[str, Any]:
        """
        Get detailed live events categories from the server.
        
        Returns:
            Dict[str, Any]: Categories with detailed information including codes, names, and descriptions.
        """
        try:
            # Track feature usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("get_live_events_categories", success=True)
            
            # Make API request to get categories endpoint
            response = self.api_handler.make_authorised_request(
                "/api/live-events/get_live_events_categories",
                method='GET'
            )
            
            if not response:
                raise Exception("Failed to retrieve live events categories")
            
            logger.info(f"Successfully retrieved {response.get('total_count', 0)} live events categories")
            
            return response
            
        except Exception as e:
            # Track failed usage
            if self.spatialbound and hasattr(self.spatialbound, 'status'):
                self.spatialbound.status.track_feature_usage("get_live_events_categories", success=False, metadata={
                    "error": "api_error"
                })
            logger.error(f"Error retrieving live events categories: {str(e)}")
            raise Exception(f"Failed to retrieve live events categories: {str(e)}")
    
    def get_available_timeframes(self) -> List[str]:
        """
        Get list of available timeframe options.
        
        Returns:
            List[str]: List of available timeframe codes.
        """
        return list(self.timeframe_options.keys())
    
    def get_account_limits(self) -> Dict[str, Any]:
        """
        Get current account limits for live events.
        
        Returns:
            Dict[str, Any]: Account limits information including max hours and events.
        """
        try:
            # Construct the endpoint with query parameters
            endpoint = "/api/live-events/disasters?hours=1&limit=1"
            
            # Make a minimal request to get account limits info
            response = self.api_handler.make_authorised_request(
                endpoint,
                method='GET'
            )
            
            if response and 'account_limits' in response:
                return response['account_limits']
            else:
                return {
                    "error": "Could not retrieve account limits",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error retrieving account limits: {str(e)}")
            return {
                "error": f"Failed to retrieve account limits: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
