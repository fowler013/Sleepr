#!/usr/bin/env python3
"""
LIVE STATS INTEGRATION - ESPN & Pro Football Reference
Real-time player stats, in-game updates, and advanced analytics
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp

class ESPNFantasyAPI:
    """ESPN Fantasy Football API client for live stats"""
    
    def __init__(self):
        self.base_url = "https://fantasy.espn.com/apis/v3/games/ffl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_live_scoring(self, week: int = 1, season: int = 2025) -> Dict:
        """Get live scoring updates for current week"""
        try:
            # ESPN's live scoring endpoint
            url = f"{self.base_url}/seasons/{season}/segments/0/leagues/0"
            params = {
                'view': ['mLiveScoring', 'mMatchupScore', 'mScoreboard'],
                'scoringPeriodId': week
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ ESPN API returned status code: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching ESPN live scoring: {e}")
            return {}
    
    def get_player_projections(self, week: int = 1, season: int = 2025) -> Dict:
        """Get ESPN player projections for the week"""
        try:
            url = f"{self.base_url}/seasons/{season}/segments/0/leagues/0"
            params = {
                'view': ['kona_player_info'],
                'scoringPeriodId': week
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_projections(data)
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Error fetching ESPN projections: {e}")
            return {}
    
    def get_live_player_stats(self, player_ids: List[str], week: int = 1) -> Dict:
        """Get live stats for specific players during games"""
        try:
            # ESPN's player stats endpoint
            stats = {}
            for player_id in player_ids:
                url = f"{self.base_url}/seasons/2025/players/{player_id}"
                params = {
                    'view': 'stats',
                    'scoringPeriodId': week
                }
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    player_data = response.json()
                    stats[player_id] = self._parse_player_stats(player_data)
                
                # Rate limiting
                time.sleep(0.1)
            
            return stats
            
        except Exception as e:
            print(f"❌ Error fetching live player stats: {e}")
            return {}
    
    def _parse_projections(self, data: Dict) -> Dict:
        """Parse ESPN projections data"""
        projections = {}
        try:
            players = data.get('players', [])
            for player in players:
                player_id = str(player.get('id', ''))
                player_info = player.get('player', {})
                
                projections[player_id] = {
                    'name': player_info.get('fullName', 'Unknown'),
                    'position': player_info.get('defaultPositionId', 0),
                    'team': player_info.get('proTeamId', 0),
                    'projection': player.get('ratings', {}).get('0', {}).get('positionalRanking', 0),
                    'ownership': player.get('ownership', {}).get('percentOwned', 0)
                }
        except Exception as e:
            print(f"⚠️ Error parsing projections: {e}")
        
        return projections
    
    def _parse_player_stats(self, data: Dict) -> Dict:
        """Parse individual player stats"""
        try:
            return {
                'points': data.get('appliedTotal', 0),
                'projected': data.get('projectedTotal', 0),
                'stats': data.get('stats', {}),
                'game_status': data.get('gameStatus', 'Unknown')
            }
        except:
            return {}

class ProFootballReferenceScraper:
    """Pro Football Reference scraper for advanced stats"""
    
    def __init__(self):
        self.base_url = "https://www.pro-football-reference.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.cache = {}
        self.cache_expiry = {}
    
    def get_weekly_stats(self, week: int = 1, year: int = 2025, position: str = 'all') -> pd.DataFrame:
        """Scrape weekly fantasy stats from PFR"""
        cache_key = f"weekly_{position}_{year}_w{week}"
        
        # Check cache first (cache for 1 hour)
        if cache_key in self.cache:
            if datetime.now() < self.cache_expiry.get(cache_key, datetime.now()):
                print(f"📋 Using cached data for {cache_key}")
                return self.cache[cache_key]
        
        try:
            if position == 'QB':
                url = f"{self.base_url}/years/{year}/fantasy-football/qb/week-{week}/"
            elif position == 'RB':
                url = f"{self.base_url}/years/{year}/fantasy-football/rb/week-{week}/"
            elif position == 'WR':
                url = f"{self.base_url}/years/{year}/fantasy-football/wr/week-{week}/"
            elif position == 'TE':
                url = f"{self.base_url}/years/{year}/fantasy-football/te/week-{week}/"
            else:
                url = f"{self.base_url}/years/{year}/fantasy-football/week-{week}/"
            
            print(f"🔍 Scraping PFR: {url}")
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', {'id': 'stats'})
                
                if table:
                    df = pd.read_html(str(table))[0]
                    df = self._clean_pfr_data(df)
                    
                    # Cache for 1 hour
                    self.cache[cache_key] = df
                    self.cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
                    
                    print(f"✅ Scraped {len(df)} player records")
                    return df
                else:
                    print("⚠️ No stats table found on PFR page")
                    return pd.DataFrame()
            else:
                print(f"⚠️ PFR returned status code: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ Error scraping PFR: {e}")
            return pd.DataFrame()
        
        # Rate limiting
        time.sleep(1)
    
    def get_player_advanced_stats(self, player_name: str, year: int = 2025) -> Dict:
        """Get advanced stats for a specific player"""
        try:
            # Convert player name to PFR format
            pfr_name = self._convert_to_pfr_name(player_name)
            
            # Try to find player page
            search_url = f"{self.base_url}/search/search.fcgi?search={pfr_name}"
            response = self.session.get(search_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for player link
                player_links = soup.find_all('a', href=re.compile(r'/players/[a-zA-Z]/.*\.htm'))
                
                if player_links:
                    player_url = self.base_url + player_links[0]['href']
                    return self._scrape_player_page(player_url, year)
            
            return {}
            
        except Exception as e:
            print(f"❌ Error getting advanced stats for {player_name}: {e}")
            return {}
    
    def get_red_zone_stats(self, week: int = 1, year: int = 2025) -> pd.DataFrame:
        """Scrape red zone usage stats"""
        try:
            url = f"{self.base_url}/years/{year}/opp.htm"
            response = self.session.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for red zone tables
                tables = soup.find_all('table')
                
                for table in tables:
                    if 'red' in str(table).lower() or 'goal' in str(table).lower():
                        df = pd.read_html(str(table))[0]
                        return self._clean_pfr_data(df)
                
            return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Error scraping red zone stats: {e}")
            return pd.DataFrame()
    
    def _clean_pfr_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize PFR data"""
        try:
            # Remove duplicate headers
            df = df[df.iloc[:, 0] != df.columns[0]]
            
            # Convert numeric columns
            numeric_columns = df.select_dtypes(include=['object']).columns
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            return df
            
        except Exception as e:
            print(f"⚠️ Error cleaning PFR data: {e}")
            return df
    
    def _convert_to_pfr_name(self, player_name: str) -> str:
        """Convert player name to PFR search format"""
        return player_name.replace(' ', '+').replace("'", "")
    
    def _scrape_player_page(self, url: str, year: int) -> Dict:
        """Scrape individual player page for advanced stats"""
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                stats = {}
                # Look for current season stats table
                tables = soup.find_all('table')
                
                for table in tables:
                    table_id = table.get('id', '')
                    if str(year) in table_id or 'stats' in table_id:
                        df = pd.read_html(str(table))[0]
                        stats[table_id] = df.to_dict('records')
                
                return stats
            
            return {}
            
        except Exception as e:
            print(f"❌ Error scraping player page: {e}")
            return {}

class LiveStatsManager:
    """Main class to coordinate live stats from multiple sources"""
    
    def __init__(self):
        self.espn = ESPNFantasyAPI()
        self.pfr = ProFootballReferenceScraper()
        self.sleeper_base = "https://api.sleeper.app/v1"
    
    async def get_comprehensive_player_data(self, player_name: str, position: str, week: int = 1) -> Dict:
        """Get comprehensive player data from all sources"""
        print(f"\n🎯 Fetching comprehensive data for {player_name} ({position})")
        
        data = {
            'player_name': player_name,
            'position': position,
            'week': week,
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        try:
            # Get ESPN projections
            espn_projections = self.espn.get_player_projections(week)
            data['sources']['espn_projections'] = espn_projections
            
            # Get PFR weekly stats
            pfr_weekly = self.pfr.get_weekly_stats(week, position=position)
            if not pfr_weekly.empty:
                # Filter for specific player
                player_stats = pfr_weekly[pfr_weekly['Player'].str.contains(player_name, case=False, na=False)]
                data['sources']['pfr_weekly'] = player_stats.to_dict('records')
            
            # Get PFR advanced stats
            pfr_advanced = self.pfr.get_player_advanced_stats(player_name)
            data['sources']['pfr_advanced'] = pfr_advanced
            
            # Combine and analyze
            data['analysis'] = self._analyze_combined_data(data['sources'])
            
            return data
            
        except Exception as e:
            print(f"❌ Error getting comprehensive data: {e}")
            data['error'] = str(e)
            return data
    
    def get_live_game_updates(self, week: int = 1) -> Dict:
        """Get live updates for ongoing games"""
        print(f"\n⚡ Fetching live game updates for Week {week}")
        
        updates = {
            'week': week,
            'timestamp': datetime.now().isoformat(),
            'live_scoring': {},
            'game_status': {},
            'trending_players': {}
        }
        
        try:
            # Get ESPN live scoring
            espn_live = self.espn.get_live_scoring(week)
            updates['live_scoring'] = espn_live
            
            # Get Sleeper trending players
            trending_url = f"{self.sleeper_base}/players/nfl/trending/add"
            response = requests.get(trending_url)
            if response.status_code == 200:
                updates['trending_players'] = response.json()
            
            return updates
            
        except Exception as e:
            print(f"❌ Error getting live updates: {e}")
            updates['error'] = str(e)
            return updates
    
    def generate_live_insights(self, league_rosters: Dict, week: int = 1) -> Dict:
        """Generate actionable insights from live data"""
        insights = {
            'week': week,
            'timestamp': datetime.now().isoformat(),
            'hot_pickups': [],
            'start_sit_alerts': [],
            'injury_updates': [],
            'breakout_candidates': []
        }
        
        try:
            # Get trending players
            trending_url = f"{self.sleeper_base}/players/nfl/trending/add?hours=24&limit=50"
            response = requests.get(trending_url)
            
            if response.status_code == 200:
                trending = response.json()
                
                for player in trending[:10]:
                    player_id = player.get('player_id')
                    
                    # Get player info
                    players_url = f"{self.sleeper_base}/players/nfl"
                    players_response = requests.get(players_url)
                    
                    if players_response.status_code == 200:
                        all_players = players_response.json()
                        player_info = all_players.get(player_id, {})
                        
                        if player_info:
                            insights['hot_pickups'].append({
                                'player_id': player_id,
                                'name': f"{player_info.get('first_name', '')} {player_info.get('last_name', '')}",
                                'position': player_info.get('position', ''),
                                'team': player_info.get('team', ''),
                                'trend_score': player.get('count', 0),
                                'reason': self._analyze_trending_reason(player_info)
                            })
            
            return insights
            
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
            insights['error'] = str(e)
            return insights
    
    def _analyze_combined_data(self, sources: Dict) -> Dict:
        """Analyze combined data from all sources"""
        analysis = {
            'confidence_score': 0,
            'recommendation': 'HOLD',
            'key_metrics': {},
            'risk_factors': []
        }
        
        try:
            # Analyze ESPN vs PFR consistency
            if sources.get('espn_projections') and sources.get('pfr_weekly'):
                analysis['confidence_score'] += 30
                analysis['recommendation'] = 'START'
            
            # Check for PFR advanced metrics
            if sources.get('pfr_advanced'):
                analysis['confidence_score'] += 20
                analysis['key_metrics']['advanced_stats_available'] = True
            
            # Risk assessment
            if analysis['confidence_score'] < 50:
                analysis['risk_factors'].append('Limited data sources')
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Error in analysis: {e}")
            return analysis
    
    def _analyze_trending_reason(self, player_info: Dict) -> str:
        """Determine why a player is trending"""
        position = player_info.get('position', '')
        team = player_info.get('team', '')
        
        reasons = [
            f"Rising {position} on {team}",
            "Potential breakout candidate",
            "Waiver wire pickup",
            "Injury replacement opportunity",
            "Favorable matchup ahead"
        ]
        
        # Simple heuristic based on position
        if position == 'RB':
            return "Potential injury replacement or committee back emerging"
        elif position == 'WR':
            return "Target share increase or favorable matchup"
        elif position == 'TE':
            return "Streaming option with upside"
        else:
            return reasons[0]

def main():
    """Demo the live stats integration"""
    print("🔥 ======================================================================")
    print("   LIVE STATS INTEGRATION - ESPN & PRO FOOTBALL REFERENCE")
    print("   Real-time player data and advanced analytics")
    print("🔥 ======================================================================")
    
    # Initialize the live stats manager
    manager = LiveStatsManager()
    
    # Test comprehensive player data
    print("\n🎯 TESTING COMPREHENSIVE PLAYER DATA:")
    test_players = [
        ("Josh Allen", "QB"),
        ("Christian McCaffrey", "RB"),
        ("Tyreek Hill", "WR"),
        ("Travis Kelce", "TE")
    ]
    
    for player_name, position in test_players:
        try:
            data = asyncio.run(manager.get_comprehensive_player_data(player_name, position))
            print(f"\n📊 {player_name} ({position}):")
            print(f"   Sources: {list(data.get('sources', {}).keys())}")
            print(f"   Analysis: {data.get('analysis', {}).get('recommendation', 'N/A')}")
        except Exception as e:
            print(f"❌ Error testing {player_name}: {e}")
    
    # Test live game updates
    print("\n⚡ TESTING LIVE GAME UPDATES:")
    try:
        live_updates = manager.get_live_game_updates()
        print(f"   Live scoring available: {bool(live_updates.get('live_scoring'))}")
        print(f"   Trending players: {len(live_updates.get('trending_players', []))}")
    except Exception as e:
        print(f"❌ Error testing live updates: {e}")
    
    # Test insights generation
    print("\n🧠 TESTING INSIGHTS GENERATION:")
    try:
        insights = manager.generate_live_insights({})
        print(f"   Hot pickups found: {len(insights.get('hot_pickups', []))}")
        print(f"   Top pickup: {insights.get('hot_pickups', [{}])[0].get('name', 'None') if insights.get('hot_pickups') else 'None'}")
    except Exception as e:
        print(f"❌ Error testing insights: {e}")
    
    print("\n✅ Live Stats Integration Demo Complete!")
    print("🔗 Ready to integrate with newsletter generators and analysis scripts")

if __name__ == "__main__":
    main()
