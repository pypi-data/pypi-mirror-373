import logging

logger = logging.getLogger(__name__)

class RouteCalculator:
    def __init__(self, api_handler):
        self.api_handler = api_handler
        self._allowed_optimisation_types = None
        self._allowed_modes_of_travel = None

    def _get_allowed_optimisation_types(self):
        """Fetch allowed optimization types from server"""
        if self._allowed_optimisation_types is None:
            try:
                response = self.api_handler.make_authorised_request("/api/optimization_types", method='GET')
                if response and 'optimization_types' in response:
                    self._allowed_optimisation_types = [opt['id'] for opt in response['optimization_types']]
                else:
                    # Fallback to default values if server doesn't respond
                    self._allowed_optimisation_types = ['shortest_path', 'green_spaces', 'residential_avoidance', 'maximise_toilets', 'improve_walkability', 'avoid_crowds', 'bicycle_facilities']
            except Exception as e:
                logger.warning(f"Failed to fetch optimization types from server: {e}")
                # Fallback to default values
                self._allowed_optimisation_types = ['shortest_path', 'green_spaces', 'residential_avoidance', 'maximise_toilets', 'improve_walkability', 'avoid_crowds', 'bicycle_facilities']
        return self._allowed_optimisation_types

    def _get_allowed_modes_of_travel(self):
        """Fetch allowed modes of travel from server"""
        if self._allowed_modes_of_travel is None:
            try:
                response = self.api_handler.make_authorised_request("/api/modes_of_travel", method='GET')
                if response and 'modes_of_travel' in response:
                    self._allowed_modes_of_travel = [mode['id'] for mode in response['modes_of_travel']]
                else:
                    # Fallback to default values if server doesn't respond
                    self._allowed_modes_of_travel = ['walk', 'drive', 'bike', 'public_transport']
            except Exception as e:
                logger.warning(f"Failed to fetch modes of travel from server: {e}")
                # Fallback to default values
                self._allowed_modes_of_travel = ['walk', 'drive', 'bike', 'public_transport']
        return self._allowed_modes_of_travel

    def get_optimization_types(self):
        """Get available optimization types from server"""
        try:
            response = self.api_handler.make_authorised_request("/api/optimization_types", method='GET')
            return response.get('optimization_types', []) if response else []
        except Exception as e:
            logger.error(f"Failed to get optimization types: {e}")
            return []

    def get_modes_of_travel(self):
        """Get available modes of travel from server"""
        try:
            response = self.api_handler.make_authorised_request("/api/modes_of_travel", method='GET')
            return response.get('modes_of_travel', []) if response else []
        except Exception as e:
            logger.error(f"Failed to get modes of travel: {e}")
            return []

    def navigate(self, route_type: str, origin, destinations: list, optimisation_type="shortest_path", mode_of_travel="walk"):
        endpoint = "/api/route_calculator"

        # Validate optimization type and mode of travel against server configuration
        allowed_optimisation_types = self._get_allowed_optimisation_types()
        allowed_modes_of_travel = self._get_allowed_modes_of_travel()

        if optimisation_type not in allowed_optimisation_types:
            return {"error": f"Invalid optimisation_type provided: {optimisation_type}. Allowed types: {allowed_optimisation_types}"}

        if mode_of_travel not in allowed_modes_of_travel:
            return {"error": f"Invalid mode_of_travel provided: {mode_of_travel}. Allowed modes: {allowed_modes_of_travel}"}

        if route_type == "address" or route_type == "postcode":
            data = {
                "origin": origin,
                "destinations": destinations
            }
        elif route_type == "points":
            data = {
                "points": [origin] + destinations
            }
        else:
            return {"error": f"Invalid route_type provided: {route_type}"}

        route_payload = {
            "type": route_type,
            "data": data,
            "optimisationType": optimisation_type,
            "modeOfTravel": mode_of_travel
        }

        try:
            response = self.api_handler.make_authorised_request(endpoint, method='POST', json=route_payload)
            return response
        except Exception as e:
            logger.error(f"Failed to calculate route: {e}")
            return {'error': str(e)}