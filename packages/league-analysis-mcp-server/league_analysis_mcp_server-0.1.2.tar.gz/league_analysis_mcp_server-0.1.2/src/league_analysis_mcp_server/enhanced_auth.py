"""
Enhanced Yahoo Authentication Module with Token Refresh
Inspired by fantasy-football-mcp-public approach
"""

import os
import json
import time
import logging
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class EnhancedYahooAuthManager:
    """Enhanced Yahoo OAuth authentication manager with token refresh."""
    
    def __init__(self):
        self.consumer_key = os.getenv('YAHOO_CONSUMER_KEY')
        self.consumer_secret = os.getenv('YAHOO_CONSUMER_SECRET')
        self.access_token = os.getenv('YAHOO_ACCESS_TOKEN')
        self.refresh_token = os.getenv('YAHOO_REFRESH_TOKEN')
        self.access_token_json = os.getenv('YAHOO_ACCESS_TOKEN_JSON')
        
        self.token_file = Path('.yahoo_token.json')
        self.env_file = Path('.env')
        
        # Token refresh URLs
        self.token_url = "https://api.login.yahoo.com/oauth2/get_token"
        
        if not self.consumer_key or not self.consumer_secret:
            logger.warning("Yahoo consumer key/secret not found in environment variables")
    
    def get_auth_credentials(self) -> Dict[str, Any]:
        """
        Get authentication credentials for YFPY with automatic token refresh.
        
        Returns:
            Dict containing auth credentials for YFPY initialization
        """
        credentials = {
            'yahoo_consumer_key': self.consumer_key,
            'yahoo_consumer_secret': self.consumer_secret
        }
        
        # Try to get fresh token
        token_data = self.get_valid_token()
        
        if token_data:
            credentials['yahoo_access_token_json'] = token_data
            logger.info("Using valid access token")
        elif self.access_token_json:
            try:
                # Try to parse existing token
                if isinstance(self.access_token_json, str):
                    token_data = json.loads(self.access_token_json)
                else:
                    token_data = self.access_token_json
                
                credentials['yahoo_access_token_json'] = token_data
                logger.info("Using configured access token")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse access token JSON: {e}")
        
        return credentials
    
    def get_valid_token(self) -> Optional[Dict[str, Any]]:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid token data or None if unable to get token
        """
        # Try to load token from file
        token_data = self.load_token_from_file()
        
        if not token_data:
            logger.debug("No token file found")
            return None
        
        # Check if token is still valid
        if self.is_token_valid(token_data):
            logger.debug("Current token is still valid")
            return token_data
        
        # Try to refresh token
        logger.info("Token expired, attempting refresh...")
        refreshed_token = self.refresh_access_token(token_data)
        
        if refreshed_token:
            self.save_token_to_file(refreshed_token)
            self.update_env_file(refreshed_token)
            logger.info("Token refreshed successfully")
            return refreshed_token
        
        logger.warning("Unable to refresh token")
        return None
    
    def load_token_from_file(self) -> Optional[Dict[str, Any]]:
        """Load token data from JSON file."""
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load token file: {e}")
            return None
    
    def save_token_to_file(self, token_data: Dict[str, Any]) -> None:
        """Save token data to JSON file."""
        try:
            # Add timestamp for tracking
            token_data['saved_at'] = int(time.time())
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            logger.debug(f"Token saved to {self.token_file}")
        except IOError as e:
            logger.error(f"Failed to save token file: {e}")
    
    def is_token_valid(self, token_data: Dict[str, Any]) -> bool:
        """
        Check if token is still valid.
        
        Args:
            token_data: Token data dictionary
            
        Returns:
            True if token is valid, False otherwise
        """
        if not token_data:
            return False
        
        # Check if we have required fields
        if 'access_token' not in token_data:
            return False
        
        # Check expiration if available
        if 'expires_in' in token_data and 'saved_at' in token_data:
            expires_at = token_data['saved_at'] + token_data['expires_in']
            current_time = int(time.time())
            
            # Add 5 minute buffer before expiration
            if current_time >= (expires_at - 300):
                logger.debug("Token expired or expiring soon")
                return False
        
        return True
    
    def refresh_access_token(self, token_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Refresh the access token using the refresh token.
        
        Args:
            token_data: Current token data
            
        Returns:
            New token data or None if refresh failed
        """
        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            logger.error("No refresh token available")
            return None
        
        if not self.consumer_key or not self.consumer_secret:
            logger.error("Consumer key/secret not available for token refresh")
            return None
        
        # Prepare refresh request
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'League-Analysis-MCP/1.0'
        }
        
        try:
            logger.debug("Requesting token refresh from Yahoo API")
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                new_token_data = response.json()
                
                # Preserve refresh token if not returned
                if 'refresh_token' not in new_token_data and refresh_token:
                    new_token_data['refresh_token'] = refresh_token
                
                logger.info("Token refresh successful")
                return new_token_data
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Token refresh request failed: {e}")
            return None
    
    def update_env_file(self, token_data: Dict[str, Any]) -> None:
        """Update .env file with new token data."""
        if not self.env_file.exists():
            logger.warning("No .env file found to update")
            return
        
        try:
            # Read current .env content
            with open(self.env_file, 'r') as f:
                lines = f.readlines()
            
            # Update or add token line
            token_json = json.dumps(token_data)
            token_line = f'YAHOO_ACCESS_TOKEN_JSON={token_json}\n'
            
            # Find and replace existing token line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('YAHOO_ACCESS_TOKEN_JSON='):
                    lines[i] = token_line
                    updated = True
                    break
            
            # Add new line if not found
            if not updated:
                lines.append(token_line)
            
            # Write back to file
            with open(self.env_file, 'w') as f:
                f.writelines(lines)
            
            logger.debug("Environment file updated with new token")
            
        except IOError as e:
            logger.error(f"Failed to update .env file: {e}")
    
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
            True if access token is configured or available in file
        """
        if self.access_token_json:
            return True
        
        if self.access_token:
            return True
        
        token_data = self.load_token_from_file()
        return bool(token_data and 'access_token' in token_data)
    
    def get_token_status(self) -> Dict[str, Any]:
        """
        Get comprehensive token status information.
        
        Returns:
            Dictionary with token status details
        """
        status = {
            'configured': self.is_configured(),
            'has_token': self.has_access_token(),
            'token_file_exists': self.token_file.exists(),
            'env_file_exists': self.env_file.exists(),
        }
        
        token_data = self.load_token_from_file()
        if token_data:
            status.update({
                'token_valid': self.is_token_valid(token_data),
                'has_refresh_token': 'refresh_token' in token_data,
                'token_created': token_data.get('saved_at'),
                'expires_in': token_data.get('expires_in')
            })
        
        return status
    
    def get_setup_instructions(self) -> str:
        """
        Get comprehensive setup instructions.
        
        Returns:
            String containing detailed setup instructions
        """
        return """
League Analysis MCP - Yahoo Fantasy Sports API Setup

🚀 AUTOMATED SETUP (Recommended):
   Run: uv run python utils/setup_yahoo_auth.py
   
   This will:
   - Guide you through Yahoo app creation
   - Automate the OAuth flow
   - Save tokens securely
   - Test the connection

📋 MANUAL SETUP:
1. Create Yahoo Developer App:
   - Go to https://developer.yahoo.com/apps/
   - Create new app:
     * Application Type: Web Application
     * Home Page URL: http://localhost
     * Redirect URI(s): oob

2. Configure Environment:
   - Copy .env.example to .env
   - Add your credentials:
     YAHOO_CONSUMER_KEY=your_consumer_key
     YAHOO_CONSUMER_SECRET=your_consumer_secret

3. Run Authentication:
   - uv run python utils/setup_yahoo_auth.py

🔧 TROUBLESHOOTING:
   - Check token status: get_server_info() tool
   - Regenerate tokens: delete .yahoo_token.json and re-run setup
   - Verify app settings: ensure redirect_uri is 'oob'

📖 DOCUMENTATION:
   - Yahoo Fantasy API: https://developer.yahoo.com/fantasysports/
   - YFPY Library: https://yfpy.uberfastman.com/
"""


def get_enhanced_auth_manager() -> EnhancedYahooAuthManager:
    """Get an enhanced Yahoo auth manager instance."""
    return EnhancedYahooAuthManager()