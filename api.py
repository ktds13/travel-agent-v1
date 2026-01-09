"""FastAPI web service wrapper for Travel Agent v2."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from agents import create_travel_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Travel Agent API",
    description="AI-powered travel planning API with RAG capabilities",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent (singleton)
agent = None

def get_agent():
    """Get or create travel agent instance."""
    global agent
    if agent is None:
        agent = create_travel_agent()
    return agent


# Request/Response Models
class TravelQuery(BaseModel):
    """Travel query request."""
    query: str = Field(..., description="Natural language travel query", min_length=1)
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "plan hiking trip in Chiang Mai for 3 days"
            }
        }


class TravelResponse(BaseModel):
    """Travel query response."""
    query: str
    response: str
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
        # Test agent initialization
        _ = get_agent()
        return HealthResponse(status="healthy")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/query", response_model=TravelResponse)
async def query_travel_agent(request: TravelQuery):
    """
    Query the travel agent with a natural language request.
    
    Examples:
    - "suggest places to visit in Chiang Mai"
    - "plan hiking trip in Chiang Mai for 3 days"
    - "tell me about Mae Kampong"
    - "compare Chiang Dao and Mae Kampong"
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Get agent and run query
        travel_agent = get_agent()
        result = travel_agent.run(request.query)
        
        logger.info("Query processed successfully")
        
        return TravelResponse(
            query=request.query,
            response=result,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        return TravelResponse(
            query=request.query,
            response="",
            success=False,
            error=str(e)
        )


@app.get("/tools")
async def list_tools():
    """List available tools in the agent."""
    try:
        travel_agent = get_agent()
        tools = [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in travel_agent.tools
        ]
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)