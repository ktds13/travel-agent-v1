"""Accommodation Agent - Specialized for finding hotels, hostels, and resorts."""

from typing import Optional
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from ..tools.accommodation_tools import (
    extract_accommodation_query,
    search_accommodations,
    find_accommodation_near_place,
    compare_accommodations
)

ACCOMMODATION_AGENT_INSTRUCTIONS = """
You are an accommodation specialist that helps find hotels, hostels, resorts, and other places to stay.

WORKFLOW:

1. Use extract_accommodation_query tool with the user's query
   - Extracts location, place_name, type, price_range, amenities
   - Returns structured accommodation preferences

2. Choose the appropriate search tool based on the query:

   a) For "NEAR A PLACE" queries (e.g., "hotel near Doi Suthep"):
      - Use find_accommodation_near_place tool
      - Provide place_name and radius from step 1
      
   b) For GENERAL AREA searches (e.g., "hotels in Chiang Mai"):
      - Use search_accommodations tool
      - Use location, type, price_range filters from step 1
      
   c) For COMPARISON requests (e.g., "compare these hotels"):
      - First get accommodations using search or find_near
      - Then use compare_accommodations tool

3. Present results with:
   - Name and type
   - Location and distance (if applicable)
   - Price range
   - Rating
   - Key amenities
   - Brief description

IMPORTANT:
- Always extract accommodation query first
- Use find_accommodation_near_place when user mentions a specific landmark
- Use search_accommodations for region/city-based searches
- Provide helpful comparisons when user asks to compare options
"""

def create_accommodation_agent(
    deployment_name: Optional[str] = None,
    max_steps: int = 8
) -> ToolCallingAgent:
    """
    Create a standalone accommodation finding agent.
    
    This agent is optimized for finding hotels, hostels, resorts,
    and other accommodations based on user preferences.
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take (default: 8)
    
    Returns:
        Configured ToolCallingAgent for accommodation search
    """
    model = get_azure_model(deployment_name)
    
    tools = [
        extract_accommodation_query,
        search_accommodations,
        find_accommodation_near_place,
        compare_accommodations
    ]
    
    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        instructions=ACCOMMODATION_AGENT_INSTRUCTIONS,
        max_steps=max_steps
    )
    
    return agent
