"""Multi-Agent Orchestrator for handling complex multi-intent queries."""

from typing import Optional
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from .generators import (
    create_itinerary_agent,
    create_places_agent,
    create_accommodation_agent,
    create_activity_agent,
    create_comparison_agent
)

MULTI_AGENT_ORCHESTRATOR_INSTRUCTIONS = """
You are a multi-agent travel orchestrator that coordinates multiple specialist agents.

You have access to these specialist agents:
1. itinerary_specialist: Creates day-by-day travel itineraries
2. places_specialist: Suggests destinations and describes places
3. accommodation_specialist: Finds hotels, hostels, resorts near landmarks or in regions
4. activity_specialist: Plans trips around specific activities
5. comparison_specialist: Compares multiple destinations

WORKFLOW FOR MULTI-INTENT QUERIES:

When the user asks for multiple things (e.g., "find hotel near Doi Suthep and describe the temple"):

1. Break down the query into subtasks
2. Delegate each subtask to the appropriate specialist agent
3. Combine their responses into a coherent answer

Examples:

Query: "find hotel near Doi Suthep and tell me about the temple"
Steps:
- Call accommodation_specialist with "find hotel near Doi Suthep"
- Call places_specialist with "describe Doi Suthep temple"
- Combine both responses

Query: "plan 3-day trip to Chiang Mai and book a resort"
Steps:
- Call itinerary_specialist with "plan 3-day trip to Chiang Mai"
- Call accommodation_specialist with "find resort in Chiang Mai"
- Present both the itinerary and accommodation options

Query: "compare beaches in Phuket and Krabi and suggest hotels"
Steps:
- Call comparison_specialist with "compare beaches in Phuket and Krabi"
- Call accommodation_specialist with "find hotels in Phuket and Krabi"
- Provide comparison followed by accommodation options

IMPORTANT RULES:
1. Identify all distinct tasks in the user's query
2. Route each task to the correct specialist
3. Execute specialist calls in logical order
4. Synthesize responses into a unified answer
5. Ensure all parts of the query are addressed
6. Avoid redundant information across responses
"""


def create_multi_agent_orchestrator(
    deployment_name: Optional[str] = None,
    max_steps: int = 20
) -> ToolCallingAgent:
    """
    Create a multi-agent orchestrator that manages specialist agents.
    
    This orchestrator can handle complex queries requiring multiple specialists,
    such as finding accommodation AND describing a place in a single query.
    
    It uses smolagents' managed_agents feature to coordinate between:
    - Itinerary planning agent
    - Places suggestion/description agent
    - Accommodation finding agent
    - Activity-focused planning agent
    - Destination comparison agent
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for orchestrator (default: 20, higher for multi-agent)
        
    Returns:
        Configured ToolCallingAgent with managed specialist agents
        
    Examples:
        >>> orchestrator = create_multi_agent_orchestrator()
        >>> result = orchestrator.run("find hotel near Doi Suthep and describe temple")
        # Orchestrator delegates to accommodation_specialist and places_specialist
    """
    model = get_azure_model(deployment_name)
    
    # Create all specialist agents with names and descriptions
    # These become callable like tools via managed_agents parameter
    managed_specialists = [
        create_itinerary_agent(
            deployment_name=deployment_name,
            max_steps=8,
            name="itinerary_specialist",
            description="Creates detailed day-by-day travel itineraries. Use when user wants a structured trip plan with daily activities."
        ),
        create_places_agent(
            deployment_name=deployment_name,
            max_steps=6,
            name="places_specialist",
            description="Suggests travel destinations and provides detailed place descriptions. Use when user asks 'where to go' or 'tell me about [place]'."
        ),
        create_accommodation_agent(
            deployment_name=deployment_name,
            max_steps=8,
            name="accommodation_specialist",
            description="Finds hotels, hostels, resorts, and accommodations. Use when user asks to 'find hotel', 'book accommodation', or wants to stay near a landmark."
        ),
        create_activity_agent(
            deployment_name=deployment_name,
            max_steps=8,
            name="activity_specialist",
            description="Plans trips organized around specific activities (hiking, diving, temples, etc.). Use when user emphasizes activities over destinations."
        ),
        create_comparison_agent(
            deployment_name=deployment_name,
            max_steps=6,
            name="comparison_specialist",
            description="Compares multiple destinations side-by-side. Use when user asks to 'compare X and Y' or needs help choosing between places."
        )
    ]
    
    # Create orchestrator with managed agents
    orchestrator = ToolCallingAgent(
        model=model,
        tools=[],  # Orchestrator uses managed_agents, not direct tools
        managed_agents=managed_specialists,
        instructions=MULTI_AGENT_ORCHESTRATOR_INSTRUCTIONS,
        max_steps=max_steps
    )
    
    return orchestrator
