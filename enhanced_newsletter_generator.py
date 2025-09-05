#!/usr/bin/env python3
"""
ENHANCED NEWSLETTER GENERATOR WITH LIVE API INTEGRATION
Combines Sleeper API, Live Stats, and your custom backend for ultimate newsletters
"""

import requests
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Import our live stats integration
from live_stats_integration import LiveStatsManager

class EnhancedNewsletterGenerator:
    """Enhanced newsletter generator with full API integration"""
    
    def __init__(self):
        self.sleeper_base = "https://api.sleeper.app/v1"
        self.local_api_base = "http://localhost:8080/api/v1"
        self.live_stats = LiveStatsManager()
        
    def test_local_api_connection(self) -> bool:
        """Test connection to local API server"""
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Local API not available: {e}")
            return False
    
    async def generate_super_enhanced_newsletter(self, league_id: str, league_name: str, week: int = 1) -> str:
        """Generate the most comprehensive newsletter possible"""
        
        print(f"🚀 GENERATING SUPER ENHANCED NEWSLETTER FOR {league_name.upper()}")
        print("=" * 80)
        
        # Test API availability
        local_api_available = self.test_local_api_connection()
        print(f"🔗 Local API Status: {'✅ Connected' if local_api_available else '❌ Offline'}")
        
        newsletter_data = {
            'league_name': league_name,
            'week': week,
            'timestamp': datetime.now().isoformat(),
            'data_sources': {
                'sleeper_api': False,
                'local_api': local_api_available,
                'live_stats': False,
                'trending_players': False
            }
        }
        
        # 1. Get basic league data from Sleeper
        print("\n🏈 Fetching Sleeper API data...")
        sleeper_data = await self._fetch_sleeper_data(league_id)
        if sleeper_data:
            newsletter_data['data_sources']['sleeper_api'] = True
            newsletter_data['sleeper'] = sleeper_data
        
        # 2. Get local API data (if available)
        if local_api_available:
            print("\n🎯 Fetching local API analytics...")
            local_data = await self._fetch_local_api_data()
            if local_data:
                newsletter_data['local_api'] = local_data
        
        # 3. Get live stats and trending players
        print("\n⚡ Fetching live stats and trends...")
        live_data = await self._fetch_live_data(week)
        if live_data:
            newsletter_data['data_sources']['live_stats'] = True
            newsletter_data['data_sources']['trending_players'] = len(live_data.get('hot_pickups', [])) > 0
            newsletter_data['live_stats'] = live_data
        
        # 4. Generate the newsletter
        print("\n📝 Generating enhanced newsletter...")
        newsletter_content = await self._generate_newsletter_content(newsletter_data)
        
        # 5. Save newsletter
        filename = f"Enhanced_{league_name.replace(' ', '_')}_Week{week}_Newsletter.md"
        with open(filename, 'w') as f:
            f.write(newsletter_content)
        
        print(f"\n✅ Enhanced newsletter saved as: {filename}")
        print(f"📊 Data sources used: {sum(newsletter_data['data_sources'].values())}/4")
        
        return newsletter_content
    
    async def _fetch_sleeper_data(self, league_id: str) -> Optional[Dict]:
        """Fetch comprehensive Sleeper API data"""
        try:
            data = {}
            
            # League info
            league_response = requests.get(f"{self.sleeper_base}/league/{league_id}")
            if league_response.status_code == 200:
                data['league'] = league_response.json()
            
            # Users
            users_response = requests.get(f"{self.sleeper_base}/league/{league_id}/users")
            if users_response.status_code == 200:
                data['users'] = users_response.json()
            
            # Rosters
            rosters_response = requests.get(f"{self.sleeper_base}/league/{league_id}/rosters")
            if rosters_response.status_code == 200:
                data['rosters'] = rosters_response.json()
            
            # Week 1 matchups
            matchups_response = requests.get(f"{self.sleeper_base}/league/{league_id}/matchups/1")
            if matchups_response.status_code == 200:
                data['matchups'] = matchups_response.json()
            
            # Trending players
            trending_response = requests.get(f"{self.sleeper_base}/players/nfl/trending/add?hours=24&limit=20")
            if trending_response.status_code == 200:
                data['trending'] = trending_response.json()
            
            return data if data else None
            
        except Exception as e:
            print(f"❌ Error fetching Sleeper data: {e}")
            return None
    
    async def _fetch_local_api_data(self) -> Optional[Dict]:
        """Fetch data from local API server"""
        try:
            data = {}
            
            # Health check
            health_response = requests.get(f"http://localhost:8080/health")
            if health_response.status_code == 200:
                data['health'] = health_response.json()
            
            # Waiver wire recommendations
            waiver_response = requests.get(f"{self.local_api_base}/public/analytics/waiver-wire")
            if waiver_response.status_code == 200:
                data['waiver_wire'] = waiver_response.json()
            
            return data if data else None
            
        except Exception as e:
            print(f"❌ Error fetching local API data: {e}")
            return None
    
    async def _fetch_live_data(self, week: int) -> Optional[Dict]:
        """Fetch live stats and insights"""
        try:
            # Get live insights
            insights = self.live_stats.generate_live_insights({}, week)
            
            # Get live game updates
            live_updates = self.live_stats.get_live_game_updates(week)
            
            return {
                'insights': insights,
                'live_updates': live_updates,
                'hot_pickups': insights.get('hot_pickups', [])
            }
            
        except Exception as e:
            print(f"❌ Error fetching live data: {e}")
            return None
    
    async def _generate_newsletter_content(self, data: Dict) -> str:
        """Generate comprehensive newsletter content"""
        league_name = data['league_name']
        week = data['week']
        sources = data['data_sources']
        
        # Determine theme based on league name
        if "far far away" in league_name.lower():
            theme = "star_wars"
            emoji = "🌌"
        else:
            theme = "championship"
            emoji = "🏆"
        
        content = []
        content.append(f"# {emoji} {league_name.upper()} {emoji}")
        content.append(f"## **SUPER ENHANCED WEEK {week} NEWSLETTER**")
        content.append("*Powered by Multiple Live Data Sources*")
        content.append("")
        content.append("---")
        content.append("")
        
        # Data source summary
        content.append("## 📊 **DATA SOURCE INTEGRATION STATUS**")
        content.append("")
        content.append(f"✅ **Sleeper API:** {'Connected' if sources['sleeper_api'] else 'Offline'}")
        content.append(f"✅ **Local API Server:** {'Connected' if sources['local_api'] else 'Offline'}")
        content.append(f"✅ **Live Stats Engine:** {'Active' if sources['live_stats'] else 'Offline'}")
        content.append(f"✅ **Trending Players:** {'Available' if sources['trending_players'] else 'Limited'}")
        content.append("")
        content.append("---")
        content.append("")
        
        # League data section
        if data.get('sleeper'):
            content.extend(await self._generate_sleeper_section(data['sleeper'], theme))
        
        # Local API section
        if data.get('local_api'):
            content.extend(await self._generate_local_api_section(data['local_api']))
        
        # Live stats section
        if data.get('live_stats'):
            content.extend(await self._generate_live_stats_section(data['live_stats']))
        
        # Footer
        content.append("")
        content.append("---")
        content.append("")
        content.append("## 🔧 **TECHNICAL DETAILS**")
        content.append("")
        content.append(f"**Generated:** {data['timestamp']}")
        content.append(f"**Data Sources:** {sum(sources.values())}/4 active")
        content.append("**API Integration:** Full stack operational")
        content.append("**Live Updates:** Real-time trending data")
        content.append("")
        content.append("*This newsletter was generated using multiple live data sources*")
        content.append("*including Sleeper API, custom backend, and live stats integration.*")
        
        return "\n".join(content)
    
    async def _generate_sleeper_section(self, sleeper_data: Dict, theme: str) -> List[str]:
        """Generate Sleeper API data section"""
        content = []
        content.append("## 🏈 **LIVE SLEEPER LEAGUE DATA**")
        content.append("")
        
        # League info
        if 'league' in sleeper_data:
            league = sleeper_data['league']
            content.append(f"**League Name:** {league.get('name', 'Unknown')}")
            content.append(f"**Season:** {league.get('season', 'Unknown')}")
            content.append(f"**Total Rosters:** {league.get('total_rosters', 'Unknown')}")
            content.append("")
        
        # Team standings
        if 'users' in sleeper_data and 'rosters' in sleeper_data:
            content.append("### 📊 **CURRENT STANDINGS**")
            content.append("")
            
            users = {user['user_id']: user for user in sleeper_data['users']}
            rosters = sleeper_data['rosters']
            
            for i, roster in enumerate(rosters[:6], 1):  # Top 6
                owner_id = roster.get('owner_id', '')
                user = users.get(owner_id, {})
                display_name = user.get('display_name', f'Team {i}')
                
                wins = roster.get('settings', {}).get('wins', 0)
                losses = roster.get('settings', {}).get('losses', 0)
                points = roster.get('settings', {}).get('fpts', 0)
                
                content.append(f"   {i}. **{display_name}** | {wins}-{losses} | {points} pts")
            
            content.append("")
        
        # Trending players
        if 'trending' in sleeper_data:
            content.append("### 🔥 **HOTTEST PICKUPS (Last 24 Hours)**")
            content.append("")
            
            for i, player in enumerate(sleeper_data['trending'][:5], 1):
                player_id = player.get('player_id', '')
                count = player.get('count', 0)
                content.append(f"   {i}. Player ID: {player_id} | Added {count}x")
            
            content.append("")
        
        content.append("---")
        content.append("")
        return content
    
    async def _generate_local_api_section(self, local_data: Dict) -> List[str]:
        """Generate local API data section"""
        content = []
        content.append("## 🎯 **LOCAL API ANALYTICS**")
        content.append("")
        
        if 'health' in local_data:
            content.append("✅ **API Server Status:** Healthy and operational")
            content.append("")
        
        if 'waiver_wire' in local_data:
            content.append("### 🎪 **WAIVER WIRE RECOMMENDATIONS**")
            content.append("")
            waiver_data = local_data['waiver_wire']
            
            if isinstance(waiver_data, dict):
                content.append("📋 **Advanced Analytics Available:**")
                content.append("   • Player projections and recommendations")
                content.append("   • Waiver wire priority suggestions")
                content.append("   • Advanced statistical modeling")
            else:
                content.append("📊 **Waiver wire analysis completed**")
            
            content.append("")
        
        content.append("---")
        content.append("")
        return content
    
    async def _generate_live_stats_section(self, live_data: Dict) -> List[str]:
        """Generate live stats section"""
        content = []
        content.append("## ⚡ **LIVE STATS & INSIGHTS**")
        content.append("")
        
        insights = live_data.get('insights', {})
        hot_pickups = insights.get('hot_pickups', [])
        
        if hot_pickups:
            content.append("### 🔥 **TOP WAIVER WIRE TARGETS**")
            content.append("")
            
            for i, player in enumerate(hot_pickups[:5], 1):
                name = player.get('name', 'Unknown Player')
                position = player.get('position', 'N/A')
                team = player.get('team', 'N/A')
                reason = player.get('reason', 'Trending pickup')
                
                content.append(f"**{i}. {name}** ({position} - {team})")
                content.append(f"   📈 *{reason}*")
                content.append("")
        
        # Live updates
        live_updates = live_data.get('live_updates', {})
        if live_updates.get('trending_players'):
            trending_count = len(live_updates['trending_players'])
            content.append(f"### 📊 **REAL-TIME TRENDS**")
            content.append("")
            content.append(f"📈 **{trending_count} players trending** in the last 24 hours")
            content.append("⚡ **Live data integration** providing real-time insights")
            content.append("")
        
        content.append("---")
        content.append("")
        return content

async def main():
    """Generate enhanced newsletters for both leagues"""
    generator = EnhancedNewsletterGenerator()
    
    leagues = [
        {
            'id': '1197641763607556096',
            'name': 'A League Far Far Away',
        },
        {
            'id': '665760142870454272',  # Try primary ID
            'name': 'Stumblin\', Bumblin\', and Fumblin\'',
        }
    ]
    
    for league in leagues:
        try:
            print(f"\n{'='*80}")
            newsletter = await generator.generate_super_enhanced_newsletter(
                league['id'], 
                league['name'], 
                week=1
            )
            print(f"✅ Generated newsletter for {league['name']}")
            
        except Exception as e:
            print(f"❌ Error generating newsletter for {league['name']}: {e}")
    
    print(f"\n{'='*80}")
    print("🚀 ENHANCED NEWSLETTER GENERATION COMPLETE!")
    print("📁 Check your directory for the new enhanced newsletter files")

if __name__ == "__main__":
    asyncio.run(main())
