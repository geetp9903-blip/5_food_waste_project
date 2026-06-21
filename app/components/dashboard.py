import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from database import queries
from app.utils.db_utils import execute_query
from app.utils.auth_utils import get_current_user
from app.utils.chart_utils import (
    apply_premium_chart_layout,
    BLUE_PALETTE,
    RED_PALETTE,
    GREEN_PALETTE,
    YELLOW_PALETTE,
    FOOD_TYPE_COLOR_MAP,
    STATUS_COLOR_MAP
)

def render_dashboard_section():
    user = get_current_user()
    
    # Header layout with Data Source Toggle
    st.title(f"📊 Analytics Dashboard for {user['Display_Name']}")
    
    col_sub, col_toggle = st.columns([2, 1])
    with col_sub:
        st.markdown("### *Explore trends, distributions, and perform SQL analytical queries.*")
    with col_toggle:
        data_source = st.radio(
            "Visualizations Data Source:",
            ["Original Raw Data (Static)", "Live App Data (Active)"],
            index=0,
            horizontal=True,
            help="Choose 'Original Raw Data' to view consistent historical analytics, or 'Live App Data' to see user session changes."
        )
        st.session_state["analytics_data_source"] = data_source
    
    # ------------------ TOP METRICS ------------------
    st.markdown("#### Platform Summary")
    
    # Get counts
    providers_receivers = queries.get_providers_receivers_by_city()
    total_providers = int(providers_receivers['Provider_Count'].sum()) if not providers_receivers.empty else 0
    total_receivers = int(providers_receivers['Receiver_Count'].sum()) if not providers_receivers.empty else 0
    
    availability = queries.get_food_availability_summary()
    if not availability.empty:
        total_listed = int(availability.iloc[0]['Total_Quantity_Listed'] or 0)
        unclaimed = int(availability.iloc[0]['Currently_Unclaimed_Quantity'] or 0)
    else:
        total_listed = 0
        unclaimed = 0
        
    status_df = queries.get_claim_status_percentage()
    completed_claims = int(status_df[status_df['Status'] == 'Completed']['Count'].sum()) if not status_df.empty else 0

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric(label="Total Food Listed (Units)", value=f"{total_listed:,}")
    with m_col2:
        st.metric(label="Available (Unclaimed)", value=f"{unclaimed:,}")
    with m_col3:
        st.metric(label="Successful Claims", value=f"{completed_claims:,}")
    with m_col4:
        st.metric(label="Registered Partners", value=f"{total_providers + total_receivers:,}", 
                  help=f"Providers: {total_providers} | Receivers: {total_receivers}")
                  
    st.markdown("---")

    # ------------------ INTERACTIVE SQL RUNNER ------------------
    st.markdown("### 🔍 Interactive SQL Query Explorer")
    st.write("Select one of the 15 pre-defined SQL queries to view the raw query code, execute it against the SQLite database, and visualize the output.")

    query_list = [
        "1. Temporal Trends of Food Claims",
        "2. Top Food Contributing Provider Types",
        "3. Provider Contact Directory by City",
        "4. Top Claiming Receivers (by Quantity)",
        "5. Food Availability Summary (Listed vs Unclaimed)",
        "6. Cities with the Highest Number of Listings",
        "7. Most Commonly Available Food Types",
        "8. Number of Claims per Food Item",
        "9. Providers with Most Successful Claims",
        "10. Claim Status Percentage Breakdown",
        "11. Average Quantity Claimed per Receiver",
        "12. Meal Type Demand (Claims)",
        "13. Total Quantity Donated by Provider",
        "14. Average Quantity Listed by Food Type",
        "15. Top 10 Listings Closest to Expiry"
    ]

    selected_query_label = st.selectbox("Choose a query for analysis:", query_list)
    
    # Render based on selection
    if selected_query_label.startswith("1. "):
        st.subheader("Query 1: Temporal Trends of Food Claims")
        st.markdown("**Description**: Evaluates the daily trend of food claims to understand platform activity over time.")
        
        sql_code = """
        SELECT DATE(Timestamp) as Claim_Date, COUNT(Claim_ID) as Total_Claims
        FROM Claims
        WHERE Timestamp IS NOT NULL AND Timestamp != ''
        GROUP BY DATE(Timestamp)
        ORDER BY Claim_Date DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_claims_temporal_trend()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Claims Over Time")
                # Sort ASC chronologically for line plotting
                df_plot = df.sort_values(by='Claim_Date', ascending=True)
                fig = px.line(df_plot, x='Claim_Date', y='Total_Claims', markers=True,
                              color_discrete_sequence=[BLUE_PALETTE[0]],
                              template='plotly_dark')
                fig.update_traces(line=dict(width=3), marker=dict(size=8, symbol='circle', line=dict(color='#0f172a', width=1.5)))
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("2. "):
        st.subheader("Query 2: Top Food Contributing Provider Types")
        st.markdown("**Description**: Displays which category of provider contributes the largest quantity of food.")
        
        sql_code = """
        SELECT p.Type as Provider_Type, 
               COUNT(fl.Food_ID) as Total_Listings,
               SUM(fl.Quantity) as Total_Quantity_Contributed
        FROM Food_Listings fl
        JOIN Providers p ON fl.Provider_ID = p.Provider_ID
        GROUP BY p.Type
        ORDER BY Total_Quantity_Contributed DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_contributions_by_provider_type()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Contribution by Type")
                fig = px.pie(df, names='Provider_Type', values='Total_Quantity_Contributed',
                             color_discrete_sequence=YELLOW_PALETTE,
                             template='plotly_dark', hole=0.4)
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("3. "):
        st.subheader("Query 3: Provider Contact Directory by City")
        st.markdown("**Description**: Parametric search listing providers in a selected city along with their contact info.")
        
        # Get unique cities
        cities_df = queries.run_query("SELECT DISTINCT City FROM Providers ORDER BY City ASC;")
        city_list = cities_df['City'].tolist() if not cities_df.empty else []
        
        selected_city = st.selectbox("Select City for Directory Lookup:", city_list)
        
        sql_code = """
        SELECT Name, Type, Address, City, Contact
        FROM Providers
        WHERE City = ?
        ORDER BY Name ASC;
        """
        st.code(sql_code.replace("?", f"'{selected_city}'"), language="sql")
        
        df = queries.get_providers_contact_by_city(selected_city)
        st.markdown(f"##### Directory for {selected_city}")
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No providers registered in this city.")

    elif selected_query_label.startswith("4. "):
        st.subheader("Query 4: Top Claiming Receivers")
        st.markdown("**Description**: Ranks receivers based on the total quantity of food claimed.")
        
        sql_code = """
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
        st.code(sql_code, language="sql")
        
        df = queries.get_top_claiming_receivers()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Top 10 Receivers (Quantity Claimed)")
                fig = px.bar(df.head(10), x='Total_Quantity_Claimed', y='Receiver_Name', orientation='h',
                             color='Receiver_Type',
                             color_discrete_sequence=BLUE_PALETTE,
                             template='plotly_dark')
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("5. "):
        st.subheader("Query 5: Food Availability Summary (Listed vs Unclaimed)")
        st.markdown("**Description**: Compares overall food donations with the amount that has not yet been marked as Completed.")
        
        sql_code = """
        SELECT 
            (SELECT SUM(Quantity) FROM Food_Listings) as Total_Quantity_Listed,
            (SELECT SUM(fl.Quantity) FROM Food_Listings fl 
             WHERE fl.Food_ID NOT IN (SELECT Food_ID FROM Claims WHERE Status = 'Completed')) as Currently_Unclaimed_Quantity;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_food_availability_summary()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Claim Status of Total Listings")
                listed = df.iloc[0]['Total_Quantity_Listed'] or 0
                unclaimed = df.iloc[0]['Currently_Unclaimed_Quantity'] or 0
                claimed = listed - unclaimed
                
                chart_df = pd.DataFrame({
                    'Category': ['Claimed/Completed', 'Available/Unclaimed'],
                    'Quantity': [claimed, unclaimed]
                })
                
                fig = px.pie(chart_df, names='Category', values='Quantity',
                             color_discrete_sequence=[GREEN_PALETTE[2], GREEN_PALETTE[0]],
                             template='plotly_dark', hole=0.4)
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("6. "):
        st.subheader("Query 6: Cities with the Highest Number of Listings")
        st.markdown("**Description**: Ranks locations based on how many surplus food items were listed.")
        
        sql_code = """
        SELECT Location as City, 
               COUNT(*) as Listing_Count, 
               SUM(Quantity) as Total_Quantity
        FROM Food_Listings
        GROUP BY Location
        ORDER BY Listing_Count DESC;
        """
        st.code(sql_code, language="sql")
        
        top_n = st.number_input("Visualize Top N Cities:", min_value=1, max_value=50, value=15, step=1)
        
        df = queries.get_cities_by_listings()
        
        if not df.empty:
            # Sort by Listing_Count DESC for both table and chart
            df = df.sort_values(by='Listing_Count', ascending=False)
            
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown(f"##### Top {top_n} Cities by Listings & Quantity")
                df_subset = df.head(top_n)
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(
                    go.Bar(x=df_subset['City'], y=df_subset['Total_Quantity'], name="Total Quantity (Units)", 
                           marker_color=BLUE_PALETTE[1], marker_line=dict(color='rgba(255,255,255,0.1)', width=1)),
                    secondary_y=False,
                )
                
                fig.add_trace(
                    go.Scatter(x=df_subset['City'], y=df_subset['Listing_Count'], name="Listing Count", mode="lines+markers", 
                               line=dict(color=BLUE_PALETTE[0], width=3),
                               marker=dict(size=8, color=BLUE_PALETTE[0], line=dict(color='#0f172a', width=1.5))),
                    secondary_y=True,
                )
                
                apply_premium_chart_layout(fig)
                fig.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                fig.update_yaxes(title_text="Total Quantity (Units)", secondary_y=False)
                fig.update_yaxes(title_text="Listing Count", secondary_y=True)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("7. "):
        st.subheader("Query 7: Most Commonly Available Food Types")
        st.markdown("**Description**: Breakdown of food listed by categories (e.g. Vegetarian, Non-Vegetarian, Vegan).")
        
        sql_code = """
        SELECT Food_Type, 
               COUNT(*) as Listing_Count, 
               SUM(Quantity) as Total_Quantity
        FROM Food_Listings
        GROUP BY Food_Type
        ORDER BY Listing_Count DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_common_food_types()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                fig = px.pie(df, names='Food_Type', values='Total_Quantity',
                             color='Food_Type', color_discrete_map=FOOD_TYPE_COLOR_MAP,
                             template='plotly_dark', hole=0.4)
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("8. "):
        st.subheader("Query 8: Number of Claims per Food Item")
        st.markdown("**Description**: Displays demand density for specific food names (shows which foods receive the most interest).")
        
        sql_code = """
        SELECT fl.Food_Name, 
               fl.Food_Type,
               COUNT(c.Claim_ID) as Claim_Count
        FROM Food_Listings fl
        LEFT JOIN Claims c ON fl.Food_ID = c.Food_ID
        GROUP BY fl.Food_ID, fl.Food_Name, fl.Food_Type
        ORDER BY Claim_Count DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_claims_per_food_item()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table (Top 15)")
                st.dataframe(df.head(15), use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Top 10 Foods by Claim Count")
                fig = px.bar(df.head(10), x='Claim_Count', y='Food_Name', orientation='h',
                             color='Food_Type', color_discrete_map=FOOD_TYPE_COLOR_MAP,
                             template='plotly_dark')
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("9. "):
        st.subheader("Query 9: Providers with Most Successful Claims")
        st.markdown("**Description**: Identifies top performing providers whose donations have successfully reached receivers.")
        
        sql_code = """
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
        st.code(sql_code, language="sql")
        
        df = queries.get_provider_highest_successful_claims()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Successful Claims Top Providers")
                fig = px.bar(df, x='Provider_Name', y='Successful_Claims_Count', color='Provider_Type',
                             color_discrete_sequence=GREEN_PALETTE,
                             template='plotly_dark')
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("10. "):
        st.subheader("Query 10: Claim Status Percentage Breakdown")
        st.markdown("**Description**: Shows active efficiency—completed vs. pending vs. canceled request rates.")
        
        sql_code = """
        SELECT Status, 
               COUNT(*) as Count, 
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims), 2) as Percentage
        FROM Claims
        GROUP BY Status;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_claim_status_percentage()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Claim Status Percentage")
                fig = px.pie(df, names='Status', values='Percentage',
                             color='Status', color_discrete_map=STATUS_COLOR_MAP,
                             template='plotly_dark', hole=0.4)
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("11. "):
        st.subheader("Query 11: Average Quantity Claimed per Receiver")
        st.markdown("**Description**: Evaluates the average sizing of claims requested by different receiving organizations.")
        
        sql_code = """
        SELECT r.Name as Receiver_Name, 
               ROUND(AVG(fl.Quantity), 2) as Avg_Quantity_Claimed
        FROM Claims c
        JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
        JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
        GROUP BY r.Receiver_ID, r.Name
        ORDER BY Avg_Quantity_Claimed DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_avg_claimed_quantity_per_receiver()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table (Top 15)")
                st.dataframe(df.head(15), use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Top 10 Receivers by Avg Claim Size")
                fig = px.bar(df.head(10), x='Avg_Quantity_Claimed', y='Receiver_Name',
                             orientation='h', color_discrete_sequence=[YELLOW_PALETTE[1]],
                             template='plotly_dark')
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("12. "):
        st.subheader("Query 12: Meal Type Demand (Claims)")
        st.markdown("**Description**: Compares which time-of-day meal types are claimed most frequently.")
        
        sql_code = """
        SELECT fl.Meal_Type, 
               COUNT(c.Claim_ID) as Claim_Count
        FROM Claims c
        JOIN Food_Listings fl ON c.Food_ID = fl.Food_ID
        GROUP BY fl.Meal_Type
        ORDER BY Claim_Count DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_meal_type_demand()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Claim Count by Meal Type")
                fig = px.bar(df, x='Meal_Type', y='Claim_Count',
                             color='Meal_Type', color_discrete_sequence=RED_PALETTE,
                             template='plotly_dark')
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("13. "):
        st.subheader("Query 13: Total Quantity Donated by Provider")
        st.markdown("**Description**: Tracks total units donated by each individual provider profile.")
        
        sql_code = """
        SELECT p.Name as Provider_Name, 
               p.Type as Provider_Type,
               SUM(fl.Quantity) as Total_Quantity_Donated
        FROM Food_Listings fl
        JOIN Providers p ON fl.Provider_ID = p.Provider_ID
        GROUP BY p.Provider_ID, p.Name, p.Type
        ORDER BY Total_Quantity_Donated DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_total_donated_by_provider()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table (Top 15)")
                st.dataframe(df.head(15), use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Top 10 Donors (Quantity)")
                fig = px.bar(df.head(10), x='Total_Quantity_Donated', y='Provider_Name',
                             orientation='h', color='Provider_Type',
                             color_discrete_sequence=BLUE_PALETTE,
                             template='plotly_dark')
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("14. "):
        st.subheader("Query 14: Average Quantity Listed by Food Type")
        st.markdown("**Description**: Displays standard listing scale by food categories.")
        
        sql_code = """
        SELECT Food_Type, 
               ROUND(AVG(Quantity), 2) as Avg_Quantity_Listed
        FROM Food_Listings
        GROUP BY Food_Type
        ORDER BY Avg_Quantity_Listed DESC;
        """
        st.code(sql_code, language="sql")
        
        df = queries.get_avg_listed_quantity_by_food_type()
        
        if not df.empty:
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("##### Raw Output Table")
                st.dataframe(df, use_container_width=True, hide_index=True)
            with col_right:
                st.markdown("##### Avg Quantity per Listing by Type")
                fig = px.bar(df, x='Food_Type', y='Avg_Quantity_Listed',
                             color='Food_Type', color_discrete_map=FOOD_TYPE_COLOR_MAP,
                             template='plotly_dark')
                apply_premium_chart_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

    elif selected_query_label.startswith("15. "):
        st.subheader("Query 15: Top 10 Listings Closest to Expiry")
        st.markdown("**Description**: Actionable alert listing foods needing immediate claiming to prevent waste.")
        
        sql_code = """
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
        st.code(sql_code, language="sql")
        
        df = queries.get_listings_closest_to_expiry()
        
        st.markdown("##### Urgently Expiring Food Items")
        if not df.empty:
            st.dataframe(
                df.style.background_gradient(subset=['Quantity'], cmap='Reds'),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No listings found with expiry dates.")
            
    st.markdown("---")
    
    # ------------------ ADDED ADVANCED INSIGHT ------------------
    st.markdown("### 💡 Quick Wastage Insights")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="color:#ef4444; margin-top:0;">Wastage Risks</h4>
                <p style="font-size:0.95rem; color:#cbd5e1; line-height:1.5;">
                    The location with the highest frequency of expiring food listings requires immediate attention. 
                    Setting up dedicated NGO delivery hubs in these cities would significantly reduce the wastage footprint.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_b:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="color:#22c55e; margin-top:0;">Success Patterns</h4>
                <p style="font-size:0.95rem; color:#cbd5e1; line-height:1.5;">
                    Restaurant type partners show the highest claim completion efficiency. 
                    Targeting restaurant unions for platform onboarding can drastically scale successful donations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
