# spatialbound/status.py
import requests
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from .config import BASE_URL

logger = logging.getLogger(__name__)

class Status:
    """
    SDK status and health monitoring system.
    This system helps ensure the SDK is working properly and provides diagnostic information.
    """
    
    def __init__(self, api_key: str, enabled: bool = True):
        self.api_key = api_key
        self.enabled = enabled
        self.session_id = None
        self.status_url = f"{BASE_URL}/telemetry"
        
        if self.enabled:
            # Initialize status monitoring
            self._create_session()
    
    def _create_session(self, account_info: Optional[Dict[str, Any]] = None):
        """Initialize status monitoring session"""
        if not self.enabled:
            return
        
        try:
            payload = {
                "account_info": account_info or {}
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            response = requests.post(
                f"{self.status_url}/session",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                logger.debug(f"Status monitoring initialized: {self.session_id[:8] if self.session_id else 'unknown'}")
            else:
                logger.debug(f"Failed to initialize status monitoring: {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Error initializing status monitoring: {e}")
    
    def update_account_info(self, account_info: Dict[str, Any]):
        """Update account information for status monitoring"""
        if not self.enabled:
            return
        
        # End current session if exists
        if self.session_id:
            self._end_session()
        
        # Create new session with account info
        self._create_session(account_info)
    
    def track_feature_usage(self, feature: str, success: bool = True, 
                          metadata: Optional[Dict[str, Any]] = None):
        """Track feature status and performance"""
        if not self.enabled or not self.session_id:
            return
        
        try:
            payload = {
                "session_id": self.session_id,
                "feature": feature,
                "success": success,
                "metadata": metadata or {}
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            response = requests.post(
                f"{self.status_url}/event",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.debug(f"Failed to track feature status: {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Error tracking feature status: {e}")
    
    def track_location_usage(self, lat: float, lon: float, feature: str, 
                           success: bool = True, metadata: Optional[Dict[str, Any]] = None):
        """Track location-based feature status"""
        if not self.enabled or not self.session_id:
            return
        
        location_metadata = {
            "latitude": lat,
            "longitude": lon,
            "feature": feature
        }
        
        if metadata:
            location_metadata.update(metadata)
        
        self.track_feature_usage("location_usage", success, location_metadata)
    
    def track_session_end(self):
        """End the status monitoring session"""
        if not self.enabled or not self.session_id:
            return
        
        self._end_session()
    
    def _end_session(self):
        """End the current status monitoring session"""
        try:
            payload = {
                "session_id": self.session_id
            }
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            response = requests.post(
                f"{self.status_url}/session/end",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Status monitoring session ended: {data.get('session_id', 'unknown')}")
            else:
                logger.debug(f"Failed to end status monitoring session: {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Error ending status monitoring session: {e}")
        finally:
            self.session_id = None
    
    def disable(self):
        """Disable status monitoring"""
        if self.enabled:
            self.track_session_end()
        self.enabled = False
    
    def enable(self):
        """Enable status monitoring"""
        self.enabled = True
        if not self.session_id:
            self._create_session()
    
    def get_user_location_info(self) -> Dict[str, Any]:
        """Get user location information for status monitoring"""
        if not self.enabled or not self.session_id:
            return {}
        
        try:
            headers = {
                "X-API-Key": self.api_key
            }
            
            response = requests.get(
                f"{self.status_url}/session/{self.session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("location", {})
            else:
                logger.debug(f"Failed to get session info: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.debug(f"Error getting session info: {e}")
            return {}
    
    def check_access_control(self, feature: str) -> Dict[str, Any]:
        """Check access control for a feature"""
        if not self.enabled or not self.session_id:
            return {"allowed": True, "restricted": False, "reason": None}
        
        try:
            headers = {
                "X-API-Key": self.api_key
            }
            
            response = requests.get(
                f"{self.status_url}/session/{self.session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("access_control", {"allowed": True, "restricted": False, "reason": None})
            else:
                return {"allowed": True, "restricted": False, "reason": None}
                
        except Exception as e:
            logger.debug(f"Error checking access control: {e}")
            return {"allowed": True, "restricted": False, "reason": None}
