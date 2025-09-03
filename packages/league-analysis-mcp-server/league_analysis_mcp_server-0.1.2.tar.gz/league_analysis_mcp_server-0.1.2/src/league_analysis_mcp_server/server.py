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
            "message": "Yahoo authentication not configured. Run setup first.",
            "setup_command": "uv run python utils/setup_yahoo_auth.py"
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
                "message": "Failed to refresh token. May need to re-run setup.",
                "current_status": new_status,
                "setup_command": "uv run python utils/setup_yahoo_auth.py"
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
        logger.info("Run 'get_setup_instructions' tool for setup help.")
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