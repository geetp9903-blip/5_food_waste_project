import sqlite3
import pandas as pd

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "food_waste.db")

def run_query(query, params=()):
    """Helper function to execute an SQL query and return a Pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
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

# --- Query 9: Provider with Highest Successful Claims ---
def get_provider_highest_successful_claims():
    query = """
    SELECT p.Name as Provider_Name, 
           p.Type as Provider_Type,
           COUNT(c.Claim_ID) as Successful_Claims_Count
    FROM Claims c
    JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
    JOIN Providers p ON fl.Provider_ID = p.Provider_ID
    WHERE c.Status = 'Completed'
    GROUP BY p.Provider_ID, p.Name, p.Type
    ORDER BY Successful_Claims_Count DESC
    LIMIT 5;
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

# --- Query 11: Average Quantity Claimed per Receiver ---
def get_avg_claimed_quantity_per_receiver():
    query = """
    SELECT r.Name as Receiver_Name, 
           ROUND(AVG(fl.Quantity), 2) as Avg_Quantity_Claimed
    FROM Claims c
    JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
    JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
    GROUP BY r.Receiver_ID, r.Name
    ORDER BY Avg_Quantity_Claimed DESC;
    """
    return run_query(query)

# --- Query 12: Meal Type Demand ---
def get_meal_type_demand():
    query = """
    SELECT fl.Meal_Type, 
           COUNT(c.Claim_ID) as Claim_Count
    FROM Claims c
    JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
    GROUP BY fl.Meal_Type
    ORDER BY Claim_Count DESC;
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

# --- Query 14: Average Quantity Listed by Food Type ---
def get_avg_listed_quantity_by_food_type():
    query = """
    SELECT Food_Type, 
           ROUND(AVG(Quantity), 2) as Avg_Quantity_Listed
    FROM Food_Listings
    GROUP BY Food_Type
    ORDER BY Avg_Quantity_Listed DESC;
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
