"""Itinerary Generation Agent - Specialized for day-by-day travel planning."""

from typing import Optional
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from ..tools.travel_tools import extract_travel_query, generate_travel_itinerary

ITINERARY_AGENT_INSTRUCTIONS = """
You are an itinerary planning specialist that creates detailed day-by-day travel plans.

WORKFLOW:

1. Use extract_travel_query tool with the user's query
   - Extracts region, country, activities, number of days
   - Searches database for relevant places
   - Returns places and days for itinerary

2. Check the result:
   - If success=False or places is empty, inform the user
   - If success=True, proceed to step 3

3. Use generate_travel_itinerary tool
   - Pass the query, places list, and days from step 1
   - This creates a structured day-by-day itinerary

IMPORTANT:
- Always extract travel query first to get context
- Use the 'days' parameter from extraction for itinerary length
- Provide clear, actionable day-by-day plans
- Include activities, timing suggestions, and practical tips
"""

def create_itinerary_agent(
    deployment_name: Optional[str] = None,
    max_steps: int = 8
) -> ToolCallingAgent:
    """
    Create a standalone itinerary planning agent.
    
    This agent is optimized for creating day-by-day travel itineraries.
    It uses only the tools necessary for itinerary generation.
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take (default: 8)
    
    Returns:
        Configured ToolCallingAgent for itinerary generation
    """
    model = get_azure_model(deployment_name)
    
    tools = [
        extract_travel_query,
        generate_travel_itinerary
    ]
    
    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        instructions=ITINERARY_AGENT_INSTRUCTIONS,
        max_steps=max_steps
    )
    
    return agent
