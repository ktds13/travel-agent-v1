from smolagents import ToolCallingAgent
from core.models import get_azure_model
from agents.tools.data_tools import (
    extract_place_structured,
    get_country_id_by_name,
    insert_place_data,
    delete_place_tool,
    delete_all_places_tool,
    web_search_location
)

"""Data Agent module for Travel Agent application."""

DATA_AGENT_INSTRUCTIONS = """
You are a travel data extraction agent.

STRICT PROCESS:

FOR INSERTION:
1. Read the user text and extract structured fields (name, country, region, latitude, longitude, category, activities)
2. Store the raw user text as raw_text variable
3. If latitude or longitude is unknown, call web_search_location(place_name, known_country, known_region) 
   - Pass any country or region you extracted from the text
   - This helps find the correct location
4. Extract latitude, longitude from the search result
5. If country or region is still unknown after search, use the values from web_search_location
6. Place name, country name, and region must be in English
7. Call get_country_id_by_name(country) to get the country ID
8. Call extract_place_structured with ALL these parameters:
   - name, category, country (ID), region, latitude, longitude, activities, raw_text
9. Get the dictionary result from extract_place_structured and pass it DIRECTLY to insert_place_data
10. Return the confirmation message

FOR SINGLE PLACE DELETION:
1. If user requests to delete/remove a specific place, extract the place name from the request
2. Call delete_place_tool(name) with the exact place name
3. Return the confirmation message

FOR DELETE ALL PLACES:
1. If user requests to delete/remove ALL places (e.g., "delete all places", "clear database", "remove everything")
2. Call delete_all_places_tool() with no arguments
3. Return the confirmation message

CRITICAL RULES:
- When calling web_search_location, ALWAYS pass known_region if you extracted "Chiang Mai" or any region from the text
- This prevents finding wrong locations in other countries
- Pass the COMPLETE dict from extract_place_structured to insert_place_data without modification
- For delete all: Look for keywords like "all", "everything", "clear", "empty" combined with "places" or "database"
"""

def create_data_agent(deployment_name: str = None, max_steps: int = 10) -> ToolCallingAgent:
    """
    Create a Data Agent using Tool Calling Agent.

    Args:
        deployment_name: Name of the Azure OpenAI deployment (defaults to env var)
        max_steps: Maximum steps for the agent to take

    Returns:
        Configured ToolCallingAgent instance
    """
    model = get_azure_model(deployment_name)

    tools = [
        extract_place_structured,
        get_country_id_by_name,
        insert_place_data,
        delete_place_tool,
        delete_all_places_tool,
        web_search_location
    ]

    agent = ToolCallingAgent(
        tools=tools,
        model=model,
        instructions=DATA_AGENT_INSTRUCTIONS,
        max_steps=max_steps
    )

    return agent