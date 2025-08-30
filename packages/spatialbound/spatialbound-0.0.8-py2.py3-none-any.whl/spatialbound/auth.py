import requests
import logging
import platform
import uuid
from datetime import datetime
from .config import BASE_URL

logger = logging.getLogger(__name__)

class Auth:
    def __init__(self, api_key):
        self.api_key = api_key

    def _get_telemetry_data(self):
        """Get telemetry data for authentication verification"""
        try:
            # Get public IP address
            ip_response = requests.get("https://api.ipify.org?format=json", timeout=5)
            if ip_response.status_code == 200:
                ip_data = ip_response.json()
                public_ip = ip_data.get('ip')
                
                # Get geolocation data
                geo_response = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=5)
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    
                    return {
                        "ip_address": public_ip,
                        "country": geo_data.get('country'),
                        "country_code": geo_data.get('countryCode'),
                        "city": geo_data.get('city'),
                        "latitude": geo_data.get('lat'),
                        "longitude": geo_data.get('lon'),
                        "timezone": geo_data.get('timezone'),
                        "isp": geo_data.get('isp'),
                        "org": geo_data.get('org'),
                        "status": geo_data.get('status')
                    }
                else:
                    return {
                        "ip_address": public_ip,
                        "error": "Could not get geolocation data"
                    }
            else:
                return {
                    "error": "Could not get IP address"
                }
                
        except Exception as e:
            logger.error(f"Error getting telemetry data: {e}")
            return {
                "error": f"Telemetry detection failed: {str(e)}"
            }

    def get_login_token(self):
        login_url = f"{BASE_URL}/login-api-key"

        # Get telemetry data for authentication verification
        telemetry_data = self._get_telemetry_data()
        
        # Create authentication payload with telemetry
        auth_payload = {
            "telemetry_verification": {
                "session_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "python_version": platform.python_version(),
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "sdk_version": "0.0.6"
                },
                "user_location": telemetry_data,
                "telemetry_enabled": True,
                "verification_hash": self._generate_verification_hash(telemetry_data)
            }
        }

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(login_url, headers=headers, json=auth_payload, timeout=40)
            response.raise_for_status()
            response_data = response.json()
            token = response_data.get("access_token")
            return token, response_data
        except requests.RequestException as ex:
            logger.error(f"Login error: {ex}")
            return None, f"Login failed: {ex}"
    
    def _generate_verification_hash(self, telemetry_data):
        """Generate a simple verification hash to detect tampering"""
        import hashlib
        
        # Create a hash from telemetry data and API key
        data_string = f"{self.api_key}:{telemetry_data.get('ip_address', '')}:{telemetry_data.get('country_code', '')}:{platform.python_version()}"
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]