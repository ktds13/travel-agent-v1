"""Agent Factory for creating mode-specific travel agents."""

from enum import Enum
from typing import Optional
from smolagents import ToolCallingAgent

from core.models import get_azure_model
from config.prompts import (
    ITINERARY_MODE_INSTRUCTIONS,
    SUGGEST_PLACES_MODE_INSTRUCTIONS,
    DESCRIBE_PLACE_MODE_INSTRUCTIONS,
    ACTIVITY_FOCUSED_MODE_INSTRUCTIONS,
    COMPARISON_MODE_INSTRUCTIONS,
)
from .tools.travel_tools import (
    extract_travel_query,
    generate_travel_itinerary,
    suggest_places,
    describe_place,
    plan_activity_focused_trip,
    compare_places,
)


class GenerationMode(Enum):
    """Available agent generation modes."""
    ITINERARY = "itinerary"
    SUGGEST_PLACES = "suggest_places"
    DESCRIBE_PLACE = "describe_place"
    ACTIVITY_FOCUSED = "activity_focused"
    COMPARISON = "comparison"


# Mode-specific configurations
MODE_CONFIGS = {
    GenerationMode.ITINERARY: {
        "tools": [extract_travel_query, generate_travel_itinerary],
        "instructions": ITINERARY_MODE_INSTRUCTIONS,
        "max_steps": 8,
        "description": "Creates day-by-day travel itineraries"
    },
    GenerationMode.SUGGEST_PLACES: {
        "tools": [extract_travel_query, suggest_places],
        "instructions": SUGGEST_PLACES_MODE_INSTRUCTIONS,
        "max_steps": 6,
        "description": "Suggests travel destinations based on preferences"
    },
    GenerationMode.DESCRIBE_PLACE: {
        "tools": [extract_travel_query, describe_place],
        "instructions": DESCRIBE_PLACE_MODE_INSTRUCTIONS,
        "max_steps": 6,
        "description": "Provides detailed information about specific places"
    },
    GenerationMode.ACTIVITY_FOCUSED: {
        "tools": [extract_travel_query, plan_activity_focused_trip],
        "instructions": ACTIVITY_FOCUSED_MODE_INSTRUCTIONS,
        "max_steps": 8,
        "description": "Plans trips around specific activities"
    },
    GenerationMode.COMPARISON: {
        "tools": [extract_travel_query, compare_places],
        "instructions": COMPARISON_MODE_INSTRUCTIONS,
        "max_steps": 6,
        "description": "Compares multiple destinations side-by-side"
    },
}


def create_agent_for_mode(
    mode: GenerationMode,
    deployment_name: Optional[str] = None
) -> ToolCallingAgent:
    """
    Create a mode-specific travel agent optimized for a particular generation mode.
    
    This factory creates lightweight, focused agents that only have the tools
    necessary for their specific task, improving efficiency and reducing token usage.

    Args:
        mode: The generation mode (from GenerationMode enum)
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)

    Returns:
        Configured ToolCallingAgent instance optimized for the specified mode

    Raises:
        ValueError: If mode is not a valid GenerationMode

    Examples:
        >>> agent = create_agent_for_mode(GenerationMode.ITINERARY)
        >>> response = agent.run("Plan a 3-day trip to Chiang Mai")
        
        >>> agent = create_agent_for_mode(GenerationMode.SUGGEST_PLACES)
        >>> response = agent.run("What beach destinations do you recommend?")
    """
    if not isinstance(mode, GenerationMode):
        raise ValueError(f"Invalid mode: {mode}. Must be a GenerationMode enum value.")
    
    config = MODE_CONFIGS[mode]
    model = get_azure_model(deployment_name)
    
    agent = ToolCallingAgent(
        model=model,
        tools=config["tools"],
        instructions=config["instructions"],
        max_steps=config["max_steps"]
    )
    
    return agent


def get_mode_from_string(mode_str: str) -> Optional[GenerationMode]:
    """
    Convert a string to a GenerationMode enum.
    
    Args:
        mode_str: Mode string (e.g., "itinerary", "suggest_places")
    
    Returns:
        GenerationMode enum value or None if invalid
    
    Examples:
        >>> mode = get_mode_from_string("itinerary")
        >>> mode == GenerationMode.ITINERARY
        True
    """
    try:
        return GenerationMode(mode_str.lower())
    except (ValueError, AttributeError):
        return None


def list_available_modes() -> list[dict]:
    """
    Get a list of all available generation modes with descriptions.
    
    Returns:
        List of dicts with mode info (mode, value, description)
    
    Examples:
        >>> modes = list_available_modes()
        >>> len(modes)
        5
    """
    return [
        {
            "mode": mode.name,
            "value": mode.value,
            "description": MODE_CONFIGS[mode]["description"]
        }
        for mode in GenerationMode
    ]
