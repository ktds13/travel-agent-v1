"""Model factory for creating Azure OpenAI models."""

from smolagents import AzureOpenAIServerModel
from config.settings import get_azure_model_config


def get_azure_model(deployment_name: str = None) -> AzureOpenAIServerModel:
    """
    Create Azure OpenAI model instance.
    
    Args:
        deployment_name: Name of the deployment (defaults to env var)
        
    Returns:
        Configured AzureOpenAIServerModel instance
    """
    config = get_azure_model_config(deployment_name)
    
    return AzureOpenAIServerModel(
        model_id=config["model_id"],
        azure_endpoint=config["azure_endpoint"],
        api_key=config["api_key"],
        api_version=config["api_version"]
    )