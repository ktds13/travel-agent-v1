"""Main entry point for Travel Agent REPL."""

import os
from dotenv import load_dotenv
from agents import create_travel_agent
load_dotenv()

def main():
    """Run the Travel Agent interactive REPL."""
    print("=" * 80)
    print("TRAVEL AGENT v2.0")
    print("=" * 80)
    print("Creating travel planning agent...")
    
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    max_steps = int(os.getenv("TRAVEL_AGENT_MAX_STEPS", "12"))
    agent = create_travel_agent(deployment_name=deployment_name, max_steps=max_steps)
    
    print("Agent ready! Ask me anything about travel planning.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            query = input("\nYou: ")
            
            if query.lower().strip() in ['exit', 'quit', 'q']:
                print("Thank you for using Travel Agent. Goodbye!")
                break
            
            if not query.strip():
                continue
            
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