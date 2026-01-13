"""Main entry point for Travel Agent REPL."""

import os
from dotenv import load_dotenv
from agents.orchestrator import route_multi_intent

load_dotenv()

def main():
    """Run the Travel Agent interactive REPL."""
    print("=" * 80)
    print("TRAVEL AGENT v3.1 - Multi-Agent Orchestrator")
    print("=" * 80)
    print("Intelligent routing to specialized agents:")
    print("  • Itinerary Agent - Day-by-day travel planning")
    print("  • Places Agent - Destination suggestions & descriptions")
    print("  • Accommodation Agent - Hotels, hostels, resorts")
    print("  • Activity Agent - Trip planning around activities")
    print("  • Comparison Agent - Compare destinations side-by-side")
    print("  • Multi-Agent Orchestrator - Complex multi-intent queries")
    print("\nExamples:")
    print("  - 'plan 3-day trip to Chiang Mai'")
    print("  - 'find hotel near Doi Suthep and describe the temple' (multi-intent)")
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
            
            print("\nAnalyzing query and routing to specialist(s)...")
            
            # Use multi-intent routing (auto-detects single vs multi-intent)
            response, mode_used = route_multi_intent(query, deployment_name)
            
            print(f"\n[Handled by: {mode_used}]")
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