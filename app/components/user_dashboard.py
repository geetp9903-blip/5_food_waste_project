import streamlit as st
import pandas as pd
from app.utils.db_utils import execute_query, execute_dml, execute_dml_returning_rowcount
from app.utils.auth_utils import get_current_user

def render_user_dashboard():
    user = get_current_user()
    user_id = user['User_ID']
    
    st.title("📋 My Dashboard")
    st.markdown("### *Manage your registrations, food listings, and claims.*")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏭 My Providers", "🏢 My Receivers", "🍱 My Food Listings", "🤝 My Claims", "📥 Incoming Claims"])
    
    # ------------------ TAB 1: MY PROVIDERS ------------------
    with tab1:
        st.subheader("My Registered Providers")
        providers = execute_query("SELECT Provider_ID, Name, Type, Address, City, Contact FROM Providers WHERE Created_By = ? ORDER BY Name ASC;", (user_id,))
        
        if providers.empty:
            st.info("You haven't registered any providers yet.")
        else:
            for _, row in providers.iterrows():
                with st.expander(f"Provider: {row['Name']} ({row['City']})"):
                    col_edit, col_del = st.columns(2)
                    
                    with col_edit:
                        st.markdown("**Edit Provider**")
                        with st.form(f"edit_prov_{row['Provider_ID']}"):
                            p_name = st.text_input("Name", value=row['Name'])
                            p_type = st.selectbox("Type", ["Restaurant", "Grocery Store", "Supermarket", "Bakery", "Individual", "Other"], index=["Restaurant", "Grocery Store", "Supermarket", "Bakery", "Individual", "Other"].index(row['Type']) if row['Type'] in ["Restaurant", "Grocery Store", "Supermarket", "Bakery", "Individual", "Other"] else 5)
                            p_address = st.text_input("Address", value=row['Address'])
                            p_city = st.text_input("City", value=row['City'])
                            p_contact = st.text_input("Contact", value=row['Contact'])
                            
                            if st.form_submit_button("Update Provider"):
                                try:
                                    execute_dml(
                                        "UPDATE Providers SET Name=?, Type=?, Address=?, City=?, Contact=? WHERE Provider_ID=? AND Created_By=?",
                                        (p_name, p_type, p_address, p_city, p_contact, row['Provider_ID'], user_id)
                                    )
                                    st.success("Provider updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating provider: {e}")
                    
                    with col_del:
                        st.markdown("**Delete Provider**")
                        st.warning("⚠️ Deleting this provider will also delete all associated food listings and claims.")
                        if st.button(f"Delete Provider {row['Provider_ID']}", key=f"del_prov_{row['Provider_ID']}", type="primary"):
                            try:
                                execute_dml("DELETE FROM Providers WHERE Provider_ID=? AND Created_By=?", (row['Provider_ID'], user_id))
                                st.success("Provider deleted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting provider: {e}")

    # ------------------ TAB 2: MY RECEIVERS ------------------
    with tab2:
        st.subheader("My Registered Receivers")
        receivers = execute_query("SELECT Receiver_ID, Name, Type, City, Contact FROM Receivers WHERE Created_By = ? ORDER BY Name ASC;", (user_id,))
        
        if receivers.empty:
            st.info("You haven't registered any receivers yet.")
        else:
            for _, row in receivers.iterrows():
                with st.expander(f"Receiver: {row['Name']} ({row['City']})"):
                    col_edit, col_del = st.columns(2)
                    
                    with col_edit:
                        st.markdown("**Edit Receiver**")
                        with st.form(f"edit_rec_{row['Receiver_ID']}"):
                            r_name = st.text_input("Name", value=row['Name'])
                            r_type = st.selectbox("Type", ["NGO", "Shelter", "Community Center", "Individual", "Other"], index=["NGO", "Shelter", "Community Center", "Individual", "Other"].index(row['Type']) if row['Type'] in ["NGO", "Shelter", "Community Center", "Individual", "Other"] else 4)
                            r_city = st.text_input("City", value=row['City'])
                            r_contact = st.text_input("Contact", value=row['Contact'])
                            
                            if st.form_submit_button("Update Receiver"):
                                try:
                                    execute_dml(
                                        "UPDATE Receivers SET Name=?, Type=?, City=?, Contact=? WHERE Receiver_ID=? AND Created_By=?",
                                        (r_name, r_type, r_city, r_contact, row['Receiver_ID'], user_id)
                                    )
                                    st.success("Receiver updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating receiver: {e}")
                    
                    with col_del:
                        st.markdown("**Delete Receiver**")
                        st.warning("⚠️ Deleting this receiver will also delete all associated claims.")
                        if st.button(f"Delete Receiver {row['Receiver_ID']}", key=f"del_rec_{row['Receiver_ID']}", type="primary"):
                            try:
                                execute_dml("DELETE FROM Receivers WHERE Receiver_ID=? AND Created_By=?", (row['Receiver_ID'], user_id))
                                st.success("Receiver deleted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting receiver: {e}")

    # ------------------ TAB 3: MY FOOD LISTINGS ------------------
    with tab3:
        st.subheader("My Food Listings")
        listings = execute_query("""
            SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Food_Type, fl.Meal_Type, p.Name as Provider_Name 
            FROM Food_Listings fl
            JOIN Providers p ON fl.Provider_ID = p.Provider_ID
            WHERE fl.Created_By = ? ORDER BY fl.Expiry_Date ASC;
        """, (user_id,))
        
        if listings.empty:
            st.info("You haven't posted any food listings yet.")
        else:
            for _, row in listings.iterrows():
                with st.expander(f"Listing: {row['Food_Name']} - {row['Quantity']} units (Exp: {row['Expiry_Date']})"):
                    st.write(f"**Provider**: {row['Provider_Name']}")
                    
                    col_edit, col_del = st.columns(2)
                    
                    with col_edit:
                        st.markdown("**Edit Listing**")
                        with st.form(f"edit_list_{row['Food_ID']}"):
                            f_name = st.text_input("Food Name", value=row['Food_Name'])
                            f_qty = st.number_input("Quantity", min_value=0, value=max(0, int(row['Quantity'])), key=f"edit_qty_{row['Food_ID']}")
                            
                            # Parse date safely
                            try:
                                exp_date = pd.to_datetime(row['Expiry_Date']).date()
                            except:
                                exp_date = pd.Timestamp.today().date()
                                
                            f_exp = st.date_input("Expiry Date", value=exp_date)
                            f_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan", "Halal", "Gluten-Free"], index=["Vegetarian", "Non-Vegetarian", "Vegan", "Halal", "Gluten-Free"].index(row['Food_Type']) if row['Food_Type'] in ["Vegetarian", "Non-Vegetarian", "Vegan", "Halal", "Gluten-Free"] else 0)
                            f_meal = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"], index=["Breakfast", "Lunch", "Dinner", "Snacks"].index(row['Meal_Type']) if row['Meal_Type'] in ["Breakfast", "Lunch", "Dinner", "Snacks"] else 0)
                            
                            if st.form_submit_button("Update Listing"):
                                try:
                                    execute_dml(
                                        "UPDATE Food_Listings SET Food_Name=?, Quantity=?, Expiry_Date=?, Food_Type=?, Meal_Type=? WHERE Food_ID=? AND Created_By=?",
                                        (f_name, f_qty, f_exp.strftime('%Y-%m-%d'), f_type, f_meal, row['Food_ID'], user_id)
                                    )
                                    st.success("Listing updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating listing: {e}")
                                    
                    with col_del:
                        st.markdown("**Delete Listing**")
                        st.warning("⚠️ Deleting this listing will also delete all associated claims.")
                        if st.button(f"Delete Listing {row['Food_ID']}", key=f"del_list_{row['Food_ID']}", type="primary"):
                            try:
                                execute_dml("DELETE FROM Food_Listings WHERE Food_ID=? AND Created_By=?", (row['Food_ID'], user_id))
                                st.success("Listing deleted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting listing: {e}")

    # ------------------ TAB 4: MY CLAIMS ------------------
    with tab4:
        st.subheader("My Claim Requests")
        claims = execute_query("""
            SELECT c.Claim_ID, c.Status, c.Timestamp, c.Claim_Quantity, fl.Food_Name, p.Name as Provider_Name, r.Name as Receiver_Name
            FROM Claims c
            JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
            JOIN Providers p ON fl.Provider_ID = p.Provider_ID
            JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
            WHERE c.Created_By = ? ORDER BY c.Timestamp DESC;
        """, (user_id,))
        
        if claims.empty:
            st.info("You haven't made any claims yet.")
        else:
            for _, row in claims.iterrows():
                with st.expander(f"Claim #{row['Claim_ID']} - {row['Food_Name']} ({row['Receiver_Name']})"):
                    # Display status badge
                    status = row['Status']
                    badge_class = f"badge-{status.lower()}" if status in ['Pending', 'Completed', 'Cancelled'] else "badge-pending"
                    st.markdown(f"Status: <span class='{badge_class}'>{status}</span>", unsafe_allow_html=True)
                    
                    st.write(f"**Requested:** {row['Timestamp']}")
                    st.write(f"**Quantity Claimed:** {row['Claim_Quantity']} units")
                    st.write(f"**Provider:** {row['Provider_Name']}")
                    
                    if status == 'Pending':
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"Cancel Claim #{row['Claim_ID']}", key=f"cancel_claim_{row['Claim_ID']}"):
                            try:
                                execute_dml(
                                    "UPDATE Claims SET Status='Cancelled' WHERE Claim_ID=? AND Created_By=?",
                                    (row['Claim_ID'], user_id)
                                )
                                st.success("Claim cancelled.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error cancelling claim: {e}")

    # ------------------ TAB 5: INCOMING CLAIMS ------------------
    with tab5:
        st.subheader("Incoming Claim Requests")
        incoming = execute_query("""
            SELECT c.Claim_ID, c.Status, c.Timestamp, c.Claim_Quantity, fl.Food_ID, fl.Food_Name, fl.Quantity as Available_Quantity, 
                   r.Name as Receiver_Name, r.Contact as Receiver_Contact, p.Name as Provider_Name
            FROM Claims c
            JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
            JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
            JOIN Providers p ON fl.Provider_ID = p.Provider_ID
            WHERE p.Created_By = ? AND c.Status = 'Pending'
            ORDER BY c.Timestamp ASC;
        """, (user_id,))
        
        if incoming.empty:
            st.info("No pending incoming claims for your food listings.")
        else:
            for _, row in incoming.iterrows():
                with st.expander(f"Claim #{row['Claim_ID']} for {row['Food_Name']} (Req: {row['Claim_Quantity']} units)"):
                    st.write(f"**From Receiver:** {row['Receiver_Name']} (Contact: {row['Receiver_Contact']})")
                    st.write(f"**Requested On:** {row['Timestamp']}")
                    st.write(f"**Your Provider:** {row['Provider_Name']}")
                    st.write(f"**Available Quantity in Listing:** {row['Available_Quantity']} units")
                    
                    col_acc, col_rej = st.columns(2)
                    with col_acc:
                        if st.button("Accept Claim", key=f"acc_claim_{row['Claim_ID']}", type="primary"):
                            try:
                                # 1. Set status to Completed
                                execute_dml("UPDATE Claims SET Status='Completed' WHERE Claim_ID=?", (row['Claim_ID'],))
                                # 2. Deduct quantity
                                new_qty = max(0, row['Available_Quantity'] - row['Claim_Quantity'])
                                execute_dml("UPDATE Food_Listings SET Quantity=? WHERE Food_ID=?", (new_qty, row['Food_ID']))
                                st.success("Claim accepted! Quantity deducted.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error accepting claim: {e}")
                    with col_rej:
                        if st.button("Reject Claim", key=f"rej_claim_{row['Claim_ID']}"):
                            try:
                                execute_dml("UPDATE Claims SET Status='Rejected' WHERE Claim_ID=?", (row['Claim_ID'],))
                                st.success("Claim rejected.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error rejecting claim: {e}")
