"""Quick test of the Travel Agent v2."""

import sys
import os

# Add travel_agent_v2 to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import create_travel_agent


def main():
    """Test creating and running the travel agent."""
    print("Testing Travel Agent v2...")
    print("=" * 80)
    
    # Test query
    test_query = "suggest places to visit in Chiang Mai"
    
    print(f"\nCreating travel agent...")
    try:
        agent = create_travel_agent()
        print("✓ Agent created successfully")
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        return
    
    print(f"\nRunning test query: '{test_query}'")
    print("-" * 80)
    
    try:
        result = agent.run(test_query)
        print("\n✓ Query executed successfully")
        print("\nResult:")
        print(result)
    except Exception as e:
        print(f"\n✗ Error running query: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()