"""Test script for mode-based agent generation."""

import os
from dotenv import load_dotenv
load_dotenv()

from agents.factory import list_available_modes, GenerationMode, create_agent_for_mode
from utils.intent import classify_generation_mode

def test_mode_listing():
    """Test listing available modes."""
    print("=" * 80)
    print("TEST: List Available Modes")
    print("=" * 80)
    
    modes = list_available_modes()
    for mode in modes:
        print(f"\n{mode['mode']} ({mode['value']})")
        print(f"  Description: {mode['description']}")
    
    print(f"\nTotal modes: {len(modes)}")
    assert len(modes) == 5, "Should have 5 modes"
    print("✓ Mode listing test passed\n")


def test_mode_classification():
    """Test query classification into modes."""
    print("=" * 80)
    print("TEST: Mode Classification")
    print("=" * 80)
    
    test_queries = [
        ("Plan a 3-day trip to Chiang Mai", "itinerary"),
        ("What places should I visit in Thailand?", "suggest_places"),
        ("Tell me about Doi Suthep", "describe_place"),
        ("Where can I go hiking in Chiang Mai?", "activity_focused"),
        ("Compare beaches in Thailand and Myanmar", "comparison"),
    ]
    
    for query, expected_mode in test_queries:
        result = classify_generation_mode(query)
        detected_mode = result["generation_mode"]
        match = "✓" if detected_mode == expected_mode else "✗"
        print(f"\n{match} Query: {query}")
        print(f"  Expected: {expected_mode}")
        print(f"  Detected: {detected_mode}")
        if result.get("days"):
            print(f"  Days: {result['days']}")
    
    print("\n✓ Mode classification test completed\n")


def test_agent_creation():
    """Test creating agents for each mode."""
    print("=" * 80)
    print("TEST: Agent Creation for Each Mode")
    print("=" * 80)
    
    for mode in GenerationMode:
        print(f"\n{mode.value}:")
        try:
            agent = create_agent_for_mode(mode)
            tools = [tool.name for tool in agent.tools]
            print("  ✓ Agent created successfully")
            print(f"  Tools ({len(tools)}): {', '.join(tools)}")
            print(f"  Max steps: {agent.max_steps}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
    
    print("\n✓ Agent creation test completed\n")


def test_mode_specific_tools():
    """Test that mode-specific agents have only relevant tools."""
    print("=" * 80)
    print("TEST: Mode-Specific Tool Configuration")
    print("=" * 80)
    
    # Expected tools for each mode
    expected_tools = {
        GenerationMode.ITINERARY: {"extract_travel_query", "generate_travel_itinerary"},
        GenerationMode.SUGGEST_PLACES: {"extract_travel_query", "suggest_places"},
        GenerationMode.DESCRIBE_PLACE: {"extract_travel_query", "describe_place"},
        GenerationMode.ACTIVITY_FOCUSED: {"extract_travel_query", "plan_activity_focused_trip"},
        GenerationMode.COMPARISON: {"extract_travel_query", "compare_places"},
    }
    
    for mode, expected in expected_tools.items():
        agent = create_agent_for_mode(mode)
        actual = {tool.name for tool in agent.tools}
        
        if actual == expected:
            print(f"\n✓ {mode.value}: Tools match expected")
            print(f"  {', '.join(sorted(actual))}")
        else:
            print(f"\n✗ {mode.value}: Tools mismatch")
            print(f"  Expected: {', '.join(sorted(expected))}")
            print(f"  Actual: {', '.join(sorted(actual))}")
    
    print("\n✓ Tool configuration test completed\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MODE-BASED AGENT GENERATION TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_mode_listing()
        test_mode_classification()
        test_agent_creation()
        test_mode_specific_tools()
        
        print("=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n{'=' * 80}")
        print(f"TEST SUITE FAILED: {e}")
        print(f"{'=' * 80}")
        import traceback
        traceback.print_exc()
