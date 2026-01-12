"""Intent extraction utilities."""

from core.llm import LLMService
from config.prompts import INTENT_EXTRACTION_PROMPT, GENERATION_MODE_PROMPT


def extract_intent(query: str) -> dict:
    """
    Extract travel intent and entities from user query.
    
    Args:
        query: User's travel query
        
    Returns:
        Dict with: place_name, region, country, category, activities, days
    """
    llm = LLMService()
    
    prompt = INTENT_EXTRACTION_PROMPT.format(query=query)
    response = llm.generate_with_prompt(prompt, temperature=0)
    
    extracted = llm.extract_json(response)
    
    # Ensure all expected keys exist
    return {
        "place_name": extracted.get("place_name"),
        "region": extracted.get("region"),
        "country": extracted.get("country"),
        "category": extracted.get("category"),
        "activities": extracted.get("activities") or [],
        "days": extracted.get("days")
    }


def classify_generation_mode(query: str) -> dict:
    """
    Classify user query into a generation mode.
    
    Determines what type of response the user is expecting:
    - itinerary: Day-by-day travel plan
    - suggest_places: List of destination recommendations
    - describe_place: Detailed info about a specific place
    - activity_focused: Trip planning around specific activities
    - comparison: Side-by-side comparison of places
    
    Args:
        query: User's travel query
        
    Returns:
        Dict with: generation_mode (str), days (int or None)
        
    Examples:
        >>> classify_generation_mode("Plan a 5-day trip to Thailand")
        {'generation_mode': 'itinerary', 'days': 5}
        
        >>> classify_generation_mode("What are the best beaches in Thailand?")
        {'generation_mode': 'suggest_places', 'days': None}
        
        >>> classify_generation_mode("Tell me about Doi Suthep")
        {'generation_mode': 'describe_place', 'days': None}
    """
    llm = LLMService()
    
    prompt = f"{GENERATION_MODE_PROMPT}\n\nUser query: {query}"
    response = llm.generate_with_prompt(prompt, temperature=0)
    
    result = llm.extract_json(response)
    
    # Ensure mode exists and is valid, default to itinerary
    valid_modes = {"itinerary", "suggest_places", "describe_place", "activity_focused", "comparison"}
    mode = result.get("generation_mode", "itinerary")
    
    if mode not in valid_modes:
        mode = "itinerary"  # Default fallback
    
    return {
        "generation_mode": mode,
        "days": result.get("days")
    }
