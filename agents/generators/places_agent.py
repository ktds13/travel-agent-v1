"""Places Agent - Specialized for suggesting and describing travel destinations."""

from typing import Optional
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from ..tools.travel_tools import extract_travel_query, suggest_places, describe_place

PLACES_AGENT_INSTRUCTIONS = """
You are a travel destination specialist that suggests places and provides detailed descriptions.

WORKFLOW:

1. Use extract_travel_query tool with the user's query
   - Extracts region, country, category, activities
   - Searches database for matching places
   - Returns relevant places with descriptions

2. Check the result:
   - If success=False or places is empty, inform the user
   - If success=True, proceed to step 3

3. Choose appropriate response:
   a) For GENERAL SUGGESTIONS (e.g., "Where should I visit?"):
      - Use suggest_places tool with the places list
      
   b) For SPECIFIC PLACE DESCRIPTION (e.g., "Tell me about Doi Suthep"):
      - Use describe_place tool with the place name

IMPORTANT:
- Always extract travel query first to get context
- Use suggest_places for listing multiple destinations
- Use describe_place for detailed information about one location
- Provide helpful, engaging descriptions with activities
"""

def create_places_agent(
    deployment_name: Optional[str] = None,
    max_steps: int = 6
) -> ToolCallingAgent:
    """
    Create a standalone places suggestion agent.
    
    This agent is optimized for suggesting travel destinations and
    providing detailed place descriptions.
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take (default: 6)
    
    Returns:
        Configured ToolCallingAgent for place suggestions
    """
    model = get_azure_model(deployment_name)
    
    tools = [
        extract_travel_query,
        suggest_places,
        describe_place
    ]
    
    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        instructions=PLACES_AGENT_INSTRUCTIONS,
        max_steps=max_steps
    )
    
    return agent
