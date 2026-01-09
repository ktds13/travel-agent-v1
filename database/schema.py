"""Database schema definitions and table creation."""

from .connection import get_connection


def create_tables():
    """Create all database tables if they don't exist."""
    conn = get_connection("master")
    cursor = conn.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'TravelAgentDB')
        BEGIN
            CREATE DATABASE TravelAgentDB;
        END
    """)
    
    conn.close()
    
    # Connect to TravelAgentDB
    conn = get_connection("TravelAgentDB")
    cursor = conn.cursor()
    
    # Create Countries table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Countries')
        BEGIN
            CREATE TABLE Countries (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            );
        END
    """)
    
    # Create CountryAliases table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CountryAliases')
        BEGIN
            CREATE TABLE CountryAliases (
                id INT IDENTITY(1,1) PRIMARY KEY,
                country_id INT NOT NULL,
                alias NVARCHAR(100) NOT NULL UNIQUE,
                FOREIGN KEY (country_id) REFERENCES Countries(id)
            );
        END
    """)
    
    # Create Regions table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Regions')
        BEGIN
            CREATE TABLE Regions (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(100) NOT NULL,
                country_id INT,
                FOREIGN KEY (country_id) REFERENCES Countries(id)
            );
        END
    """)
    
    # Create Activities table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Activities')
        BEGIN
            CREATE TABLE Activities (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            );
        END
    """)
    
    # Create Places table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Places')
        BEGIN
            CREATE TABLE Places (
                id INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(200) NOT NULL,
                category NVARCHAR(100),
                country INT,
                region NVARCHAR(200),
                latitude FLOAT,
                longitude FLOAT,
                activities NVARCHAR(MAX),
                raw_text NVARCHAR(MAX),
                embedding VARBINARY(MAX),
                FOREIGN KEY (country) REFERENCES Countries(id)
            );
        END
    """)
    
    # Create PlaceActivities junction table
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PlaceActivities')
        BEGIN
            CREATE TABLE PlaceActivities (
                id INT IDENTITY(1,1) PRIMARY KEY,
                place_id INT NOT NULL,
                activity_id INT NOT NULL,
                FOREIGN KEY (place_id) REFERENCES Places(id),
                FOREIGN KEY (activity_id) REFERENCES Activities(id)
            );
        END
    """)
    
    conn.commit()
    conn.close()
    
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()