from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from .models import (
    PlayerProjectionModel,
    WaiverWireRecommendationModel,
    TradeAnalyzerModel,
    DynastyValueModel
)
from .sleeper_client import SleeperAPIClient
from .data_processor import DataProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sleepr Analytics API",
    description="Advanced analytics and ML models for fantasy football dynasty management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models and clients
sleeper_client = SleeperAPIClient()
data_processor = DataProcessor()
projection_model = PlayerProjectionModel()
waiver_model = WaiverWireRecommendationModel()
trade_analyzer = TradeAnalyzerModel()
dynasty_model = DynastyValueModel()

# Pydantic models for requests/responses
class PlayerProjectionRequest(BaseModel):
    player_id: str
    weeks_ahead: int = 4
    league_settings: Optional[Dict[str, Any]] = None

class PlayerProjectionResponse(BaseModel):
    player_id: str
    player_name: str
    position: str
    team: str
    projected_points: float
    confidence_interval: List[float]
    projection_breakdown: Dict[str, float]
    injury_risk: float
    trending: str  # "up", "down", "stable"

class WaiverWireRequest(BaseModel):
    league_id: str
    team_id: str
    position_needs: Optional[List[str]] = None
    budget_constraint: Optional[float] = None

class WaiverWireRecommendation(BaseModel):
    player_id: str
    player_name: str
    position: str
    team: str
    recommendation_score: float
    projected_points: float
    ownership_percentage: float
    trending_score: float
    reasoning: str
    priority_level: str  # "high", "medium", "low"

class TradeAnalysisRequest(BaseModel):
    giving_players: List[str]
    receiving_players: List[str]
    league_id: str
    team_id: str
    draft_picks: Optional[Dict[str, List[str]]] = None  # year -> [round.pick]

class TradeAnalysisResponse(BaseModel):
    trade_grade: str  # A+, A, B+, B, C+, C, D+, D, F
    value_difference: float
    short_term_impact: Dict[str, float]
    long_term_impact: Dict[str, float]
    position_impact: Dict[str, float]
    risk_assessment: Dict[str, Any]
    recommendation: str
    reasoning: str

class DynastyValueRequest(BaseModel):
    player_id: str
    league_settings: Optional[Dict[str, Any]] = None

class DynastyValueResponse(BaseModel):
    player_id: str
    player_name: str
    current_value: float
    projected_value_1year: float
    projected_value_2year: float
    projected_value_3year: float
    peak_value_year: int
    value_trend: str
    age_curve_position: str
    dynasty_tier: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": {
            "projection_model": projection_model.is_loaded(),
            "waiver_model": waiver_model.is_loaded(),
            "trade_analyzer": trade_analyzer.is_loaded(),
            "dynasty_model": dynasty_model.is_loaded()
        }
    }

@app.post("/projections/player", response_model=PlayerProjectionResponse)
async def get_player_projection(request: PlayerProjectionRequest):
    """Get detailed player projections with confidence intervals"""
    try:
        # Get player data from Sleeper
        player_data = await sleeper_client.get_player(request.player_id)
        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Get recent performance data
        performance_data = await sleeper_client.get_player_stats(
            request.player_id, 
            weeks=8
        )
        
        # Process data for model
        processed_data = data_processor.prepare_projection_data(
            player_data, 
            performance_data,
            request.league_settings
        )
        
        # Generate projection
        projection = projection_model.predict(processed_data, request.weeks_ahead)
        
        return PlayerProjectionResponse(
            player_id=request.player_id,
            player_name=player_data["full_name"],
            position=player_data["position"],
            team=player_data["team"],
            projected_points=projection["points"],
            confidence_interval=projection["confidence_interval"],
            projection_breakdown=projection["breakdown"],
            injury_risk=projection["injury_risk"],
            trending=projection["trend"]
        )
        
    except Exception as e:
        logger.error(f"Error generating player projection: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating projection")

@app.post("/waiver-wire/recommendations")
async def get_waiver_recommendations(request: WaiverWireRequest) -> List[WaiverWireRecommendation]:
    """Get AI-powered waiver wire recommendations"""
    try:
        # Get league and team data
        league_data = await sleeper_client.get_league(request.league_id)
        team_data = await sleeper_client.get_team(request.team_id)
        available_players = await sleeper_client.get_available_players(request.league_id)
        
        # Process data for recommendations
        processed_data = data_processor.prepare_waiver_data(
            team_data,
            available_players,
            league_data,
            request.position_needs
        )
        
        # Generate recommendations
        recommendations = waiver_model.recommend(
            processed_data,
            budget_constraint=request.budget_constraint
        )
        
        # Format response
        formatted_recommendations = []
        for rec in recommendations:
            player_data = await sleeper_client.get_player(rec["player_id"])
            formatted_recommendations.append(
                WaiverWireRecommendation(
                    player_id=rec["player_id"],
                    player_name=player_data["full_name"],
                    position=player_data["position"],
                    team=player_data["team"],
                    recommendation_score=rec["score"],
                    projected_points=rec["projected_points"],
                    ownership_percentage=rec["ownership"],
                    trending_score=rec["trending"],
                    reasoning=rec["reasoning"],
                    priority_level=rec["priority"]
                )
            )
        
        return formatted_recommendations
        
    except Exception as e:
        logger.error(f"Error generating waiver recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")

@app.post("/trade/analyze", response_model=TradeAnalysisResponse)
async def analyze_trade(request: TradeAnalysisRequest):
    """Analyze a proposed trade with detailed metrics"""
    try:
        # Get player data for all involved players
        giving_data = []
        for player_id in request.giving_players:
            player = await sleeper_client.get_player(player_id)
            stats = await sleeper_client.get_player_stats(player_id, weeks=16)
            giving_data.append({"player": player, "stats": stats})
        
        receiving_data = []
        for player_id in request.receiving_players:
            player = await sleeper_client.get_player(player_id)
            stats = await sleeper_client.get_player_stats(player_id, weeks=16)
            receiving_data.append({"player": player, "stats": stats})
        
        # Get team context
        team_data = await sleeper_client.get_team(request.team_id)
        league_data = await sleeper_client.get_league(request.league_id)
        
        # Analyze trade
        analysis = trade_analyzer.analyze(
            giving_data,
            receiving_data,
            team_data,
            league_data,
            request.draft_picks
        )
        
        return TradeAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing trade: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing trade")

@app.post("/dynasty/value", response_model=DynastyValueResponse)
async def get_dynasty_value(request: DynastyValueRequest):
    """Get comprehensive dynasty value analysis for a player"""
    try:
        # Get player data
        player_data = await sleeper_client.get_player(request.player_id)
        if not player_data:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Get historical performance
        historical_data = await sleeper_client.get_player_career_stats(request.player_id)
        
        # Process for dynasty model
        processed_data = data_processor.prepare_dynasty_data(
            player_data,
            historical_data,
            request.league_settings
        )
        
        # Generate dynasty analysis
        analysis = dynasty_model.analyze(processed_data)
        
        return DynastyValueResponse(
            player_id=request.player_id,
            player_name=player_data["full_name"],
            current_value=analysis["current_value"],
            projected_value_1year=analysis["value_1year"],
            projected_value_2year=analysis["value_2year"],
            projected_value_3year=analysis["value_3year"],
            peak_value_year=analysis["peak_year"],
            value_trend=analysis["trend"],
            age_curve_position=analysis["age_curve"],
            dynasty_tier=analysis["tier"]
        )
        
    except Exception as e:
        logger.error(f"Error analyzing dynasty value: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing dynasty value")

@app.get("/analytics/insights/{team_id}")
async def get_team_insights(team_id: str):
    """Get comprehensive team insights and recommendations"""
    try:
        # Get team data
        team_data = await sleeper_client.get_team(team_id)
        league_data = await sleeper_client.get_league(team_data["league_id"])
        
        # Generate insights
        insights = {
            "team_strength": await _analyze_team_strength(team_data),
            "position_analysis": await _analyze_positions(team_data),
            "age_analysis": await _analyze_team_age(team_data),
            "trade_opportunities": await _find_trade_opportunities(team_data, league_data),
            "draft_strategy": await _generate_draft_strategy(team_data, league_data),
            "waiver_priorities": await _get_waiver_priorities(team_data),
            "championship_odds": await _calculate_championship_odds(team_data, league_data)
        }
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating team insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating insights")

# Helper functions
async def _analyze_team_strength(team_data):
    """Analyze overall team strength"""
    # Implementation for team strength analysis
    pass

async def _analyze_positions(team_data):
    """Analyze positional strengths and weaknesses"""
    # Implementation for position analysis
    pass

async def _analyze_team_age(team_data):
    """Analyze team age profile"""
    # Implementation for age analysis
    pass

async def _find_trade_opportunities(team_data, league_data):
    """Find potential trade opportunities"""
    # Implementation for trade opportunity finder
    pass

async def _generate_draft_strategy(team_data, league_data):
    """Generate draft strategy recommendations"""
    # Implementation for draft strategy
    pass

async def _get_waiver_priorities(team_data):
    """Get waiver wire priorities"""
    # Implementation for waiver priorities
    pass

async def _calculate_championship_odds(team_data, league_data):
    """Calculate championship probability"""
    # Implementation for championship odds
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
