import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Data processing utilities for fantasy football analytics
    """
    
    def __init__(self):
        self.position_scoring = {
            "QB": {"passing_yards": 0.04, "passing_tds": 4, "rushing_yards": 0.1, "rushing_tds": 6, "interceptions": -2},
            "RB": {"rushing_yards": 0.1, "rushing_tds": 6, "receiving_yards": 0.1, "receiving_tds": 6, "receptions": 1},
            "WR": {"receiving_yards": 0.1, "receiving_tds": 6, "receptions": 1, "rushing_yards": 0.1, "rushing_tds": 6},
            "TE": {"receiving_yards": 0.1, "receiving_tds": 6, "receptions": 1},
            "K": {"field_goals": 3, "extra_points": 1},
            "DEF": {"defensive_tds": 6, "interceptions": 2, "fumble_recoveries": 2, "sacks": 1}
        }
    
    def prepare_projection_data(self, player_data: Dict, performance_data: List[Dict], 
                              league_settings: Optional[Dict] = None) -> Dict:
        """Prepare data for player projection model"""
        try:
            # Extract basic player info
            processed = {
                "player_id": player_data.get("player_id"),
                "position": player_data.get("position"),
                "age": self._calculate_age(player_data.get("birth_date")),
                "years_exp": player_data.get("years_exp", 0),
                "team": player_data.get("team"),
                "injury_status": player_data.get("injury_status", "Healthy")
            }
            
            # Process performance data
            if performance_data:
                df = pd.DataFrame(performance_data)
                
                # Calculate season averages
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                processed["season_averages"] = df[numeric_cols].mean().to_dict()
                
                # Calculate trends (last 4 weeks vs season)
                if len(df) >= 4:
                    recent_avg = df.tail(4)[numeric_cols].mean()
                    season_avg = df[numeric_cols].mean()
                    processed["trending"] = ((recent_avg - season_avg) / season_avg).fillna(0).to_dict()
                else:
                    processed["trending"] = {col: 0 for col in numeric_cols}
                
                # Fantasy points calculation
                processed["fantasy_points"] = self._calculate_fantasy_points(df, processed["position"])
                
                # Consistency metrics
                processed["consistency"] = {
                    "coefficient_of_variation": df[numeric_cols].std() / df[numeric_cols].mean(),
                    "boom_bust_ratio": self._calculate_boom_bust_ratio(df, processed["position"])
                }
            else:
                # Default values if no performance data
                processed.update({
                    "season_averages": {},
                    "trending": {},
                    "fantasy_points": [],
                    "consistency": {"coefficient_of_variation": {}, "boom_bust_ratio": 0}
                })
            
            # League-specific adjustments
            if league_settings:
                processed["scoring_settings"] = league_settings
                processed["adjusted_scoring"] = self._adjust_for_scoring(
                    processed["fantasy_points"], 
                    league_settings
                )
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preparing projection data: {str(e)}")
            return {}
    
    def prepare_waiver_data(self, team_data: Dict, available_players: List[Dict], 
                           league_data: Dict, position_needs: Optional[List[str]] = None) -> Dict:
        """Prepare data for waiver wire recommendations"""
        try:
            processed = {
                "team_id": team_data.get("team_id"),
                "current_roster": team_data.get("players", []),
                "league_settings": league_data.get("scoring_settings", {}),
                "league_size": len(league_data.get("rosters", [])),
                "position_needs": position_needs or []
            }
            
            # Analyze team strengths/weaknesses
            processed["position_analysis"] = self._analyze_team_positions(team_data)
            
            # Process available players
            processed["available_players"] = []
            for player_info in available_players:
                player_data = player_info["player_data"]
                
                # Filter by position needs if specified
                if position_needs and player_data.get("position") not in position_needs:
                    continue
                
                processed_player = {
                    "player_id": player_info["player_id"],
                    "position": player_data.get("position"),
                    "age": self._calculate_age(player_data.get("birth_date")),
                    "team": player_data.get("team"),
                    "injury_status": player_data.get("injury_status", "Healthy"),
                    "ownership_percentage": player_data.get("ownership_percentage", 0)
                }
                
                processed["available_players"].append(processed_player)
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preparing waiver data: {str(e)}")
            return {}
    
    def prepare_dynasty_data(self, player_data: Dict, historical_data: List[Dict], 
                           league_settings: Optional[Dict] = None) -> Dict:
        """Prepare data for dynasty value analysis"""
        try:
            processed = {
                "player_id": player_data.get("player_id"),
                "position": player_data.get("position"),
                "age": self._calculate_age(player_data.get("birth_date")),
                "years_exp": player_data.get("years_exp", 0),
                "draft_round": player_data.get("draft_round"),
                "draft_pick": player_data.get("draft_pick"),
                "college": player_data.get("college")
            }
            
            # Process historical performance
            if historical_data:
                df = pd.DataFrame(historical_data)
                
                # Career trajectory
                yearly_stats = df.groupby('season').agg({
                    'fantasy_points': 'sum',
                    'games_played': 'count'
                }).reset_index()
                
                processed["career_trajectory"] = yearly_stats.to_dict('records')
                
                # Peak performance indicators
                processed["peak_performance"] = {
                    "best_season": yearly_stats.loc[yearly_stats['fantasy_points'].idxmax()].to_dict(),
                    "consistency_score": yearly_stats['fantasy_points'].std() / yearly_stats['fantasy_points'].mean()
                }
                
                # Age curve analysis
                processed["age_curve"] = self._analyze_age_curve(df, processed["position"], processed["age"])
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preparing dynasty data: {str(e)}")
            return {}
    
    def _calculate_age(self, birth_date: str) -> int:
        """Calculate player age from birth date"""
        if not birth_date:
            return 25  # Default age
        
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 25
    
    def _calculate_fantasy_points(self, stats_df: pd.DataFrame, position: str) -> List[float]:
        """Calculate fantasy points for each game"""
        if position not in self.position_scoring:
            return []
        
        scoring = self.position_scoring[position]
        points = []
        
        for _, row in stats_df.iterrows():
            game_points = 0
            for stat, value in scoring.items():
                game_points += row.get(stat, 0) * value
            points.append(game_points)
        
        return points
    
    def _calculate_boom_bust_ratio(self, stats_df: pd.DataFrame, position: str) -> float:
        """Calculate boom/bust ratio"""
        fantasy_points = self._calculate_fantasy_points(stats_df, position)
        if not fantasy_points:
            return 0
        
        avg_points = np.mean(fantasy_points)
        boom_threshold = avg_points * 1.5
        bust_threshold = avg_points * 0.5
        
        booms = sum(1 for pts in fantasy_points if pts >= boom_threshold)
        busts = sum(1 for pts in fantasy_points if pts <= bust_threshold)
        
        return booms / max(busts, 1)
    
    def _adjust_for_scoring(self, fantasy_points: List[float], league_settings: Dict) -> List[float]:
        """Adjust fantasy points for league-specific scoring"""
        # Implementation would adjust based on league scoring settings
        # For now, return original points
        return fantasy_points
    
    def _analyze_team_positions(self, team_data: Dict) -> Dict:
        """Analyze team's positional strengths and weaknesses"""
        # Mock implementation - would analyze actual roster
        return {
            "QB": {"strength": "average", "depth": 2},
            "RB": {"strength": "weak", "depth": 1},
            "WR": {"strength": "strong", "depth": 4},
            "TE": {"strength": "weak", "depth": 1}
        }
    
    def _analyze_age_curve(self, historical_df: pd.DataFrame, position: str, current_age: int) -> Dict:
        """Analyze where player is on typical age curve"""
        # Position-specific age curves
        age_curves = {
            "QB": {"peak_start": 27, "peak_end": 33, "decline_start": 34},
            "RB": {"peak_start": 23, "peak_end": 27, "decline_start": 28},
            "WR": {"peak_start": 25, "peak_end": 29, "decline_start": 30},
            "TE": {"peak_start": 26, "peak_end": 30, "decline_start": 31}
        }
        
        curve = age_curves.get(position, age_curves["WR"])
        
        if current_age < curve["peak_start"]:
            phase = "ascending"
        elif current_age <= curve["peak_end"]:
            phase = "peak"
        elif current_age <= curve["decline_start"]:
            phase = "plateau"
        else:
            phase = "declining"
        
        return {
            "current_phase": phase,
            "years_to_peak": max(0, curve["peak_start"] - current_age),
            "years_of_peak_left": max(0, curve["peak_end"] - current_age)
        }
