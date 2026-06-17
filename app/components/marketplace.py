import streamlit as st
import pandas as pd
from datetime import datetime
from app.utils.db_utils import execute_query, execute_dml
from app.utils.auth_utils import get_current_user

def render_marketplace_section():
    user = get_current_user()
    st.title("🍱 Food Marketplace")
    st.markdown("### *List surplus food and claim active listings.*")

    tab1, tab2 = st.tabs(["📤 List Surplus Food", "🤝 Claim Available Food"])

    # Fetch dynamic lists for selectboxes
    providers_df = execute_query("SELECT Provider_ID, Name, City, Type FROM Providers WHERE Created_By = ? ORDER BY Name ASC;", (user['User_ID'],))
    receivers_df = execute_query("SELECT Receiver_ID, Name, City FROM Receivers WHERE Created_By = ? ORDER BY Name ASC;", (user['User_ID'],))

    # Format options for select boxes
    provider_options = {}
    if not providers_df.empty:
        for _, row in providers_df.iterrows():
            label = f"{row['Name']} ({row['City']} - {row['Type']})"
            provider_options[label] = {
                'id': row['Provider_ID'],
                'city': row['City'],
                'type': row['Type']
            }
            
    receiver_options = {}
    if not receivers_df.empty:
        for _, row in receivers_df.iterrows():
            label = f"{row['Name']} ({row['City']})"
            receiver_options[label] = row['Receiver_ID']

    # ------------------ TAB 1: LIST SURPLUS FOOD (CREATE) ------------------
    with tab1:
        st.subheader("List New Surplus Food Item")
        
        if not provider_options:
            st.warning("⚠️ No providers registered yet. Please register a provider first in the 'Partner Registration' tab!")
        else:
            with st.form("list_food_form", clear_on_submit=True):
                selected_provider_label = st.selectbox("Select Listing Provider *", list(provider_options.keys()))
                food_name = st.text_input("Food Name *", placeholder="e.g. Assorted Pastries, Lentil Soup")
                quantity = st.number_input("Quantity (Units) *", min_value=1, value=10, step=1)
                expiry_date = st.date_input("Expiry Date *", min_value=datetime.today())
                food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan", "Halal", "Gluten-Free"])
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
                
                submit_food = st.form_submit_button("Publish Surplus Food Listing")
                
                if submit_food:
                    if not food_name:
                        st.error("Please enter a food name.")
                    else:
                        provider_info = provider_options[selected_provider_label]
                        try:
                            query = """
                            INSERT INTO Food_Listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type, Created_By)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """
                            formatted_expiry = expiry_date.strftime('%Y-%m-%d')
                            new_id = execute_dml(query, (
                                food_name, 
                                quantity, 
                                formatted_expiry, 
                                provider_info['id'], 
                                provider_info['type'], 
                                provider_info['city'], 
                                food_type, 
                                meal_type,
                                user['User_ID']
                            ))
                            st.success(f"🎉 Food Listing added successfully! Listing ID: {new_id}")
                        except Exception as e:
                            st.error(f"Error publishing listing: {e}")

    # ------------------ TAB 2: CLAIM FOOD (TRANSACTION / CREATE CLAIMS) ------------------
    with tab2:
        st.subheader("Claim Available Food Listings")
        st.write("Browse current donations and log a claim request.")
        
        # Pull available listings (Unclaimed or whose claim isn't 'Completed')
        available_query = """
        SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Location as City, 
               fl.Food_Type, fl.Meal_Type, p.Name as Provider_Name, p.Contact as Provider_Contact
        FROM Food_Listings fl
        JOIN Providers p ON fl.Provider_ID = p.Provider_ID
        WHERE fl.Food_ID NOT IN (SELECT Food_ID FROM Claims WHERE Status = 'Completed')
          AND fl.Quantity > 0
        ORDER BY fl.Expiry_Date ASC;
        """
        listings = execute_query(available_query)
        
        # Filter filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            cities = ["All"] + sorted(listings['City'].unique().tolist()) if not listings.empty else ["All"]
            filter_city = st.selectbox("Filter City:", cities)
        with col_f2:
            food_types = ["All"] + sorted(listings['Food_Type'].unique().tolist()) if not listings.empty else ["All"]
            filter_ft = st.selectbox("Filter Food Type:", food_types)
        with col_f3:
            meal_types = ["All"] + sorted(listings['Meal_Type'].unique().tolist()) if not listings.empty else ["All"]
            filter_mt = st.selectbox("Filter Meal Type:", meal_types)
            
        # Apply filters
        filtered_listings = listings.copy()
        if not listings.empty:
            if filter_city != "All":
                filtered_listings = filtered_listings[filtered_listings['City'] == filter_city]
            if filter_ft != "All":
                filtered_listings = filtered_listings[filtered_listings['Food_Type'] == filter_ft]
            if filter_mt != "All":
                filtered_listings = filtered_listings[filtered_listings['Meal_Type'] == filter_mt]

        # Display listings
        if not filtered_listings.empty:
            st.dataframe(filtered_listings, use_container_width=True, hide_index=True)
            
            # Claim interface
            st.markdown("#### Log a Claim Request")
            
            if not receiver_options:
                st.warning("⚠️ No receivers registered yet. Please register a receiver first in the 'Partner Registration' tab!")
            else:
                # Build drop down of available listings based on filtered results
                food_choices = {}
                for _, row in filtered_listings.iterrows():
                    label = f"ID: {row['Food_ID']} | {row['Food_Name']} ({row['Quantity']} units, exp: {row['Expiry_Date']})"
                    food_choices[label] = { 'id': row['Food_ID'], 'qty': row['Quantity'] }
                    
                with st.form("claim_food_form"):
                    selected_food_label = st.selectbox("Choose Food Item to Claim:", list(food_choices.keys()))
                    selected_receiver_label = st.selectbox("Select Requesting Receiver:", list(receiver_options.keys()))
                    claim_qty = st.number_input("Quantity to Claim", min_value=1, value=1, step=1)
                    
                    claim_btn = st.form_submit_button("Request Claim")
                    
                    if claim_btn:
                        food_id = food_choices[selected_food_label]['id']
                        max_qty = food_choices[selected_food_label]['qty']
                        receiver_id = receiver_options[selected_receiver_label]
                        timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Check for duplicates
                        existing_claim = execute_query(
                            "SELECT 1 FROM Claims WHERE Food_ID = ? AND Receiver_ID = ? AND Status = 'Pending';", 
                            (food_id, receiver_id)
                        )
                        
                        if not existing_claim.empty:
                            st.error("⚠️ You already have a pending claim for this food item from this receiver. Please wait for the provider to respond.")
                        elif claim_qty > max_qty:
                            st.error(f"⚠️ Cannot claim more than available quantity ({max_qty}).")
                        else:
                            try:
                                # Insert claim with 'Pending' status
                                claim_query = """
                                INSERT INTO Claims (Food_ID, Receiver_ID, Status, Timestamp, Claim_Quantity, Created_By)
                                VALUES (?, ?, 'Pending', ?, ?, ?);
                                """
                                new_claim_id = execute_dml(claim_query, (food_id, receiver_id, timestamp_str, claim_qty, user['User_ID']))
                                st.success(f"🎉 Claim successfully requested! Claim ID: {new_claim_id}. Status: Pending.")
                            except Exception as e:
                                st.error(f"Error submitting claim: {e}")
        else:
            st.info("No surplus food items are currently available for claiming.")


