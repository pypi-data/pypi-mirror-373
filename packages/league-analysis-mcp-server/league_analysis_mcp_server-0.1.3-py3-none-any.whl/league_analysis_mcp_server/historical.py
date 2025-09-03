"""
Historical Data Analysis Tools for League Analysis MCP Server
"""

import logging
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter
import statistics

from yfpy import YahooFantasySportsQuery
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_historical_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register historical analysis tools."""
    
    def get_yahoo_query(league_id: str, game_id: str, sport: str = "nfl") -> YahooFantasySportsQuery:
        """Create a Yahoo Fantasy Sports Query object for specific season."""
        auth_manager = app_state["auth_manager"]
        
        if not auth_manager.is_configured():
            raise ValueError("Yahoo authentication not configured. Run check_setup_status() to begin setup.")
        
        auth_credentials = auth_manager.get_auth_credentials()
        
        return YahooFantasySportsQuery(
            league_id=league_id,
            game_id=game_id,
            **auth_credentials
        )
    
    
    @mcp.tool()
    def get_historical_drafts(league_id: str, sport: str = "nfl", 
                             seasons: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get draft results from previous seasons.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: List of season years to analyze (default: last 3 years)
        
        Returns:
            Historical draft data across seasons
        """
        try:
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            if not seasons:
                # Default to last 3 available seasons
                available_seasons = list(game_ids.get(sport, {}).keys())
                seasons = sorted(available_seasons, reverse=True)[:3]
            
            drafts_by_season = {}
            
            for season in seasons:
                game_id = game_ids.get(sport, {}).get(season)
                if not game_id:
                    continue
                
                # Check cache first
                cached_data = cache_manager.get_historical_data(
                    sport, season, league_id, "draft_results"
                )
                
                if cached_data:
                    drafts_by_season[season] = cached_data
                    continue
                
                try:
                    yahoo_query = get_yahoo_query(league_id, game_id, sport)
                    draft_results = yahoo_query.get_league_draft_results()
                    
                    draft_picks = []
                    for pick in draft_results:
                        pick_data = {
                            "pick": getattr(pick, 'pick', 0),
                            "round": getattr(pick, 'round', 0),
                            "team_id": getattr(pick, 'team_key', '').split('.')[-1] if getattr(pick, 'team_key', '') else 'Unknown',
                            "player_name": getattr(pick, 'player_name', 'Unknown'),
                            "player_id": getattr(pick, 'player_id', 'Unknown'),
                            "position": getattr(pick, 'player_position', 'Unknown'),
                            "cost": getattr(pick, 'cost', 0)  # For auction drafts
                        }
                        draft_picks.append(pick_data)
                    
                    season_draft_data = {
                        "season": season,
                        "total_picks": len(draft_picks),
                        "draft_picks": draft_picks,
                        "is_auction": any(pick['cost'] > 0 for pick in draft_picks)
                    }
                    
                    # Cache the result
                    cache_manager.set_historical_data(
                        sport, season, league_id, "draft_results", season_draft_data
                    )
                    
                    drafts_by_season[season] = season_draft_data
                    
                except Exception as e:
                    logger.warning(f"Failed to get draft data for {season}: {e}")
                    continue
            
            return {
                "league_id": league_id,
                "sport": sport,
                "seasons_analyzed": list(drafts_by_season.keys()),
                "drafts": drafts_by_season,
                "total_seasons": len(drafts_by_season)
            }
            
        except Exception as e:
            logger.error(f"Error getting historical drafts: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def get_season_transactions(league_id: str, sport: str = "nfl", 
                              season: str = None) -> Dict[str, Any]:
        """
        Get all transactions for a specific season.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            season: Season year to analyze
        
        Returns:
            Transaction history for the season
        """
        try:
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            if not season:
                return {"error": "Season parameter is required"}
            
            game_id = game_ids.get(sport, {}).get(season)
            if not game_id:
                return {"error": f"No game_id found for {sport} {season}"}
            
            # Check cache first
            cached_data = cache_manager.get_historical_data(
                sport, season, league_id, "transactions"
            )
            
            if cached_data:
                return cached_data
            
            yahoo_query = get_yahoo_query(league_id, game_id, sport)
            transactions = yahoo_query.get_league_transactions()
            
            transaction_data = []
            for transaction in transactions:
                trans_data = {
                    "transaction_id": getattr(transaction, 'transaction_id', 'Unknown'),
                    "type": getattr(transaction, 'type', 'Unknown'),
                    "status": getattr(transaction, 'status', 'Unknown'),
                    "timestamp": getattr(transaction, 'timestamp', 'Unknown'),
                    "players": []
                }
                
                players = getattr(transaction, 'players', [])
                for player in players:
                    player_data = {
                        "player_id": getattr(player, 'player_id', 'Unknown'),
                        "name": getattr(player, 'name', {}).get('full', 'Unknown'),
                        "transaction_data": getattr(player, 'transaction_data', {})
                    }
                    trans_data["players"].append(player_data)
                
                transaction_data.append(trans_data)
            
            result = {
                "league_id": league_id,
                "sport": sport,
                "season": season,
                "transactions": transaction_data,
                "total_transactions": len(transaction_data),
                "transaction_types": list(set(t["type"] for t in transaction_data))
            }
            
            # Cache the result
            cache_manager.set_historical_data(
                sport, season, league_id, "transactions", result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting season transactions: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def analyze_manager_history(league_id: str, sport: str = "nfl", 
                               seasons: Optional[List[str]] = None,
                               team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze historical patterns for league managers.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: List of seasons to analyze (default: last 3 years)
            team_id: Specific team to analyze (optional)
        
        Returns:
            Manager performance patterns and analytics
        """
        try:
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            if not seasons:
                # Default to last 3 available seasons
                available_seasons = list(game_ids.get(sport, {}).keys())
                seasons = sorted(available_seasons, reverse=True)[:3]
            
            manager_stats = defaultdict(lambda: {
                "seasons": [],
                "total_wins": 0,
                "total_losses": 0,
                "total_points": 0.0,
                "avg_rank": [],
                "championships": 0,
                "playoff_appearances": 0
            })
            
            for season in seasons:
                game_id = game_ids.get(sport, {}).get(season)
                if not game_id:
                    continue
                
                # Check cache for standings
                cached_standings = cache_manager.get_historical_data(
                    sport, season, league_id, "standings"
                )
                
                if not cached_standings:
                    try:
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
                                "points_for": getattr(team, 'points_for', 0.0)
                            }
                            teams_data.append(team_data)
                        
                        cached_standings = {
                            "teams": teams_data,
                            "season": season
                        }
                        
                        cache_manager.set_historical_data(
                            sport, season, league_id, "standings", cached_standings
                        )
                        
                    except Exception as e:
                        logger.warning(f"Failed to get standings for {season}: {e}")
                        continue
                
                # Process standings data
                for team in cached_standings["teams"]:
                    tid = team["team_id"]
                    if team_id and tid != team_id:
                        continue
                    
                    manager_stats[tid]["seasons"].append(season)
                    manager_stats[tid]["total_wins"] += team["wins"]
                    manager_stats[tid]["total_losses"] += team["losses"]
                    manager_stats[tid]["total_points"] += team["points_for"]
                    manager_stats[tid]["avg_rank"].append(team["rank"])
                    
                    # Check for championships and playoffs (assuming top 6 make playoffs)
                    if team["rank"] == 1:
                        manager_stats[tid]["championships"] += 1
                    if team["rank"] <= 6:  # Configurable playoff threshold
                        manager_stats[tid]["playoff_appearances"] += 1
            
            # Calculate averages and patterns
            analysis_results = {}
            for tid, stats in manager_stats.items():
                seasons_played = len(stats["seasons"])
                if seasons_played == 0:
                    continue
                
                analysis_results[tid] = {
                    "team_id": tid,
                    "seasons_analyzed": stats["seasons"],
                    "seasons_played": seasons_played,
                    "total_wins": stats["total_wins"],
                    "total_losses": stats["total_losses"],
                    "win_percentage": stats["total_wins"] / (stats["total_wins"] + stats["total_losses"]) if (stats["total_wins"] + stats["total_losses"]) > 0 else 0,
                    "avg_points_per_season": stats["total_points"] / seasons_played,
                    "avg_rank": statistics.mean(stats["avg_rank"]) if stats["avg_rank"] else 0,
                    "best_rank": min(stats["avg_rank"]) if stats["avg_rank"] else 0,
                    "worst_rank": max(stats["avg_rank"]) if stats["avg_rank"] else 0,
                    "championships": stats["championships"],
                    "championship_rate": stats["championships"] / seasons_played,
                    "playoff_appearances": stats["playoff_appearances"],
                    "playoff_rate": stats["playoff_appearances"] / seasons_played,
                    "consistency_score": 1 - (statistics.stdev(stats["avg_rank"]) / statistics.mean(stats["avg_rank"])) if len(stats["avg_rank"]) > 1 and statistics.mean(stats["avg_rank"]) > 0 else 0
                }
            
            return {
                "league_id": league_id,
                "sport": sport,
                "seasons_analyzed": seasons,
                "team_filter": team_id,
                "manager_analysis": analysis_results,
                "total_managers": len(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing manager history: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def compare_seasons(league_id: str, sport: str = "nfl", 
                       seasons: List[str] = None) -> Dict[str, Any]:
        """
        Compare league performance across multiple seasons.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: List of seasons to compare
        
        Returns:
            Comparative analysis across seasons
        """
        try:
            if not seasons or len(seasons) < 2:
                return {"error": "At least 2 seasons required for comparison"}
            
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            season_comparisons = {}
            
            for season in seasons:
                game_id = game_ids.get(sport, {}).get(season)
                if not game_id:
                    continue
                
                # Get cached standings
                cached_standings = cache_manager.get_historical_data(
                    sport, season, league_id, "standings"
                )
                
                if cached_standings:
                    teams = cached_standings["teams"]
                    
                    season_stats = {
                        "total_teams": len(teams),
                        "avg_wins": statistics.mean([t["wins"] for t in teams]),
                        "avg_points": statistics.mean([t["points_for"] for t in teams]),
                        "highest_score": max([t["points_for"] for t in teams]),
                        "lowest_score": min([t["points_for"] for t in teams]),
                        "score_variance": statistics.variance([t["points_for"] for t in teams]) if len(teams) > 1 else 0,
                        "competitive_balance": statistics.stdev([t["wins"] for t in teams]) if len(teams) > 1 else 0
                    }
                    
                    season_comparisons[season] = season_stats
            
            # Calculate trends
            if len(season_comparisons) >= 2:
                sorted_seasons = sorted(season_comparisons.keys())
                
                trends = {
                    "scoring_trend": "increasing" if season_comparisons[sorted_seasons[-1]]["avg_points"] > season_comparisons[sorted_seasons[0]]["avg_points"] else "decreasing",
                    "competition_trend": "more_competitive" if season_comparisons[sorted_seasons[-1]]["competitive_balance"] < season_comparisons[sorted_seasons[0]]["competitive_balance"] else "less_competitive"
                }
            else:
                trends = {}
            
            return {
                "league_id": league_id,
                "sport": sport,
                "seasons_compared": list(season_comparisons.keys()),
                "season_statistics": season_comparisons,
                "trends": trends,
                "comparison_complete": len(season_comparisons) == len(seasons)
            }
            
        except Exception as e:
            logger.error(f"Error comparing seasons: {e}")
            return {"error": str(e)}