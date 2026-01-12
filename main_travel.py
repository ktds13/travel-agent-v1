"""Main entry point for Travel Agent REPL."""

import os
from dotenv import load_dotenv
from agents import create_travel_agent_for_query
load_dotenv()

def main():
    """Run the Travel Agent interactive REPL."""
    print("=" * 80)
    print("TRAVEL AGENT v2.0 - Mode-Based Agent System")
    print("=" * 80)
    print("Agent will automatically select the best mode for your query.")
    print("Available modes: itinerary, suggest_places, describe_place, activity_focused, comparison")
    print("\nType 'exit' or 'quit' to end the session.\n")
    
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    
    while True:
        try:
            query = input("\nYou: ")
            
            if query.lower().strip() in ['exit', 'quit', 'q']:
                print("Thank you for using Travel Agent. Goodbye!")
                break
            
            if not query.strip():
                continue
            
            print("\nCreating mode-specific agent...")
            agent, mode = create_travel_agent_for_query(query, deployment_name)
            print(f"Mode detected: {mode}")
            
            print("\nTravel Agent:")
            result = agent.run(query)
            print(result)
            print()
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different query.\n")


if __name__ == "__main__":
    main()