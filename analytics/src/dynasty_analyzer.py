"""
Dynasty-Specific Analytics for Your Sleeper Leagues
Custom analysis for "A League Far Far Away" and "Stumblin', Bumblin', and Fumblin'"
"""

import json
import pandas as pd
from datetime import datetime
from sleeper_client import SleeperAPIClient, SleeperDataProcessor

class DynastyAnalyzer:
    """Advanced dynasty analytics for your specific leagues"""
    
    def __init__(self):
        self.client = SleeperAPIClient()
        self.processor = SleeperDataProcessor(self.client)
        
        # Your specific leagues
        self.leagues = {
            "1197641763607556096": "A League Far Far Away",
            "1180092430900092928": "Stumblin', Bumblin', and Fumblin'"
        }
    
    def analyze_dynasty_assets(self, league_id: str) -> dict:
        """Analyze dynasty assets for long-term value"""
        try:
            # Get current players data
            players_db = self.client.get_players()
            league_data = self.processor.analyze_league(league_id)
            
            dynasty_analysis = {
                'league_name': league_data['league_info']['name'],
                'league_id': league_id,
                'team_evaluations': [],
                'league_insights': {}
            }
            
            # Analyze each team's dynasty value
            for roster in league_data['rosters']:
                team_eval = self._evaluate_dynasty_team(roster, players_db)
                dynasty_analysis['team_evaluations'].append(team_eval)
            
            # Sort teams by dynasty score
            dynasty_analysis['team_evaluations'].sort(
                key=lambda x: x['dynasty_score'], reverse=True
            )
            
            # Add league-wide insights
            dynasty_analysis['league_insights'] = self._generate_league_insights(
                dynasty_analysis['team_evaluations']
            )
            
            return dynasty_analysis
            
        except Exception as e:
            print(f"Error in dynasty analysis: {e}")
            return {}
    
    def _evaluate_dynasty_team(self, roster: dict, players_db: dict) -> dict:
        """Evaluate a single team's dynasty value"""
        team_eval = {
            'owner': roster['owner'],
            'roster_id': roster['roster_id'],
            'record': f"{roster['wins']}-{roster['losses']}-{roster['ties']}",
            'points_for': roster['points_for'],
            'young_assets': [],
            'aging_assets': [],
            'elite_assets': [],
            'dynasty_score': 0,
            'strategy_recommendation': '',
            'trade_suggestions': []
        }
        
        # Analyze each player on the roster
        for player_id in roster['players']:
            if player_id in players_db:
                player = players_db[player_id]
                player_analysis = self._analyze_player_dynasty_value(player)
                
                # Categorize players
                if player_analysis['age'] <= 24 and player_analysis['position'] in ['RB', 'WR', 'QB']:
                    team_eval['young_assets'].append(player_analysis)
                elif player_analysis['age'] >= 29:
                    team_eval['aging_assets'].append(player_analysis)
                
                # Add to dynasty score
                team_eval['dynasty_score'] += player_analysis['dynasty_value']
        
        # Generate strategy recommendation
        team_eval['strategy_recommendation'] = self._recommend_dynasty_strategy(team_eval, roster)
        
        return team_eval
    
    def _analyze_player_dynasty_value(self, player: dict) -> dict:
        """Analyze individual player's dynasty value"""
        # Extract player info
        age = player.get('age', 25)  # Default age if not available
        position = player.get('position', 'UNKNOWN')
        years_exp = player.get('years_exp', 0)
        
        # Base dynasty value calculation
        dynasty_value = 5.0  # Base value
        
        # Age factor (younger = more valuable in dynasty)
        if age <= 22:
            dynasty_value += 3.0
        elif age <= 25:
            dynasty_value += 2.0
        elif age <= 27:
            dynasty_value += 1.0
        elif age >= 30:
            dynasty_value -= 2.0
        elif age >= 32:
            dynasty_value -= 4.0
        
        # Position factor (QB/WR age better than RB)
        if position == 'QB' and age <= 30:
            dynasty_value += 2.0
        elif position == 'WR' and age <= 28:
            dynasty_value += 1.5
        elif position == 'RB' and age >= 28:
            dynasty_value -= 2.0
        elif position == 'TE' and age <= 26:
            dynasty_value += 1.0
        
        return {
            'player_id': player.get('player_id', ''),
            'name': f"{player.get('first_name', '')} {player.get('last_name', '')}".strip(),
            'position': position,
            'age': age,
            'years_exp': years_exp,
            'team': player.get('team', ''),
            'dynasty_value': max(0, dynasty_value)  # Don't go negative
        }
    
    def _recommend_dynasty_strategy(self, team_eval: dict, roster: dict) -> str:
        """Recommend dynasty strategy based on team composition"""
        win_pct = roster['wins'] / max(1, roster['wins'] + roster['losses'])
        young_count = len(team_eval['young_assets'])
        aging_count = len(team_eval['aging_assets'])
        dynasty_score = team_eval['dynasty_score']
        
        if win_pct >= 0.7 and dynasty_score >= 100:
            return "Championship Window - Aggressive moves for title"
        elif win_pct >= 0.6 and young_count >= 5:
            return "Contender with Future - Selective improvements"
        elif young_count >= 8:
            return "Youth Movement - Build for 2-3 years out"
        elif aging_count >= 6 and win_pct <= 0.4:
            return "Full Rebuild - Trade veterans for picks and youth"
        elif dynasty_score <= 60:
            return "Asset Accumulation - Focus on picks and young talent"
        else:
            return "Steady Building - Balanced approach"
    
    def _generate_league_insights(self, team_evaluations: list) -> dict:
        """Generate league-wide dynasty insights"""
        dynasty_scores = [team['dynasty_score'] for team in team_evaluations]
        
        return {
            'average_dynasty_score': sum(dynasty_scores) / len(dynasty_scores),
            'top_dynasty_team': team_evaluations[0]['owner'] if team_evaluations else 'N/A',
            'most_rebuilding': team_evaluations[-1]['owner'] if team_evaluations else 'N/A',
            'competitive_balance': max(dynasty_scores) - min(dynasty_scores) if dynasty_scores else 0,
            'league_phase': self._determine_league_phase(team_evaluations)
        }
    
    def _determine_league_phase(self, team_evaluations: list) -> str:
        """Determine what phase the league is in"""
        rebuilding_count = sum(1 for team in team_evaluations 
                             if 'Rebuild' in team['strategy_recommendation'])
        contending_count = sum(1 for team in team_evaluations 
                             if 'Championship' in team['strategy_recommendation'])
        
        if contending_count >= 4:
            return "Highly Competitive - Multiple contenders"
        elif rebuilding_count >= 6:
            return "Transitional - Many teams rebuilding"
        else:
            return "Balanced - Mixed strategies"
    
    def generate_weekly_insights(self, league_id: str, week: int = 1) -> dict:
        """Generate weekly insights for dynasty management"""
        try:
            matchups = self.client.get_matchups(league_id, week)
            transactions = self.client.get_transactions(league_id, week)
            
            insights = {
                'week': week,
                'league_name': self.leagues.get(league_id, 'Unknown League'),
                'matchup_analysis': [],
                'transaction_trends': {},
                'waiver_wire_priority': []
            }
            
            # Analyze matchups for dynasty implications
            for matchup in matchups:
                if matchup.get('matchup_id'):
                    insights['matchup_analysis'].append({
                        'roster_id': matchup['roster_id'],
                        'points': matchup.get('points', 0),
                        'starters': matchup.get('starters', []),
                        'dynasty_impact': 'Analyze starter choices for future value'
                    })
            
            # Analyze transactions
            position_adds = {}
            for transaction in transactions:
                transaction_type = transaction.get('type', 'unknown')
                if transaction_type in ['waiver', 'free_agent']:
                    adds = transaction.get('adds', {})
                    for player_id in adds.keys():
                        # Would need to look up player position
                        position_adds[player_id] = transaction
            
            insights['transaction_trends'] = {
                'total_transactions': len(transactions),
                'waiver_activity': len([t for t in transactions if t.get('type') == 'waiver']),
                'trade_activity': len([t for t in transactions if t.get('type') == 'trade'])
            }
            
            return insights
            
        except Exception as e:
            print(f"Error generating weekly insights: {e}")
            return {}

def main():
    """Run dynasty analysis for your leagues"""
    analyzer = DynastyAnalyzer()
    
    print("🏈 Dynasty Analysis for Your Sleeper Leagues")
    print("=" * 50)
    
    for league_id, league_name in analyzer.leagues.items():
        print(f"\n📊 Analyzing {league_name}...")
        
        # Dynasty asset analysis
        dynasty_analysis = analyzer.analyze_dynasty_assets(league_id)
        
        if dynasty_analysis:
            print(f"\nTop Dynasty Teams in {league_name}:")
            for i, team in enumerate(dynasty_analysis['team_evaluations'][:5], 1):
                print(f"{i}. {team['owner']} - Score: {team['dynasty_score']:.1f}")
                print(f"   Strategy: {team['strategy_recommendation']}")
                print(f"   Record: {team['record']}")
                print(f"   Young Assets: {len(team['young_assets'])}")
                print(f"   Aging Assets: {len(team['aging_assets'])}")
                print()
            
            # League insights
            insights = dynasty_analysis['league_insights']
            print(f"League Phase: {insights['league_phase']}")
            print(f"Average Dynasty Score: {insights['average_dynasty_score']:.1f}")
            print(f"Competitive Balance: {insights['competitive_balance']:.1f}")
        
        # Weekly insights
        weekly_insights = analyzer.generate_weekly_insights(league_id, 1)
        if weekly_insights:
            print(f"\nWeek 1 Transaction Activity:")
            trends = weekly_insights['transaction_trends']
            print(f"Total Transactions: {trends['total_transactions']}")
            print(f"Waiver Claims: {trends['waiver_activity']}")
            print(f"Trades: {trends['trade_activity']}")
        
        print("\n" + "="*50)
    
    # Save detailed analysis
    all_analysis = {}
    for league_id in analyzer.leagues.keys():
        all_analysis[league_id] = analyzer.analyze_dynasty_assets(league_id)
    
    with open('dynasty_analysis.json', 'w') as f:
        json.dump(all_analysis, f, indent=2)
    
    print("📈 Detailed dynasty analysis saved to dynasty_analysis.json")

if __name__ == "__main__":
    main()
