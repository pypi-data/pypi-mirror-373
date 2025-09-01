"""
Foreva AI SDK HTTP Client
Handles secure API communication without exposing secrets
"""

import json
import logging
import time
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from . import __version__
from .exceptions import (
    ForevaAPIError, 
    ForevaAuthenticationError,
    ForevaNotFoundError,
    ForevaRateLimitError,
    ForevaTestLimitError,
    ForevaSubscriptionRequiredError,
    ForevaNetworkError
)
# No more environment/routing imports - all server-controlled now!

logger = logging.getLogger(__name__)


class ForevaAPIClient:
    """
    Secure HTTP client for Foreva API
    
    Security features:
    - API keys never logged or exposed in errors
    - Automatic retry with exponential backoff
    - Request signing for sensitive operations
    - Rate limit handling
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = self._get_base_url_from_api_key(api_key)
        
        # Create session with retries
        self.session = requests.Session()
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers (no sensitive info in User-Agent for security)  
        self.session.headers.update({
            'User-Agent': f'foreva-python-sdk/{__version__}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _get_base_url_from_api_key(self, api_key: str) -> str:
        """
        Get base URL from build-time configuration
        Different SDK builds connect to different environments
        """
        from .config import get_base_url
        return get_base_url()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers (separated for security)"""
        return {
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response with proper error handling
        Never expose API keys in error messages
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {}
        
        if response.status_code == 200:
            return data
        elif response.status_code == 401:
            raise ForevaAuthenticationError("Invalid API key", response.status_code, data)
        elif response.status_code == 402:
            # Handle both dict and string error responses
            error_msg = 'Subscription required for live mode'
            if isinstance(data, dict) and 'error' in data:
                if isinstance(data['error'], dict):
                    error_msg = data['error'].get('message', error_msg)
                else:
                    error_msg = str(data['error'])
            elif isinstance(data, str):
                error_msg = data
            
            raise ForevaSubscriptionRequiredError(error_msg, response.status_code, data)
        elif response.status_code == 404:
            # Handle both dict and string error responses  
            error_msg = 'Resource not found'
            if isinstance(data, dict) and 'error' in data:
                if isinstance(data['error'], dict):
                    error_msg = data['error'].get('message', error_msg)
                else:
                    error_msg = str(data['error'])
            elif isinstance(data, str):
                error_msg = data
                
            raise ForevaNotFoundError(error_msg, response.status_code, data)
        elif response.status_code == 429:
            # Handle both dict and string error responses
            if isinstance(data, dict):
                error_data = data.get('error', {})
                if isinstance(error_data, dict):
                    error_msg = error_data.get('message', 'Rate limit exceeded')
                elif isinstance(error_data, str):
                    error_msg = error_data
                else:
                    error_msg = 'Rate limit exceeded'
            else:
                error_msg = str(data) if data else 'Rate limit exceeded'
            
            # Check if it's a test mode limit error
            if 'test mode limit' in error_msg.lower() or 'test limit' in error_msg.lower():
                raise ForevaTestLimitError(error_msg, response.status_code, data)
            else:
                raise ForevaRateLimitError(error_msg, response.status_code, data)
        else:
            # Handle both {"error": {"message": "..."}} and {"error": "..."} formats
            error_data = data.get('error', f'API error: {response.status_code}')
            if isinstance(error_data, dict):
                error_message = error_data.get('message', f'API error: {response.status_code}')
            else:
                error_message = str(error_data)
            raise ForevaAPIError(error_message, response.status_code, data)
    
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self._debug_log(f"GET {endpoint}", params)
            response = self.session.get(
                url, 
                params=params,
                headers=self._get_auth_headers(),
                timeout=30
            )
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            self._error_log(f"Network error for GET {endpoint}", e)
            raise ForevaNetworkError(f"Network error: {type(e).__name__}")
    
    def post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self._debug_log(f"POST {endpoint}", data)
            response = self.session.post(
                url,
                json=data,
                headers=self._get_auth_headers(),
                timeout=30
            )
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            self._error_log(f"Network error for POST {endpoint}", e)
            raise ForevaNetworkError(f"Network error: {type(e).__name__}")
    
    def put(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"PUT {endpoint}")
            response = self.session.put(
                url,
                json=data,
                headers=self._get_auth_headers(),
                timeout=30
            )
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error for PUT {endpoint}: {type(e).__name__}")
            raise ForevaNetworkError(f"Network error: {type(e).__name__}")
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"DELETE {endpoint}")
            response = self.session.delete(
                url,
                headers=self._get_auth_headers(),
                timeout=30
            )
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error for DELETE {endpoint}: {type(e).__name__}")
            raise ForevaNetworkError(f"Network error: {type(e).__name__}")
    
    def close(self):
        """Close the session"""
        self.session.close()
        
    # ============ SDK METHODS ============
    
    def get_config(self) -> Dict[str, Any]:
        """Fetch server configuration"""
        return self.get("/config")
    
    def setup_agent(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup agent with server"""
        return self.post("/agents/setup", config_data)
    
    def load_agent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load existing agent"""
        return self.get("/agents/load", params)
    
    def list_agents(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """List agents"""
        return self.get("/agents", params)
    
    def sync_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Force immediate sync of agent with recent updates"""
        return self.post("/agents/sync", data)
    
    def _debug_log(self, action: str, data: Any = None):
        """Log debug info for debug builds only"""
        from .config import is_debug_build, should_show_internal_logs
        
        if is_debug_build() and should_show_internal_logs():
            logger.debug(f"🔧 {action}")
            if data:
                logger.debug(f"   Data: {data}")
    
    def _error_log(self, action: str, error: Exception):
        """Log errors with appropriate detail level"""
        from .config import is_debug_build, should_show_detailed_errors
        
        if is_debug_build() and should_show_detailed_errors():
            logger.error(f"🚨 DEBUG: {action} - {type(error).__name__}: {str(error)}")
        else:
            logger.error(f"❌ {action} - {type(error).__name__}")