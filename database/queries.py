import sqlite3
import pandas as pd

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "food_waste.db")
DB_STATIC_PATH = os.path.join(BASE_DIR, "database", "food_waste_static.db")

def get_current_db_path():
    """Helper to dynamically resolve which database path to connect to."""
    try:
        import streamlit as st
        # If the user explicitly sets to Live App Data, query DB_PATH.
        # Otherwise, default to DB_STATIC_PATH for consistent raw visualizations.
        source = st.session_state.get("analytics_data_source")
        if source == "Live App Data (Active)":
            return DB_PATH
    except Exception:
        pass
    return DB_STATIC_PATH

def run_query(query, params=()):
    """Helper function to execute an SQL query and return a Pandas DataFrame."""
    db_file = get_current_db_path()
    conn = sqlite3.connect(db_file)
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

# --- Helper Query for Top Metrics ---
def get_providers_receivers_by_city():
    query = """
    SELECT City, 
           SUM(Is_Provider) as Provider_Count, 
           SUM(Is_Receiver) as Receiver_Count
    FROM (
        SELECT City, 1 as Is_Provider, 0 as Is_Receiver FROM Providers
        UNION ALL
        SELECT City, 0 as Is_Provider, 1 as Is_Receiver FROM Receivers
    )
    GROUP BY City;
    """
    return run_query(query)

# --- Query 1: Temporal Trends of Food Claims ---
def get_claims_temporal_trend():
    query = """
    SELECT DATE(Timestamp) as Claim_Date, COUNT(Claim_ID) as Total_Claims
    FROM Claims
    WHERE Timestamp IS NOT NULL AND Timestamp != ''
    GROUP BY DATE(Timestamp)
    ORDER BY Claim_Date DESC;
    """
    return run_query(query)

# --- Query 2: Contributions by Provider Type ---
def get_contributions_by_provider_type():
    query = """
    SELECT p.Type as Provider_Type, 
           COUNT(fl.Food_ID) as Total_Listings,
           SUM(fl.Quantity) as Total_Quantity_Contributed
    FROM Food_Listings fl
    JOIN Providers p ON fl.Provider_ID = p.Provider_ID
    GROUP BY p.Type
    ORDER BY Total_Quantity_Contributed DESC;
    """
    return run_query(query)

# --- Query 3: Providers Contact Info by City (Parameterized) ---
def get_providers_contact_by_city(city):
    query = """
    SELECT Name, Type, Address, City, Contact
    FROM Providers
    WHERE City = ?
    ORDER BY Name ASC;
    """
    return run_query(query, (city,))

# --- Query 4: Top Claiming Receivers ---
def get_top_claiming_receivers():
    query = """
    SELECT r.Name as Receiver_Name, 
           r.Type as Receiver_Type, 
           COUNT(c.Claim_ID) as Total_Claims,
           SUM(fl.Quantity) as Total_Quantity_Claimed
    FROM Claims c
    JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
    GROUP BY r.Receiver_ID, r.Name, r.Type
    ORDER BY Total_Quantity_Claimed DESC;
    """
    return run_query(query)

# --- Query 5: Total Food Quantity Available (Overall vs Unclaimed) ---
def get_food_availability_summary():
    query = """
    SELECT 
        (SELECT SUM(Quantity) FROM Food_Listings) as Total_Quantity_Listed,
        (SELECT SUM(fl.Quantity) FROM Food_Listings fl 
         WHERE fl.Food_ID NOT IN (SELECT Food_ID FROM Claims WHERE Status = 'Completed')) as Currently_Unclaimed_Quantity;
    """
    return run_query(query)

# --- Query 6: Cities with the Highest Food Listings ---
def get_cities_by_listings():
    query = """
    SELECT Location as City, 
           COUNT(*) as Listing_Count, 
           SUM(Quantity) as Total_Quantity
    FROM Food_Listings
    GROUP BY Location
    ORDER BY Total_Quantity DESC;
    """
    return run_query(query)

# --- Query 7: Most Commonly Available Food Types ---
def get_common_food_types():
    query = """
    SELECT Food_Type, 
           COUNT(*) as Listing_Count, 
           SUM(Quantity) as Total_Quantity
    FROM Food_Listings
    GROUP BY Food_Type
    ORDER BY Listing_Count DESC;
    """
    return run_query(query)

# --- Query 8: Claims per Food Item ---
def get_claims_per_food_item():
    query = """
    SELECT fl.Food_Name, 
           fl.Food_Type,
           COUNT(c.Claim_ID) as Claim_Count
    FROM Food_Listings fl
    LEFT JOIN Claims c ON fl.Food_ID = c.Food_ID
    GROUP BY fl.Food_ID, fl.Food_Name, fl.Food_Type
    ORDER BY Claim_Count DESC;
    """
    return run_query(query)

# --- Query 9: Top Diverse Providers by Food Type ---
def get_top_diverse_providers_by_food_type():
    query = """
    SELECT p.Name as Provider_Name, 
           p.Type as Provider_Type,
           COUNT(DISTINCT fl.Food_Type) as Distinct_Food_Types
    FROM Food_Listings fl
    JOIN Providers p ON fl.Provider_ID = p.Provider_ID
    GROUP BY p.Provider_ID, p.Name, p.Type
    ORDER BY Distinct_Food_Types DESC;
    """
    return run_query(query)

# --- Query 10: Claim Status Percentage ---
def get_claim_status_percentage():
    query = """
    SELECT Status, 
           COUNT(*) as Count, 
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims), 2) as Percentage
    FROM Claims
    GROUP BY Status;
    """
    return run_query(query)

# --- Query 11: Receiver Claim Volume Distribution ---
def get_receiver_claim_volume_distribution():
    query = """
    SELECT 
        CASE 
            WHEN Total_Qty BETWEEN 0 AND 25 THEN '0-25'
            WHEN Total_Qty BETWEEN 26 AND 50 THEN '26-50'
            WHEN Total_Qty BETWEEN 51 AND 75 THEN '51-75'
            WHEN Total_Qty BETWEEN 76 AND 100 THEN '76-100'
            WHEN Total_Qty BETWEEN 101 AND 125 THEN '101-125'
            WHEN Total_Qty BETWEEN 126 AND 150 THEN '126-150'
            WHEN Total_Qty BETWEEN 151 AND 175 THEN '151-175'
            WHEN Total_Qty BETWEEN 176 AND 200 THEN '176-200'
        END as Volume_Bracket,
        COUNT(*) as Receiver_Count
    FROM (
        SELECT r.Receiver_ID, SUM(fl.Quantity) as Total_Qty
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
        GROUP BY r.Receiver_ID
    )
    GROUP BY Volume_Bracket
    ORDER BY MIN(Total_Qty) ASC;
    """
    return run_query(query)

# --- Query 12: City-wise Claim Completion Rate ---
def get_city_claim_completion_rate():
    query = """
    SELECT fl.Location as City,
           COUNT(c.Claim_ID) as Total_Claims,
           SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) as Completed_Claims,
           ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(c.Claim_ID), 1) as Completion_Rate
    FROM Claims c
    JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
    GROUP BY fl.Location
    HAVING COUNT(c.Claim_ID) >= 5
    ORDER BY Completion_Rate DESC;
    """
    return run_query(query)

# --- Query 13: Total Donated Food per Provider ---
def get_total_donated_by_provider():
    query = """
    SELECT p.Name as Provider_Name, 
           p.Type as Provider_Type,
           SUM(fl.Quantity) as Total_Quantity_Donated
    FROM Food_Listings fl
    JOIN Providers p ON fl.Provider_ID = p.Provider_ID
    GROUP BY p.Provider_ID, p.Name, p.Type
    ORDER BY Total_Quantity_Donated DESC;
    """
    return run_query(query)

# --- Query 14: Provider Type Efficiency (Claims vs Listings) ---
def get_provider_type_efficiency():
    query = """
    SELECT p.Type as Provider_Type,
           COUNT(DISTINCT fl.Food_ID) as Total_Listings,
           COUNT(DISTINCT c.Claim_ID) as Total_Claims,
           ROUND(COUNT(DISTINCT c.Claim_ID) * 100.0 / COUNT(DISTINCT fl.Food_ID), 1) as Claim_Rate_Pct
    FROM Food_Listings fl
    JOIN Providers p ON fl.Provider_ID = p.Provider_ID
    LEFT JOIN Claims c ON fl.Food_ID = c.Food_ID
    GROUP BY p.Type
    ORDER BY Claim_Rate_Pct DESC;
    """
    return run_query(query)

# --- Query 15: Food Listings Closest to Expiry ---
def get_listings_closest_to_expiry():
    query = """
    SELECT Food_Name, 
           Expiry_Date, 
           Quantity, 
           Location as City,
           Provider_Type
    FROM Food_Listings
    WHERE Expiry_Date IS NOT NULL AND Expiry_Date != ''
    ORDER BY Expiry_Date ASC
    LIMIT 10;
    """
    return run_query(query)

# --- Helper Query for Understand/Education Page Impact Metrics ---
def get_platform_impact_metrics():
    query = """
    SELECT 
        (SELECT COALESCE(SUM(fl.Quantity), 0) 
         FROM Claims c 
         JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID 
         WHERE c.Status = 'Completed') as Total_Food_Saved,
         
        (SELECT COUNT(*) FROM Providers) + (SELECT COUNT(*) FROM Receivers) as Active_Partners,
        
        (SELECT COALESCE(SUM(Quantity), 0) 
         FROM Food_Listings 
         WHERE Food_ID NOT IN (SELECT Food_ID FROM Claims WHERE Status = 'Completed')) as Active_Listings_Quantity,
         
        (SELECT COUNT(*) FROM Claims WHERE Status = 'Completed') as Successful_Claims;
    """
    return run_query(query)
