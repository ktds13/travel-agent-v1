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
