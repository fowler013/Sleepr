"""
FastAPI service for Sleepr analytics
Provides REST API endpoints for machine learning predictions and analytics
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from analytics import SleeprAnalytics
from models import PlayerPerformanceModel, WaiverWireAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Sleepr Analytics API",
    description="Fantasy Football Analytics and Machine Learning API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analytics
analytics = SleeprAnalytics()
performance_model = PlayerPerformanceModel()
waiver_analyzer = WaiverWireAnalyzer()

# Pydantic models for request/response
class PlayerAnalysisRequest(BaseModel):
    player_id: int
    weeks_back: int = 8

class PlayerProjectionResponse(BaseModel):
    player_id: int
    projected_points: float
    confidence: float
    ceiling: float
    floor: float
    trend: str

class WaiverWireRequest(BaseModel):
    league_id: str
    position: Optional[str] = None
    max_results: int = 10

class WaiverWirePlayer(BaseModel):
    player_id: int
    name: str
    position: str
    opportunity_score: float
    reason: str
    projected_points: float

class TradeAnalysisRequest(BaseModel):
    player_ids: List[int]

class TradeAnalysisResponse(BaseModel):
    trade_values: dict
    recommendation: str
    confidence: float

class LineupOptimizationRequest(BaseModel):
    team_id: int
    week: int

class LineupOptimizationResponse(BaseModel):
    team_id: int
    week: int
    optimized_lineup: dict
    total_projected: float

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Sleepr Analytics API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "models_loaded": True
    }

@app.post("/analytics/player-projection", response_model=PlayerProjectionResponse)
async def get_player_projection(request: PlayerAnalysisRequest):
    """Get ML-based performance projection for a player"""
    try:
        result = analytics.analyze_player_performance(
            request.player_id, 
            request.weeks_back
        )
        
        return PlayerProjectionResponse(
            player_id=result['player_id'],
            projected_points=result['projected_points'],
            confidence=result['confidence'],
            ceiling=result['projected_points'] * 1.4,
            floor=result['projected_points'] * 0.6,
            trend=result['trend']
        )
    except Exception as e:
        logger.error(f"Error in player projection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/waiver-wire", response_model=List[WaiverWirePlayer])
async def get_waiver_wire_recommendations(request: WaiverWireRequest):
    """Get waiver wire pickup recommendations"""
    try:
        targets = analytics.get_waiver_wire_targets(
            request.league_id, 
            request.position
        )
        
        return [
            WaiverWirePlayer(
                player_id=target['player_id'],
                name=target['name'],
                position=target['position'],
                opportunity_score=target['opportunity_score'],
                reason=target['reason'],
                projected_points=target.get('projected_points', 0.0)
            )
            for target in targets[:request.max_results]
        ]
    except Exception as e:
        logger.error(f"Error in waiver wire analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/trade-analysis", response_model=TradeAnalysisResponse)
async def analyze_trade(request: TradeAnalysisRequest):
    """Analyze trade value and provide recommendations"""
    try:
        result = analytics.analyze_trade_value(request.player_ids)
        
        return TradeAnalysisResponse(
            trade_values=result['trade_values'],
            recommendation=result['recommendation'],
            confidence=result['confidence']
        )
    except Exception as e:
        logger.error(f"Error in trade analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analytics/lineup-optimization", response_model=LineupOptimizationResponse)
async def optimize_lineup(request: LineupOptimizationRequest):
    """Optimize lineup for maximum projected points"""
    try:
        result = analytics.optimize_lineup(request.team_id, request.week)
        
        return LineupOptimizationResponse(
            team_id=result['team_id'],
            week=result['week'],
            optimized_lineup=result['optimized_lineup'],
            total_projected=result['total_projected']
        )
    except Exception as e:
        logger.error(f"Error in lineup optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/dynasty-analysis/{team_id}")
async def get_dynasty_analysis(team_id: int):
    """Get dynasty team analysis and recommendations"""
    try:
        result = analytics.dynasty_asset_analysis(team_id)
        return result
    except Exception as e:
        logger.error(f"Error in dynasty analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
