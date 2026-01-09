import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration

DATABASE_CONFIG = {
    "server": os.getenv("DB_SERVER", "ADMIN\\MSSQLSERVER03"),
    "username": os.getenv("DB_USERNAME", "sa"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
    "database": os.getenv("DB_DATABASE", "TravelAgentDB")
}

# Azure OpenAI Model Configurations
MODEL_CONFIGS = {
    "gpt-4.1-mini": {
        "endpoint": "EASTUS",
        "key": "EASTUS",
        "api_version": "2024-10-01-preview"
    },
    "gpt-5-mini": {
        "endpoint": "EASTUS", 
        "key": "EASTUS",
        "api_version": "2024-10-01-preview"
    },
    "DeepSeek-V3.1": {
        "endpoint": "EASTUS",
        "key": "EASTUS",
        "api_version": "2024-10-01-preview"
    },
    "gpt-4.1-nano": {
        "endpoint": "SWEDENCENTRAL",
        "key": "SWEDENCENTRAL",
        "api_version": "2024-12-01-preview"
    },
    "gpt-4o-mini-tts-2": {
        "endpoint": "EASTUS2",
        "key": "EASTUS2",
        "api_version": "2024-10-01-preview"
    },
}

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Embedding Configuration
EMBEDDING_MODEL = "sentence-transformers/LaBSE"
EMBEDDING_DIMENSION = 768

# Canonical Categories for Travel Places
CANONICAL_CATEGORIES = [
    "beach", "temple", "mountain", "city", "village",
    "historical site", "natural park", "waterfall",
    "cultural site", "adventure", "relaxation"
]


def get_azure_model_config(deployment_name: str = None) -> dict:
    """
    Get Azure OpenAI model configuration.
    
    Args:
        deployment_name: Name of the deployment (defaults to env var)
        
    Returns:
        dict with endpoint, api_key, api_version, and model_id
    """
    deployment = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
    
    if deployment not in MODEL_CONFIGS:
        raise ValueError(f"Unknown deployment: {deployment}. Available: {list(MODEL_CONFIGS.keys())}")
    
    config = MODEL_CONFIGS[deployment]
    
    return {
        "model_id": deployment,
        "azure_endpoint": os.getenv(f"AZURE_OPENAI_ENDPOINT_{config['endpoint']}"),
        "api_key": os.getenv(f"AZURE_OPENAI_API_KEY_{config['key']}"),
        "api_version": config["api_version"]
    }