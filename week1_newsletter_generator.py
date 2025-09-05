#!/usr/bin/env python3
"""
A League Far Far Away - Live Data Updater
Fetch latest league data and create comprehensive Week 1 analysis
"""

import requests
import json
from datetime import datetime

def fetch_live_league_data():
    """Fetch the most current league data from Sleeper API"""
    league_id = "1197641763607556096"
    
    print("🌌 ======================================================================")
    print("   A LEAGUE FAR FAR AWAY - LIVE DATA UPDATE")
    print("   Fetching latest league information for Week 1 analysis")
    print("🌌 ======================================================================")
    
    try:
        # Get basic league info
        print("\n🔍 Fetching league settings...")
        league_url = f"https://api.sleeper.app/v1/league/{league_id}"
        league_response = requests.get(league_url)
        league_data = league_response.json() if league_response.status_code == 200 else None
        
        # Get users/owners
        print("🔍 Fetching team owners...")
        users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
        users_response = requests.get(users_url)
        users_data = users_response.json() if users_response.status_code == 200 else None
        
        # Get rosters
        print("🔍 Fetching team rosters...")
        rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
        rosters_response = requests.get(rosters_url)
        rosters_data = rosters_response.json() if rosters_response.status_code == 200 else None
        
        # Get matchups for week 1
        print("🔍 Fetching Week 1 matchups...")
        matchups_url = f"https://api.sleeper.app/v1/league/{league_id}/matchups/1"
        matchups_response = requests.get(matchups_url)
        matchups_data = matchups_response.json() if matchups_response.status_code == 200 else None
        
        if league_data and users_data and rosters_data:
            print("✅ Successfully fetched all league data!")
            return {
                'league': league_data,
                'users': users_data,
                'rosters': rosters_data,
                'matchups': matchups_data
            }
        else:
            print("⚠️ Some data unavailable, using framework analysis...")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def analyze_current_league_state(data):
    """Analyze the current league state with live data"""
    if not data:
        return create_framework_analysis()
    
    league = data['league']
    users = data['users']
    rosters = data['rosters']
    matchups = data.get('matchups', [])
    
    print(f"\n📊 **LIVE LEAGUE ANALYSIS:**")
    print("=" * 35)
    print(f"   League Name: {league.get('name', 'A League Far Far Away')}")
    print(f"   Season: {league.get('season', '2025')}")
    print(f"   Week: {league.get('leg', 1)}")
    print(f"   Teams: {len(rosters)}")
    
    # Create user lookup
    user_lookup = {user['user_id']: user for user in users}
    
    # Analyze teams and rosters
    teams = []
    for roster in rosters:
        owner_id = roster.get('owner_id')
        user = user_lookup.get(owner_id, {})
        
        team_data = {
            'roster_id': roster.get('roster_id'),
            'team_name': user.get('metadata', {}).get('team_name', 'Unknown Team'),
            'owner': user.get('display_name', 'Unknown'),
            'avatar': user.get('avatar', ''),
            'players': roster.get('players', []),
            'starters': roster.get('starters', []),
            'wins': roster.get('settings', {}).get('wins', 0),
            'losses': roster.get('settings', {}).get('losses', 0),
            'points_for': roster.get('settings', {}).get('fpts', 0.0),
        }
        teams.append(team_data)
    
    # Sort teams by roster_id for consistent ordering
    teams.sort(key=lambda x: x['roster_id'])
    
    # Analyze Week 1 matchups if available
    week1_matchups = []
    if matchups:
        matchup_pairs = {}
        for matchup in matchups:
            matchup_id = matchup.get('matchup_id')
            if matchup_id not in matchup_pairs:
                matchup_pairs[matchup_id] = []
            matchup_pairs[matchup_id].append(matchup)
        
        for matchup_id, teams_in_matchup in matchup_pairs.items():
            if len(teams_in_matchup) == 2:
                team1_roster_id = teams_in_matchup[0]['roster_id']
                team2_roster_id = teams_in_matchup[1]['roster_id']
                
                team1 = next((t for t in teams if t['roster_id'] == team1_roster_id), None)
                team2 = next((t for t in teams if t['roster_id'] == team2_roster_id), None)
                
                if team1 and team2:
                    week1_matchups.append({
                        'matchup_id': matchup_id,
                        'team1': team1,
                        'team2': team2,
                        'team1_points': teams_in_matchup[0].get('points', 0),
                        'team2_points': teams_in_matchup[1].get('points', 0)
                    })
    
    return {
        'league': league,
        'teams': teams,
        'matchups': week1_matchups,
        'settings': league.get('scoring_settings', {}),
        'roster_positions': league.get('roster_positions', [])
    }

def create_framework_analysis():
    """Create analysis using framework when API data unavailable"""
    teams = [
        {"roster_id": 1, "team_name": "Foxtrot", "owner": "Nivet", "tier": "Championship"},
        {"roster_id": 2, "team_name": "Lights, Camera, JACKSON🔥", "owner": "mjwuAU", "tier": "Championship"},
        {"roster_id": 3, "team_name": "Stone and Sky", "owner": "OldManLoganX", "tier": "Contender"},
        {"roster_id": 4, "team_name": "Jordan's Love stuff", "owner": "blazers07", "tier": "Contender"},
        {"roster_id": 5, "team_name": "Josh the tip", "owner": "bowick13", "tier": "Playoff Hunt"},
        {"roster_id": 6, "team_name": "Allen and Associates", "owner": "cdnoles", "tier": "Playoff Hunt"},
        {"roster_id": 7, "team_name": "Unknown Team", "owner": "Wallliie", "tier": "Middle Pack"},
        {"roster_id": 8, "team_name": "CDL Drizzy", "owner": "jhud12", "tier": "Middle Pack"},
        {"roster_id": 9, "team_name": "CokerCola", "owner": "CokerCola", "tier": "Rebuild"},
        {"roster_id": 10, "team_name": "Unknown Team", "owner": "elalande", "tier": "Rebuild"},
        {"roster_id": 11, "team_name": "Unknown Team", "owner": "icavanah", "tier": "Rebuild"},
        {"roster_id": 12, "team_name": "Show Me Those TDs", "owner": "fowlmouthlass", "tier": "Development"}
    ]
    
    # Create mock Week 1 matchups
    matchups = [
        {"matchup_id": 1, "team1": teams[0], "team2": teams[7]},  # Foxtrot vs CDL Drizzy
        {"matchup_id": 2, "team1": teams[1], "team2": teams[11]}, # Lights Camera vs Show Me TDs
        {"matchup_id": 3, "team1": teams[2], "team2": teams[4]},  # Stone and Sky vs Josh the tip
        {"matchup_id": 4, "team1": teams[3], "team2": teams[5]},  # Jordan's Love vs Allen Associates
        {"matchup_id": 5, "team1": teams[6], "team2": teams[8]},  # Unknown vs CokerCola
        {"matchup_id": 6, "team1": teams[9], "team2": teams[10]}, # elalande vs icavanah
    ]
    
    return {
        'league': {'name': 'A League Far Far Away', 'season': '2025'},
        'teams': teams,
        'matchups': matchups,
        'settings': {'rec': 1.0, 'pass_td': 4},
        'roster_positions': ['QB', 'RB', 'RB', 'WR', 'WR', 'TE', 'FLEX', 'SUPER_FLEX', 'K', 'DEF']
    }

def generate_week1_newsletter(league_data):
    """Generate the exciting Week 1 newsletter in markdown format"""
    
    newsletter = """# 🌌 A LEAGUE FAR FAR AWAY 🌌
## **INAUGURAL DYNASTY SEASON - WEEK 1 NEWSLETTER**
*The Galaxy's Greatest Fantasy Football League Begins*

---

### 🎬 **OPENING CRAWL**

*A long time ago, in a galaxy far, far away...*

**Twelve mighty franchises have assembled** to battle for dynasty supremacy in the most epic fantasy football league this side of the Outer Rim. Armed with **Superflex weapons**, **PPR blasters**, and **28-man deep benches**, these galactic commanders will wage war across multiple seasons for ultimate glory.

The **INAUGURAL SEASON** begins NOW! May the Force... and the fantasy points... be with you.

---

## 📊 **LEAGUE INTEL BRIEFING**
### *Know Your Weapons of War*

**🏆 League Format:** 12-Team Dynasty Superflex PPR  
**⚙️ Scoring System:** 1.0 PPR, 4-point passing TDs  
**🛡️ Roster Construction:** 28 total spots (deep dynasty benches)  
**⚡ Superflex Edge:** QBs are GOLD - hoard them like kyber crystals  
**🎯 Dynasty Focus:** Build for 2025-2027, not just this season  

---

## 🏟️ **WEEK 1 GALACTIC BATTLEGROUND**
### *Six Epic Matchups to Rule the Galaxy*

"""

    # Add matchup analysis
    if league_data['matchups']:
        for i, matchup in enumerate(league_data['matchups'], 1):
            team1 = matchup['team1']
            team2 = matchup['team2']
            
            newsletter += f"""
#### **MATCHUP {i}: THE {get_matchup_subtitle(team1, team2)}**
**🆚 {team1['team_name']} ({team1['owner']}) vs {team2['team_name']} ({team2['owner']})**

{get_detailed_matchup_analysis(team1, team2)}

---
"""

    # Add power rankings
    newsletter += """
## 🏆 **INAUGURAL SEASON POWER RANKINGS**
### *Galactic Senate's Official Dynasty Tier List*

"""
    
    teams_by_tier = organize_teams_by_tier(league_data['teams'])
    
    for tier, teams in teams_by_tier.items():
        newsletter += f"""
### **{tier.upper()} TIER** {get_tier_emoji(tier)}
"""
        for team in teams:
            newsletter += f"**{team['team_name']}** ({team['owner']}) - {get_team_analysis(team)}\n\n"

    # Add players to watch section
    newsletter += """
---

## 👀 **WEEK 1 PLAYERS TO WATCH**
### *Rising Stars in the Galaxy*

### **🏈 QUARTERBACKS (Your Superflex Weapons)**
- **Caleb Williams** - The #1 rookie begins his dynasty reign
- **Anthony Richardson** - Year 2 leap potential with elite rushing floor
- **C.J. Stroud** - Sophomore surge after Rookie of the Year campaign
- **Drake Maye** - Patriots rookie with massive upside
- **Jayden Daniels** - Commanders dual-threat ready to explode

### **🎯 WIDE RECEIVERS (PPR Dynasty Gold)**
- **Rome Odunze** - Bears rookie WR1 with Caleb Williams chemistry
- **Marvin Harrison Jr.** - Cardinals generational talent, instant impact
- **Malik Nabers** - Giants featured role with massive target share
- **Ladd McConkey** - Chargers slot weapon, Herbert's new favorite
- **Jordan Addison** - Vikings WR1 opportunity with Jefferson attention

### **💨 RUNNING BACKS (Dynasty Youth Movement)**
- **Jahmyr Gibbs** - Lions explosive dual-threat back
- **De'Von Achane** - Dolphins speed demon with Tua connection
- **Bijan Robinson** - Falcons workhorse finally unleashed
- **MarShawn Lloyd** - Packers rookie with clear path to carries

### **🏆 TIGHT ENDS (Streaming Gold)**
- **Sam LaPorta** - Lions TE1, consistent weekly starter
- **Brock Bowers** - Raiders rookie unicorn, immediate impact
- **Trey McBride** - Cardinals target monster in Kyler's offense

---

## 🎯 **DYNASTY STRATEGY INTEL**
### *Long-term Galactic Domination*

### **INAUGURAL SEASON PRIORITIES:**
1. **🏈 Establish QB Depth** - Superflex demands 3+ startable QBs
2. **📈 Target Youth** - Dynasty gold is players 25 and under
3. **💰 Accumulate Picks** - Rookie drafts build dynasty foundations
4. **🔄 Stay Active** - Best dynasty managers make 50+ trades/season
5. **⏳ Think 3 Years** - Build for 2026-2027, compete in 2025

### **TRADE TARGETS (Buy Low Opportunities):**
**Struggling Rookies** - Perfect time to acquire future stars
**Injured Veterans** - Championship pieces at discount prices  
**QB Depth** - Other owners may undervalue Superflex importance
**Young TEs** - Position scarcity creates future value

### **TRADE AWAY (Sell High Candidates):**
**Aging QBs** - Aaron Rodgers, Russell Wilson won't last
**Veteran TEs** - Travis Kelce, George Kittle at peak value
**Older RBs** - Derrick Henry, Aaron Jones declining assets

---

## 📅 **WEEK 1 BOLD PREDICTIONS**
### *Fortune Favors the Bold*

🔮 **HIGHEST SCORING TEAM:** Lights, Camera, JACKSON🔥 (160+ points)  
🔮 **BIGGEST UPSET:** CokerCola defeats a playoff contender  
🔮 **ROOKIE BREAKOUT:** Rome Odunze goes for 8+ catches, 100+ yards  
🔮 **QB EXPLOSION:** Anthony Richardson rushes for 2 TDs  
🔮 **WAIVER WIRE HERO:** Unknown handcuff RB saves someone's week  

---

## 🏅 **INAUGURAL SEASON AWARDS TO WATCH**

**🏆 EMPEROR'S CUP** - Championship Trophy  
**⚔️ DEATH STAR DESTROYER** - Highest Single Week Score  
**🎯 TRADE FEDERATION MASTER** - Most Active Trader  
**🌟 PADAWAN LEARNER** - Best Rookie Manager Performance  
**💀 SARLACC PIT DWELLER** - Last Place (Punishment TBD)  

---

## 🚨 **LEAGUE ANNOUNCEMENTS**

### **TRADE DEADLINE ALERT:**
Trade deadlines matter in dynasty! Stay active and aggressive.

### **WAIVER WIRE WARFARE:**
FAAB budgets are limited - spend wisely on league-changing adds.

### **DYNASTY ROOKIE DRAFT:**
Post-season rookie draft order determined by playoff results + lottery.

---

## 🎬 **CLOSING CREDITS**

The galaxy awaits your dynasty destiny. Whether you're building for the future or competing for immediate glory, remember: **In dynasty, patience and aggression must balance, like the Force itself.**

Good luck, commanders. May your lineups be strong, your trades be profitable, and your dynasty reign eternal.

**The adventure begins... NOW!**

---

*This newsletter was crafted by the Galactic Fantasy Council  
For weekly updates and trade discussions, join us in the league chat*

🌌 **A LEAGUE FAR FAR AWAY - WHERE LEGENDS ARE BORN** 🌌
"""

    return newsletter

def get_matchup_subtitle(team1, team2):
    """Generate exciting subtitle for matchup"""
    subtitles = [
        "CLASH OF TITANS",
        "BATTLE FOR SUPREMACY", 
        "GALACTIC SHOWDOWN",
        "DYNASTY DUEL",
        "EPIC CONFRONTATION",
        "CHAMPIONSHIP PREVIEW"
    ]
    return subtitles[abs(hash(team1['team_name'] + team2['team_name'])) % len(subtitles)]

def get_detailed_matchup_analysis(team1, team2):
    """Generate detailed matchup analysis"""
    
    # Determine favorite based on team analysis
    team1_tier = get_team_tier(team1)
    team2_tier = get_team_tier(team2) 
    
    tier_rankings = {"Championship": 4, "Contender": 3, "Playoff Hunt": 2, "Middle Pack": 1, "Rebuild": 0, "Development": 0}
    
    if tier_rankings.get(team1_tier, 1) > tier_rankings.get(team2_tier, 1):
        favorite = team1
        underdog = team2
    else:
        favorite = team2
        underdog = team1
    
    return f"""
**📊 MATCHUP BREAKDOWN:**
- **Favorite:** {favorite['team_name']} ({favorite['owner']}) - {get_team_tier(favorite)} tier
- **Underdog:** {underdog['team_name']} ({underdog['owner']}) - {get_team_tier(underdog)} tier

**🎯 KEY BATTLE POINTS:**
- **QB Advantage:** {get_qb_analysis(favorite, underdog)}
- **Skill Position Edge:** {get_skill_analysis(favorite, underdog)}
- **X-Factor:** {get_xfactor_analysis(favorite, underdog)}

**🔮 PREDICTION:** {favorite['team_name']} wins a {get_game_style(favorite, underdog)} battle
**📈 Confidence Level:** {get_confidence_level(favorite, underdog)}
"""

def get_team_tier(team):
    """Determine team tier based on name/owner"""
    championship_teams = ["Foxtrot", "Lights, Camera, JACKSON🔥"]
    contender_teams = ["Stone and Sky", "Jordan's Love stuff"]
    playoff_teams = ["Josh the tip", "Allen and Associates"]
    middle_teams = ["CDL Drizzy"]
    rebuild_teams = ["CokerCola"]
    
    if team['team_name'] in championship_teams:
        return "Championship"
    elif team['team_name'] in contender_teams:
        return "Contender"
    elif team['team_name'] in playoff_teams:
        return "Playoff Hunt"
    elif team['team_name'] in middle_teams:
        return "Middle Pack"
    elif team['team_name'] in rebuild_teams:
        return "Rebuild"
    else:
        return "Development"

def get_qb_analysis(favorite, underdog):
    """Generate QB analysis for matchup"""
    analyses = [
        "Superflex depth gives clear edge to favorite",
        "QB room quality will determine this matchup",
        "Both teams have solid QB foundations",
        "Rookie QB upside vs veteran consistency battle",
        "Mobile QB advantage in rushing matchups"
    ]
    return analyses[abs(hash(favorite['team_name'])) % len(analyses)]

def get_skill_analysis(favorite, underdog):
    """Generate skill position analysis"""
    analyses = [
        "WR depth advantage in PPR format",
        "RB stability vs boom/bust potential",
        "TE streaming vs elite tier difference",
        "Rookie breakout potential on both sides",
        "Veteran consistency vs youthful upside"
    ]
    return analyses[abs(hash(underdog['team_name'])) % len(analyses)]

def get_xfactor_analysis(favorite, underdog):
    """Generate X-factor analysis"""
    factors = [
        "Waiver wire pickups making immediate impact",
        "Rookie performance in inaugural debut",
        "Injury report changes lineup dynamics",
        "Weather conditions affecting outdoor games",
        "Coaching decisions in tight divisional games"
    ]
    return factors[abs(hash(favorite['team_name'] + underdog['team_name'])) % len(factors)]

def get_game_style(favorite, underdog):
    """Determine game style prediction"""
    styles = ["high-scoring", "defensive", "back-and-forth", "close", "potential blowout"]
    return styles[abs(hash(favorite['owner'] + underdog['owner'])) % len(styles)]

def get_confidence_level(favorite, underdog):
    """Generate confidence level"""
    levels = ["High (70%+)", "Medium-High (60-70%)", "Medium (50-60%)", "Toss-up (50/50)"]
    return levels[abs(hash(favorite['team_name'] + underdog['team_name'])) % len(levels)]

def organize_teams_by_tier(teams):
    """Organize teams by tier for power rankings"""
    tiers = {
        "championship": [],
        "contender": [],
        "playoff hunt": [],
        "middle pack": [],
        "rebuild": [],
        "development": []
    }
    
    for team in teams:
        tier = get_team_tier(team).lower().replace(" ", " ")
        if tier in tiers:
            tiers[tier].append(team)
        else:
            tiers["development"].append(team)
    
    return tiers

def get_tier_emoji(tier):
    """Get emoji for tier"""
    emojis = {
        "championship": "🏆",
        "contender": "⚔️",
        "playoff hunt": "🎯",
        "middle pack": "⚡",
        "rebuild": "🏗️",
        "development": "🌱"
    }
    return emojis.get(tier, "🌟")

def get_team_analysis(team):
    """Get brief team analysis"""
    analyses = {
        "Foxtrot": "Dynasty expertise meets inaugural opportunity",
        "Lights, Camera, JACKSON🔥": "Explosive offensive potential with proven management",
        "Stone and Sky": "Consistent performer looking to establish new dynasty",
        "Jordan's Love stuff": "High-ceiling QB play with supporting cast questions",
        "Josh the tip": "Solid foundation with room for growth",
        "Allen and Associates": "Elite QB anchor with depth needs",
        "CDL Drizzy": "Dark horse potential in inaugural season",
        "CokerCola": "Youth movement with long-term upside",
        "Show Me Those TDs": "Touchdown-focused strategy meets reality"
    }
    return analyses.get(team['team_name'], "Unknown potential in inaugural season")

if __name__ == "__main__":
    # Fetch live data
    live_data = fetch_live_league_data()
    
    # Analyze current state
    league_analysis = analyze_current_league_state(live_data)
    
    # Generate newsletter
    newsletter_content = generate_week1_newsletter(league_analysis)
    
    # Save newsletter to markdown file
    with open('/Users/tevinfowler/Documents/Sleepr/Week1_Newsletter.md', 'w') as f:
        f.write(newsletter_content)
    
    print(f"\n🎉 Week 1 Newsletter Generated Successfully!")
    print("📁 Saved as: Week1_Newsletter.md")
    print("📋 Ready to copy/paste into Sleeper league chat!")
    print("\n" + "="*70)
    print("NEWSLETTER PREVIEW:")
    print("="*70)
    print(newsletter_content[:1000] + "...\n[Newsletter continues...]")
