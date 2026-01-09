"""Database connection management."""

import pyodbc
from config.settings import DATABASE_CONFIG


def get_connection(database: str = None) -> pyodbc.Connection:
    """
    Create database connection.
    
    Args:
        database: Database name (defaults to master for admin operations)
        
    Returns:
        pyodbc Connection object
    """
    db = database or DATABASE_CONFIG.get("database", "master")
    
    conn_str = (
        f"DRIVER={{{DATABASE_CONFIG['driver']}}};"
        f"SERVER={DATABASE_CONFIG['server']};"
        f"DATABASE={db};"
        f"UID={DATABASE_CONFIG['username']};"
        f"PWD={DATABASE_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    
    return pyodbc.connect(conn_str, autocommit=True)