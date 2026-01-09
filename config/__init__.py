"""Configuration module for Travel Agent."""

from .settings import (
     DATABASE_CONFIG,
    MODEL_CONFIGS,
    GROQ_API_KEY,
    CANONICAL_CATEGORIES,
    get_azure_model_config
)

from .prompts import (
    SYSTEM_PROMPT,
    INTENT_EXTRACTION_PROMPT,
    GENERATION_MODE_PROMPT,
    itinerary_prompt_template
)

__all__ = [
    "DATABASE_CONFIG",
    "MODEL_CONFIGS",
    "GROQ_API_KEY",
    "CANONICAL_CATEGORIES",
    "get_azure_model_config",
    "SYSTEM_PROMPT",
    "INTENT_EXTRACTION_PROMPT", 
    "GENERATION_MODE_PROMPT",
    "itinerary_prompt_template"
]