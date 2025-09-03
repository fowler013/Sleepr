"""
Detailed Analysis of Nivet's Dynasty Teams
Foxtrot and House Fowler Analysis
"""

import json
from sleeper_client import SleeperAPIClient

class NivetDynastyAnalysis:
    """Specific analysis for Nivet's teams"""
    
    def __init__(self):
        # Load analysis data
        with open('dynasty_analysis.json', 'r') as f:
            self.dynasty_data = json.load(f)
        
        # Nivet's teams
        self.teams = {
            "A League Far Far Away": {
                "league_id": "1197641763607556096",
                "roster_id": 1,
                "dynasty_score": 200.0,
                "possible_name": "Foxtrot"  # QB-rich team, building phase
            },
            "Stumblin', Bumblin', and Fumblin'": {
                "league_id": "1180092430900092928", 
                "roster_id": 2,
                "dynasty_score": 230.5,
                "possible_name": "House Fowler"  # WR-rich team, higher score
            }
        }
    
    def analyze_team(self, league_name):
        """Detailed analysis of a specific team"""
        team_info = self.teams[league_name]
        league_id = team_info["league_id"]
        roster_id = team_info["roster_id"]
        
        # Find team in dynasty analysis
        dynasty_teams = self.dynasty_data[league_id]['team_evaluations']
        team_data = None
        
        for team in dynasty_teams:
            if team['roster_id'] == roster_id:
                team_data = team
                break
        
        if not team_data:
            print(f"❌ Could not find team data")
            return None
        
        print(f"\n🏈 {team_info['possible_name']} - {league_name}")
        print("=" * 60)
        
        # Basic team info
        print(f"Dynasty Score: {team_data['dynasty_score']:.1f}")
        print(f"League Rank: {self._get_team_rank(dynasty_teams, roster_id)}/12")
        print(f"Strategy: {team_data['strategy_recommendation']}")
        print(f"Record: {team_data['record']}")
        print(f"Points For: {team_data['points_for']}")
        
        # Asset breakdown
        print(f"\nAsset Breakdown:")
        print(f"  Young Assets (≤24): {len(team_data['young_assets'])}")
        print(f"  Aging Assets (≥29): {len(team_data['aging_assets'])}")
        print(f"  Total Roster Value: {team_data['dynasty_score']:.1f}")
        
        # Top young assets
        print(f"\n🌟 Top Young Assets:")
        young_sorted = sorted(team_data['young_assets'], 
                            key=lambda x: x['dynasty_value'], reverse=True)
        
        for i, player in enumerate(young_sorted[:8], 1):
            print(f"  {i:2d}. {player['name']:20} ({player['position']:2}, {player['age']:2}yo, {player['team']}) - Value: {player['dynasty_value']:.1f}")
        
        # Aging assets to consider trading
        if team_data['aging_assets']:
            print(f"\n⏰ Aging Assets (Trade Candidates):")
            aging_sorted = sorted(team_data['aging_assets'], 
                                key=lambda x: x['dynasty_value'], reverse=True)
            
            for i, player in enumerate(aging_sorted[:5], 1):
                print(f"  {i}. {player['name']:20} ({player['position']:2}, {player['age']:2}yo, {player['team']}) - Value: {player['dynasty_value']:.1f}")
        
        # Position analysis
        self._analyze_positions(team_data)
        
        # Specific recommendations
        self._generate_recommendations(team_data, league_name)
        
        return team_data
    
    def _get_team_rank(self, dynasty_teams, roster_id):
        """Get team's rank in the league"""
        sorted_teams = sorted(dynasty_teams, key=lambda x: x['dynasty_score'], reverse=True)
        for i, team in enumerate(sorted_teams, 1):
            if team['roster_id'] == roster_id:
                return i
        return "Unknown"
    
    def _analyze_positions(self, team_data):
        """Analyze team by position"""
        print(f"\n📊 Positional Analysis:")
        
        positions = {}
        all_players = team_data['young_assets'] + team_data['aging_assets']
        
        for player in all_players:
            pos = player['position']
            if pos not in positions:
                positions[pos] = {
                    'players': [],
                    'total_value': 0,
                    'avg_age': 0
                }
            positions[pos]['players'].append(player)
            positions[pos]['total_value'] += player['dynasty_value']
        
        # Calculate stats and display
        for pos in ['QB', 'RB', 'WR', 'TE']:
            if pos in positions:
                players = positions[pos]['players']
                avg_age = sum(p['age'] for p in players) / len(players)
                avg_value = positions[pos]['total_value'] / len(players)
                
                strength = "STRONG" if len(players) >= 3 and avg_value >= 7 else "WEAK"
                print(f"  {pos:2}: {len(players):2d} players, avg age {avg_age:4.1f}, avg value {avg_value:4.1f} - {strength}")
                
                # List top players at position
                top_players = sorted(players, key=lambda x: x['dynasty_value'], reverse=True)[:2]
                for player in top_players:
                    print(f"      └── {player['name']} ({player['age']}yo, {player['dynasty_value']:.1f})")
    
    def _generate_recommendations(self, team_data, league_name):
        """Generate specific recommendations"""
        print(f"\n💡 Specific Recommendations for {league_name}:")
        
        dynasty_score = team_data['dynasty_score']
        young_count = len(team_data['young_assets'])
        aging_count = len(team_data['aging_assets'])
        
        # Strategy-specific advice
        if dynasty_score >= 220:
            print("  🏆 ELITE DYNASTY TEAM:")
            print("    - You're in great shape for the future")
            print("    - Continue patient building approach") 
            print("    - Only trade young assets for elite young talent")
            print("    - Target 2026-2027 championship window")
            
        elif dynasty_score >= 200:
            print("  📈 STRONG DYNASTY POSITION:")
            print("    - Solid foundation, continue youth movement")
            print("    - Trade aging assets for additional picks")
            print("    - Target breakout candidates on waivers")
            print("    - Build toward 2025-2026 competitiveness")
            
        else:
            print("  🔧 REBUILDING PHASE:")
            print("    - Sell ALL aging assets immediately")
            print("    - Accumulate 2025 & 2026 draft picks")
            print("    - Target players under 24 years old")
            print("    - Plan for 2026+ championship window")
        
        # Specific trade suggestions
        print(f"\n  🔄 Trade Suggestions:")
        if team_data['aging_assets']:
            best_aging = max(team_data['aging_assets'], key=lambda x: x['dynasty_value'])
            print(f"    - SELL HIGH: {best_aging['name']} ({best_aging['age']}yo) while still valuable")
        
        if young_count >= 12:
            print(f"    - CONSOLIDATE: Trade young depth for elite young talent")
            print(f"    - TARGET: Top-24 dynasty players under 25")
        
        # Waiver wire focus
        print(f"\n  🎯 Waiver Wire Focus:")
        print("    - Target rookie WRs with increasing snap counts")
        print("    - Monitor RB handcuffs with aging starters")
        print("    - Look for young TEs in good offensive systems")
        
        # 2025 Draft Strategy
        print(f"\n  📋 2025 Draft Strategy:")
        if dynasty_score >= 220:
            print("    - Trade picks for immediate young talent")
            print("    - Focus on BPA (Best Player Available)")
        else:
            print("    - Accumulate early round picks")
            print("    - Target WR and QB in early rounds")
            print("    - Trade veterans for additional picks")
    
    def compare_teams(self):
        """Compare both teams"""
        print(f"\n🆚 TEAM COMPARISON")
        print("=" * 60)
        
        team1_data = None
        team2_data = None
        
        # Analyze both teams
        for league_name in self.teams.keys():
            team_info = self.teams[league_name]
            league_id = team_info["league_id"]
            roster_id = team_info["roster_id"]
            
            dynasty_teams = self.dynasty_data[league_id]['team_evaluations']
            for team in dynasty_teams:
                if team['roster_id'] == roster_id:
                    if league_name == "A League Far Far Away":
                        team1_data = team
                    else:
                        team2_data = team
                    break
        
        if team1_data and team2_data:
            print(f"Foxtrot (A League Far Far Away):")
            print(f"  Dynasty Score: {team1_data['dynasty_score']:.1f}")
            print(f"  Young Assets: {len(team1_data['young_assets'])}")
            print(f"  League Rank: {self._get_team_rank(self.dynasty_data['1197641763607556096']['team_evaluations'], 1)}/12")
            
            print(f"\nHouse Fowler (Stumblin', Bumblin', and Fumblin'):")
            print(f"  Dynasty Score: {team2_data['dynasty_score']:.1f}")
            print(f"  Young Assets: {len(team2_data['young_assets'])}")  
            print(f"  League Rank: {self._get_team_rank(self.dynasty_data['1180092430900092928']['team_evaluations'], 2)}/12")
            
            # Overall assessment
            print(f"\n🏆 OVERALL ASSESSMENT:")
            if team2_data['dynasty_score'] > team1_data['dynasty_score']:
                diff = team2_data['dynasty_score'] - team1_data['dynasty_score']
                print(f"  House Fowler is your stronger dynasty team (+{diff:.1f} points)")
                print(f"  House Fowler: Championship contender in 1-2 years")
                print(f"  Foxtrot: Solid team, focus on youth accumulation")
            else:
                print(f"  Both teams are well-positioned for the future")
            
            print(f"\n📅 TIMELINE:")
            print(f"  House Fowler: Compete in 2025-2026")
            print(f"  Foxtrot: Compete in 2026-2027")

def main():
    """Run Nivet's dynasty analysis"""
    analyzer = NivetDynastyAnalysis()
    
    print("🏈 NIVET'S DYNASTY EMPIRE ANALYSIS")
    print("Detailed breakdown of Foxtrot and House Fowler")
    print("=" * 70)
    
    # Analyze both teams
    analyzer.analyze_team("A League Far Far Away")  # Foxtrot
    analyzer.analyze_team("Stumblin', Bumblin', and Fumblin'")  # House Fowler
    
    # Compare teams
    analyzer.compare_teams()
    
    print(f"\n" + "=" * 70)
    print("🎯 KEY TAKEAWAYS:")
    print("1. Both teams are in excellent dynasty position")
    print("2. Focus on youth accumulation and patient building")
    print("3. Trade aging assets before they lose value")
    print("4. Target 2025-2027 championship windows")
    print("5. Monitor rookies and breakout candidates closely")

if __name__ == "__main__":
    main()
