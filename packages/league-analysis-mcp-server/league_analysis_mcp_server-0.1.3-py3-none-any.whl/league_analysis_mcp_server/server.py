"""
Main MCP Server for League Analysis using FastMCP 2.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastmcp import FastMCP
from pydantic import BaseModel
import uvicorn

from .enhanced_auth import get_enhanced_auth_manager
from .cache import get_cache_manager
from .tools import register_tools
from .resources import register_resources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path(__file__).parent / "config" / "settings.json"
with open(config_path) as f:
    config = json.load(f)

# Load game ID mappings
game_ids_path = Path(__file__).parent / "config" / "game_ids.json"
with open(game_ids_path) as f:
    game_ids = json.load(f)

# Initialize FastMCP server
mcp = FastMCP(
    name=config["server"]["name"],
    version=config["server"]["version"],
    description=config["server"]["description"]
)

# Global state
app_state = {
    "auth_manager": get_enhanced_auth_manager(),
    "cache_manager": get_cache_manager(),
    "config": config,
    "game_ids": game_ids
}


@mcp.tool()
def get_server_info() -> Dict[str, Any]:
    """
    Get information about the League Analysis MCP server.
    
    Returns:
        Server configuration and status information
    """
    auth_manager = app_state["auth_manager"]
    cache_manager = app_state["cache_manager"]
    
    return {
        "server": config["server"],
        "supported_sports": config["supported_sports"],
        "features": config["features"],
        "authentication": auth_manager.get_token_status(),
        "cache_stats": cache_manager.get_cache_stats(),
        "setup_required": not auth_manager.is_configured()
    }


@mcp.tool()
def get_setup_instructions() -> str:
    """
    Get setup instructions for Yahoo Fantasy Sports API access.
    
    Returns:
        Setup instructions as a string
    """
    auth_manager = app_state["auth_manager"]
    return auth_manager.get_setup_instructions()


@mcp.tool()
def list_available_seasons(sport: str) -> Dict[str, Any]:
    """
    List available seasons for a given sport.
    
    Args:
        sport: Sport code (nfl, nba, mlb, nhl)
    
    Returns:
        Available seasons and game IDs for the sport
    """
    if sport.lower() not in config["supported_sports"]:
        return {
            "error": f"Unsupported sport: {sport}",
            "supported_sports": config["supported_sports"]
        }
    
    sport_data = game_ids.get(sport.lower(), {})
    current_code = game_ids.get("current_codes", {}).get(sport.lower())
    
    return {
        "sport": sport.lower(),
        "current_season_code": current_code,
        "available_seasons": sport_data,
        "total_seasons": len(sport_data)
    }


@mcp.tool()
def refresh_yahoo_token() -> Dict[str, Any]:
    """
    Refresh the Yahoo API access token.
    
    Returns:
        Token refresh status and new token information
    """
    auth_manager = app_state["auth_manager"]
    
    if not auth_manager.is_configured():
        return {
            "status": "error",
            "message": "Yahoo authentication not configured. Check your setup status.",
            "next_step": "Run check_setup_status() to see what needs to be configured"
        }
    
    # Get current token status
    old_status = auth_manager.get_token_status()
    
    # Force a token refresh by getting a valid token
    try:
        token_data = auth_manager.get_valid_token()
        new_status = auth_manager.get_token_status()
        
        if token_data:
            return {
                "status": "success",
                "message": "Token refreshed successfully",
                "old_status": old_status,
                "new_status": new_status
            }
        else:
            return {
                "status": "error", 
                "message": "Failed to refresh token. May need to re-authenticate.",
                "current_status": new_status,
                "next_step": "Try reset_authentication() to start fresh, or check_setup_status() for details"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Token refresh failed: {str(e)}",
            "current_status": auth_manager.get_token_status()
        }


@mcp.tool()
def clear_cache(cache_type: str = "all") -> Dict[str, Any]:
    """
    Clear cache data.
    
    Args:
        cache_type: Type of cache to clear ('all', 'current', 'historical')
    
    Returns:
        Cache clearing status
    """
    cache_manager = app_state["cache_manager"]
    
    if cache_type == "all":
        cache_manager.cache.clear()
        return {"status": "success", "message": "All cache cleared"}
    elif cache_type == "current":
        # Clear current season data only
        keys_to_delete = []
        for key in cache_manager.cache._cache.keys():
            if key.startswith("curr_"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            cache_manager.cache.delete(key)
        
        return {
            "status": "success", 
            "message": f"Cleared {len(keys_to_delete)} current season cache entries"
        }
    else:
        return {"status": "error", "message": "Invalid cache_type. Use 'all', 'current', or 'historical'"}


# =============================================================================
# New Streamlined Authentication Setup Tools
# =============================================================================

@mcp.tool()
def check_setup_status() -> Dict[str, Any]:
    """
    Check the current authentication setup status and provide next steps.
    
    Returns:
        Current setup state and actionable next steps
    """
    auth_manager = app_state["auth_manager"]
    
    # Check if consumer credentials exist
    has_credentials = auth_manager.consumer_key and auth_manager.consumer_secret
    
    # Check if tokens exist
    token_status = auth_manager.get_token_status()
    has_tokens = token_status.get("has_access_token", False)
    is_token_valid = token_status.get("is_valid", False)
    
    # Determine setup state
    if not has_credentials:
        state = "credentials_needed"
        next_step = "Create a Yahoo Developer app and save credentials using save_yahoo_credentials()"
        message = "Yahoo API credentials not found. You need to create a Yahoo Developer app first."
    elif not has_tokens:
        state = "oauth_needed"  
        next_step = "Complete OAuth flow using start_oauth_flow()"
        message = "Credentials found but no access tokens. You need to complete the OAuth authorization."
    elif not is_token_valid:
        state = "token_expired"
        next_step = "Refresh your token using refresh_yahoo_token()"
        message = "Access token has expired and needs to be refreshed."
    else:
        state = "complete"
        next_step = "You're all set! Try using get_league_info() or other fantasy tools."
        message = "Authentication is fully configured and working."
    
    return {
        "setup_state": state,
        "message": message,
        "next_step": next_step,
        "details": {
            "has_credentials": has_credentials,
            "has_tokens": has_tokens,
            "is_token_valid": is_token_valid,
            "token_status": token_status
        }
    }


@mcp.tool()
def create_yahoo_app() -> Dict[str, Any]:
    """
    Provide step-by-step instructions for creating a Yahoo Developer application.
    
    Returns:
        Instructions for creating Yahoo app with exact values to use
    """
    return {
        "title": "Create Yahoo Fantasy Sports API Application",
        "url": "https://developer.yahoo.com/apps/",
        "steps": [
            "1. Go to https://developer.yahoo.com/apps/",
            "2. Sign in with your Yahoo account (same one you use for fantasy)",
            "3. Click 'Create an App' button",
            "4. Fill out the form with these exact values:",
            "   • Application Name: League Analysis MCP",
            "   • Application Type: Web Application",
            "   • Description: Fantasy Sports Analysis for MCP",
            "   • Home Page URL: http://localhost",
            "   • Redirect URI(s): oob",
            "5. Click 'Create App'",
            "6. Copy your Consumer Key and Consumer Secret from the app details page",
            "7. Use save_yahoo_credentials() with your keys"
        ],
        "important_notes": [
            "• Use 'oob' (out-of-band) for the redirect URI - this is required",
            "• Make sure to use the same Yahoo account for the app and your fantasy leagues",
            "• Keep your Consumer Key and Consumer Secret secure"
        ],
        "next_tool": "save_yahoo_credentials(consumer_key, consumer_secret)"
    }


@mcp.tool()
def save_yahoo_credentials(consumer_key: str, consumer_secret: str) -> Dict[str, Any]:
    """
    Save Yahoo API credentials and validate them.
    
    Args:
        consumer_key: Your Yahoo app's Consumer Key
        consumer_secret: Your Yahoo app's Consumer Secret
    
    Returns:
        Status of credential saving and next steps
    """
    if not consumer_key or not consumer_secret:
        return {
            "status": "error",
            "message": "Both consumer_key and consumer_secret are required",
            "next_step": "Get your credentials from https://developer.yahoo.com/apps/ and try again"
        }
    
    if len(consumer_key) < 10 or len(consumer_secret) < 10:
        return {
            "status": "error", 
            "message": "Credentials appear too short. Please verify you copied them correctly.",
            "next_step": "Double-check your Consumer Key and Consumer Secret from your Yahoo app"
        }
    
    try:
        auth_manager = app_state["auth_manager"]
        
        # Save credentials using the auth manager
        success = auth_manager.save_credentials(consumer_key, consumer_secret)
        
        if success:
            return {
                "status": "success",
                "message": f"Yahoo credentials saved successfully! Consumer Key: {consumer_key[:10]}...",
                "next_step": "Start OAuth flow using start_oauth_flow()",
                "next_tool": "start_oauth_flow()"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to save credentials. Check file permissions.",
                "next_step": "Verify the server has write access to the .env file"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error saving credentials: {str(e)}",
            "next_step": "Check the error and try again"
        }


@mcp.tool()
def start_oauth_flow() -> Dict[str, Any]:
    """
    Start the Yahoo OAuth authorization flow.
    
    Returns:
        Authorization URL and instructions for completing OAuth
    """
    auth_manager = app_state["auth_manager"]
    
    if not auth_manager.consumer_key:
        return {
            "status": "error",
            "message": "Consumer key not found. Save credentials first.",
            "next_step": "Run save_yahoo_credentials() with your app credentials"
        }
    
    try:
        # Generate authorization URL
        auth_url = auth_manager.get_authorization_url()
        
        return {
            "status": "ready",
            "message": "OAuth flow started. Please visit the URL below.",
            "authorization_url": auth_url,
            "instructions": [
                "1. Click or copy the authorization URL above",
                "2. Sign in to Yahoo (use the same account as your fantasy leagues)", 
                "3. Click 'Agree' to authorize League Analysis MCP",
                "4. Copy the verification code from the success page",
                "5. Use complete_oauth_flow() with your verification code"
            ],
            "next_tool": "complete_oauth_flow(verification_code)"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start OAuth flow: {str(e)}",
            "next_step": "Check your consumer credentials and try again"
        }


@mcp.tool()
def complete_oauth_flow(verification_code: str) -> Dict[str, Any]:
    """
    Complete the Yahoo OAuth flow with the verification code.
    
    Args:
        verification_code: The verification code from Yahoo's authorization page
    
    Returns:
        OAuth completion status and connection test results
    """
    if not verification_code:
        return {
            "status": "error",
            "message": "Verification code is required",
            "next_step": "Get the verification code from Yahoo and try again"
        }
    
    auth_manager = app_state["auth_manager"]
    
    try:
        # Exchange verification code for tokens
        success = auth_manager.exchange_code_for_tokens(verification_code)
        
        if success:
            # Test the connection
            test_result = auth_manager.test_connection()
            
            if test_result:
                return {
                    "status": "success",
                    "message": "🎉 Yahoo OAuth setup completed successfully!",
                    "details": "Authentication is working and tokens are saved.",
                    "next_steps": [
                        "Your setup is complete! You can now use all fantasy tools:",
                        "• get_league_info(league_id, sport) - Get league information",
                        "• get_standings(league_id, sport) - View league standings", 
                        "• list_available_seasons(sport) - See available seasons",
                        "• analyze_manager_history(league_id, sport) - Historical analysis"
                    ],
                    "token_status": auth_manager.get_token_status()
                }
            else:
                return {
                    "status": "partial_success",
                    "message": "Tokens saved but connection test inconclusive",
                    "details": "This may be normal if you haven't specified a league yet",
                    "next_step": "Try using get_league_info() with a real league ID to fully test"
                }
        else:
            return {
                "status": "error",
                "message": "Failed to exchange verification code for tokens",
                "next_step": "Verify the verification code is correct and hasn't expired"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"OAuth completion failed: {str(e)}",
            "next_step": "Check the verification code and try again"
        }


@mcp.tool()
def test_yahoo_connection() -> Dict[str, Any]:
    """
    Test the Yahoo API connection and return detailed status.
    
    Returns:
        Connection test results and troubleshooting information
    """
    auth_manager = app_state["auth_manager"]
    
    # Get comprehensive status
    setup_status = check_setup_status()
    
    if setup_status["setup_state"] != "complete":
        return {
            "status": "not_configured",
            "message": "Authentication not fully configured",
            "current_state": setup_status["setup_state"],
            "next_step": setup_status["next_step"]
        }
    
    try:
        # Test actual API connection
        test_result = auth_manager.test_connection()
        token_status = auth_manager.get_token_status()
        
        if test_result:
            return {
                "status": "success",
                "message": "✅ Yahoo API connection is working perfectly!",
                "token_status": token_status,
                "next_steps": [
                    "You can now use all fantasy sports tools",
                    "Try get_league_info(league_id, sport) with your league"
                ]
            }
        else:
            return {
                "status": "warning",
                "message": "⚠️ Connection test was inconclusive", 
                "details": "This may be normal without a specific league ID",
                "token_status": token_status,
                "next_step": "Try using get_league_info() with a real league to fully test"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Connection test failed: {str(e)}",
            "token_status": auth_manager.get_token_status(),
            "troubleshooting": [
                "1. Check if your tokens are expired (they refresh automatically)",
                "2. Verify your Yahoo account has access to fantasy leagues",
                "3. Try refresh_yahoo_token() to force a token refresh"
            ]
        }


@mcp.tool()
def reset_authentication() -> Dict[str, Any]:
    """
    Reset all authentication data and start fresh.
    
    Returns:
        Reset status and next steps
    """
    try:
        auth_manager = app_state["auth_manager"]
        
        # Clear all authentication data
        success = auth_manager.reset_authentication()
        
        if success:
            return {
                "status": "success",
                "message": "🔄 Authentication data cleared successfully",
                "next_step": "Run check_setup_status() to start setup from beginning"
            }
        else:
            return {
                "status": "error",
                "message": "Failed to reset authentication data",
                "next_step": "Check file permissions and try again"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Reset failed: {str(e)}",
            "next_step": "Manual cleanup may be required"
        }


# Register tools and resources from other modules
def initialize_server():
    """Initialize the server with tools and resources."""
    logger.info("Initializing League Analysis MCP Server...")
    
    # Register tools and resources
    register_tools(mcp, app_state)
    register_resources(mcp, app_state)
    
    # Validate configuration
    auth_manager = app_state["auth_manager"]
    if not auth_manager.is_configured():
        logger.warning("Yahoo authentication not configured. Only public league access available.")
        logger.info("Run 'check_setup_status' tool to begin streamlined setup.")
    else:
        logger.info("Yahoo authentication configured successfully.")
    
    logger.info(f"Server initialized with {len(config['supported_sports'])} sports supported")
    logger.info(f"Historical analysis: {'enabled' if config['features']['historical_analysis'] else 'disabled'}")


def main():
    """Main entry point for the server."""
    try:
        initialize_server()
        
        # Start the server
        logger.info("Starting League Analysis MCP Server...")
        mcp.run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()