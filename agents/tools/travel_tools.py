"""Travel Tools for the Tool Calling Agent."""


from typing import List, Optional
from smolagents import tool

from utils.intent import extract_intent
from utils.rag import retrieve_places, build_rag_context
from database.operations import load_country_aliases
from core.llm import generate_itinerary


@tool
def extract_travel_query(user_input: str) -> dict:
    """
    Main Tool for extracting travel-related queries from user input.
    Automatically extracts intent (region, country, activities, days, etc.),
    searches database with appropriate filters, and returns structured results.

    Use this tool as the primary tool for any travel-related user input.

    Args:
        user_input: The user's input string containing travel requests.

    Returns:
        dict: Contains 'intent', 'places', 'days', 'message', 'success'.
    """

    intent = extract_intent(user_input)

        # Normalize country using aliases
    country = intent.get("country")
    if country:
        aliases = load_country_aliases()
        normalized = aliases.get(country)
        if normalized:
            print(f"Country normalized: {country} -> {normalized}")
            intent["country"] = normalized
        else:
            print(f"Country '{country}' not in database, skipping filter")
            intent["country"] = None

      # Search database - prefer activities over category
    use_category = intent.get("category") if not intent.get("activities") else None
    use_country = None  # Skip country filter to avoid over-filtering
    
    retrieved = retrieve_places(
        query=user_input,
        place_name=intent.get("place_name"),
        region=intent.get("region"),
        country=use_country,
        category=use_category,
        requested_activities=intent.get("activities") or [],
        top_k=5
    )
    
    places = build_rag_context(retrieved)
    
    if not places:
        missing = []
        if not intent.get("region") and not intent.get("country"):
            missing.append("location (region or country)")
        if not intent.get("activities") and not intent.get("category"):
            missing.append("activity type or category")
        
        message = "No places found matching your criteria."
        if missing:
            message += f" Missing: {', '.join(missing)}. Please provide more details."
        
        return {
            "intent": intent,
            "places": [],
            "days": intent.get("days"),
            "message": message,
            "success": False
        }
    
    return {
        "intent": intent,
        "places": places,
        "days": intent.get("days") or 3,
        "message": f"Found {len(places)} places matching your query.",
        "success": True
    }

@tool
def generate_travel_itinerary(query: str, places: List[dict], days: Optional[int] = None) -> str:
    """
    Generate a day-by-day travel itinerary from a list of places.

    Args:
        query: The user's original travel request.
        places: List of places to include in the itinerary.
        days: Number of days for the trip. Defaults to 3 if not provided.
    
    Returns:
        str: A formatted travel itinerary in markdown.
    """
    if not places:
        return "Cannot generate itinerary: No places provided. Please search for places first."
    
    trip_days = days if days is not None else 3
    return generate_itinerary(query, trip_days, places)


@tool
def suggest_places(query: str, places: List[dict]) -> str:
    """
    Suggest travel places based on user preferences.
    Returns a list of recommended places with brief descriptions.
    
    Use this when user asks for suggestions like:
    - "What places should I visit?"
    - "Suggest some destinations"
    - "Where can I go for..."

    Args:
        query: The user's travel query.
        places: List of places with activities and relevance.
    
    Returns:
        str: Formatted list of place suggestions with activities.
    """
    if not places:
        return "I couldn't find any places to suggest. Please provide more details about your preferences."
    
    suggestions = ["Based on your query, here are some suggested places to visit:\n"]
    for i, place in enumerate(places, 1):
        activities_str = ", ".join(place.get("activities", [])[:5])
        relevance = place.get("relevance", 0)
        suggestions.append(
            f"{i}. **{place['name']}** (relevance: {relevance:.2f})\n"
            f"   Activities: {activities_str}"
        )
    
    return "\n".join(suggestions)


@tool
def describe_place(place_name: str, places: List[dict]) -> str:
    """
    Describe a specific travel place in detail.
    Provides information about activities, characteristics, and recommendations.
    
    Use this when user asks about a specific place:
    - "Tell me about [place]"
    - "What can I do in [place]?"
    - "Describe [place]"

    Args:
        place_name: Name of the place to describe.
        places: List of places to search from.
    
    Returns:
        str: Detailed description of the place.
    """
    if not places:
        return f"I couldn't find information about '{place_name}' in the database."
    
    # Find matching place
    target_place = None
    for place in places:
        if place_name.lower() in place["name"].lower() or place["name"].lower() in place_name.lower():
            target_place = place
            break
    
    if not target_place:
        target_place = places[0]  # Use most relevant
    
    activities = target_place.get("activities", [])
    activities_str = ", ".join(activities)
    
    description = f"**{target_place['name']}**\n\n"
    description += f"{target_place['name']} is a wonderful destination "
    
    if activities:
        description += f"known for activities such as {activities_str}. "
    
    description += "\n\nThis location offers a variety of experiences that make it a great choice for travelers"
    
    if len(activities) >= 2:
        description += f" interested in {activities[0]} and {activities[1]}."
    elif len(activities) == 1:
        description += f" interested in {activities[0]}."
    else:
        description += " interested in exploration and adventure."
    
    return description


@tool
def plan_activity_focused_trip(query: str, places: List[dict], activities: List[str] = None) -> str:
    """
    Plan a trip focused on specific activities across multiple places.
    Groups places by shared activities.

    Args:
        query: The user's travel query.
        places: List of places with activities.
        activities: List of activities to focus on (optional).
    
    Returns:
        str: Activity-focused trip plan.
    """
    if not places:
        return "No places found for the requested activities."
    
    # Collect all activities
    all_activities = set()
    for place in places:
        all_activities.update([a.lower() for a in place.get("activities", [])])
    
    # Filter by requested activities
    if activities:
        relevant = [a for a in all_activities if any(req.lower() in a.lower() for req in activities)]
    else:
        relevant = list(all_activities)
    
    response = ["**Activity-Focused Trip Plan**\n"]
    response.append("Based on your interests, here are activities you can enjoy:\n")
    
    # Group places by activity
    activity_places = {}
    for activity in relevant:
        activity_places[activity] = []
        for place in places:
            place_acts = [a.lower() for a in place.get("activities", [])]
            if activity in place_acts:
                activity_places[activity].append(place["name"])
    
    for activity, place_list in sorted(activity_places.items(), key=lambda x: len(x[1]), reverse=True):
        if place_list:
            places_str = ", ".join(place_list[:3])
            response.append(f"\n**{activity.title()}**")
            response.append(f"Available at: {places_str}")
    
    return "\n".join(response)


@tool
def compare_places(places: List[dict], place_names: Optional[List[str]] = None) -> str:
    """
    Compare two or more travel places side-by-side.

    Args:
        places: List of places to compare.
        place_names: Optional specific place names to compare.
    
    Returns:
        str: Detailed comparison of places.
    """
    if not places or len(places) < 2:
        return "I need at least 2 places to make a comparison."
    
    # Filter to specific names if provided
    if place_names and len(place_names) >= 2:
        filtered = []
        for name in place_names[:3]:
            for place in places:
                if name.lower() in place["name"].lower() or place["name"].lower() in name.lower():
                    filtered.append(place)
                    break
        if len(filtered) >= 2:
            places = filtered
    
    compare_list = places[:min(3, len(places))]
    
    response = ["**Place Comparison**\n"]
    
    for i, place in enumerate(compare_list, 1):
        activities = ", ".join(place.get("activities", [])[:6])
        relevance = place.get("relevance", 0)
        response.append(f"\n**{i}. {place['name']}** (relevance: {relevance:.2f})")
        response.append(f"Activities: {activities}")
    
    # Summary
    if len(compare_list) >= 2:
        p1 = compare_list[0]
        p2 = compare_list[1]
        
        p1_acts = set([a.lower() for a in p1.get("activities", [])])
        p2_acts = set([a.lower() for a in p2.get("activities", [])])
        
        shared = p1_acts & p2_acts
        unique_p1 = p1_acts - p2_acts
        unique_p2 = p2_acts - p1_acts
        
        response.append("\n**Summary:**")
        if shared:
            response.append(f"- Shared: {', '.join(list(shared)[:3])}")
        if unique_p1:
            response.append(f"- Unique to {p1['name']}: {', '.join(list(unique_p1)[:3])}")
        if unique_p2:
            response.append(f"- Unique to {p2['name']}: {', '.join(list(unique_p2)[:3])}")
    
    return "\n".join(response)