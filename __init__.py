"""Travel Agent v2 - Clean, modular implementation using ToolCallingAgent."""

__version__ = "2.0.0"
__author__ = "Travel Agent Team"

from .agents import create_travel_agent, create_data_agent
from .database.schema import create_tables

__all__ = [
    'create_travel_agent',
    'create_data_agent',
    'create_tables',
]