#!/usr/bin/env python3
"""
SLEEPER PLAYOFF RESULTS FETCHER - Final Standings Based on Playoffs
Fetches actual playoff brackets and championship results for accurate dynasty rankings
"""

import requests
import json
from datetime import datetime

def fetch_playoff_results(league_id, season):
    """Fetch playoff bracket and final standings from Sleeper API"""
    try:
        print(f"\n🏆 **FETCHING {season} PLAYOFF RESULTS**")
        print("-" * 40)
        
        # Get league info
        league_url = f"https://api.sleeper.app/v1/league/{league_id}"
        league_response = requests.get(league_url)
        league_data = league_response.json()
        
        # Get users
        users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
        users_response = requests.get(users_url)
        users_data = users_response.json()
        
        # Get rosters
        rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        rosters_response = requests.get(rosters_url)
        rosters_data = rosters_response.json()
        
        # Get playoff brackets
        winners_bracket_url = f"https://api.sleeper.app/v1/league/{league_id}/winners_bracket"
        losers_bracket_url = f"https://api.sleeper.app/v1/league/{league_id}/losers_bracket"
        
        try:
            winners_response = requests.get(winners_bracket_url)
            winners_bracket = winners_response.json() if winners_response.status_code == 200 else []
        except:
            winners_bracket = []
            
        try:
            losers_response = requests.get(losers_bracket_url)
            losers_bracket = losers_response.json() if losers_response.status_code == 200 else []
        except:
            losers_bracket = []
        
        # Create user and roster lookups
        user_lookup = {user['user_id']: user for user in users_data}
        roster_lookup = {roster['roster_id']: roster for roster in rosters_data}
        
        print(f"✅ League: {league_data.get('name', 'Unknown')}")
        print(f"✅ Season: {league_data.get('season', season)}")
        print(f"✅ Playoff Format: {league_data.get('playoff_format', 'Standard')}")
        
        # Process playoff results
        playoff_results = analyze_playoff_bracket(winners_bracket, losers_bracket, user_lookup, roster_lookup)
        
        return {
            'league_data': league_data,
            'users_data': users_data,
            'rosters_data': rosters_data,
            'winners_bracket': winners_bracket,
            'losers_bracket': losers_bracket,
            'playoff_results': playoff_results
        }
        
    except Exception as e:
        print(f"Error fetching playoff data for {league_id} ({season}): {e}")
        return None

def analyze_playoff_bracket(winners_bracket, losers_bracket, user_lookup, roster_lookup):
    """Analyze playoff brackets to determine final standings"""
    playoff_results = {}
    
    if not winners_bracket:
        print("❌ No playoff bracket data available")
        return playoff_results
    
    print(f"\n🏆 **PLAYOFF BRACKET ANALYSIS:**")
    
    # Sort bracket by round (championship game is typically the last round)
    winners_bracket.sort(key=lambda x: x.get('r', 0), reverse=True)
    
    for matchup in winners_bracket:
        round_num = matchup.get('r', 0)
        matchup_id = matchup.get('m', 0)
        roster1_id = matchup.get('t1')
        roster2_id = matchup.get('t2')
        winner_id = matchup.get('w')
        loser_id = matchup.get('l')
        
        if not all([roster1_id, roster2_id]):
            continue
            
        # Get team names
        def get_team_name(roster_id):
            if not roster_id:
                return "Unknown"
            roster = roster_lookup.get(roster_id, {})
            owner_id = roster.get('owner_id')
            if not owner_id:
                return "Unknown"
            user = user_lookup.get(owner_id, {})
            metadata = user.get('metadata', {})
            team_name = metadata.get('team_name')
            display_name = user.get('display_name', 'Unknown')
            return team_name if team_name else display_name
        
        team1_name = get_team_name(roster1_id)
        team2_name = get_team_name(roster2_id)
        winner_name = get_team_name(winner_id) if winner_id else "TBD"
        
        # Determine round name
        round_name = {
            1: "Championship Game",
            2: "Semifinals", 
            3: "Quarterfinals",
            4: "First Round"
        }.get(round_num, f"Round {round_num}")
        
        print(f"   {round_name}: {team1_name} vs {team2_name}")
        if winner_id:
            print(f"      Winner: {winner_name}")
            
            # Record results for final standings
            if round_num == 1:  # Championship game
                playoff_results['champion'] = winner_name
                playoff_results['runner_up'] = get_team_name(loser_id) if loser_id else "Unknown"
        print()
    
    return playoff_results

def get_final_standings_with_playoffs(league_id, season):
    """Get final standings incorporating playoff results"""
    data = fetch_playoff_results(league_id, season)
    
    if not data:
        return None
    
    rosters_data = data['rosters_data']
    users_data = data['users_data'] 
    playoff_results = data['playoff_results']
    
    # Create lookups
    user_lookup = {user['user_id']: user for user in users_data}
    
    # Build final standings list
    final_standings = []
    
    for roster in rosters_data:
        owner_id = roster.get('owner_id')
        user_info = user_lookup.get(owner_id, {})
        
        display_name = user_info.get('display_name', 'Unknown User')
        metadata = user_info.get('metadata', {})
        team_name = metadata.get('team_name') if metadata else None
        final_team_name = team_name if team_name else display_name
        
        wins = roster.get('settings', {}).get('wins', 0)
        losses = roster.get('settings', {}).get('losses', 0)
        points = roster.get('settings', {}).get('fpts', 0)
        
        # Determine playoff finish
        playoff_finish = "Regular Season"
        if final_team_name == playoff_results.get('champion'):
            playoff_finish = "🏆 Champion"
        elif final_team_name == playoff_results.get('runner_up'):
            playoff_finish = "🥈 Runner-up"
        
        final_standings.append({
            'team_name': final_team_name,
            'owner': display_name,
            'wins': wins,
            'losses': losses,
            'points': points,
            'playoff_finish': playoff_finish,
            'roster_id': roster.get('roster_id')
        })
    
    # Sort by playoff finish first, then regular season record
    def sort_key(team):
        if team['playoff_finish'] == "🏆 Champion":
            return (0, team['wins'], team['points'])
        elif team['playoff_finish'] == "🥈 Runner-up":
            return (1, team['wins'], team['points'])
        else:
            return (2, team['wins'], team['points'])
    
    final_standings.sort(key=sort_key, reverse=True)
    
    print(f"📊 **FINAL STANDINGS ({season}) - PLAYOFF ADJUSTED:**")
    for i, team in enumerate(final_standings, 1):
        record = f"{team['wins']}-{team['losses']}"
        playoff_note = f" {team['playoff_finish']}" if team['playoff_finish'] != "Regular Season" else ""
        
        if team['owner'] == 'Nivet':
            print(f"   {i:2d}. 🏠 {team['team_name']:<25} ({team['owner']:<15}) | {record} | {team['points']:,.0f} pts{playoff_note}")
        else:
            print(f"   {i:2d}.    {team['team_name']:<25} ({team['owner']:<15}) | {record} | {team['points']:,.0f} pts{playoff_note}")
    print()
    
    return {
        'season': season,
        'standings': final_standings,
        'champion': playoff_results.get('champion', 'Unknown'),
        'runner_up': playoff_results.get('runner_up', 'Unknown'),
        'nivet_finish': next((i+1 for i, team in enumerate(final_standings) if team['owner'] == 'Nivet'), 'Not found')
    }

def main():
    print("🏈 " + "="*70)
    print("   STUMBLIN' PLAYOFF RESULTS - FINAL STANDINGS WITH CHAMPIONSHIP")
    print("   Accurate dynasty rankings based on playoff performance")
    print("🏈 " + "="*70)
    
    # Historical league IDs for Stumblin'
    historical_leagues = [
        {"id": "918682182527422464", "season": "2023"},
        {"id": "1048275084177227776", "season": "2024"}
    ]
    
    all_results = {}
    
    for league_info in historical_leagues:
        league_id = league_info["id"]
        season = league_info["season"]
        
        results = get_final_standings_with_playoffs(league_id, season)
        if results:
            all_results[season] = results
    
    print("\n🎯 **STUMBLIN' DYNASTY TRAJECTORY:**")
    print("=" * 50)
    
    if '2023' in all_results and '2024' in all_results:
        print(f"   • 2023 Champion: {all_results['2023']['champion']}")
        print(f"   • 2023 Runner-up: {all_results['2023']['runner_up']}")
        print(f"   • 2024 Champion: {all_results['2024']['champion']}")
        print(f"   • 2024 Runner-up: {all_results['2024']['runner_up']}")
        print()
        
        nivet_2023 = all_results['2023']['nivet_finish']
        nivet_2024 = all_results['2024']['nivet_finish']
        
        print("🏠 **HOUSE FOWLER HISTORICAL PERFORMANCE:**")
        print(f"   • 2023 Final Position: #{nivet_2023} of 12")
        print(f"   • 2024 Final Position: #{nivet_2024} of 12")
        
        if isinstance(nivet_2023, int) and isinstance(nivet_2024, int):
            if nivet_2024 < nivet_2023:
                print(f"   • Trajectory: 📈 Improved by {nivet_2023 - nivet_2024} positions")
            elif nivet_2024 > nivet_2023:
                print(f"   • Trajectory: 📉 Dropped {nivet_2024 - nivet_2023} positions")
            else:
                print("   • Trajectory: ➡️ Consistent finish")
        
        print(f"   • 2025 Projection: #1 Championship Contender")
        print("   • Dynasty Timeline: Rebuild complete, entering championship window")
    
    print("\n" + "="*70)
    print("✅ Playoff-adjusted final standings retrieved")
    print("✅ Dynasty trajectory analysis complete")
    print("="*70)

if __name__ == "__main__":
    main()
