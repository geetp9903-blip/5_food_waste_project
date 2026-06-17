import streamlit as st
from database import queries
from app.utils.auth_utils import get_current_user

def render_education_section():
    user = get_current_user()
    st.title(f"🌱 Welcome, {user['Display_Name']}!")
    st.markdown("### *Understand, Decide, and Act for a Zero-Waste Community*")
    
    # Fetch dynamic impact metrics from DB
    metrics_df = queries.get_platform_impact_metrics()
    if not metrics_df.empty:
        total_food_saved = int(metrics_df.iloc[0]['Total_Food_Saved'] or 0)
        active_partners = int(metrics_df.iloc[0]['Active_Partners'] or 0)
        active_listings_qty = int(metrics_df.iloc[0]['Active_Listings_Quantity'] or 0)
        successful_claims = int(metrics_df.iloc[0]['Successful_Claims'] or 0)
    else:
        total_food_saved = 0
        active_partners = 0
        active_listings_qty = 0
        successful_claims = 0

    # Conversions
    co2_saved = round(total_food_saved * 2.5, 1) # kg of CO2 equivalent
    meals_provided = int(total_food_saved * 2) # assuming 0.5 units/kg per meal

    # Hero Introduction
    st.markdown(
        """
        <div class="glass-card">
            <h3 style="color: #38bdf8; margin-top: 0;">Our Mission</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #cbd5e1;">
                Food waste is a major global issue, with millions of tons of edible food discarded daily by restaurants, supermarkets, and households, while communities around the world struggle with food security. 
                Our platform bridges this gap by connecting local <strong>Food Providers</strong> (restaurants, stores, individuals) with local <strong>Receivers</strong> (NGOs, shelters, community kitchens) to rapidly redistribute surplus food before it expires.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("#### Platform Impact by the Numbers 📈")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; border-top: 4px solid #38bdf8;">
                <h2 style="color: #38bdf8; margin: 0;">{total_food_saved:,}</h2>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin: 5px 0 0 0;">Total Food Saved (Units)</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col2:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; border-top: 4px solid #818cf8;">
                <h2 style="color: #818cf8; margin: 0;">{meals_provided:,}</h2>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin: 5px 0 0 0;">Social Impact (Meals Provided)</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col3:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; border-top: 4px solid #4ade80;">
                <h2 style="color: #4ade80; margin: 0;">{co2_saved:,} kg</h2>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin: 5px 0 0 0;">Environmental Impact (CO2 Saved)</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    m_col4, m_col5, m_col6 = st.columns(3)
    with m_col4:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; border-top: 4px solid #a78bfa;">
                <h2 style="color: #a78bfa; margin: 0;">{active_partners}</h2>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin: 5px 0 0 0;">Active Partners Connected</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col5:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; border-top: 4px solid #facc15;">
                <h2 style="color: #facc15; margin: 0;">{active_listings_qty:,}</h2>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin: 5px 0 0 0;">Active Food Listings (Units)</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m_col6:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center; border-top: 4px solid #fb7185;">
                <h2 style="color: #fb7185; margin: 0;">{successful_claims:,}</h2>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin: 5px 0 0 0;">Successful Claim Distributions</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 🗺️ Your Step-by-Step Workflow Guide")
    
    guide_col1, guide_col2 = st.columns(2)
    
    with guide_col1:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: #38bdf8; margin-top:0;">Step 1: Build Your Network (Register)</h4>
                <p style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.5;">
                    To participate in the marketplace, you must first register your entity. Head over to the <strong>Register (Partners)</strong> tab on the top menu.
                    <br><br>
                    • <strong>Providers:</strong> Register as a restaurant, grocery store, or individual with surplus food to give away.<br>
                    • <strong>Receivers:</strong> Register as an NGO, shelter, or community center looking to claim available food.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div class="glass-card" style="height: 100%; margin-top: 15px;">
                <h4 style="color: #a78bfa; margin-top:0;">Step 3: Track & Approve (My Dashboard)</h4>
                <p style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.5;">
                    The <strong>My Dashboard</strong> section is your command center for managing operations.
                    <br><br>
                    • <strong>Providers:</strong> Check the <em>Incoming Claims</em> tab to review, accept, or reject claim requests. Accepting automatically deducts the quantity!<br>
                    • <strong>Receivers:</strong> Track your requests in the <em>My Claims</em> tab to see if providers have approved your claims.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        
    with guide_col2:
        st.markdown(
            """
            <div class="glass-card" style="height: 100%;">
                <h4 style="color: #4ade80; margin-top:0;">Step 2: Use the Marketplace (Act)</h4>
                <p style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.5;">
                    Once registered, visit the <strong>Marketplace (Act)</strong> tab to perform active redistributions.
                    <br><br>
                    • <strong>Donate:</strong> Under <em>List Surplus Food</em>, select your registered provider and publish a new food listing with its available quantity.<br>
                    • <strong>Claim:</strong> Under <em>Claim Available Food</em>, browse real-time listings from other providers. Select a food item, specify the quantity you need, and submit a claim request on behalf of your registered receiver.
                </p>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="glass-card" style="height: 100%; margin-top: 15px;">
                <h4 style="color: #fb7185; margin-top:0;">Step 4: Explore Data (Analytics)</h4>
                <p style="font-size: 0.95rem; color: #cbd5e1; line-height: 1.5;">
                    Head over to the <strong>Analytics (Decide)</strong> tab to see the bigger picture. 
                    <br><br>
                    We compile all donor and claim transactions into an SQL database, enabling real-time charts, metrics, and automated visualization of regional food waste trends.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
