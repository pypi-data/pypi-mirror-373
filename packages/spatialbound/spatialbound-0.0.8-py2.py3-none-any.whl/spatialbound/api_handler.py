# spatialbound/api_handler.py
import requests
from .auth import Auth
from .config import BASE_URL
from .version import __version__
import logging

logger = logging.getLogger(__name__)

class APIHandler:
    def __init__(self, api_key):
        self.auth = Auth(api_key)
        self.token, self.login_response = self.auth.get_login_token()
        self.client_version = __version__
        
                # Add version to login response
        if isinstance(self.login_response, dict):
            self.login_response["client_version"] = self.client_version
            
        # Try to get server version
        if self.token:
            self.get_server_version()
    
    def get_server_version(self):
        """
        Get the version of the server API
        """
        try:
            endpoint = "/version"
            response = self.make_authorised_request(endpoint, method='GET')
            
            if response and 'version' in response:
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

    def make_authorised_request(self, endpoint, method='GET', data=None, json=None, files=None):
        if not self.token:
            return {"error": "Authentication token is missing"}
        url = f"{BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'User-Agent': f"Spatialbound-Python/{self.client_version}"  # Add client version in User-Agent
        }
        try:
            response = requests.request(method, url, headers=headers, data=data, json=json, files=files, verify=True, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as ex:
            return {"error": str(ex)}