from smolagents import tool
from database.operations import (
    get_country_id,
    insert_place,
    delete_place_by_name,
    clear_places
)
from core.embedding import embed_to_bytes

@tool
def extract_place_structured(
    name: str,
    category: str | None = None,
    country: str | None = None,
    region: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    activities: list[str] | None = None,
    raw_text: str | None = None
) -> dict:
    """
    Extract structured travel place data from raw description.

    Args:
        name (str): Full place name in English.
        category (str | None): Place category (e.g., city, beach).
        country (str | None): Country ID from database.
        region (str | None): Region or city name.
        latitude (float | None): Latitude of the place.
        longitude (float | None): Longitude of the place.
        activities (list[str]): List of activities.
        raw_text (str): Original input text.
    Returns:
        dict: A structured dictionary containing name, category, country,
            region, activities, and raw_text (without embedding).
    """

    return{
        "name": name,
        "category": category,
        "country":  country,
        "region": region,
        "latitude": latitude,
        "longitude": longitude,
        "activities": activities or [],
        "raw_text": raw_text
    }

@tool
def get_country_id_by_name(country: str) -> int:
    """
    Get the country ID from the database by country name.

    Args:
        country (str): The name of the country.
    Returns:
        int: The ID of the country in the database, or None if not found.
     """
   
    country_id = get_country_id(country)
    return country_id
@tool
def final_answer(answer: str) -> str:
    """
    Return the final answer string.

    Args:
        answer (str): The final answer string.
    Returns:
        str: The same final answer string.
    """
    return answer

@tool
def delete_place_tool(name: str) -> str:
    """
    Delete a place from the database by name.

    Args:
        name (str): The exact name of the place to delete.
    Returns:
        str: Confirmation message indicating whether the place was deleted.
    """
    try:
        delete_place_by_name(name)
        return f"Successfully deleted place: {name}"
    except Exception as e:
        return f"Error deleting place '{name}': {str(e)}"

@tool
def delete_all_places_tool() -> str:
    """
    Delete all places from the database.
    WARNING: This will permanently remove all place records and their associated activities.

    Returns:
        str: Confirmation message indicating all places were deleted.
    """
    try:
        clear_places()
        return "Successfully deleted all places from the database."
    except Exception as e:
        return f"Error deleting all places: {str(e)}"

@tool
def web_search_location(place_name: str, known_country: str = None, known_region: str = None) -> dict:
    """
    Search to find location details for a place including country, region, latitude, and longitude.
    Uses OpenStreetMap for coordinates and reverse geocoding for missing location data.
    Country and region names are in English.

    Args:
        place_name (str): The name of the place to search for.
        known_country (str): Already extracted country name (optional) in English.
        known_region (str): Already extracted region name (optional) in English.
    Returns:
        dict: Location details containing country, region, latitude, and longitude.
    """
    import requests
    
    country = known_country
    region = known_region
    latitude = None
    longitude = None
    
    try:
        # Build search query with all known information
        search_parts = [place_name]
        if region:
            search_parts.append(region)
        if country:
            search_parts.append(country)
        search_query = ", ".join(search_parts)
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": search_query,
            "format": "json",
            "addressdetails": 1,
            "limit": 3
        }
        headers = {
            "User-Agent": "TravelAgent/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            best_result = None
            for result in data:
                address = result.get("address", {})
                result_country = address.get("country")
                
                if region:
                    result_region = (
                        address.get("state") or 
                        address.get("region") or 
                        address.get("province") or
                        address.get("county") or
                        address.get("city") or
                        address.get("town")
                    )
                    if result_region and region.lower() in result_region.lower():
                        best_result = result
                        break
                if country and country.lower() in result_country.lower():
                    best_result = result
            if not best_result:
                best_result = data[0]
             
            latitude = float(best_result.get("lat")) if best_result.get("lat") else None
            longitude = float(best_result.get("lon")) if best_result.get("lon") else None
            
            # Extract country and region from OpenStreetMap address data
            address = best_result.get("address", {})
            
            if not country:
                country = address.get("country")
            
            if not region:
                # Try multiple possible region fields in order of preference
                region = (
                    address.get("state") or 
                    address.get("region") or 
                    address.get("province") or
                    address.get("county") or
                    address.get("city") or
                    address.get("town")
                )
                    
    except Exception as e:
        print(f"OpenStreetMap error: {e}")
    
    return {
        "country": country,
        "region": region,
        "latitude": latitude,
        "longitude": longitude
    }

@tool
def insert_place_data(data: dict) -> str:
    """
    Insert place data into the database.
    Generates embedding from raw_text before insertion.

    Args:
        data (dict): The place data to insert.
    Returns:
        str: Confirmation message.
    """
    # Generate embedding from raw_text before inserting
    if data.get("raw_text"):
        data["embedding"] = embed_to_bytes(data["raw_text"])
    else:
        data["embedding"] = None
   
    if data.get('embedding'):
        print(f"DEBUG: embedding length: {len(data['embedding'])} bytes")
    
    insert_place(data)
    return f'Inserted place: {data["name"]}'