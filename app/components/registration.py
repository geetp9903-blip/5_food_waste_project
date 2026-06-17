import streamlit as st
import pandas as pd
from app.utils.db_utils import execute_query, execute_dml
from app.utils.auth_utils import get_current_user

def render_registration_section():
    user = get_current_user()
    st.title("👥 Partner Registration & Directory")
    st.markdown("### *Join the network as a food provider or receiver, and browse our directory.*")
    
    tab1, tab2, tab3 = st.tabs(["📝 Register Provider", "📝 Register Receiver", "📖 Active Directories"])
    
    # ------------------ TAB 1: PROVIDER REGISTRATION ------------------
    with tab1:
        st.subheader("Register as a Food Provider")
        st.write("Are you a restaurant, grocery store, supermarket, or individual with surplus food? Register below to start donating.")
        
        with st.form("provider_reg_form", clear_on_submit=True):
            p_name = st.text_input("Name / Business Name *", placeholder="e.g. Green Valley Grocers")
            p_type = st.selectbox("Provider Type *", ["Restaurant", "Grocery Store", "Supermarket", "Bakery", "Individual", "Other"])
            p_address = st.text_input("Street Address *", placeholder="123 Sustainability Way")
            p_city = st.text_input("City *", placeholder="e.g. Seattle")
            p_contact = st.text_input("Contact Number / Email *", placeholder="+1-555-0199")
            
            submit_p = st.form_submit_button("Register Provider")
            
            if submit_p:
                if not (p_name and p_address and p_city and p_contact):
                    st.error("Please fill out all fields marked with an asterisk (*).")
                else:
                    try:
                        # Insert into Database
                        query = """
                        INSERT INTO Providers (Name, Type, Address, City, Contact, Created_By)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """
                        new_id = execute_dml(query, (p_name, p_type, p_address, p_city.strip(), p_contact, user['User_ID']))
                        st.success(f"🎉 Provider successfully registered! Assigned ID: {new_id}")
                    except Exception as e:
                        st.error(f"Error registering provider: {e}")

    # ------------------ TAB 2: RECEIVER REGISTRATION ------------------
    with tab2:
        st.subheader("Register as a Food Receiver")
        st.write("Are you an NGO, shelter, community kitchen, or individual in need? Register below to request food.")
        
        with st.form("receiver_reg_form", clear_on_submit=True):
            r_name = st.text_input("Name / Organization Name *", placeholder="e.g. City Shelter")
            r_type = st.selectbox("Receiver Type *", ["NGO", "Shelter", "Community Center", "Individual", "Other"])
            r_city = st.text_input("City *", placeholder="e.g. Seattle")
            r_contact = st.text_input("Contact Number / Email *", placeholder="+1-555-0245")
            
            submit_r = st.form_submit_button("Register Receiver")
            
            if submit_r:
                if not (r_name and r_city and r_contact):
                    st.error("Please fill out all fields marked with an asterisk (*).")
                else:
                    try:
                        # Insert into Database
                        query = """
                        INSERT INTO Receivers (Name, Type, City, Contact, Created_By)
                        VALUES (?, ?, ?, ?, ?);
                        """
                        new_id = execute_dml(query, (r_name, r_type, r_city.strip(), r_contact, user['User_ID']))
                        st.success(f"🎉 Receiver successfully registered! Assigned ID: {new_id}")
                    except Exception as e:
                        st.error(f"Error registering receiver: {e}")

    # ------------------ TAB 3: DIRECTORIES ------------------
    with tab3:
        st.subheader("Browse Active Partners")
        
        dir_choice = st.radio("Choose Directory to View:", ["Providers (Donors)", "Receivers (Claimants)"], horizontal=True)
        
        if dir_choice == "Providers (Donors)":
            st.markdown("#### Registered Food Providers")
            
            # Fetch providers
            providers = execute_query("SELECT Provider_ID, Name, Type, Address, City, Contact FROM Providers ORDER BY Name ASC;")
            
            # Filters
            p_search = st.text_input("Search Providers by Name or Address:", "")
            p_cities = ["All"] + sorted(providers['City'].unique().tolist()) if not providers.empty else ["All"]
            p_city_filter = st.selectbox("Filter by City:", p_cities)
            
            filtered_p = providers.copy()
            if p_search:
                filtered_p = filtered_p[filtered_p['Name'].str.contains(p_search, case=False, na=False) | 
                                        filtered_p['Address'].str.contains(p_search, case=False, na=False)]
            if p_city_filter != "All":
                filtered_p = filtered_p[filtered_p['City'] == p_city_filter]
                
            if not filtered_p.empty:
                st.dataframe(filtered_p, use_container_width=True, hide_index=True)
            else:
                st.info("No providers match your search criteria.")
                
        else:
            st.markdown("#### Registered Food Receivers")
            
            # Fetch receivers
            receivers = execute_query("SELECT Receiver_ID, Name, Type, City, Contact FROM Receivers ORDER BY Name ASC;")
            
            # Filters
            r_search = st.text_input("Search Receivers by Name:", "")
            r_cities = ["All"] + sorted(receivers['City'].unique().tolist()) if not receivers.empty else ["All"]
            r_city_filter = st.selectbox("Filter by City:", r_cities)
            
            filtered_r = receivers.copy()
            if r_search:
                filtered_r = filtered_r[filtered_r['Name'].str.contains(r_search, case=False, na=False)]
            if r_city_filter != "All":
                filtered_r = filtered_r[filtered_r['City'] == r_city_filter]
                
            if not filtered_r.empty:
                st.dataframe(filtered_r, use_container_width=True, hide_index=True)
            else:
                st.info("No receivers match your search criteria.")
