"""
MCP Resources for Yahoo Fantasy Sports API
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


def register_resources(mcp, app_state: Dict[str, Any]):
    """Register all MCP resources (read-only data endpoints)."""
    
    @mcp.resource("league_overview/{sport}/{league_id}")
    def get_league_overview(sport: str, league_id: str) -> str:
        """
        Provides a comprehensive overview of league information.
        """
        try:
            season = None  # Could be extended to support season parameter
            
            config = app_state["config"]
            if sport not in config["supported_sports"]:
                return f"Error: Unsupported sport '{sport}'. Supported: {', '.join(config['supported_sports'])}"
            
            # This would typically fetch data, but for demonstration we'll return a template
            overview = f"""
# League Overview: {sport.upper()} League {league_id}
Season: {season or 'Current'}

## Quick Stats
- Sport: {sport.upper()}
- League ID: {league_id}
- Season: {season or 'Current'}

## Available Data
- League settings and rules
- Current standings
- Team rosters
- Recent matchups
- Transaction history
- Historical analysis (if multiple seasons available)

## Next Steps
Use the available tools to dive deeper into specific aspects:
- get_league_info: Basic league information
- get_standings: Current standings
- get_team_roster: Individual team rosters
- get_matchups: Weekly matchup information
- analyze_manager_history: Historical performance patterns
"""
            return overview
            
        except Exception as e:
            logger.error(f"Error in league_overview resource: {e}")
            return f"Error: {str(e)}"
    
    
    @mcp.resource("current_week/{sport}/{league_id}")
    def get_current_week_info(sport: str, league_id: str) -> str:
        """
        Provides current week matchup and league activity.
        """
        try:
            
            current_week = f"""
# Current Week Activity: {sport.upper()} League {league_id}

## This Week's Focus
- Active matchups and projections
- Injury reports affecting lineups
- Waiver wire activity
- Trade deadline considerations

## Key Metrics to Monitor
- Projected vs actual points
- Player performance trends
- Lineup optimization opportunities
- Competitive balance indicators

Use get_matchups tool with current week for detailed matchup analysis.
"""
            return current_week
            
        except Exception as e:
            logger.error(f"Error in current_week resource: {e}")
            return f"Error: {str(e)}"
    
    
    @mcp.resource("league_history/{sport}/{league_id}")
    def get_league_history_summary(sport: str, league_id: str) -> str:
        """
        Provides multi-season league history and trends.
        """
        try:
            seasons_param = "3"  # Default to last 3 seasons
            
            game_ids = app_state["game_ids"]
            available_seasons = list(game_ids.get(sport, {}).keys())
            
            history_summary = f"""
# League History: {sport.upper()} League {league_id}

## Available Historical Data
- Total seasons with data: {len(available_seasons)}
- Seasons available: {', '.join(sorted(available_seasons, reverse=True)[:10])}...
- Analysis capabilities: Draft patterns, manager tendencies, championship history

## Historical Analysis Tools Available
- get_historical_drafts: Draft results across seasons
- analyze_manager_history: Manager performance patterns  
- compare_seasons: Season-to-season comparisons
- get_season_transactions: Transaction history by season

## Key Historical Insights
Use the historical analysis tools to uncover:
- Which managers consistently perform well
- Draft strategy evolution over time
- Trading patterns between specific managers
- Championship and playoff trends
- League competitive balance changes

## Recommended Analysis
1. Start with analyze_manager_history for overall patterns
2. Use get_historical_drafts to see draft evolution
3. Compare recent seasons with compare_seasons
4. Dive into specific season transactions as needed
"""
            return history_summary
            
        except Exception as e:
            logger.error(f"Error in league_history resource: {e}")
            return f"Error: {str(e)}"
    
    
    @mcp.resource("manager_profiles/{sport}/{league_id}")
    def get_manager_profiles_summary(sport: str, league_id: str) -> str:
        """
        Provides manager profiling and tendency analysis.
        """
        try:
            team_id = None  # Could be extended to support specific team analysis
            
            profile_summary = f"""
# Manager Profiles: {sport.upper()} League {league_id}
{f"Focus: Team {team_id}" if team_id else "All Managers"}

## Manager Analysis Capabilities

### Performance Metrics
- Win/loss records across seasons
- Average finish position
- Playoff appearance rate
- Championship frequency
- Consistency scoring

### Behavioral Patterns  
- Draft position preferences
- Trading frequency and partners
- Waiver wire activity levels
- Lineup management effectiveness

### Predictive Insights
- Success trajectory trends
- Risk tolerance indicators
- Strategic tendencies
- Head-to-head matchup advantages

## Available Analysis Tools
- analyze_manager_history: Core performance metrics
- get_historical_drafts: Draft strategy patterns
- get_season_transactions: Trading behavior analysis

## Manager Categories
Based on historical analysis, managers typically fall into:
- **Champions**: Consistent top performers
- **Contenders**: Regular playoff participants  
- **Wildcards**: Unpredictable season outcomes
- **Rebuilders**: Focus on future seasons
- **Casual**: Less active management style

Use analyze_manager_history to get specific data for classification.
"""
            return profile_summary
            
        except Exception as e:
            logger.error(f"Error in manager_profiles resource: {e}")
            return f"Error: {str(e)}"