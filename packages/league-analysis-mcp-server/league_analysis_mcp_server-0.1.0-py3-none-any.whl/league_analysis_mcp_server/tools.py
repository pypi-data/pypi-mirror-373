"""
MCP Tools for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP
from .historical import register_historical_tools
from .analytics import register_analytics_tools

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register all MCP tools."""
    
    def get_yahoo_query(league_id: str, game_id: Optional[str] = None, sport: str = "nfl") -> YahooFantasySportsQuery:
        """Create a Yahoo Fantasy Sports Query object."""
        auth_manager = app_state["auth_manager"]
        cache_manager = app_state["cache_manager"]
        
        if not auth_manager.is_configured():
            raise ValueError("Yahoo authentication not configured. Run get_setup_instructions for help.")
        
        auth_credentials = auth_manager.get_auth_credentials()
        
        # Use game_id if provided, otherwise use current season
        if game_id:
            query_params = {**auth_credentials, 'game_id': game_id}
        else:
            query_params = {**auth_credentials, 'game_code': sport}
        
        return YahooFantasySportsQuery(
            league_id=league_id,
            **query_params
        )
    
    
    @mcp.tool()
    def get_league_info(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get basic league information and settings.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional, uses current if not provided)
        
        Returns:
            League information and settings
        """
        try:
            cache_manager = app_state["cache_manager"]
            
            # Check cache first
            if season:
                cached_data = cache_manager.get_historical_data(sport, season, league_id, "league_info")
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "league_info")
            
            if cached_data:
                return cached_data
            
            # Get game_id for specific season if provided
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}
            
            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            league = yahoo_query.get_league()
            
            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "name": getattr(league, 'name', 'Unknown'),
                "season_type": getattr(league, 'season', 'Unknown'),
                "num_teams": getattr(league, 'num_teams', 0),
                "scoring_type": getattr(league, 'scoring_type', 'Unknown'),
                "league_type": getattr(league, 'league_type', 'Unknown'),
                "renew": getattr(league, 'renew', 'Unknown'),
                "renewed": getattr(league, 'renewed', 'Unknown'),
                "start_week": getattr(league, 'start_week', 1),
                "current_week": getattr(league, 'current_week', 1),
                "end_week": getattr(league, 'end_week', 17)
            }
            
            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "league_info", result)
            else:
                cache_manager.set_current_data(sport, league_id, "league_info", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting league info: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def get_standings(league_id: str, sport: str = "nfl", season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current league standings.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)
        
        Returns:
            League standings information
        """
        try:
            cache_manager = app_state["cache_manager"]
            
            # Check cache first
            if season:
                cached_data = cache_manager.get_historical_data(sport, season, league_id, "standings")
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "standings")
            
            if cached_data:
                return cached_data
            
            # Get game_id for specific season if provided
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}
            
            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            standings = yahoo_query.get_league_standings()
            
            teams_data = []
            for team in standings:
                team_data = {
                    "team_id": getattr(team, 'team_id', 'Unknown'),
                    "name": getattr(team, 'name', 'Unknown'),
                    "rank": getattr(team, 'rank', 0),
                    "wins": getattr(team, 'wins', 0),
                    "losses": getattr(team, 'losses', 0),
                    "ties": getattr(team, 'ties', 0),
                    "win_percentage": getattr(team, 'win_percentage', 0.0),
                    "points_for": getattr(team, 'points_for', 0.0),
                    "points_against": getattr(team, 'points_against', 0.0)
                }
                teams_data.append(team_data)
            
            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "teams": teams_data,
                "total_teams": len(teams_data)
            }
            
            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "standings", result)
            else:
                cache_manager.set_current_data(sport, league_id, "standings", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting standings: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def get_team_roster(league_id: str, team_id: str, sport: str = "nfl", 
                       season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get roster for a specific team.
        
        Args:
            league_id: Yahoo league ID
            team_id: Team ID within the league
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Specific season year (optional)
        
        Returns:
            Team roster information
        """
        try:
            cache_manager = app_state["cache_manager"]
            
            # Check cache first
            cache_key_params = {"team_id": team_id}
            if season:
                cached_data = cache_manager.get_historical_data(sport, season, league_id, "team_roster", **cache_key_params)
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "team_roster", **cache_key_params)
            
            if cached_data:
                return cached_data
            
            # Get game_id for specific season if provided
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}
            
            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            roster = yahoo_query.get_team_roster_by_week(team_id, 1)  # Default to week 1
            
            players_data = []
            for player in roster:
                player_data = {
                    "player_id": getattr(player, 'player_id', 'Unknown'),
                    "name": getattr(player, 'name', {}).get('full', 'Unknown'),
                    "position_type": getattr(player, 'position_type', 'Unknown'),
                    "eligible_positions": getattr(player, 'eligible_positions', []),
                    "selected_position": getattr(player, 'selected_position', {}),
                    "team_abbr": getattr(player, 'editorial_team_abbr', 'Unknown')
                }
                players_data.append(player_data)
            
            result = {
                "league_id": league_id,
                "team_id": team_id,
                "sport": sport,
                "season": season or "current",
                "roster": players_data,
                "roster_size": len(players_data)
            }
            
            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "team_roster", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "team_roster", result, **cache_key_params)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting team roster: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def get_matchups(league_id: str, sport: str = "nfl", week: Optional[int] = None,
                    season: Optional[str] = None) -> Dict[str, Any]:
        """
        Get matchups for a specific week.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            week: Week number (optional, uses current week if not provided)
            season: Specific season year (optional)
        
        Returns:
            Matchup information for the specified week
        """
        try:
            cache_manager = app_state["cache_manager"]
            
            # Check cache first
            cache_key_params = {"week": week} if week else {}
            if season:
                cached_data = cache_manager.get_historical_data(sport, season, league_id, "matchups", **cache_key_params)
            else:
                cached_data = cache_manager.get_current_data(sport, league_id, "matchups", **cache_key_params)
            
            if cached_data:
                return cached_data
            
            # Get game_id for specific season if provided
            game_id = None
            if season:
                game_id = app_state["game_ids"].get(sport, {}).get(season)
                if not game_id:
                    return {"error": f"No game_id found for {sport} {season}"}
            
            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            
            # Get current week if not provided
            if not week:
                league = yahoo_query.get_league()
                week = getattr(league, 'current_week', 1)
            
            matchups = yahoo_query.get_league_matchups_by_week(week)
            
            matchup_data = []
            for matchup in matchups:
                matchup_info = {
                    "week": week,
                    "is_playoffs": getattr(matchup, 'is_playoffs', False),
                    "is_consolation": getattr(matchup, 'is_consolation', False),
                    "teams": []
                }
                
                teams = getattr(matchup, 'teams', [])
                for team in teams:
                    team_info = {
                        "team_id": getattr(team, 'team_id', 'Unknown'),
                        "name": getattr(team, 'name', 'Unknown'),
                        "points": getattr(team, 'points', 0.0),
                        "projected_points": getattr(team, 'projected_points', 0.0)
                    }
                    matchup_info["teams"].append(team_info)
                
                matchup_data.append(matchup_info)
            
            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season or "current",
                "week": week,
                "matchups": matchup_data,
                "total_matchups": len(matchup_data)
            }
            
            # Cache the result
            if season:
                cache_manager.set_historical_data(sport, season, league_id, "matchups", result, **cache_key_params)
            else:
                cache_manager.set_current_data(sport, league_id, "matchups", result, **cache_key_params)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting matchups: {e}")
            return {"error": str(e)}
    
    
    # Register historical analysis tools
    register_historical_tools(mcp, app_state)
    
    # Register analytics tools
    register_analytics_tools(mcp, app_state)