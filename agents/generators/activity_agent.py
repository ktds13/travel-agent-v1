"""Activity Agent - Specialized for planning trips around specific activities."""

from typing import Optional
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from ..tools.travel_tools import extract_travel_query, plan_activity_focused_trip

ACTIVITY_AGENT_INSTRUCTIONS = """
You are an activity-focused travel specialist that plans trips around specific interests and activities.

WORKFLOW:

1. Use extract_travel_query tool with the user's query
   - Extracts activities (e.g., hiking, diving, temples)
   - Searches database for places matching those activities
   - Returns places grouped by activities

2. Check the result:
   - If success=False or places is empty, inform the user
   - If success=True, proceed to step 3

3. Use plan_activity_focused_trip tool
   - Pass the query, places list, and activities from step 1
   - This groups destinations by shared activities
   - Creates an activity-centric plan

IMPORTANT:
- Always extract travel query first to identify activities
- Focus on grouping places by what you can DO there
- Highlight shared activities across multiple destinations
- Provide practical activity-specific recommendations
- Suggest the best places for each activity type
"""

def create_activity_agent(
    deployment_name: Optional[str] = None,
    max_steps: int = 8,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> ToolCallingAgent:
    """
    Create a standalone activity-focused planning agent.
    
    This agent is optimized for planning trips organized around
    specific activities and interests.
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take (default: 8)
        name: Optional name for the agent (required when used as managed agent)
        description: Optional description (required when used as managed agent)
    
    Returns:
        Configured ToolCallingAgent for activity-focused planning
    """
    model = get_azure_model(deployment_name)
    
    tools = [
        extract_travel_query,
        plan_activity_focused_trip
    ]
    
    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        instructions=ACTIVITY_AGENT_INSTRUCTIONS,
        max_steps=max_steps,
        name=name,
        description=description
    )
    
    return agent
