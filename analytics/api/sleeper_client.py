import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SleeperAPIClient:
    """
    Async client for Sleeper Fantasy Football API
    """
    
    def __init__(self):
        self.base_url = "https://api.sleeper.app/v1"
        self.session = None
        self._players_cache = {}
        self._cache_expiry = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make async GET request to Sleeper API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {url}")
                    return {}
        except Exception as e:
            logger.error(f"Error making API request to {url}: {str(e)}")
            return {}
    
    async def get_user(self, user_id: str) -> Dict:
        """Get user information"""
        return await self._get(f"user/{user_id}")
    
    async def get_user_leagues(self, user_id: str, sport: str = "nfl", season: str = "2024") -> List[Dict]:
        """Get user's leagues for a season"""
        return await self._get(f"user/{user_id}/leagues/{sport}/{season}")
    
    async def get_league(self, league_id: str) -> Dict:
        """Get league information"""
        return await self._get(f"league/{league_id}")
    
    async def get_league_rosters(self, league_id: str) -> List[Dict]:
        """Get all rosters in a league"""
        return await self._get(f"league/{league_id}/rosters")
    
    async def get_league_users(self, league_id: str) -> List[Dict]:
        """Get all users in a league"""
        return await self._get(f"league/{league_id}/users")
    
    async def get_league_matchups(self, league_id: str, week: int) -> List[Dict]:
        """Get matchups for a specific week"""
        return await self._get(f"league/{league_id}/matchups/{week}")
    
    async def get_league_transactions(self, league_id: str, round_num: int = 1) -> List[Dict]:
        """Get league transactions"""
        return await self._get(f"league/{league_id}/transactions/{round_num}")
    
    async def get_all_players(self, sport: str = "nfl") -> Dict:
        """Get all NFL players (cached)"""
        cache_key = f"all_players_{sport}"
        
        # Check cache first
        if cache_key in self._players_cache:
            cache_time = self._cache_expiry.get(cache_key)
            if cache_time and datetime.now() < cache_time:
                return self._players_cache[cache_key]
        
        # Fetch from API
        players = await self._get(f"players/{sport}")
        
        # Cache for 1 hour
        self._players_cache[cache_key] = players
        self._cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
        
        return players
    
    async def get_player(self, player_id: str) -> Dict:
        """Get specific player information"""
        all_players = await self.get_all_players()
        return all_players.get(player_id, {})
    
    async def get_nfl_state(self) -> Dict:
        """Get current NFL state (week, season, etc.)"""
        return await self._get("state/nfl")
    
    async def get_trending_players(self, sport: str = "nfl", add_drop: str = "add", 
                                 hours: int = 24, limit: int = 25) -> List[Dict]:
        """Get trending players"""
        params = {
            "add_drop": add_drop,
            "hours": hours,
            "limit": limit
        }
        return await self._get(f"players/{sport}/trending", params)
    
    async def get_player_stats(self, player_id: str, weeks: int = 8, season: str = "2024") -> List[Dict]:
        """Get player stats for recent weeks"""
        try:
            nfl_state = await self.get_nfl_state()
            current_week = nfl_state.get("week", 1)
            
            stats = []
            start_week = max(1, current_week - weeks)
            
            for week in range(start_week, current_week + 1):
                week_stats = await self._get(f"stats/nfl/regular/{season}/{week}")
                player_stats = week_stats.get(player_id, {})
                if player_stats:
                    player_stats["week"] = week
                    player_stats["season"] = season
                    stats.append(player_stats)
            
            return stats
        except Exception as e:
            logger.error(f"Error fetching player stats for {player_id}: {str(e)}")
            return []
    
    async def get_player_career_stats(self, player_id: str) -> List[Dict]:
        """Get player career statistics"""
        try:
            career_stats = []
            current_year = datetime.now().year
            
            # Get last 3 seasons
            for year in range(current_year - 2, current_year + 1):
                season_stats = []
                for week in range(1, 19):  # Regular season weeks
                    week_stats = await self._get(f"stats/nfl/regular/{year}/{week}")
                    player_stats = week_stats.get(player_id, {})
                    if player_stats:
                        player_stats["week"] = week
                        player_stats["season"] = year
                        season_stats.append(player_stats)
                
                if season_stats:
                    career_stats.extend(season_stats)
            
            return career_stats
        except Exception as e:
            logger.error(f"Error fetching career stats for {player_id}: {str(e)}")
            return []
    
    async def get_team(self, team_id: str) -> Dict:
        """Get team/roster information"""
        # This would need to be implemented based on how you store team data
        # For now, return mock data structure
        return {
            "team_id": team_id,
            "roster_id": "1",
            "league_id": "league_123",
            "user_id": "user_456",
            "players": [],
            "starters": [],
            "taxi": [],
            "reserve": []
        }
    
    async def get_available_players(self, league_id: str) -> List[Dict]:
        """Get available players in a league"""
        try:
            rosters = await self.get_league_rosters(league_id)
            all_players = await self.get_all_players()
            
            # Get all rostered players
            rostered_players = set()
            for roster in rosters:
                if roster.get("players"):
                    rostered_players.update(roster["players"])
                if roster.get("taxi"):
                    rostered_players.update(roster["taxi"])
                if roster.get("reserve"):
                    rostered_players.update(roster["reserve"])
            
            # Filter available players
            available = []
            for player_id, player_data in all_players.items():
                if player_id not in rostered_players:
                    # Only include relevant positions
                    if player_data.get("position") in ["QB", "RB", "WR", "TE", "K", "DEF"]:
                        available.append({
                            "player_id": player_id,
                            "player_data": player_data
                        })
            
            return available
        except Exception as e:
            logger.error(f"Error fetching available players: {str(e)}")
            return []
    
    async def search_players(self, query: str, position: str = None) -> List[Dict]:
        """Search for players by name or other criteria"""
        try:
            all_players = await self.get_all_players()
            results = []
            
            query_lower = query.lower()
            
            for player_id, player_data in all_players.items():
                # Check name match
                full_name = player_data.get("full_name", "").lower()
                first_name = player_data.get("first_name", "").lower()
                last_name = player_data.get("last_name", "").lower()
                
                name_match = (query_lower in full_name or 
                            query_lower in first_name or 
                            query_lower in last_name)
                
                # Check position filter
                position_match = (position is None or 
                                player_data.get("position") == position)
                
                if name_match and position_match:
                    results.append({
                        "player_id": player_id,
                        **player_data
                    })
            
            # Sort by relevance (exact name matches first)
            results.sort(key=lambda x: (
                query_lower != x.get("full_name", "").lower(),
                x.get("full_name", "")
            ))
            
            return results[:50]  # Limit results
            
        except Exception as e:
            logger.error(f"Error searching players: {str(e)}")
            return []
