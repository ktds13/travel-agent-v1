"""Travel Agent implementation using Tool Calling Agent."""

from smolagents import ToolCallingAgent
from core.models import get_azure_model
from .tools.travel_tools import (
    extract_travel_query,
    generate_travel_itinerary,
    suggest_places,
    describe_place,
    plan_activity_focused_trip,
    compare_places
)

TRAVEL_AGENT_INSTRUCTIONS = """
You are a travel planning assistant that helps users plan trips, suggest destinations, and create itineraries based on their preferences.

WORKFLOW - Follow these steps for every user request:

1. Use extract_travel_query tool with the user's query
    - This automatically extracts intent (region, country, activities, days, etc.) from the user's request.
    - Searches database with appropriate filters to find relevant places.
    - Returns structured results as context for later steps.

2. Check the result from step 1:
    - If success=False or places is empty, return the message to the user
    - If success=True, proceed to step 3.

3. Determine response type based on user intent and choose the appropriate tool:
    a) For DAY-BY-DAY ITINERARY requests
        - Use generate_travel_itinerary tool with the extracted days and places context.
    b) For SUGGESTING PLACES requests
        - Use suggest_places tool with the places context.
    c) For DESCRIBING A SPECIFIC PLACE requests
        - Use describe_place tool with the place name.
    d) For ACTIVITY-FOCUSED TRIP requests
        - Use plan_activity_focused_trip tool with the activities and places context.
    e) For COMPARISON requests
        - Use compare_places tool with the list of place names.

IMPORTANT RULES:
- Always use extract_travel_query first to understand user intent.
- Use only the tools provided; do not generate information independently.
- If the extracted intent lacks sufficient information, inform the user accordingly.
- Provide clear, concise, and helpful responses based on the tool outputs.
- Use the 'days' parameter from the extracted intent for itinerary generation.
- Use the 'places' from extract_travel_query as context for all tools except describe_place.
"""

def create_travel_agent(deployment_name: str = None, max_steps: int = 12) -> ToolCallingAgent:
    """
    Create a Travel Agent using Tool Calling Agent.

    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take

    Returns:
        Configured ToolCallingAgent instance
    """
    model = get_azure_model(deployment_name)

    tools = [
        extract_travel_query,
        generate_travel_itinerary,
        suggest_places,
        describe_place,
        plan_activity_focused_trip,
        compare_places
    ]

    agent = ToolCallingAgent(
        model=model,
        tools=tools,
        instructions=TRAVEL_AGENT_INSTRUCTIONS,
        max_steps=max_steps
    )

    return agent