"""
Advanced Analytics and Pattern Recognition Tools for League Analysis MCP Server
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import json

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_analytics_tools(mcp: FastMCP, app_state: Dict[str, Any]):
    """Register advanced analytics and pattern recognition tools."""
    
    @mcp.tool()
    def analyze_draft_strategy(league_id: str, sport: str = "nfl", 
                              seasons: Optional[List[str]] = None,
                              team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze draft strategies and identify manager tendencies.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: List of seasons to analyze (default: last 3 years)
            team_id: Specific team to analyze (optional)
        
        Returns:
            Draft strategy analysis and patterns
        """
        try:
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            if not seasons:
                available_seasons = list(game_ids.get(sport, {}).keys())
                seasons = sorted(available_seasons, reverse=True)[:3]
            
            draft_strategies = defaultdict(lambda: {
                "position_preferences": defaultdict(list),
                "round_strategies": defaultdict(list),
                "auction_spending": [],
                "early_round_positions": [],
                "late_round_positions": [],
                "total_drafts": 0
            })
            
            for season in seasons:
                # Get cached draft data
                cached_draft = cache_manager.get_historical_data(
                    sport, season, league_id, "draft_results"
                )
                
                if not cached_draft:
                    continue
                
                draft_picks = cached_draft.get("draft_picks", [])
                is_auction = cached_draft.get("is_auction", False)
                
                for pick in draft_picks:
                    tid = pick.get("team_id", "Unknown")
                    if team_id and tid != team_id:
                        continue
                    
                    position = pick.get("position", "Unknown")
                    round_num = pick.get("round", 0)
                    cost = pick.get("cost", 0)
                    
                    draft_strategies[tid]["total_drafts"] += 1
                    draft_strategies[tid]["position_preferences"][position].append(round_num)
                    draft_strategies[tid]["round_strategies"][round_num].append(position)
                    
                    if is_auction and cost > 0:
                        draft_strategies[tid]["auction_spending"].append({
                            "player": pick.get("player_name", "Unknown"),
                            "position": position,
                            "cost": cost
                        })
                    
                    # Categorize early vs late round preferences
                    if round_num <= 3:
                        draft_strategies[tid]["early_round_positions"].append(position)
                    elif round_num >= 10:
                        draft_strategies[tid]["late_round_positions"].append(position)
            
            # Analyze patterns
            strategy_analysis = {}
            for tid, data in draft_strategies.items():
                if data["total_drafts"] == 0:
                    continue
                
                # Position preference analysis
                position_stats = {}
                for pos, rounds in data["position_preferences"].items():
                    position_stats[pos] = {
                        "times_drafted": len(rounds),
                        "avg_round": statistics.mean(rounds),
                        "earliest_round": min(rounds),
                        "latest_round": max(rounds)
                    }
                
                # Early round strategy
                early_positions = Counter(data["early_round_positions"])
                late_positions = Counter(data["late_round_positions"])
                
                # Draft philosophy classification
                rb_early = early_positions.get("RB", 0)
                wr_early = early_positions.get("WR", 0)
                
                if rb_early > wr_early * 1.5:
                    strategy_type = "RB-Heavy"
                elif wr_early > rb_early * 1.5:
                    strategy_type = "Zero-RB"
                else:
                    strategy_type = "Balanced"
                
                strategy_analysis[tid] = {
                    "team_id": tid,
                    "seasons_analyzed": len([s for s in seasons if any(p.get("team_id") == tid for s_data in [cache_manager.get_historical_data(sport, s, league_id, "draft_results")] if s_data for p in s_data.get("draft_picks", []))]),
                    "total_picks_analyzed": data["total_drafts"],
                    "position_preferences": position_stats,
                    "early_round_focus": dict(early_positions.most_common(3)),
                    "late_round_focus": dict(late_positions.most_common(3)),
                    "draft_strategy_type": strategy_type,
                    "auction_data": {
                        "total_auction_picks": len(data["auction_spending"]),
                        "avg_cost_per_pick": statistics.mean([p["cost"] for p in data["auction_spending"]]) if data["auction_spending"] else 0,
                        "highest_cost_pick": max(data["auction_spending"], key=lambda x: x["cost"]) if data["auction_spending"] else None
                    } if data["auction_spending"] else None
                }
            
            return {
                "league_id": league_id,
                "sport": sport,
                "seasons_analyzed": seasons,
                "team_filter": team_id,
                "draft_strategies": strategy_analysis,
                "total_teams_analyzed": len(strategy_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing draft strategy: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def predict_trade_likelihood(league_id: str, sport: str = "nfl",
                                team1_id: str = None, team2_id: str = None,
                                seasons: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Predict trade likelihood between managers based on historical patterns.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            team1_id: First team ID (optional)
            team2_id: Second team ID (optional)
            seasons: Seasons to analyze for patterns (default: last 3 years)
        
        Returns:
            Trade likelihood predictions and historical trade patterns
        """
        try:
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            if not seasons:
                available_seasons = list(game_ids.get(sport, {}).keys())
                seasons = sorted(available_seasons, reverse=True)[:3]
            
            trade_matrix = defaultdict(lambda: defaultdict(int))
            trade_details = defaultdict(list)
            
            for season in seasons:
                # Get cached transaction data
                cached_transactions = cache_manager.get_historical_data(
                    sport, season, league_id, "transactions"
                )
                
                if not cached_transactions:
                    continue
                
                transactions = cached_transactions.get("transactions", [])
                
                for transaction in transactions:
                    if transaction.get("type") != "trade":
                        continue
                    
                    # Extract team IDs from trade (simplified - would need more complex parsing in reality)
                    players = transaction.get("players", [])
                    if len(players) >= 2:
                        # This is a simplified approach - real implementation would need to parse
                        # the transaction structure more carefully
                        trade_teams = set()
                        for player in players:
                            transaction_data = player.get("transaction_data", {})
                            # Extract team IDs from transaction data
                            # This would need actual YFPY transaction structure analysis
                        
                        if len(trade_teams) == 2:
                            t1, t2 = list(trade_teams)
                            trade_matrix[t1][t2] += 1
                            trade_matrix[t2][t1] += 1
                            trade_details[f"{t1}-{t2}"].append({
                                "season": season,
                                "players": [p.get("name", "Unknown") for p in players],
                                "timestamp": transaction.get("timestamp")
                            })
            
            # Calculate trade probabilities
            if team1_id and team2_id:
                # Specific pair analysis
                trades_between = trade_matrix[team1_id][team2_id]
                total_seasons = len(seasons)
                
                prediction = {
                    "team1_id": team1_id,
                    "team2_id": team2_id,
                    "historical_trades": trades_between,
                    "seasons_analyzed": total_seasons,
                    "trades_per_season": trades_between / total_seasons if total_seasons > 0 else 0,
                    "likelihood_score": min(trades_between / max(total_seasons, 1), 1.0),
                    "trade_history": trade_details.get(f"{team1_id}-{team2_id}", []),
                    "recommendation": "High" if trades_between >= 2 else "Medium" if trades_between >= 1 else "Low"
                }
            else:
                # League-wide analysis
                all_trade_pairs = {}
                for t1, partners in trade_matrix.items():
                    for t2, count in partners.items():
                        if t1 < t2:  # Avoid duplicates
                            pair_key = f"{t1}-{t2}"
                            all_trade_pairs[pair_key] = {
                                "team1_id": t1,
                                "team2_id": t2,
                                "total_trades": count,
                                "trades_per_season": count / len(seasons) if seasons else 0,
                                "likelihood_score": min(count / max(len(seasons), 1), 1.0)
                            }
                
                prediction = {
                    "league_id": league_id,
                    "sport": sport,
                    "seasons_analyzed": seasons,
                    "all_trade_pairs": all_trade_pairs,
                    "most_active_pairs": sorted(all_trade_pairs.items(), 
                                              key=lambda x: x[1]["total_trades"], reverse=True)[:5],
                    "total_unique_pairs": len(all_trade_pairs)
                }
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting trade likelihood: {e}")
            return {"error": str(e)}
    
    
    @mcp.tool()
    def evaluate_manager_skill(league_id: str, sport: str = "nfl",
                              seasons: Optional[List[str]] = None,
                              team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate manager skill based on multiple performance metrics.
        
        Args:
            league_id: Yahoo league ID
            sport: Sport code (nfl, nba, mlb, nhl)
            seasons: Seasons to analyze (default: last 3 years)
            team_id: Specific team to evaluate (optional)
        
        Returns:
            Comprehensive manager skill evaluation
        """
        try:
            cache_manager = app_state["cache_manager"]
            game_ids = app_state["game_ids"]
            
            if not seasons:
                available_seasons = list(game_ids.get(sport, {}).keys())
                seasons = sorted(available_seasons, reverse=True)[:3]
            
            manager_metrics = defaultdict(lambda: {
                "wins": [],
                "points_for": [],
                "points_against": [],
                "ranks": [],
                "playoff_appearances": 0,
                "championships": 0,
                "seasons_played": 0
            })
            
            # Collect performance data
            for season in seasons:
                cached_standings = cache_manager.get_historical_data(
                    sport, season, league_id, "standings"
                )
                
                if not cached_standings:
                    continue
                
                teams = cached_standings.get("teams", [])
                for team in teams:
                    tid = team.get("team_id")
                    if team_id and tid != team_id:
                        continue
                    
                    manager_metrics[tid]["wins"].append(team.get("wins", 0))
                    manager_metrics[tid]["points_for"].append(team.get("points_for", 0))
                    manager_metrics[tid]["points_against"].append(team.get("points_against", 0))
                    manager_metrics[tid]["ranks"].append(team.get("rank", 999))
                    manager_metrics[tid]["seasons_played"] += 1
                    
                    if team.get("rank", 999) == 1:
                        manager_metrics[tid]["championships"] += 1
                    if team.get("rank", 999) <= 6:  # Assuming 6 playoff teams
                        manager_metrics[tid]["playoff_appearances"] += 1
            
            # Calculate skill scores
            skill_evaluations = {}
            for tid, metrics in manager_metrics.items():
                if metrics["seasons_played"] == 0:
                    continue
                
                seasons_played = metrics["seasons_played"]
                
                # Core metrics
                avg_wins = statistics.mean(metrics["wins"])
                avg_points = statistics.mean(metrics["points_for"])
                avg_rank = statistics.mean(metrics["ranks"])
                
                # Advanced metrics
                win_consistency = 1 - (statistics.stdev(metrics["wins"]) / avg_wins) if avg_wins > 0 and len(metrics["wins"]) > 1 else 0
                scoring_consistency = 1 - (statistics.stdev(metrics["points_for"]) / avg_points) if avg_points > 0 and len(metrics["points_for"]) > 1 else 0
                rank_consistency = 1 - (statistics.stdev(metrics["ranks"]) / avg_rank) if avg_rank > 0 and len(metrics["ranks"]) > 1 else 0
                
                # Skill components (0-100 scale)
                win_rate_score = min((avg_wins / 13) * 100, 100)  # Assuming ~13 games per season
                playoff_rate_score = (metrics["playoff_appearances"] / seasons_played) * 100
                championship_rate_score = (metrics["championships"] / seasons_played) * 100
                consistency_score = (win_consistency + scoring_consistency + rank_consistency) / 3 * 100
                
                # Overall skill score (weighted average)
                overall_skill = (
                    win_rate_score * 0.3 +
                    playoff_rate_score * 0.25 +
                    championship_rate_score * 0.25 +
                    consistency_score * 0.2
                )
                
                # Skill tier classification
                if overall_skill >= 80:
                    skill_tier = "Elite"
                elif overall_skill >= 65:
                    skill_tier = "Above Average"
                elif overall_skill >= 50:
                    skill_tier = "Average"
                elif overall_skill >= 35:
                    skill_tier = "Below Average"
                else:
                    skill_tier = "Needs Improvement"
                
                skill_evaluations[tid] = {
                    "team_id": tid,
                    "seasons_analyzed": seasons_played,
                    "overall_skill_score": round(overall_skill, 2),
                    "skill_tier": skill_tier,
                    "component_scores": {
                        "win_rate": round(win_rate_score, 2),
                        "playoff_rate": round(playoff_rate_score, 2),
                        "championship_rate": round(championship_rate_score, 2),
                        "consistency": round(consistency_score, 2)
                    },
                    "performance_metrics": {
                        "avg_wins": round(avg_wins, 2),
                        "avg_points": round(avg_points, 2),
                        "avg_rank": round(avg_rank, 2),
                        "championships": metrics["championships"],
                        "playoff_appearances": metrics["playoff_appearances"]
                    },
                    "strengths": [],
                    "areas_for_improvement": []
                }
                
                # Identify strengths and weaknesses
                scores = skill_evaluations[tid]["component_scores"]
                if scores["win_rate"] >= 70:
                    skill_evaluations[tid]["strengths"].append("Consistent regular season performance")
                if scores["playoff_rate"] >= 75:
                    skill_evaluations[tid]["strengths"].append("Strong playoff qualifier")
                if scores["championship_rate"] >= 33:
                    skill_evaluations[tid]["strengths"].append("Championship-level manager")
                if scores["consistency"] >= 70:
                    skill_evaluations[tid]["strengths"].append("Very consistent performance")
                
                if scores["win_rate"] < 40:
                    skill_evaluations[tid]["areas_for_improvement"].append("Regular season record")
                if scores["playoff_rate"] < 50:
                    skill_evaluations[tid]["areas_for_improvement"].append("Playoff qualification")
                if scores["consistency"] < 40:
                    skill_evaluations[tid]["areas_for_improvement"].append("Performance consistency")
            
            return {
                "league_id": league_id,
                "sport": sport,
                "seasons_analyzed": seasons,
                "team_filter": team_id,
                "skill_evaluations": skill_evaluations,
                "league_average_skill": statistics.mean([e["overall_skill_score"] for e in skill_evaluations.values()]) if skill_evaluations else 0,
                "total_managers_evaluated": len(skill_evaluations)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating manager skill: {e}")
            return {"error": str(e)}