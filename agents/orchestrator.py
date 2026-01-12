"""Orchestrator Agent - Routes user queries to specialized generation agents."""

from typing import Optional, Dict
from smolagents import ToolCallingAgent
from core.models import get_azure_model
from utils.intent import classify_generation_mode
from .generators import (
    create_itinerary_agent,
    create_places_agent,
    create_accommodation_agent,
    create_activity_agent,
    create_comparison_agent
)

ORCHESTRATOR_INSTRUCTIONS = """
You are the main travel assistant orchestrator that routes user requests to specialized agents.

Your job is simple:
1. Understand what the user wants
2. Route their request to the appropriate specialist agent
3. Return the specialist's response

You do NOT need to use any tools - you should analyze the user's query and respond with
which type of assistance they need:
- "itinerary" - for day-by-day trip planning
- "places" - for destination suggestions or place descriptions
- "accommodation" - for finding hotels, hostels, resorts
- "activity" - for trips focused on specific activities
- "comparison" - for comparing multiple destinations

Simply state which specialist can help and what you understood from their request.
The system will automatically route to the correct agent.
"""

# Agent cache to avoid recreating agents
_agent_cache: Dict[str, ToolCallingAgent] = {}


def get_or_create_specialist(
    mode: str,
    deployment_name: Optional[str] = None
) -> ToolCallingAgent:
    """
    Get or create a specialist agent for the given mode.
    Uses caching to avoid recreating agents.
    
    Args:
        mode: Generation mode (itinerary, places, accommodation, activity, comparison)
        deployment_name: Azure OpenAI deployment name
    
    Returns:
        Cached or newly created specialist agent
    """
    cache_key = f"{mode}_{deployment_name or 'default'}"
    
    if cache_key not in _agent_cache:
        if mode == "itinerary":
            _agent_cache[cache_key] = create_itinerary_agent(deployment_name)
        elif mode == "suggest_places" or mode == "describe_place":
            # Both use the places agent
            _agent_cache[cache_key] = create_places_agent(deployment_name)
        elif mode == "find_accommodation":
            _agent_cache[cache_key] = create_accommodation_agent(deployment_name)
        elif mode == "activity_focused":
            _agent_cache[cache_key] = create_activity_agent(deployment_name)
        elif mode == "comparison":
            _agent_cache[cache_key] = create_comparison_agent(deployment_name)
        else:
            # Fallback to itinerary agent
            _agent_cache[cache_key] = create_itinerary_agent(deployment_name)
    
    return _agent_cache[cache_key]


def route_to_specialist(
    query: str,
    deployment_name: Optional[str] = None,
    explicit_mode: Optional[str] = None
) -> tuple[str, str]:
    """
    Route a user query to the appropriate specialist agent and get response.
    
    This is the main orchestration function that:
    1. Classifies the user's intent
    2. Gets or creates the appropriate specialist agent
    3. Runs the query through that agent
    4. Returns the response
    
    Args:
        query: User's travel query
        deployment_name: Azure OpenAI deployment name
        explicit_mode: Optional explicit mode (bypasses classification)
    
    Returns:
        Tuple of (response, mode_used) where:
        - response: The specialist agent's response
        - mode_used: The generation mode that was used
    """
    # Classify intent or use explicit mode
    if explicit_mode:
        mode = explicit_mode
    else:
        classification = classify_generation_mode(query)
        mode = classification.get("generation_mode", "itinerary")
    
    # Get the specialist agent
    specialist = get_or_create_specialist(mode, deployment_name)
    
    # Run the query through the specialist
    response = specialist.run(query)
    
    return response, mode


def create_orchestrator(
    deployment_name: Optional[str] = None,
    max_steps: int = 3
) -> ToolCallingAgent:
    """
    Create the main orchestrator agent.
    
    This is a lightweight agent that analyzes user queries and determines
    which specialist agent should handle the request. It doesn't actually
    perform the work - it just routes to the appropriate specialist.
    
    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take (default: 3)
    
    Returns:
        Configured ToolCallingAgent for orchestration
    
    Note:
        In practice, you may want to use route_to_specialist() directly
        rather than creating an orchestrator agent, as it's more efficient.
    """
    model = get_azure_model(deployment_name)
    
    # Orchestrator doesn't need tools - it just classifies and routes
    agent = ToolCallingAgent(
        model=model,
        tools=[],
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        max_steps=max_steps
    )
    
    return agent


def clear_agent_cache():
    """Clear the cached specialist agents. Useful for testing or reloading."""
    global _agent_cache
    _agent_cache.clear()
