import sqlite3

# Create Database Connection
connection = sqlite3.connect('BrokeAz.db')

# Initialize Python to Run SQL Queries
cursor = connection.cursor()

# Create our stock table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY, 
        symbol TEXT NOT NULL UNIQUE, 
        company TEXT NOT NULL
    )
""")

# Create our stock_price table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_price (
        id INTEGER PRIMARY KEY, 
        stock_id INTEGER,
        start NOT NULL,
        end NOT NULL,
        open NOT NULL, 
        high NOT NULL, 
        low NOT NULL, 
        close NOT NULL, 
        volume NOT NULL,
        vwap NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stock (id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS questrade_token (
        id INTEGER PRIMARY KEY,
        refresh_token STRING NOT NULL,
        access_token STRING NOT NULL,
        api_server STRING NOT NULL,
        token_type STRING NOT NULL
    )
""")

# Commit to save the changes
connection.commit()

