"""Test multi-agent orchestrator with various query types."""

import os
from dotenv import load_dotenv
from agents.orchestrator import route_multi_intent, clear_agent_cache

load_dotenv()

def test_query(query: str, description: str):
    """Test a single query and display results."""
    print("\n" + "=" * 80)
    print(f"TEST: {description}")
    print("=" * 80)
    print(f"Query: {query}")
    print("\nProcessing...")
    
    try:
        response, mode = route_multi_intent(query)
        print(f"\n[Mode Used: {mode}]")
        print("\nResponse:")
        print("-" * 80)
        print(response)
        print("-" * 80)
        print("✓ Success")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test suite for multi-agent orchestrator."""
    print("\n" + "=" * 80)
    print("MULTI-AGENT ORCHESTRATOR TEST SUITE")
    print("=" * 80)
    print("\nTesting various query types:")
    print("  1. Single-intent queries (should use specific specialist)")
    print("  2. Multi-intent queries (should use multi-agent orchestrator)")
    print("\n")
    
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    
    # Test 1: Single-intent - Itinerary
    test_query(
        "plan 3-day trip to Chiang Mai",
        "Single Intent: Itinerary Planning"
    )
    
    # Test 2: Single-intent - Accommodation
    test_query(
        "find hotel near Doi Suthep",
        "Single Intent: Accommodation Search"
    )
    
    # Test 3: Single-intent - Place Description
    test_query(
        "tell me about Mae Kampong",
        "Single Intent: Place Description"
    )
    
    # Test 4: Multi-intent - Accommodation + Description
    test_query(
        "find hotel near Doi Suthep and describe the temple",
        "Multi-Intent: Accommodation + Place Description"
    )
    
    # Test 5: Multi-intent - Itinerary + Accommodation
    test_query(
        "plan 3-day trip to Chiang Mai and suggest hotels",
        "Multi-Intent: Itinerary + Accommodation"
    )
    
    # Test 6: Multi-intent - Comparison + Accommodation
    test_query(
        "compare Chiang Mai and Bangkok and find hotels in both cities",
        "Multi-Intent: Comparison + Accommodation"
    )
    
    # Test 7: Single-intent - Comparison
    test_query(
        "compare Mae Kampong and Chiang Dao",
        "Single Intent: Destination Comparison"
    )
    
    # Test 8: Multi-intent - Places + Activity
    test_query(
        "suggest places for hiking in Chiang Mai and plan activities",
        "Multi-Intent: Place Suggestion + Activity Planning"
    )
    
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print("  - Single-intent queries should route to specific specialists")
    print("  - Multi-intent queries should use 'multi-agent' orchestrator")
    print("  - All queries should complete without errors")
    print("\n")

if __name__ == "__main__":
    main()
