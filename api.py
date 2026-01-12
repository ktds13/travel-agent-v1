"""FastAPI web service wrapper for Travel Agent v3 - Orchestrated Specialists."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging
from agents.orchestrator import route_to_specialist, get_or_create_specialist
from agents.factory import GenerationMode, list_available_modes, create_standalone_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Travel Agent API",
    description="AI-powered travel planning API with orchestrated specialist agents",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mode-specific agent cache
agent_cache: Dict[str, object] = {}


# Request/Response Models
class TravelQuery(BaseModel):
    """Travel query request."""
    query: str = Field(..., description="Natural language travel query", min_length=1)
    mode: Optional[str] = Field(None, description="Optional explicit generation mode override")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "plan hiking trip in Chiang Mai for 3 days",
                "mode": "itinerary"
            }
        }


class TravelResponse(BaseModel):
    """Travel query response."""
    query: str
    response: str
    mode: str
    success: bool = True
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "2.0.0"


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(status="healthy")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    try:
        return HealthResponse(status="healthy")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/query", response_model=TravelResponse)
async def query_travel_agent(request: TravelQuery):
    """
    Query the travel agent with a natural language request.
    
    The orchestrator automatically routes your query to the appropriate specialist agent:
    - Itinerary Agent: For day-by-day trip planning
    - Places Agent: For destination suggestions and descriptions
    - Accommodation Agent: For hotels, hostels, and resorts
    - Activity Agent: For activity-focused trip planning
    - Comparison Agent: For comparing destinations
    
    You can optionally specify a mode to directly use a specific specialist.
    
    Examples:
    - "suggest places to visit in Chiang Mai"
    - "plan hiking trip in Chiang Mai for 3 days"
    - "find hotel near Doi Suthep"
    - "tell me about Mae Kampong"
    - "compare Chiang Dao and Mae Kampong"
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Use orchestrator to route to specialist
        result, mode = route_to_specialist(
            query=request.query,
            explicit_mode=request.mode
        )
        logger.info(f"Routed to specialist: {mode}")
        
        logger.info("Query processed successfully")
        
        return TravelResponse(
            query=request.query,
            response=result,
            mode=mode,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        return TravelResponse(
            query=request.query,
            response="",
            mode="error",
            success=False,
            error=str(e)
        )


@app.post("/agent/{mode}", response_model=TravelResponse)
async def query_specific_agent(mode: str, request: TravelQuery):
    """
    Directly query a specific specialist agent by mode.
    
    Available modes:
    - itinerary: Day-by-day travel planning
    - suggest_places or describe_place: Destination suggestions
    - find_accommodation: Hotel/hostel/resort search
    - activity_focused: Activity-based tripspecialist agents."""
    try:
        from agents.tools.travel_tools import (
            extract_travel_query,
            generate_travel_itinerary,
            suggest_places,
            describe_place,
            plan_activity_focused_trip,
            compare_places,
        )
        from agents.tools.accommodation_tools import (
            extract_accommodation_query,
            search_accommodations,
            find_accommodation_near_place,
            compare_accommodations,
        )
        
        all_tools = [
            # Travel tools
            extract_travel_query,
            generate_travel_itinerary,
            suggest_places,
            describe_place,
            plan_activity_focused_trip,
            compare_places,
            # Accommodation tools
            extract_accommodation_query,
            search_accommodations,
            find_accommodation_near_place,
            compare_accommodations,
        ]
        
        tools = [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in all_tools
        ]
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/modes")
async def list_modes():
    """List available generation modes."""
    try:
        modes = list_available_modes()
        return {"modes": modes}
    except Exception as e:
        logger.error(f"Failed to list modes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_tools():
    """List all available tools across all modes."""
    try:
        from agents.tools.travel_tools import (
            extract_travel_query,
            generate_travel_itinerary,
            suggest_places,
            describe_place,
            plan_activity_focused_trip,
            compare_places,
        )
        
        all_tools = [
            extract_travel_query,
            generate_travel_itinerary,
            suggest_places,
            describe_place,
            plan_activity_focused_trip,
            compare_places,
        ]
        
        tools = [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in all_tools
        ]
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)