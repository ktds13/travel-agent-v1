"""Main entry point for Data Ingestion Agent."""

import os
from dotenv import load_dotenv
from agents import create_data_agent

load_dotenv()
def main():
    """Run the Data Ingestion Agent REPL."""
    print("=" * 80)
    print("TRAVEL AGENT DATA INGESTION v2.0")
    print("=" * 80)
    print("Creating data ingestion agent...")
    
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    max_steps = int(os.getenv("DATA_AGENT_MAX_STEPS", "12"))
    agent = create_data_agent(deployment_name=deployment_name, max_steps=max_steps)
    
    print("Agent ready! Ask me anything about data ingestion.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            query = input("\nYou: ")
            
            if query.lower().strip() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not query.strip():
                continue
            response = agent.run(query)
            print(f"\nAgent: {response}\n")
            print()
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break


if __name__ == "__main__":
    main()