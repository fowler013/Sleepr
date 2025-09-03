"""
Personal Dynasty Assistant for Your Sleeper Teams
Customized analysis for your specific teams: "Foxtrot" and "House Fowler"
"""

import json
import pandas as pd
from datetime import datetime
from sleeper_client import SleeperAPIClient, SleeperDataProcessor

class PersonalDynastyAssistant:
    """Your personal dynasty advisor for Foxtrot and House Fowler"""
    
    def __init__(self):
        self.client = SleeperAPIClient()
        self.processor = SleeperDataProcessor(self.client)
        
        # Your leagues
        self.leagues = {
            "1197641763607556096": "A League Far Far Away",
            "1180092430900092928": "Stumblin', Bumblin', and Fumblin'"
        }
        
        # Your team names and possible usernames
        self.your_teams = {
            "Foxtrot": None,  # Will find the actual roster_id
            "House Fowler": None
        }
        
        # Load league data
        with open('league_analysis.json', 'r') as f:
            self.league_data = json.load(f)
        
        # Load dynasty analysis
        with open('dynasty_analysis.json', 'r') as f:
            self.dynasty_data = json.load(f)
    
    def find_your_teams(self, your_username=None):
        """Find your teams by username or manual identification"""
        print("🔍 Finding your teams in the leagues...")
        
        for league_id, league_name in self.leagues.items():
            print(f"\n📊 League: {league_name}")
            rosters = self.league_data[league_id]['analysis']['rosters']
            
            print("Available teams:")
            for i, roster in enumerate(rosters, 1):
                print(f"{i:2d}. {roster['owner']} (Roster ID: {roster['roster_id']})")
        
        # Manual identification since team names aren't directly available
        return self._manual_team_identification()
    
    def _manual_team_identification(self):
        """Helper to manually identify your teams"""
        print("\n🎯 Please identify your teams from the lists above:")
        print("Based on the roster analysis, please let me know which usernames correspond to:")
        print("- Foxtrot team")
        print("- House Fowler team")
        
        # For now, I'll analyze all teams and you can tell me which ones are yours
        return {
            "need_manual_identification": True,
            "available_teams": self._get_all_team_summaries()
        }
    
    def _get_all_team_summaries(self):
        """Get summary of all teams for identification"""
        all_teams = {}
        
        for league_id, league_name in self.leagues.items():
            all_teams[league_id] = {
                "league_name": league_name,
                "teams": []
            }
            
            rosters = self.league_data[league_id]['analysis']['rosters']
            dynasty_teams = self.dynasty_data[league_id]['team_evaluations']
            
            # Create lookup for dynasty scores
            dynasty_lookup = {team['roster_id']: team for team in dynasty_teams}
            
            for roster in rosters:
                dynasty_info = dynasty_lookup.get(roster['roster_id'], {})
                
                team_summary = {
                    "owner": roster['owner'],
                    "roster_id": roster['roster_id'],
                    "record": f"{roster['wins']}-{roster['losses']}-{roster['ties']}",
                    "points_for": roster['points_for'],
                    "dynasty_score": dynasty_info.get('dynasty_score', 0),
                    "young_assets": len(dynasty_info.get('young_assets', [])),
                    "aging_assets": len(dynasty_info.get('aging_assets', [])),
                    "strategy": dynasty_info.get('strategy_recommendation', 'Unknown')
                }
                all_teams[league_id]["teams"].append(team_summary)
        
        return all_teams
    
    def analyze_specific_team(self, league_id, roster_id, team_name):
        """Detailed analysis of a specific team"""
        print(f"\n🏈 Analyzing {team_name}")
        print("=" * 50)
        
        # Find team in dynasty analysis
        dynasty_teams = self.dynasty_data[league_id]['team_evaluations']
        team_data = None
        
        for team in dynasty_teams:
            if team['roster_id'] == roster_id:
                team_data = team
                break
        
        if not team_data:
            print(f"❌ Could not find team data for roster {roster_id}")
            return
        
        # Basic team info
        print(f"Owner: {team_data['owner']}")
        print(f"Record: {team_data['record']}")
        print(f"Points For: {team_data['points_for']}")
        print(f"Dynasty Score: {team_data['dynasty_score']:.1f}")
        print(f"Strategy: {team_data['strategy_recommendation']}")
        
        # Young assets analysis
        print(f"\n🌟 Young Assets ({len(team_data['young_assets'])} players):")
        young_sorted = sorted(team_data['young_assets'], 
                            key=lambda x: x['dynasty_value'], reverse=True)
        
        for player in young_sorted[:10]:  # Top 10
            print(f"  • {player['name']} ({player['position']}, {player['age']}yo) - "
                  f"Value: {player['dynasty_value']:.1f} - {player['team']}")
        
        # Aging assets analysis
        if team_data['aging_assets']:
            print(f"\n⏰ Aging Assets ({len(team_data['aging_assets'])} players):")
            aging_sorted = sorted(team_data['aging_assets'], 
                                key=lambda x: x['dynasty_value'], reverse=True)
            
            for player in aging_sorted[:5]:  # Top 5
                print(f"  • {player['name']} ({player['position']}, {player['age']}yo) - "
                      f"Value: {player['dynasty_value']:.1f} - {player['team']}")
        
        # Dynasty recommendations
        print(f"\n💡 Dynasty Recommendations:")
        self._generate_team_recommendations(team_data, league_id)
        
        return team_data
    
    def _generate_team_recommendations(self, team_data, league_id):
        """Generate specific recommendations for the team"""
        strategy = team_data['strategy_recommendation']
        young_count = len(team_data['young_assets'])
        aging_count = len(team_data['aging_assets'])
        dynasty_score = team_data['dynasty_score']
        
        print(f"  🎯 Primary Strategy: {strategy}")
        
        if "Youth Movement" in strategy:
            print("  📈 Youth Movement Strategy:")
            print("    - Continue accumulating young talent")
            print("    - Trade aging assets for picks/young players")
            print("    - Target rookie WRs and young QBs")
            print("    - Be patient - compete in 2-3 years")
            
        elif "Championship Window" in strategy:
            print("  🏆 Championship Strategy:")
            print("    - Trade picks for proven veterans")
            print("    - Target immediate impact players")
            print("    - Consider trading young depth for stars")
            print("    - Win-now mentality")
            
        elif "Rebuilding" in strategy:
            print("  🔧 Rebuilding Strategy:")
            print("    - Sell ALL aging assets immediately")
            print("    - Accumulate 2025-2027 draft picks")
            print("    - Target players under 25 years old")
            print("    - Plan for 3+ year rebuild")
        
        # Specific positional advice
        print(f"\n  🎯 Positional Focus Areas:")
        self._analyze_positional_needs(team_data)
        
        # Trade suggestions
        print(f"\n  🔄 Trade Suggestions:")
        self._suggest_trades(team_data, strategy)
    
    def _analyze_positional_needs(self, team_data):
        """Analyze positional strengths and weaknesses"""
        positions = {}
        
        # Count players by position
        all_players = team_data['young_assets'] + team_data['aging_assets']
        for player in all_players:
            pos = player['position']
            if pos not in positions:
                positions[pos] = {'count': 0, 'avg_age': 0, 'total_value': 0}
            positions[pos]['count'] += 1
            positions[pos]['avg_age'] += player['age']
            positions[pos]['total_value'] += player['dynasty_value']
        
        # Calculate averages
        for pos in positions:
            if positions[pos]['count'] > 0:
                positions[pos]['avg_age'] /= positions[pos]['count']
                positions[pos]['avg_value'] = positions[pos]['total_value'] / positions[pos]['count']
        
        for pos, data in positions.items():
            status = "STRONG" if data['count'] >= 3 and data['avg_value'] >= 7 else "WEAK"
            print(f"    {pos}: {data['count']} players, avg age {data['avg_age']:.1f}, "
                  f"avg value {data.get('avg_value', 0):.1f} - {status}")
    
    def _suggest_trades(self, team_data, strategy):
        """Suggest specific trade scenarios"""
        if "Youth Movement" in strategy:
            if team_data['aging_assets']:
                oldest_valuable = max(team_data['aging_assets'], 
                                    key=lambda x: x['age'])
                print(f"    - SELL: {oldest_valuable['name']} while value remains")
                print(f"    - TARGET: 2025 1st round picks")
        
        elif "Championship Window" in strategy:
            if len(team_data['young_assets']) > 10:
                print(f"    - TRADE: Young depth pieces for proven veterans")
                print(f"    - TARGET: Top-12 RBs or WRs for playoff push")
        
        print(f"    - Monitor: Waiver wire for breakout candidates")
        print(f"    - Focus: Trade deadline decisions based on record")
    
    def compare_your_teams(self, team1_data, team2_data):
        """Compare your two dynasty teams"""
        print(f"\n🆚 Comparing Your Teams")
        print("=" * 50)
        
        teams = [
            ("Foxtrot", team1_data),
            ("House Fowler", team2_data)
        ]
        
        for name, data in teams:
            if data:
                print(f"\n{name}:")
                print(f"  Dynasty Score: {data['dynasty_score']:.1f}")
                print(f"  Young Assets: {len(data['young_assets'])}")
                print(f"  Strategy: {data['strategy_recommendation']}")
        
        # Determine which team is better positioned
        if team1_data and team2_data:
            if team1_data['dynasty_score'] > team2_data['dynasty_score']:
                print(f"\n🏆 Foxtrot has better long-term dynasty value")
            else:
                print(f"\n🏆 House Fowler has better long-term dynasty value")

def main():
    """Run personal dynasty analysis"""
    assistant = PersonalDynastyAssistant()
    
    print("🏈 Personal Dynasty Assistant for Foxtrot & House Fowler")
    print("=" * 60)
    
    # First, let's see all teams to identify yours
    team_summaries = assistant.find_your_teams()
    
    if team_summaries.get("need_manual_identification"):
        print("\n📋 All Teams Summary:")
        
        for league_id, league_info in team_summaries["available_teams"].items():
            print(f"\n🏟️  {league_info['league_name']}:")
            print("-" * 40)
            
            for team in sorted(league_info['teams'], 
                             key=lambda x: x['dynasty_score'], reverse=True):
                print(f"{team['owner']:15} | Score: {team['dynasty_score']:6.1f} | "
                      f"Young: {team['young_assets']:2d} | Aging: {team['aging_assets']:2d} | "
                      f"{team['strategy']}")
        
        print("\n" + "=" * 60)
        print("🎯 NEXT STEPS:")
        print("1. Identify which usernames are 'Foxtrot' and 'House Fowler'")
        print("2. Update the script with your specific roster IDs")
        print("3. Get detailed dynasty analysis for your teams")
        print("\nExample: If 'jhud12' is Foxtrot, I can analyze that team specifically")

if __name__ == "__main__":
    main()
