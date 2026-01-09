# Travel Agent AI System

An intelligent travel agent system powered by Azure OpenAI and Smolagents framework, featuring data ingestion, semantic search, and travel planning capabilities.

## Features

- **Data Ingestion Agent**: Extract and store structured travel place information
- **Travel Planning Agent**: Intelligent travel recommendations based on user preferences
- **Semantic Search**: Vector similarity search using LaBSE embeddings
- **Location Intelligence**: Automatic geocoding and location data enrichment
- **PostgreSQL Database**: Robust data storage with vector embeddings

## Project Structure

```
travel_agent/
├── agents/                 # Agent implementations
│   ├── data_agent.py      # Data ingestion agent
│   ├── travel_agent.py    # Travel planning agent
│   └── tools/             # Agent tools
│       ├── data_tools.py  # Data extraction and insertion tools
│       └── travel_tools.py # Travel search and planning tools
├── config/                # Configuration
│   ├── prompts.py        # Agent prompts
│   └── settings.py       # Application settings
├── core/                  # Core functionality
│   ├── embedding.py      # Text embedding service
│   ├── llm.py           # LLM interfaces
│   └── models.py        # Model configurations
├── database/             # Database layer
│   ├── connection.py    # Database connection
│   ├── operations.py    # CRUD operations
│   ├── queries.py       # Query builders
│   └── schema.py        # Database schema
├── utils/                # Utilities
│   ├── geo.py          # Geographic utilities
│   ├── intent.py       # Intent classification
│   └── rag.py          # RAG utilities
├── main_data.py         # Data ingestion CLI
└── main_travel.py       # Travel agent CLI

## Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- Azure OpenAI API access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ktds13/travel_agent.git
cd travel_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"

# Database
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="travel_db"
export DB_USER="your-username"
export DB_PASSWORD="your-password"
```

4. Initialize the database:
```bash
python -c "from database.schema import create_schema; create_schema()"
```

## Usage

### Data Ingestion

Run the data ingestion agent to add travel places:

```bash
python main_data.py
```

Example input:
```
The Merlion is the iconic national symbol of Singapore, featuring a mythical 
creature with the head of a lion and the body of a fish...
```

### Travel Planning

Run the travel planning agent for recommendations:

```bash
python main_travel.py
```

Example queries:
- "I want to visit beaches in Thailand"
- "Recommend historical sites in Europe"
- "What are the best activities in Singapore?"

## Architecture

### Components

- **Embedding Service**: Uses LaBSE model for multilingual text embeddings
- **Vector Search**: PostgreSQL pgvector for semantic similarity
- **Agent Framework**: Smolagents for tool-calling capabilities
- **LLM Integration**: Azure OpenAI GPT-4 models

### Database Schema

- **countries**: Country reference data
- **places**: Travel destinations with embeddings
- **activities**: Place activities
- **place_activities**: Many-to-many relationship

## Technologies

- **smolagents**: Agent framework with tool calling
- **sentence-transformers**: Text embedding models
- **psycopg2**: PostgreSQL adapter
- **Azure OpenAI**: LLM backend
- **OpenStreetMap Nominatim**: Geocoding service

## License

MIT License

## Author

ktds13
