"""Geo-location utilities for web search and location data."""

import requests
import math
from typing import Optional, Tuple, List, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
        
    Returns:
        Distance in kilometers
        
    Examples:
        >>> haversine_distance(18.7883, 98.9853, 18.8050, 98.9219)
        2.13  # approximately 2.13 km
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return round(distance, 2)


def find_nearby(
    target_lat: float,
    target_lon: float,
    items: List[dict],
    radius_km: float = 10.0,
    lat_key: str = 'latitude',
    lon_key: str = 'longitude'
) -> List[Tuple[dict, float]]:
    """
    Find items within a specified radius of a target location.
    
    Args:
        target_lat: Target latitude
        target_lon: Target longitude
        items: List of dictionaries with location data
        radius_km: Search radius in kilometers (default: 10km)
        lat_key: Key name for latitude in items (default: 'latitude')
        lon_key: Key name for longitude in items (default: 'longitude')
        
    Returns:
        List of tuples (item, distance_km) sorted by distance, ascending
        
    Examples:
        >>> places = [{'name': 'Place A', 'latitude': 18.8, 'longitude': 98.9}]
        >>> nearby = find_nearby(18.79, 98.98, places, radius_km=5)
        >>> [(item['name'], dist) for item, dist in nearby]
        [('Place A', 1.52)]
    """
    nearby_items = []
    
    for item in items:
        # Skip items without coordinates
        if lat_key not in item or lon_key not in item:
            continue
            
        item_lat = item.get(lat_key)
        item_lon = item.get(lon_key)
        
        # Skip if coordinates are None
        if item_lat is None or item_lon is None:
            continue
        
        # Calculate distance
        distance = haversine_distance(target_lat, target_lon, float(item_lat), float(item_lon))
        
        # Add if within radius
        if distance <= radius_km:
            nearby_items.append((item, distance))
    
    # Sort by distance (closest first)
    nearby_items.sort(key=lambda x: x[1])
    
    return nearby_items


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
