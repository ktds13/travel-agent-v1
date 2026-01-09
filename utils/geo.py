"""Geo-location utilities for web search and location data."""

import requests
from typing import Optional, Tuple


def web_search_location(place_name: str) -> Optional[dict]:
    """
    Search for location information using OpenStreetMap Nominatim API.
    
    Args:
        place_name: Name of the place to search
        
    Returns:
        Dict with lat, lon, display_name or None if not found
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "TravelAgent/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        if results:
            result = results[0]
            return {
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
                "display_name": result["display_name"]
            }
    except Exception as e:
        print(f"Error searching location '{place_name}': {e}")
    
    return None


def get_region(location_data: dict) -> Optional[str]:
    """
    Extract region from location data.
    
    Args:
        location_data: Dict with location information
        
    Returns:
        Region name or None
    """
    if not location_data:
        return None
    
    display_name = location_data.get("display_name", "")
    parts = [p.strip() for p in display_name.split(",")]
    
    # Typically region is in parts[1] or parts[2]
    if len(parts) >= 2:
        return parts[1]
    
    return None


def get_coordinates(place_name: str) -> Optional[Tuple[float, float]]:
    """
    Get latitude and longitude for a place.
    
    Args:
        place_name: Name of the place
        
    Returns:
        Tuple of (latitude, longitude) or None
    """
    location = web_search_location(place_name)
    if location:
        return (location["lat"], location["lon"])
    return None
