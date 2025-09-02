"""
NotifyOn Python SDK Client
"""

import os
from typing import Optional
import requests
from .exceptions import ConfigurationError, APIError


class NotifyOn:
    """
    NotifyOn client for sending notifications
    
    Usage:
        from notifyon import NotifyOn
        
        notifyon = NotifyOn(api_key="your_api_key")
        notifyon.send("user_123")
        notifyon.send("user_123", "Task complete")
    """
    
    DEFAULT_API_URL = "https://api.notifyon.app"
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize NotifyOn client
        
        Args:
            api_key: Your NotifyOn API key. If not provided, will look for NOTIFYON_API_KEY env var
            api_url: Optional API URL override for self-hosted or development
        """
        self.api_key = api_key or os.environ.get("NOTIFYON_API_KEY")
        if not self.api_key:
            raise ConfigurationError(
                "API key is required. Pass it to NotifyOn() or set NOTIFYON_API_KEY environment variable"
            )
        
        self.api_url = (api_url or os.environ.get("NOTIFYON_API_URL", self.DEFAULT_API_URL)).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        })
    
    def send(self, user_id: str, message: Optional[str] = None) -> dict:
        """
        Send a notification to a user
        
        Args:
            user_id: The external user ID to notify
            message: Optional custom message for the notification
            
        Returns:
            dict: Response from the API
            
        Raises:
            APIError: If the API returns an error response
        """
        if not user_id:
            raise ValueError("user_id is required")
        
        payload = {"userId": user_id}
        if message:
            payload["message"] = message
        
        try:
            response = self.session.post(
                f"{self.api_url}/v1/send",
                json=payload,
                timeout=10
            )
            
            # Check for successful response
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise APIError("Invalid API key")
            elif response.status_code == 400:
                error_data = response.json()
                raise APIError(f"Bad request: {error_data.get('error', 'Unknown error')}")
            else:
                raise APIError(f"API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise APIError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise APIError("Failed to connect to NotifyOn API")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Support for context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up on context manager exit"""
        self.close()