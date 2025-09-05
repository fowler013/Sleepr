#!/usr/bin/env python3
"""
HISTORICAL LEAGUE DATA FETCHER - 2023 & 2024 Stumblin' League Results
Fetches historical performance data to enhance dynasty analysis
"""

import requests
import json
from datetime import datetime

def fetch_historical_league_data(league_id, season):
    """Fetch historical league data from Sleeper API"""
    try:
        # Get league info
        league_url = f"https://api.sleeper.app/v1/league/{league_id}"
        league_response = requests.get(league_url)
        league_data = league_response.json()
        
        # Get users in league
        users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
        users_response = requests.get(users_url)
        users_data = users_response.json()
        
        # Get rosters with final standings
        rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        rosters_response = requests.get(rosters_url)
        rosters_data = rosters_response.json()
        
        # Get playoffs bracket
        winners_bracket_url = f"https://api.sleeper.app/v1/league/{league_id}/winners_bracket"
        try:
            winners_response = requests.get(winners_bracket_url)
            winners_data = winners_response.json() if winners_response.status_code == 200 else None
        except:
            winners_data = None
        
        return league_data, users_data, rosters_data, winners_data
    except Exception as e:
        print(f"Error fetching data for league {league_id} ({season}): {e}")
        return None, None, None, None

def process_historical_data():
    """Process and display historical league data"""
    print("📊 **HISTORICAL STUMBLIN' LEAGUE DATA**")
    print("=" * 60)
    
    historical_leagues = [
        {"id": "918682182527422464", "season": "2023"},
        {"id": "1048275084177227776", "season": "2024"}
    ]
    
    historical_results = {}
    
    for league_info in historical_leagues:
        league_id = league_info["id"]
        season = league_info["season"]
        
        print(f"\n🏈 **{season} SEASON RESULTS**")
        print("-" * 40)
        
        league_data, users_data, rosters_data, playoffs_data = fetch_historical_league_data(league_id, season)
        
        if not all([league_data, users_data, rosters_data]):
            print(f"❌ Could not fetch {season} data")
            continue
        
        # Create user lookup
        user_lookup = {user['user_id']: user for user in users_data}
        
        # Process final standings
        final_standings = []
        for roster in sorted(rosters_data, key=lambda x: x.get('roster_id', 0)):
            owner_id = roster.get('owner_id')
            user_info = user_lookup.get(owner_id, {})
            
            display_name = user_info.get('display_name', 'Unknown User')
            metadata = user_info.get('metadata', {})
            team_name = metadata.get('team_name') if metadata else None
            final_team_name = team_name if team_name else display_name
            
            wins = roster.get('settings', {}).get('wins', 0)
            losses = roster.get('settings', {}).get('losses', 0)
            points = roster.get('settings', {}).get('fpts', 0)
            
            final_standings.append({
                'team_name': final_team_name,
                'owner': display_name,
                'wins': wins,
                'losses': losses,
                'points': points,
                'roster_id': roster.get('roster_id')
            })
        
        # Sort by wins, then by points
        final_standings.sort(key=lambda x: (x['wins'], x['points']), reverse=True)
        
        print("📈 **FINAL STANDINGS:**")
        for i, team in enumerate(final_standings, 1):
            record = f"{team['wins']}-{team['losses']}"
            if team['owner'] == 'Nivet':
                print(f"   {i:2d}. 🏠 {team['team_name']:<20} ({team['owner']:<15}) | {record} | {team['points']:,.0f} pts")
            else:
                print(f"   {i:2d}.    {team['team_name']:<20} ({team['owner']:<15}) | {record} | {team['points']:,.0f} pts")
        
        historical_results[season] = {
            'standings': final_standings,
            'champion': final_standings[0]['team_name'] if final_standings else 'Unknown',
            'nivet_finish': next((i+1 for i, team in enumerate(final_standings) if team['owner'] == 'Nivet'), 'Not found')
        }
        
        print()
    
    return historical_results

def update_league_settings():
    """Display correct league settings"""
    print("\n⚙️ **LEAGUE SETTINGS & FORMAT**")
    print("=" * 60)
    
    print("🏈 **A League Far Far Away (2025)**")
    print("   • Format: 12-Team Dynasty Superflex")
    print("   • Scoring: PPR (Point Per Reception)")
    print("   • TE Premium: Enhanced TE scoring")
    print("   • League Type: Dynasty (Keep all players)")
    print("   • League ID: 1197641763607556096")
    print()
    
    print("🏈 **Stumblin', Bumblin', and Fumblin' (2025)**")
    print("   • Format: 12-Team Dynasty Superflex")
    print("   • Scoring: Half-PPR (0.5 Point Per Reception)")
    print("   • TE Premium: Enhanced TE scoring")
    print("   • League Type: Dynasty (Keep all players)")
    print("   • League ID: 1180092430900092928")
    print("   • Historical: 2021-2025 (5 seasons)")
    print()
    
    print("📊 **SCORING IMPLICATIONS:**")
    print("   • Superflex: QB values significantly higher")
    print("   • TEP: Elite TEs (Kelce, Andrews, LaPorta) premium")
    print("   • Half-PPR vs PPR: Slight RB advantage in Stumblin'")
    print("   • Dynasty: Long-term asset management critical")
    print()

def analyze_historical_trends(historical_data):
    """Analyze historical trends for dynasty insights"""
    print("🔍 **HISTORICAL ANALYSIS & TRENDS**")
    print("=" * 60)
    
    if '2023' in historical_data and '2024' in historical_data:
        nivet_2023 = historical_data['2023']['nivet_finish']
        nivet_2024 = historical_data['2024']['nivet_finish']
        
        print("🏆 **HOUSE FOWLER HISTORICAL PERFORMANCE:**")
        print(f"   • 2023 Finish: #{nivet_2023} of 12")
        print(f"   • 2024 Finish: #{nivet_2024} of 12")
        
        if isinstance(nivet_2023, int) and isinstance(nivet_2024, int):
            if nivet_2024 < nivet_2023:
                print(f"   • Trend: 📈 Improved by {nivet_2023 - nivet_2024} positions")
            elif nivet_2024 > nivet_2023:
                print(f"   • Trend: 📉 Dropped {nivet_2024 - nivet_2023} positions")
            else:
                print("   • Trend: ➡️ Consistent finish")
        print()
        
        print("🎯 **DYNASTY BUILDING INSIGHTS:**")
        print("   • Superflex Dynasty: QB depth absolutely critical")
        print("   • TEP Format: Target elite young TEs (LaPorta, Bowers)")
        print("   • Half-PPR: RBs slightly more valuable than full PPR")
        print("   • 5-Year League: Established trade patterns and rivalries")
        print()
        
        print("📈 **CHAMPIONSHIP PATTERNS:**")
        champions = [historical_data.get('2023', {}).get('champion'), 
                    historical_data.get('2024', {}).get('champion')]
        if champions[0] and champions[1]:
            print(f"   • 2023 Champion: {champions[0]}")
            print(f"   • 2024 Champion: {champions[1]}")
            if champions[0] == champions[1]:
                print("   • Repeat Champion: Dominant dynasty established")
            else:
                print("   • Different Champions: Competitive balance")
        print()

def main():
    print("🏈 " + "="*70)
    print("   HISTORICAL LEAGUE ANALYSIS - 2023 & 2024 RESULTS")
    print("   Enhanced Dynasty Context with League Settings")
    print("🏈 " + "="*70)
    
    update_league_settings()
    historical_data = process_historical_data()
    analyze_historical_trends(historical_data)
    
    print("💡 **DYNASTY STRATEGY RECOMMENDATIONS:**")
    print("=" * 60)
    print("   🎯 **Superflex Priority**: Secure 3+ startable QBs")
    print("   📈 **TEP Advantage**: Target elite TEs before breakout")
    print("   🏆 **Championship Window**: House Fowler 2025-2027")
    print("   💱 **Trade Strategy**: Sell aging assets for future picks")
    print("   🔄 **Long-term View**: 5+ year dynasty requires patience")
    print()
    print("=" * 70)
    print("✅ Historical data integrated - Dynasty analysis enhanced")
    print("=" * 70)

if __name__ == "__main__":
    main()
