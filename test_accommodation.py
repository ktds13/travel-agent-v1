"""
Test script for Accommodation Finder Agent
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.factory import GenerationMode, create_agent_for_mode

def test_accommodation_queries():
    """Test various accommodation finder queries."""
    
    test_queries = [
        "find hotel near Doi Kham",
        "find budget accommodation in Chiang Mai",
        "where to stay near Doi Inthanon",
        "compare hotels near Doi Suthep",
        "find luxury resort in Chiang Mai mountains",
    ]
    
    print("=" * 80)
    print("ACCOMMODATION FINDER AGENT TEST")
    print("=" * 80)
    print()
    
    # Create accommodation finder agent
    agent = create_agent_for_mode(GenerationMode.FIND_ACCOMMODATION)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}: {query}")
        print('=' * 80)
        
        try:
            result = agent.run(query)
            print(f"\nResult:\n{result}")
        except Exception as e:
            print(f"\nError: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_accommodation_queries()
