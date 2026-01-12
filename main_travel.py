"""Main entry point for Travel Agent REPL."""

import os
from dotenv import load_dotenv
from agents.orchestrator import route_to_specialist

load_dotenv()

def main():
    """Run the Travel Agent interactive REPL."""
    print("=" * 80)
    print("TRAVEL AGENT v3.0 - Orchestrated Specialist Agents")
    print("=" * 80)
    print("Main agent routes your query to specialized agents:")
    print("  • Itinerary Agent - Day-by-day travel planning")
    print("  • Places Agent - Destination suggestions & descriptions")
    print("  • Accommodation Agent - Hotels, hostels, resorts")
    print("  • Activity Agent - Trip planning around activities")
    print("  • Comparison Agent - Compare destinations side-by-side")
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
            
            print("\nRouting to specialist agent...")
            
            # Use orchestrator to route to appropriate specialist
            response, mode_used = route_to_specialist(query, deployment_name)
            
            print(f"\n[Handled by: {mode_used} agent]")
            print("\nTravel Agent:")
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again with a different query.\n")


if __name__ == "__main__":
    main()