"""
Quick test for Accommodation Finder Agent
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.factory import GenerationMode, create_agent_for_mode

# Create accommodation finder agent
agent = create_agent_for_mode(GenerationMode.FIND_ACCOMMODATION)

# Test single query
query = "find hotel near Doi Suthep"
print(f"Query: {query}\n")
result = agent.run(query)
print(f"\nResult:\n{result}")
