"""
Yahoo OAuth Authentication Module for League Analysis MCP Server
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class YahooAuthManager:
    """Manages Yahoo OAuth authentication for fantasy sports API access."""
    
    def __init__(self):
        self.consumer_key = os.getenv('YAHOO_CONSUMER_KEY')
        self.consumer_secret = os.getenv('YAHOO_CONSUMER_SECRET')
        self.access_token_json = os.getenv('YAHOO_ACCESS_TOKEN_JSON')
        
        if not self.consumer_key or not self.consumer_secret:
            logger.warning("Yahoo consumer key/secret not found in environment variables")
    
    def get_auth_credentials(self) -> Dict[str, Any]:
        """
        Get authentication credentials for YFPY.
        
        Returns:
            Dict containing auth credentials for YFPY initialization
        """
        credentials = {
            'yahoo_consumer_key': self.consumer_key,
            'yahoo_consumer_secret': self.consumer_secret
        }
        
        if self.access_token_json:
            try:
                # Try to parse as JSON string
                if isinstance(self.access_token_json, str):
                    token_data = json.loads(self.access_token_json)
                else:
                    token_data = self.access_token_json
                
                credentials['yahoo_access_token_json'] = token_data
                logger.info("Using pre-configured access token")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse access token JSON: {e}")
        
        return credentials
    
    def is_configured(self) -> bool:
        """
        Check if authentication is properly configured.
        
        Returns:
            True if consumer key and secret are available
        """
        return bool(self.consumer_key and self.consumer_secret)
    
    def has_access_token(self) -> bool:
        """
        Check if access token is available.
        
        Returns:
            True if access token is configured
        """
        return bool(self.access_token_json)
    
    def get_setup_instructions(self) -> str:
        """
        Get setup instructions for Yahoo app configuration.
        
        Returns:
            String containing setup instructions
        """
        return """
Yahoo Fantasy Sports API Setup Instructions:

1. Go to https://developer.yahoo.com/apps/
2. Create a new app with these settings:
   - Application Name: Your app name
   - Application Type: Web Application
   - Description: Your app description
   - Home Page URL: http://localhost (or your domain)
   - Redirect URI(s): oob (for desktop apps)

3. Copy your Consumer Key and Consumer Secret

4. Set environment variables:
   YAHOO_CONSUMER_KEY=your_consumer_key
   YAHOO_CONSUMER_SECRET=your_consumer_secret

5. For private leagues, you'll also need to set:
   YAHOO_ACCESS_TOKEN_JSON={"access_token":"...","refresh_token":"...","token_type":"bearer"}

6. Run the server with: python -m src.server

Note: For public leagues only, you can skip the access token setup.
"""


def get_auth_manager() -> YahooAuthManager:
    """Get a configured Yahoo auth manager instance."""
    return YahooAuthManager()