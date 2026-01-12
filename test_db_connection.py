"""Test SQL Server connection"""
import pyodbc

# Test connection
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=ADMIN\\MSSQLSERVER03;"
    "DATABASE=TravelAgentDB;"
    "UID=sa;"
    "PWD=admin;"
    "TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str, autocommit=True)
    print("✓ Connected to SQL Server successfully!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()
    print(f"✓ SQL Server Version: {version[0][:80]}...")
    
    cursor.execute("SELECT DB_NAME()")
    db = cursor.fetchone()
    print(f"✓ Current Database: {db[0]}")
    
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    tables = cursor.fetchall()
    print(f"\n✓ Tables in database ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    print("\n✓ Connection test completed!")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
