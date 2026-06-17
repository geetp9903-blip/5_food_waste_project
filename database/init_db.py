import os
import sqlite3
import pandas as pd

# Paths
DATA_DIR = "/Users/ferrarifanboy/Desktop/Labmentix_Internship/5_food_waste_project/data"
DB_PATH = "/Users/ferrarifanboy/Desktop/Labmentix_Internship/5_food_waste_project/database/food_waste.db"

def init_database():
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Drop existing tables if they exist to start fresh
    cursor.execute("DROP TABLE IF EXISTS Claims;")
    cursor.execute("DROP TABLE IF EXISTS Food_Listings;")
    cursor.execute("DROP TABLE IF EXISTS Providers;")
    cursor.execute("DROP TABLE IF EXISTS Receivers;")
    cursor.execute("DROP TABLE IF EXISTS Users;")

    # Create tables with constraints
    print("Creating tables...")
    cursor.execute("""
    CREATE TABLE Users (
        User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT NOT NULL UNIQUE,
        Password_Hash TEXT NOT NULL,
        Display_Name TEXT NOT NULL,
        Created_At TEXT DEFAULT (datetime('now'))
    );
    """)
    cursor.execute("""
    CREATE TABLE Providers (
        Provider_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT,
        Address TEXT,
        City TEXT,
        Contact TEXT,
        Created_By INTEGER REFERENCES Users(User_ID)
    );
    """)

    cursor.execute("""
    CREATE TABLE Receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT,
        City TEXT,
        Contact TEXT,
        Created_By INTEGER REFERENCES Users(User_ID)
    );
    """)

    cursor.execute("""
    CREATE TABLE Food_Listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT NOT NULL,
        Quantity INTEGER NOT NULL CHECK (Quantity >= 0),
        Expiry_Date TEXT,
        Provider_ID INTEGER,
        Provider_Type TEXT,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT,
        Created_By INTEGER REFERENCES Users(User_ID),
        FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE Claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT DEFAULT 'Pending',
        Timestamp TEXT,
        Claim_Quantity INTEGER DEFAULT 1,
        Created_By INTEGER REFERENCES Users(User_ID),
        FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID) ON DELETE CASCADE,
        FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID) ON DELETE CASCADE
    );
    """)

    conn.commit()
    print("Tables created successfully.")

    # Load and clean CSVs
    print("Loading datasets...")
    providers_df = pd.read_csv(os.path.join(DATA_DIR, "providers_data.csv"))
    receivers_df = pd.read_csv(os.path.join(DATA_DIR, "receivers_data.csv"))
    food_listings_df = pd.read_csv(os.path.join(DATA_DIR, "food_listings_data.csv"))
    claims_df = pd.read_csv(os.path.join(DATA_DIR, "claims_data.csv"))

    # Clean date columns
    # Expiry_Date formatting to standard YYYY-MM-DD
    food_listings_df['Expiry_Date'] = pd.to_datetime(food_listings_df['Expiry_Date'], errors='coerce')
    food_listings_df['Expiry_Date'] = food_listings_df['Expiry_Date'].dt.strftime('%Y-%m-%d')

    # Clean food types to correct messy CSV data
    canonical_types = {
        'Bread': 'Vegetarian',
        'Soup': 'Vegetarian',
        'Fruits': 'Vegan',
        'Vegetables': 'Vegan',
        'Dairy': 'Vegetarian',
        'Rice': 'Vegan',
        'Pasta': 'Vegetarian',
        'Salad': 'Vegan',
        'Chicken': 'Non-Vegetarian',
        'Fish': 'Non-Vegetarian'
    }
    food_listings_df['Food_Type'] = food_listings_df['Food_Name'].map(canonical_types).fillna(food_listings_df['Food_Type'])

    # Timestamp formatting to YYYY-MM-DD HH:MM:SS
    claims_df['Timestamp'] = pd.to_datetime(claims_df['Timestamp'], errors='coerce')
    claims_df['Timestamp'] = claims_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Insert data into tables using pandas to_sql
    print("Ingesting data into SQL database...")
    providers_df.to_sql("Providers", conn, if_exists="append", index=False)
    receivers_df.to_sql("Receivers", conn, if_exists="append", index=False)
    food_listings_df.to_sql("Food_Listings", conn, if_exists="append", index=False)
    claims_df.to_sql("Claims", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print("Database initialization complete! Saved to:", DB_PATH)

def migrate_database():
    """Migrates an existing database to add Users table and Created_By columns."""
    print("Migrating database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT NOT NULL UNIQUE,
        Password_Hash TEXT NOT NULL,
        Display_Name TEXT NOT NULL,
        Created_At TEXT DEFAULT (datetime('now'))
    );
    """)

    # Function to safely add column
    def add_column_if_not_exists(table, column, definition):
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [info[1] for info in cursor.fetchall()]
        if column not in columns:
            print(f"Adding {column} to {table}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition};")
        else:
            print(f"Column {column} already exists in {table}.")

    # Add Created_By to existing tables
    add_column_if_not_exists("Providers", "Created_By", "INTEGER REFERENCES Users(User_ID)")
    add_column_if_not_exists("Receivers", "Created_By", "INTEGER REFERENCES Users(User_ID)")
    add_column_if_not_exists("Food_Listings", "Created_By", "INTEGER REFERENCES Users(User_ID)")
    add_column_if_not_exists("Claims", "Created_By", "INTEGER REFERENCES Users(User_ID)")
    add_column_if_not_exists("Claims", "Claim_Quantity", "INTEGER DEFAULT 1")

    # Clean up existing data types
    print("Cleaning up messy food types in active database...")
    canonical_types = {
        'Bread': 'Vegetarian',
        'Soup': 'Vegetarian',
        'Fruits': 'Vegan',
        'Vegetables': 'Vegan',
        'Dairy': 'Vegetarian',
        'Rice': 'Vegan',
        'Pasta': 'Vegetarian',
        'Salad': 'Vegan',
        'Chicken': 'Non-Vegetarian',
        'Fish': 'Non-Vegetarian'
    }
    for name, ftype in canonical_types.items():
        cursor.execute("UPDATE Food_Listings SET Food_Type = ? WHERE Food_Name = ?;", (ftype, name))

    conn.commit()
    conn.close()
    print("Database migration complete!")

if __name__ == "__main__":
    migrate_database()
