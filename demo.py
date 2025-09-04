#!/usr/bin/env python3
"""
Sleepr Demo Script - Check Your Fantasy Football Teams
This script demonstrates how to use Sleepr to check your dynasty team status
"""

import json
import os
from pathlib import Path

# Sample data based on your existing dynasty analysis
DEMO_USER_DATA = {
    "username": "Nivet",
    "teams": [
        {
            "league_name": "A League Far Far Away",
            "team_name": "FOXTROT",
            "dynasty_rank": 8,
            "dynasty_score": 200.0,
            "total_teams": 12,
            "status": "STRONG BUILDER",
            "championship_timeline": "2026-2027",
            "key_assets": [
                {"name": "J.J. McCarthy", "position": "QB", "age": 22, "value": "Elite Dynasty Asset"},
                {"name": "Luther Burden", "position": "WR", "age": 21, "value": "Future WR1"},
                {"name": "Jayden Daniels", "position": "QB", "age": 24, "value": "Proven Starter"},
                {"name": "George Pickens", "position": "WR", "age": 24, "value": "Ascending Talent"}
            ],
            "recommendations": [
                "TRADE: Mike Gesicki + Russell Wilson + Aaron Jones",
                "TARGET: Young RBs and draft picks",
                "ACCUMULATE: 2025 & 2026 draft picks"
            ]
        },
        {
            "league_name": "Stumblin', Bumblin', and Fumblin'",
            "team_name": "HOUSE FOWLER",
            "dynasty_rank": 2,
            "dynasty_score": 230.5,
            "total_teams": 12,
            "status": "ELITE DYNASTY",
            "championship_timeline": "2025-2026",
            "key_assets": [
                {"name": "Keon Coleman", "position": "WR", "age": 22, "value": "Future WR1 Upside"},
                {"name": "Pat Bryant", "position": "WR", "age": 22, "value": "High-Ceiling Prospect"},
                {"name": "Tetairoa McMillan", "position": "WR", "age": 22, "value": "Elite Rookie WR"},
                {"name": "Jonathon Brooks", "position": "RB", "age": 22, "value": "Potential RB1"}
            ],
            "recommendations": [
                "TRADE: Dallas Goedert - sell before value drops",
                "TARGET: Young elite QB (CJ Stroud tier)",
                "TARGET: Young elite TE (Brock Bowers tier)",
                "HOLD: All young WR assets - dynasty goldmine"
            ]
        }
    ]
}

def display_team_status(username="Nivet"):
    """Display comprehensive team status for a user"""
    print("🏈 " + "="*60)
    print(f"   SLEEPR FANTASY FOOTBALL - {username.upper()}'S TEAMS")
    print("🏈 " + "="*60)
    print()
    
    user_data = DEMO_USER_DATA
    
    if not user_data["teams"]:
        print("❌ No teams found. Make sure you've synced your Sleeper leagues!")
        return
    
    # Overall summary
    total_teams = len(user_data["teams"])
    avg_rank = sum(team["dynasty_rank"] for team in user_data["teams"]) / total_teams
    
    print(f"📊 DYNASTY EMPIRE OVERVIEW")
    print(f"   Total Teams: {total_teams}")
    print(f"   Average Dynasty Rank: #{avg_rank:.1f}")
    print(f"   Championship Windows: Multiple elite opportunities")
    print()
    
    # Display each team
    for i, team in enumerate(user_data["teams"], 1):
        print(f"🏆 TEAM {i}: {team['team_name']}")
        print(f"   League: {team['league_name']}")
        print(f"   Dynasty Rank: #{team['dynasty_rank']} of {team['total_teams']} (Score: {team['dynasty_score']})")
        print(f"   Status: {team['status']}")
        print(f"   Championship Timeline: {team['championship_timeline']}")
        print()
        
        print("   🌟 KEY ASSETS:")
        for asset in team["key_assets"]:
            print(f"      • {asset['name']} ({asset['position']}, {asset['age']}) - {asset['value']}")
        print()
        
        print("   📈 RECOMMENDED ACTIONS:")
        for rec in team["recommendations"]:
            print(f"      • {rec}")
        print()
        print("-" * 60)
        print()
    
    # Quick action items
    print("🎯 IMMEDIATE PRIORITIES:")
    print("   1. Monitor waiver wire for breakout WR prospects")
    print("   2. Consider trading aging veterans for picks")
    print("   3. Target young QB/TE upgrades")
    print("   4. Accumulate 2025 & 2026 draft capital")
    print()
    
    print("🔗 NEXT STEPS:")
    print("   • Run: `python src/analytics.py` for detailed projections")
    print("   • Run: `make run-api` to start the web dashboard")
    print("   • Visit: http://localhost:8080/swagger for API docs")
    print("   • Check: Dynasty reports in /analytics/reports/")

def show_quick_stats():
    """Show quick stats and key metrics"""
    print("📊 QUICK DYNASTY METRICS:")
    print()
    
    teams = DEMO_USER_DATA["teams"]
    
    for team in teams:
        status_emoji = "🚀" if "ELITE" in team["status"] else "📈"
        print(f"{status_emoji} {team['team_name']}")
        print(f"   Dynasty Rank: #{team['dynasty_rank']} | Score: {team['dynasty_score']}")
        print(f"   Young Assets: {len([a for a in team['key_assets'] if a['age'] <= 23])} players under 24")
        print()

def show_trade_targets():
    """Display current trade targets and opportunities"""
    print("🔄 TRADE OPPORTUNITIES:")
    print()
    
    print("SELL TARGETS (High Value, Aging):")
    print("   • Russell Wilson (QB) - Get picks before retirement")
    print("   • Aaron Jones (RB) - Sell high on veteran production")
    print("   • Dallas Goedert (TE) - Move before decline")
    print()
    
    print("BUY TARGETS (Youth + Upside):")
    print("   • Young RBs: Omarion Hampton, TreVeyon Henderson")
    print("   • Elite QBs: CJ Stroud, Anthony Richardson")
    print("   • Future TEs: Brock Bowers, Sam LaPorta")
    print()

def main():
    """Main demo function"""
    print("🏈 Welcome to Sleepr Fantasy Football Management!")
    print()
    
    while True:
        print("Choose an option:")
        print("1. 📊 View Team Status")
        print("2. 📈 Quick Stats")
        print("3. 🔄 Trade Opportunities")
        print("4. 📋 How to use the full app")
        print("5. 🚪 Exit")
        print()
        
        choice = input("Enter choice (1-5): ").strip()
        print()
        
        if choice == "1":
            display_team_status()
        elif choice == "2":
            show_quick_stats()
        elif choice == "3":
            show_trade_targets()
        elif choice == "4":
            show_how_to_use()
        elif choice == "5":
            print("🏈 Thanks for using Sleepr! Good luck with your dynasty teams!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        print()
        input("Press Enter to continue...")
        print("\n" + "="*60 + "\n")

def show_how_to_use():
    """Show how to use the full application"""
    print("🚀 HOW TO USE SLEEPR:")
    print()
    print("1. SETUP (with Docker):")
    print("   docker compose up -d          # Start all services")
    print("   make db-migrate                # Run database migrations")
    print("   make db-seed                   # Add sample data")
    print()
    print("2. SYNC YOUR TEAMS:")
    print("   • Visit http://localhost:8080/swagger")
    print("   • Use POST /api/users/sync-sleeper")
    print("   • Enter your Sleeper username")
    print()
    print("3. VIEW ANALYTICS:")
    print("   • Dashboard: http://localhost:3000")
    print("   • API: http://localhost:8080")
    print("   • Analytics: http://localhost:8000")
    print("   • Monitoring: http://localhost:3001 (Grafana)")
    print()
    print("4. FEATURES:")
    print("   • Dynasty team analysis")
    print("   • Trade recommendations")
    print("   • Waiver wire insights")
    print("   • Player projections")
    print("   • League comparisons")
    print()
    print("5. DEVELOPMENT:")
    print("   make run-api                   # Go backend")
    print("   make run-analytics             # Python ML engine")
    print("   cd web/frontend && npm start  # React frontend")

if __name__ == "__main__":
    main()
