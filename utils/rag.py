"""RAG (Retrieval-Augmented Generation) utilities."""

import numpy as np
from database.queries import get_place_activities
from core.embedding import text_to_embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity score
    """
    return np.dot(a, b)


def retrieve_places(
    query: str,
    place_name: str = None,
    region: str = None,
    country: str = None,
    category: str = None,
    requested_activities: list = None,
    top_k: int = 5
):
    """
    Retrieve places from database with filters and semantic ranking.
    
    Args:
        query: Search query
        place_name: Filter by place name
        region: Filter by region
        country: Filter by country
        category: Filter by category
        requested_activities: Filter by activities
        top_k: Number of results
        
    Returns:
        List of tuples: (score, place_dict)
    """
    print(f"Retrieving places: region={region}, country={country}, category={category}")
    print(f"Requested activities: {requested_activities}")
    
    # Get places from database
    places_data = get_place_activities(query, place_name, region, country, category)
    
    candidates = []
    for name, place_activities_str, embedding in places_data:
        print(f"Evaluating place: {name}")
        print(f"  Activities: {place_activities_str}")
        
        # Parse activities
        if isinstance(place_activities_str, str):
            place_activities = [a.strip() for a in place_activities_str.split(",")]
        else:
            place_activities = []
        
        place_activities = [a.lower() for a in place_activities]
        
        # Filter by activities if specified
        if requested_activities:
            match = all(
                any(req.lower() == act for act in place_activities)
                for req in requested_activities
            )
            if not match:
                print(f"  Skipping {name} due to activity mismatch")
                continue
        
        # Skip places with missing or corrupted embeddings
        if embedding is None:
            print(f"  Skipping {name} due to missing embedding")
            continue
        
        try:
            emb_array = np.frombuffer(embedding, dtype=np.float32)
        except ValueError as e:
            print(f"  Skipping {name} due to corrupted embedding: {e}")
            continue
        
        candidates.append({
            "name": name,
            "activities": place_activities,
            "embedding": emb_array
        })
    
    if not candidates:
        print("No candidates after filtering")
        return []
    
    # Semantic ranking
    q_emb = text_to_embedding(query).reshape(1, -1)
    place_embs = np.vstack([
        p["embedding"].reshape(1, -1) if p["embedding"].ndim == 1 else p["embedding"]
        for p in candidates
    ])
    
    scores = np.dot(place_embs, q_emb.T).flatten()
    
    ranked = sorted(
        zip(scores, candidates),
        key=lambda x: x[0],
        reverse=True
    )
    
    return ranked[:top_k]


def build_rag_context(ranked_places):
    """
    Build RAG context from ranked places.
    
    Args:
        ranked_places: List of (score, place_dict) tuples
        
    Returns:
        List of place dicts with name, activities, relevance
    """
    context = []
    for score, place in ranked_places:
        print(f"Building RAG context for place: {place['name']}")
        context.append({
            "name": place["name"],
            "activities": place["activities"],
            "relevance": round(float(score), 3)
        })
    return context
