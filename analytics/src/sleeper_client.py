"""
Sleeper API Integration Service
Fetches real data from Sleeper Fantasy Football API
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SleeperAPIClient:
    """Client for interacting with Sleeper Fantasy Football API"""
    
    def __init__(self, base_url: str = "https://api.sleeper.app/v1"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sleepr Fantasy Football App'
        })
    
    def get_league(self, league_id: str) -> Dict:
        """Get league information"""
        try:
            response = self.session.get(f"{self.base_url}/league/{league_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get league {league_id}: {e}")
            raise
    
    def get_rosters(self, league_id: str) -> List[Dict]:
        """Get all rosters in a league"""
        try:
            response = self.session.get(f"{self.base_url}/league/{league_id}/rosters")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get rosters for league {league_id}: {e}")
            raise
    
    def get_users(self, league_id: str) -> List[Dict]:
        """Get all users in a league"""
        try:
            response = self.session.get(f"{self.base_url}/league/{league_id}/users")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get users for league {league_id}: {e}")
            raise
    
    def get_user(self, user_id: str) -> Dict:
        """Get user information"""
        try:
            response = self.session.get(f"{self.base_url}/user/{user_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise
    
    def get_matchups(self, league_id: str, week: int) -> List[Dict]:
        """Get matchups for a specific week"""
        try:
            response = self.session.get(f"{self.base_url}/league/{league_id}/matchups/{week}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get matchups for league {league_id}, week {week}: {e}")
            raise
    
    def get_transactions(self, league_id: str, week: int) -> List[Dict]:
        """Get transactions for a specific week"""
        try:
            response = self.session.get(f"{self.base_url}/league/{league_id}/transactions/{week}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get transactions for league {league_id}, week {week}: {e}")
            raise
    
    def get_traded_picks(self, league_id: str) -> List[Dict]:
        """Get traded picks for a league"""
        try:
            response = self.session.get(f"{self.base_url}/league/{league_id}/traded_picks")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get traded picks for league {league_id}: {e}")
            raise
    
    def get_players(self) -> Dict:
        """Get all NFL players (cached by Sleeper)"""
        try:
            response = self.session.get(f"{self.base_url}/players/nfl")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get players: {e}")
            raise

class SleeperDataProcessor:
    """Process and analyze Sleeper data for your specific leagues"""
    
    def __init__(self, api_client: SleeperAPIClient):
        self.client = api_client
        
    def analyze_league(self, league_id: str) -> Dict:
        """Comprehensive analysis of a league"""
        try:
            # Get basic league info
            league_info = self.client.get_league(league_id)
            rosters = self.client.get_rosters(league_id)
            users = self.client.get_users(league_id)
            
            # Create user lookup
            user_lookup = {user['user_id']: user for user in users}
            
            # Analyze rosters
            roster_analysis = []
            for roster in rosters:
                owner = user_lookup.get(roster['owner_id'], {})
                roster_data = {
                    'roster_id': roster['roster_id'],
                    'owner': owner.get('display_name', 'Unknown'),
                    'owner_id': roster['owner_id'],
                    'players': roster.get('players', []),
                    'starters': roster.get('starters', []),
                    'reserve': roster.get('reserve', []),
                    'taxi': roster.get('taxi', []),
                    'wins': roster.get('settings', {}).get('wins', 0),
                    'losses': roster.get('settings', {}).get('losses', 0),
                    'ties': roster.get('settings', {}).get('ties', 0),
                    'points_for': roster.get('settings', {}).get('fpts', 0),
                    'points_against': roster.get('settings', {}).get('fpts_against', 0)
                }
                roster_analysis.append(roster_data)
            
            return {
                'league_info': {
                    'league_id': league_info['league_id'],
                    'name': league_info['name'],
                    'season': league_info['season'],
                    'status': league_info['status'],
                    'is_dynasty': league_info.get('settings', {}).get('type') == 2,
                    'total_rosters': league_info['total_rosters'],
                    'scoring_settings': league_info.get('scoring_settings', {}),
                    'roster_positions': league_info.get('roster_positions', [])
                },
                'rosters': roster_analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze league {league_id}: {e}")
            raise
    
    def get_dynasty_insights(self, league_id: str) -> Dict:
        """Get dynasty-specific insights for a league"""
        league_data = self.analyze_league(league_id)
        
        # Dynasty-specific analysis
        insights = {
            'league_id': league_id,
            'is_dynasty': league_data['league_info']['is_dynasty'],
            'team_analysis': [],
            'league_trends': {}
        }
        
        # Analyze each team for dynasty value
        for roster in league_data['rosters']:
            team_insight = {
                'owner': roster['owner'],
                'record': f"{roster['wins']}-{roster['losses']}-{roster['ties']}",
                'points_for': roster['points_for'],
                'points_against': roster['points_against'],
                'roster_size': len(roster['players']),
                'strategy_suggestion': self._suggest_dynasty_strategy(roster)
            }
            insights['team_analysis'].append(team_insight)
        
        return insights
    
    def _suggest_dynasty_strategy(self, roster: Dict) -> str:
        """Suggest dynasty strategy based on team composition"""
        wins = roster['wins']
        losses = roster['losses']
        total_games = wins + losses
        
        if total_games == 0:
            return "Season just starting - monitor early performance"
        
        win_percentage = wins / total_games
        
        if win_percentage >= 0.7:
            return "Contending - consider trading picks for proven talent"
        elif win_percentage >= 0.4:
            return "Middling - evaluate at trade deadline"
        else:
            return "Rebuilding - sell veterans for picks and young talent"

# Example usage functions for your specific leagues
def analyze_your_leagues():
    """Analyze your specific Sleeper leagues"""
    client = SleeperAPIClient()
    processor = SleeperDataProcessor(client)
    
    # Your league IDs from the URLs
    league_ids = [
        "1197641763607556096",  # First league
        "1180092430900092928"   # Second league
    ]
    
    results = {}
    
    for league_id in league_ids:
        try:
            print(f"Analyzing league {league_id}...")
            league_analysis = processor.analyze_league(league_id)
            dynasty_insights = processor.get_dynasty_insights(league_id)
            
            results[league_id] = {
                'analysis': league_analysis,
                'dynasty_insights': dynasty_insights
            }
            
            # Print summary
            league_info = league_analysis['league_info']
            print(f"League: {league_info['name']}")
            print(f"Season: {league_info['season']}")
            print(f"Dynasty: {league_info['is_dynasty']}")
            print(f"Teams: {league_info['total_rosters']}")
            print("---")
            
        except Exception as e:
            print(f"Error analyzing league {league_id}: {e}")
            results[league_id] = {'error': str(e)}
    
    return results

if __name__ == "__main__":
    # Test the API with your leagues
    results = analyze_your_leagues()
    
    # Save results to file for inspection
    with open('league_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Analysis complete! Check league_analysis.json for detailed results.")
