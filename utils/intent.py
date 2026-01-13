"""Intent extraction utilities."""

from core.llm import LLMService
from config.prompts import INTENT_EXTRACTION_PROMPT, GENERATION_MODE_PROMPT, MULTI_INTENT_CLASSIFICATION_PROMPT


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
    valid_modes = {
        "itinerary",
        "suggest_places",
        "describe_place",
        "activity_focused",
        "comparison",
        "find_accommodation"  # Added for hotel/hostel/resort search
    }
    mode = result.get("generation_mode", "itinerary")
    
    if mode not in valid_modes:
        mode = "itinerary"  # Default fallback
    
    return {
        "generation_mode": mode,
        "days": result.get("days")
    }


def classify_multi_intent(query: str) -> dict:
    """
    Detect if user query contains multiple intents requiring different specialist agents.
    
    This classifier identifies queries that ask for multiple tasks, such as:
    - "find hotel near Doi Suthep and describe the temple" (accommodation + description)
    - "plan 3-day trip and book resort" (itinerary + accommodation)
    - "compare Chiang Mai and Bangkok and suggest hotels" (comparison + accommodation)
    
    Args:
        query: User's travel query
        
    Returns:
        Dict with:
        - is_multi_intent (bool): True if multiple intents detected
        - primary_intent (str): The main intent/mode
        - intents (list): List of intent dicts with mode, entity, details
        - reasoning (str): Explanation of classification
        
    Examples:
        >>> classify_multi_intent("find hotel near Doi Suthep and tell me about the temple")
        {
            'is_multi_intent': True,
            'primary_intent': 'find_accommodation',
            'intents': [
                {'mode': 'find_accommodation', 'entity': 'Doi Suthep', 'details': '...'},
                {'mode': 'describe_place', 'entity': 'Doi Suthep temple', 'details': '...'}
            ],
            'reasoning': 'Query asks to find hotel AND describe place'
        }
        
        >>> classify_multi_intent("plan 3-day trip to Chiang Mai")
        {
            'is_multi_intent': False,
            'primary_intent': 'itinerary',
            'intents': [{'mode': 'itinerary', 'entity': 'Chiang Mai', 'details': '3-day trip'}],
            'reasoning': 'Only one task requested'
        }
    """
    llm = LLMService()
    
    prompt = MULTI_INTENT_CLASSIFICATION_PROMPT.format(query=query)
    response = llm.generate_with_prompt(prompt, temperature=0)
    
    result = llm.extract_json(response)
    
    # Validate and provide defaults
    return {
        "is_multi_intent": result.get("is_multi_intent", False),
        "primary_intent": result.get("primary_intent", "itinerary"),
        "intents": result.get("intents", []),
        "reasoning": result.get("reasoning", "Classification completed")
    }

