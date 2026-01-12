"""Accommodation Tools for the Travel Agent."""

from typing import List, Optional, Dict
from smolagents import tool

from utils.geo import haversine_distance, find_nearby, get_coordinates
from database.connection import get_connection


@tool
def extract_accommodation_query(user_input: str) -> dict:
    """
    Extract accommodation preferences and requirements from user input.
    Parses location, budget, accommodation type, amenities, and other preferences.
    
    Use this as the first tool when user asks about accommodations, hotels, hostels, or where to stay.
    
    Args:
        user_input: The user's accommodation request
        
    Returns:
        dict: Contains 'location', 'place_name', 'type', 'price_range', 'amenities', 'radius_km', 'success'
    """
    from core.llm import LLMService
    
    prompt = f"""
Extract accommodation preferences from this query.

User query: "{user_input}"

Return ONLY valid JSON in this exact format:
{{
  "location": "Chiang Mai",
  "place_name": "Doi Kham",
  "type": "hotel",
  "price_range": "mid-range",
  "amenities": ["wifi", "pool"],
  "radius_km": 10
}}

Fields:
- location: City/region (e.g., "Chiang Mai", "Bangkok")
- place_name: Specific place to be near (e.g., "Doi Suthep", "Old City") or null
- type: hotel, hostel, resort, guesthouse, villa, or null for any
- price_range: budget, mid-range, luxury, or null for any
- amenities: List of desired amenities or empty array
- radius_km: Distance from place in km (default 10)

Use null for missing values. Do not add markdown formatting.
"""
    
    llm = LLMService()
    response = llm.generate_with_prompt(prompt, temperature=0)
    extracted = llm.extract_json(response)
    
    return {
        "location": extracted.get("location"),
        "place_name": extracted.get("place_name"),
        "type": extracted.get("type"),
        "price_range": extracted.get("price_range"),
        "amenities": extracted.get("amenities") or [],
        "radius_km": extracted.get("radius_km", 10),
        "success": True
    }


@tool
def search_accommodations(
    location: str = None,
    accommodation_type: str = None,
    price_range: str = None,
    min_rating: float = None,
    limit: int = 10
) -> List[dict]:
    """
    Search for accommodations based on filters.
    Returns hotels, hostels, resorts, and other accommodations matching criteria.
    
    Use this to find accommodations in a specific area with optional filters.
    
    Args:
        location: City or region name (e.g., "Chiang Mai", "Mae Kampong")
        accommodation_type: Type filter (hotel, hostel, resort, guesthouse, villa)
        price_range: budget, mid-range, or luxury
        min_rating: Minimum rating (0-5)
        limit: Maximum results to return
        
    Returns:
        List of accommodation dictionaries with name, type, location, price, rating, amenities
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    query = """
        SELECT 
            a.id,
            a.name,
            a.type,
            a.region,
            a.latitude,
            a.longitude,
            a.price_range,
            a.price_min,
            a.price_max,
            a.currency,
            a.rating,
            a.amenities,
            a.description,
            a.contact_info
        FROM accommodations a
        WHERE 1=1
    """
    
    params = []
    
    if location:
        query += " AND a.region LIKE ?"
        params.append(f"%{location}%")
    
    if accommodation_type:
        query += " AND a.type LIKE ?"
        params.append(f"%{accommodation_type}%")
    
    if price_range:
        query += " AND a.price_range = ?"
        params.append(price_range)
    
    if min_rating:
        query += " AND a.rating >= ?"
        params.append(min_rating)
    
    query += " ORDER BY a.rating DESC, a.price_min ASC"
    
    # SQL Server: Add TOP to SELECT instead of LIMIT
    query = query.replace("SELECT ", f"SELECT TOP {limit} ")
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    accommodations = []
    for row in results:
        import json
        amenities_list = json.loads(row[11]) if row[11] else []
        
        accommodations.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "region": row[3],
            "latitude": float(row[4]) if row[4] else None,
            "longitude": float(row[5]) if row[5] else None,
            "price_range": row[6],
            "price_min": float(row[7]) if row[7] else None,
            "price_max": float(row[8]) if row[8] else None,
            "currency": row[9],
            "rating": float(row[10]) if row[10] else None,
            "amenities": amenities_list,
            "description": row[12],
            "contact": row[13]
        })
    
    cursor.close()
    conn.close()
    
    if not accommodations:
        return [{
            "message": f"No accommodations found in {location or 'the area'}",
            "success": False
        }]
    
    return accommodations


@tool
def find_accommodation_near_place(
    place_name: str,
    radius_km: float = 10.0,
    accommodation_type: str = None,
    price_range: str = None,
    limit: int = 10
) -> str:
    """
    Find accommodations near a specific travel destination or landmark.
    Perfect for queries like "find hotel near Doi Suthep" or "accommodation near Old City".
    
    Use this when user wants to stay near a specific place, temple, attraction, or landmark.
    
    Args:
        place_name: Name of the place/landmark (e.g., "Doi Suthep", "Old City", "Doi Kham")
        radius_km: Search radius in kilometers (default: 10km)
        accommodation_type: Optional type filter (hotel, hostel, resort, etc.)
        price_range: Optional price filter (budget, mid-range, luxury)
        limit: Maximum results to return
        
    Returns:
        str: Formatted list of nearby accommodations with distances
    """
    # First, get coordinates of the place
    coords = get_coordinates(place_name)
    
    if not coords:
        # Try to find in database
        conn = get_connection("TravelAgentDB")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT TOP 1 latitude, longitude 
            FROM places 
            WHERE name LIKE ?
        """, (f"%{place_name}%",))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            return f"Could not find location coordinates for '{place_name}'. Please try a different place name or be more specific."
        
        coords = (float(result[0]), float(result[1]))
    
    target_lat, target_lon = coords
    
    # Get all accommodations (with optional filters)
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    query = """
        SELECT 
            a.name,
            a.type,
            a.region,
            a.latitude,
            a.longitude,
            a.price_range,
            a.price_min,
            a.price_max,
            a.currency,
            a.rating,
            a.amenities,
            a.description
        FROM accommodations a
        WHERE a.latitude IS NOT NULL AND a.longitude IS NOT NULL
    """
    
    params = []
    
    if accommodation_type:
        query += " AND a.type LIKE ?"
        params.append(f"%{accommodation_type}%")
    
    if price_range:
        query += " AND a.price_range = ?"
        params.append(price_range)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert to list of dicts
    import json
    all_accommodations = []
    for row in results:
        amenities_list = json.loads(row[10]) if row[10] else []
        all_accommodations.append({
            "name": row[0],
            "type": row[1],
            "region": row[2],
            "latitude": float(row[3]),
            "longitude": float(row[4]),
            "price_range": row[5],
            "price_min": float(row[6]) if row[6] else None,
            "price_max": float(row[7]) if row[7] else None,
            "currency": row[8],
            "rating": float(row[9]) if row[9] else None,
            "amenities": amenities_list,
            "description": row[11]
        })
    
    # Find accommodations within radius
    nearby = find_nearby(target_lat, target_lon, all_accommodations, radius_km=radius_km)
    
    if not nearby:
        return f"No accommodations found within {radius_km}km of {place_name}. Try increasing the search radius or check nearby cities."
    
    # Format response
    response = [f"**Accommodations near {place_name}** (within {radius_km}km):\n"]
    
    for i, (accommodation, distance) in enumerate(nearby[:limit], 1):
        price_str = f"${accommodation['price_min']}-{accommodation['price_max']}" if accommodation['price_min'] else "Price varies"
        rating_str = f"⭐ {accommodation['rating']}/5.0" if accommodation['rating'] else "Not rated"
        amenities_str = ", ".join(accommodation['amenities'][:5]) if accommodation['amenities'] else "Basic amenities"
        
        response.append(
            f"\n{i}. **{accommodation['name']}** ({accommodation['type'].title()})\n"
            f"   📍 {distance}km from {place_name}\n"
            f"   💰 {price_str} ({accommodation['price_range']})\n"
            f"   {rating_str}\n"
            f"   🏨 {amenities_str}\n"
            f"   {accommodation['description'][:150]}..."
        )
    
    return "\n".join(response)


@tool
def compare_accommodations(accommodations: List[dict]) -> str:
    """
    Compare multiple accommodations side-by-side.
    Shows price, rating, amenities, and key differences.
    
    Use this when user wants to compare different hotels or accommodation options.
    
    Args:
        accommodations: List of accommodation dictionaries to compare
        
    Returns:
        str: Detailed comparison of accommodations
    """
    if not accommodations or len(accommodations) < 2:
        return "Need at least 2 accommodations to compare. Please search for accommodations first."
    
    compare_list = accommodations[:3]  # Compare max 3
    
    response = ["**Accommodation Comparison**\n"]
    
    for i, acc in enumerate(compare_list, 1):
        price_str = f"${acc.get('price_min', '?')}-{acc.get('price_max', '?')}"
        rating = acc.get('rating', 'N/A')
        amenities = acc.get('amenities', [])
        amenities_str = ", ".join(amenities[:6]) if amenities else "Basic amenities"
        
        response.append(
            f"\n**{i}. {acc.get('name', 'Unknown')}** ({acc.get('type', 'accommodation').title()})\n"
            f"Region: {acc.get('region', 'N/A')}\n"
            f"Price: {price_str} ({acc.get('price_range', 'N/A')})\n"
            f"Rating: ⭐ {rating}/5.0\n"
            f"Amenities: {amenities_str}\n"
            f"Description: {acc.get('description', 'No description')[:120]}..."
        )
    
    # Add comparison summary if we have exactly 2
    if len(compare_list) == 2:
        acc1, acc2 = compare_list
        
        response.append("\n**Comparison Summary:**")
        
        # Price comparison
        if acc1.get('price_min') and acc2.get('price_min'):
            if acc1['price_min'] < acc2['price_min']:
                response.append(f"- **More affordable**: {acc1['name']}")
            elif acc2['price_min'] < acc1['price_min']:
                response.append(f"- **More affordable**: {acc2['name']}")
            else:
                response.append("- **Similar pricing**")
        
        # Rating comparison
        if acc1.get('rating') and acc2.get('rating'):
            if acc1['rating'] > acc2['rating']:
                response.append(f"- **Higher rated**: {acc1['name']} ({acc1['rating']} vs {acc2['rating']})")
            elif acc2['rating'] > acc1['rating']:
                response.append(f"- **Higher rated**: {acc2['name']} ({acc2['rating']} vs {acc1['rating']})")
            else:
                response.append(f"- **Same rating**: {acc1['rating']}/5.0")
        
        # Amenity differences
        amenities1 = set(acc1.get('amenities', []))
        amenities2 = set(acc2.get('amenities', []))
        
        unique1 = amenities1 - amenities2
        unique2 = amenities2 - amenities1
        
        if unique1:
            response.append(f"- **Unique to {acc1['name']}**: {', '.join(list(unique1)[:3])}")
        if unique2:
            response.append(f"- **Unique to {acc2['name']}**: {', '.join(list(unique2)[:3])}")
    
    return "\n".join(response)
