"""Comparison Agent - Specialized for comparing multiple destinations."""

from typing import Optional
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from ..tools.travel_tools import extract_travel_query, compare_places

COMPARISON_AGENT_INSTRUCTIONS = """
You are a destination comparison specialist that helps users decide between multiple travel options.

WORKFLOW:

1. Use extract_travel_query tool with the user's query
   - Extracts places to compare
   - Searches database for those specific places
   - Returns place information with activities

2. Check the result:
   - If success=False or places is empty, inform the user
   - If success=True, proceed to step 3

3. Use compare_places tool
   - Pass the places list from step 1
   - Optionally specify place_names to compare
   - This provides side-by-side comparison

IMPORTANT:
- Always extract travel query first to get place information
- Compare based on activities, characteristics, and appeal
- Highlight shared activities and unique features
- Provide clear recommendations based on user preferences
- Help users make informed decisions
"""

def create_comparison_agent(
    deployment_name: Optional[str] = None,
    max_steps: int = 6,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> ToolCallingAgent:
    """
    Create a standalone destination comparison agent.
    
    This agent is optimized for comparing multiple travel destinations
    side-by-side to help users make decisions.
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take (default: 6)
        name: Optional name for the agent (required when used as managed agent)
        description: Optional description (required when used as managed agent)
    
    Returns:
        Configured ToolCallingAgent for place comparison
    """
    model = get_azure_model(deployment_name)
    
    tools = [
        extract_travel_query,
        compare_places
    ]
    
    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        instructions=COMPARISON_AGENT_INSTRUCTIONS,
        max_steps=max_steps,
        name=name,
        description=description
    )
    
    return agent
