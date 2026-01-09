import json
import numpy as np
from .connection import get_connection

def link_place_activities(cursor, place_id: int, activities: list):
    """
    Link activities to a place in the junction table.
    
    Args:
        cursor: Database cursor
        place_id: Place ID
        activities: List of activity names
    """
    for activity_name in activities:
        # Get or create activity
        cursor.execute(
            "SELECT id FROM activities WHERE name = ?",
            activity_name
        )
        row = cursor.fetchone()
        
        if row:
            activity_id = row[0]
        else:
            cursor.execute(
                "INSERT INTO activities (name) OUTPUT INSERTED.id VALUES (?)",
                activity_name
            )
            activity_id = cursor.fetchone()[0]
        
        # Link place and activity
        cursor.execute(
            "INSERT INTO place_activities (place_id, activity_id) VALUES (?, ?)",
            place_id, activity_id
        )


def insert_place(data: dict):
    """
    Insert a place into the database.
    
    Args:
        data: Dict with place information including:
            - name: Place name
            - category: Category
            - country: Country ID or None
            - region: Region name
            - latitude, longitude: Coordinates
            - activities: List of activity names
            - raw_text: Raw description text
            - embedding: Embedding bytes
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO places 
        (name, category, country, region, latitude, longitude, activities, raw_text, embedding)
        OUTPUT INSERTED.id
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Convert activities list to JSON string
    activities = data.get("activities")
    if activities and isinstance(activities, list):
        activities_json = json.dumps(activities)
    else:
        activities_json = None
    
    cursor.execute(
        sql,
        data["name"],
        data.get("category"),
        data.get("country"),
        data.get("region"),
        data.get("latitude"),
        data.get("longitude"),
        activities_json,
        data.get("raw_text"),
        data.get("embedding")
    )
    
    row = cursor.fetchone()
    if not row:
        raise Exception("Failed to retrieve place_id")
    
    place_id = row[0]
    print(f"Inserted place ID: {place_id}")
    
    # Link activities
    if data.get("activities"):
        link_place_activities(cursor, place_id, data.get("activities", []))
    
    conn.commit()
    conn.close()

def delete_place_by_name(name: str):
    """
    Delete a place by name.
    
    Args:
        name: Place name
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM place_activities WHERE place_id IN (SELECT id FROM places WHERE name = ?)",
        name
    )
    cursor.execute("DELETE FROM places WHERE name = ?", name)
    
    conn.commit()
    conn.close()


def clear_places():
    """Clear all places from database."""
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM place_activities WHERE place_id IN (SELECT id FROM places)")
    cursor.execute("DELETE FROM places")
    
    conn.commit()
    conn.close()


def get_country_id(country_name: str):
    """
    Get country ID by name.
    
    Args:
        country_name: Country name
        
    Returns:
        Country ID or None
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM Countries WHERE name = ?", country_name)
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None


def load_country_aliases():
    """
    Load country aliases mapping.
    
    Returns:
        Dict mapping alias -> canonical country name
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ca.alias, c.name
        FROM CountryAliases ca
        JOIN Countries c ON ca.country_id = c.id
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return {alias: country for alias, country in rows}