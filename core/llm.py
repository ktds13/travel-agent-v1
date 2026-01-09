"""LLM Service for interacting with language models."""

import json
from groq import Groq
from config.settings import GROQ_API_KEY
from config.prompts import SYSTEM_PROMPT, itinerary_prompt_template 


class LLMService:
    """Service for LLM operations using Groq."""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize LLM service.
        
        Args:
            model: Model name to use
        """
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = model
    
    def generate(self, messages: list, temperature: float = 0.2, response_format: str = None) -> str:
        """
        Generate completion from messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            response_format: Optional response format (e.g., 'json_object')
            
        Returns:
            Generated text content
        """
        kwargs = {
            "model": self.model,
            "temperature": temperature,
            "messages": messages
        }
        
        if response_format:
            kwargs["response_format"] = {"type": response_format}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def generate_with_prompt(self, user_prompt: str, system_prompt: str = None, temperature: float = 0.2) -> str:
        """
        Generate completion with system and user prompts.
        
        Args:
            user_prompt: User message
            system_prompt: System message (optional)
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        
        return self.generate(messages, temperature)
    
    def extract_json(self, content: str) -> dict:
        """
        Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            content: Response content that may contain JSON
            
        Returns:
            Parsed JSON dict
        """
        if not content:
            return {}
        
        content = content.strip()
        
        # Remove markdown code blocks
        if content.startswith("```"):
            parts = content.split("```")
            if len(parts) >= 2:
                content = parts[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {content}")
            print(f"Error: {e}")
            return {}


def generate_itinerary(user_query: str, days: int, places_context: list) -> str:
    """
    Generate a day-by-day travel itinerary.
    
    Args:
        user_query: User's travel request
        days: Number of days
        places_context: List of places with activities
        
    Returns:
        Formatted itinerary text
    """
    llm = LLMService()
    
    print(f"Generating itinerary with {len(places_context)} places for {days} days")
    
    prompt = itinerary_prompt_template(user_query, days, places_context)
    
    return llm.generate_with_prompt(
        user_prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2
    )

