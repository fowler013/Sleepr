#!/usr/bin/env python3
"""
SLEEPER LEAGUE DATA FETCHER - Get Real Team Names and Users
Fetches actual league data from Sleeper API to ensure accurate team names
"""

import requests
import json
from datetime import datetime

def fetch_league_info(league_id):
    """Fetch league information from Sleeper API"""
    try:
        # Get league info
        league_url = f"https://api.sleeper.app/v1/league/{league_id}"
        league_response = requests.get(league_url)
        league_data = league_response.json()
        
        # Get users in league
        users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
        users_response = requests.get(users_url)
        users_data = users_response.json()
        
        # Get rosters
        rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        rosters_response = requests.get(rosters_url)
        rosters_data = rosters_response.json()
        
        return league_data, users_data, rosters_data
    except Exception as e:
        print(f"Error fetching data for league {league_id}: {e}")
        return None, None, None

def process_league_data(league_id, league_name):
    """Process and display league data"""
    print(f"\n🏈 **{league_name.upper()}**")
    print("=" * 60)
    print(f"League ID: {league_id}")
    
    league_data, users_data, rosters_data = fetch_league_info(league_id)
    
    if not all([league_data, users_data, rosters_data]):
        print("❌ Could not fetch league data from Sleeper API")
        return None
    
    print(f"League Name: {league_data.get('name', 'Unknown')}")
    print(f"Season: {league_data.get('season', 'Unknown')}")
    print(f"Sport: {league_data.get('sport', 'Unknown')}")
    print(f"Total Rosters: {league_data.get('total_rosters', 'Unknown')}")
    
    # Create user lookup
    user_lookup = {user['user_id']: user for user in users_data}
    
    print(f"\n📋 **TEAMS & OWNERS:**")
    teams = []
    
    for roster in sorted(rosters_data, key=lambda x: x.get('roster_id', 0)):
        roster_id = roster.get('roster_id')
        owner_id = roster.get('owner_id')
        
        # Get user info
        user_info = user_lookup.get(owner_id, {})
        display_name = user_info.get('display_name', 'Unknown User')
        username = user_info.get('username', 'unknown')
        
        # Get team metadata (team name if set)
        metadata = user_info.get('metadata', {})
        team_name = metadata.get('team_name') if metadata else None
        
        # Use team name if available, otherwise use display name
        final_team_name = team_name if team_name else display_name
        
        wins = roster.get('settings', {}).get('wins', 0)
        losses = roster.get('settings', {}).get('losses', 0)
        points = roster.get('settings', {}).get('fpts', 0)
        
        print(f"   {roster_id:2d}. {final_team_name:<25} | Owner: {display_name:<20} | Record: {wins}-{losses} | Points: {points}")
        
        teams.append({
            'roster_id': roster_id,
            'team_name': final_team_name,
            'owner_name': display_name,
            'username': username,
            'wins': wins,
            'losses': losses,
            'points': points
        })
    
    return {
        'league_id': league_id,
        'league_name': league_data.get('name'),
        'season': league_data.get('season'),
        'teams': teams
    }

def generate_updated_analysis(league_data):
    """Generate updated analysis with real team names"""
    print(f"\n🎯 **UPDATED ANALYSIS TEMPLATE**")
    print("=" * 60)
    
    if not league_data:
        return
    
    print(f"# {league_data['league_name']} ({league_data['season']})")
    print(f"League ID: {league_data['league_id']}")
    print()
    
    # Sort teams by points for power rankings
    sorted_teams = sorted(league_data['teams'], key=lambda x: x['points'], reverse=True)
    
    print("## Power Rankings:")
    for i, team in enumerate(sorted_teams, 1):
        record = f"{team['wins']}-{team['losses']}"
        print(f"{i}. **{team['team_name']}** ({team['owner_name']}) - {record} - {team['points']} pts")
    
    print()

def main():
    print("🏈 " + "="*70)
    print("   SLEEPER LEAGUE DATA FETCHER - REAL TEAM NAMES & USERS")
    print("🏈 " + "="*70)
    
    # League IDs from the URLs provided
    leagues = [
        ("1197641763607556096", "A League Far Far Away"),
        ("1180092430900092928", "Stumblin', Bumblin', and Fumblin'")
    ]
    
    all_league_data = []
    
    for league_id, expected_name in leagues:
        league_data = process_league_data(league_id, expected_name)
        if league_data:
            all_league_data.append(league_data)
            generate_updated_analysis(league_data)
    
    print(f"\n" + "="*70)
    print("✅ **LEAGUE DATA FETCH COMPLETE**")
    print(f"   Successfully retrieved data for {len(all_league_data)} leagues")
    print("   Ready to update analysis scripts with real team names")
    print("="*70)
    
    # Save data to JSON for reference
    with open('/Users/tevinfowler/Documents/Sleepr/real_league_data.json', 'w') as f:
        json.dump(all_league_data, f, indent=2)
    print(f"\n💾 League data saved to real_league_data.json")

if __name__ == "__main__":
    main()
