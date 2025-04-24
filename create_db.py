import sqlite3
import os
import codecs
import re

def create_database():
    """Create SQLite database and populate it with address data"""
    # Define database file path
    db_path = os.path.join(os.path.dirname(__file__), 'addresses.db')
    
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table with proper Unicode support
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT COLLATE NOCASE,
        street TEXT COLLATE NOCASE,
        latitude REAL,
        longitude REAL
    )
    ''')
    
    # Read the data file
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'Koordinaten.txt')
    
    # Process each line
    with codecs.open(data_path, 'r', encoding='iso-8859-1') as file:
        for line in file:
            # Extract data using regex to handle the tuple-like format
            match = re.match(r"\('([^']+)', ([0-9.]+), ([0-9.]+)\)", line.strip())
            if match:
                address = match.group(1)
                latitude = float(match.group(2))
                longitude = float(match.group(3))
                
                # Extract street name (everything before the house number)
                street_match = re.match(r"(.+?)\s+\d+", address)
                street = street_match.group(1) if street_match else address
                
                # Insert data into database
                cursor.execute(
                    "INSERT INTO addresses (address, street, latitude, longitude) VALUES (?, ?, ?, ?)",
                    (address, street, latitude, longitude)
                )
    
    # Create indexes for better search performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_address ON addresses (address)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_street ON addresses (street)")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database created at {db_path}")

if __name__ == "__main__":
    create_database()