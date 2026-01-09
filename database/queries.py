"""Database query operations."""

import numpy as np
from .connection import get_connection
from core.embedding import text_to_embedding


def get_place_activities(
    query: str,
    place_name: str = None,
    region: str = None,
    country: str = None,
    category: str = None
):
    """
    Get places with their activities based on filters.
    
    Args:
        query: Search query for semantic fallback
        place_name: Filter by place name
        region: Filter by region
        country: Filter by country name
        category: Filter by category
        
    Returns:
        List of tuples: (name, activities_string, embedding_bytes)
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    # If no filters, use semantic search
    if not any([place_name, region, country, category]):
        return semantic_search_all(query, top_k=5)
    
    sql = """
        SELECT
            p.name,
            STRING_AGG(a.name, ', ') AS activities,
            p.embedding
        FROM places p
        JOIN place_activities pa ON p.id = pa.place_id
        JOIN activities a ON pa.activity_id = a.id
    """
    
    # Add country join if needed
    if country:
        sql += " LEFT JOIN Countries c ON p.country = c.id"
    
    sql += " WHERE 1=1"
    
    params = []
    
    if place_name:
        sql += " AND p.name LIKE ?"
        params.append(f"%{place_name}%")
    
    if region:
        sql += " AND p.region LIKE ?"
        params.append(f"%{region}%")
    
    if country:
        sql += " AND c.name LIKE ?"
        params.append(f"%{country}%")
    
    if category:
        sql += " AND p.category LIKE ?"
        params.append(f"%{category}%")
    
    sql += " GROUP BY p.name, p.region, p.embedding"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    print(f"Retrieved {len(rows)} rows from database.")
    conn.close()
    
    return rows


def filter_by_region(region: str):
    """
    Filter places by region.
    
    Args:
        region: Region name to filter
        
    Returns:
        List of place dicts with name, activities, embedding
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, region, activities, embedding FROM places WHERE region = ?",
        region
    )
    rows = cursor.fetchall()
    conn.close()
    
    places = []
    for name, region, activities, embedding in rows:
        if embedding:
            emb_array = np.frombuffer(embedding, dtype=np.float32)
        else:
            emb_array = None
            
        places.append({
            "name": name,
            "activities": activities,
            "embedding": emb_array
        })
    
    return places


def semantic_search_all(query: str, top_k: int = 5):
    """
    Semantic search across all places.
    
    Args:
        query: Search query
        top_k: Number of top results
        
    Returns:
        List of tuples: (name, activities_string, embedding_bytes)
    """
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.name,
            STRING_AGG(a.name, ', ') AS activities,
            p.embedding
        FROM places p
        JOIN place_activities pa ON p.id = pa.place_id
        JOIN activities a ON pa.activity_id = a.id
        GROUP BY p.name, p.embedding
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return semantic_rank(rows, query, top_k)


def semantic_rank(rows, query: str, top_k: int):
    """
    Rank database rows by semantic similarity.
    
    Args:
        rows: Database rows with embeddings
        query: Query text
        top_k: Number of results to return
        
    Returns:
        Top-k ranked rows
    """
    q_emb = text_to_embedding(query)
    
    scored = []
    for row in rows:
        if row.embedding:
            try:
                emb = np.frombuffer(row.embedding, dtype=np.float32)
                score = np.dot(q_emb, emb)
                scored.append((score, row))
            except ValueError:
                # Skip corrupted embeddings
                continue
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [row for _, row in scored[:top_k]]