import streamlit as st
import sys
import os

# Add root folder to sys.path so modules import correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure database is initialized on Cloud deployment
from database.init_db import init_database, DB_PATH
if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
    init_database()

# Set up page configurations first
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling imports
from app.utils.style_utils import inject_premium_styles
from app.components.education import render_education_section
from app.components.dashboard import render_dashboard_section
from app.components.registration import render_registration_section
from app.components.marketplace import render_marketplace_section
from app.components.auth_page import render_auth_page
# from app.components.user_dashboard import render_user_dashboard # Will add soon
from app.utils.auth_utils import is_logged_in, get_current_user, logout

def render_navbar():
    """Renders the horizontal navigation bar."""
    user = get_current_user()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.markdown("<h3 style='margin:0; padding-top:10px;'><span style='color:#38bdf8;'>🌱 Zero</span>Waste</h3>", unsafe_allow_html=True)
        
    with col2:
        # Navigation buttons in a row
        nav_cols = st.columns(5)
        pages = ["Home (Understand)", "Analytics (Decide)", "Register (Partners)", "Marketplace (Act)", "My Dashboard"]
        
        for i, page in enumerate(pages):
            with nav_cols[i]:
                # If it's the current page, style it differently (primary)
                is_current = st.session_state.get('current_page') == page
                if st.button(page.split(" ")[0], key=f"nav_{i}", type="primary" if is_current else "secondary", use_container_width=True):
                    st.session_state['current_page'] = page
                    st.rerun()

    with col3:
        st.markdown(f"<div style='text-align:right; padding-top:15px; font-size:0.9rem;'>Welcome, <b>{user['Display_Name']}</b></div>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            logout()
            st.rerun()

def main():
    # Inject Custom Aesthetics CSS
    inject_premium_styles()

    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "Home (Understand)"

    # Auth Gate
    if not is_logged_in():
        render_auth_page()
    else:
        # Render top navigation
        st.markdown("<div class='nav-container'>", unsafe_allow_html=True)
        render_navbar()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Routing
        current_page = st.session_state.get('current_page')
        
        if current_page == "Home (Understand)":
            render_education_section()
        elif current_page == "Analytics (Decide)":
            render_dashboard_section()
        elif current_page == "Register (Partners)":
            render_registration_section()
        elif current_page == "Marketplace (Act)":
            render_marketplace_section()
        elif current_page == "My Dashboard":
            # Will be added in Step 5
            try:
                from app.components.user_dashboard import render_user_dashboard
                render_user_dashboard()
            except ImportError:
                st.warning("My Dashboard is currently under construction.")

    # App footer
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; font-size: 0.85rem; color: #475569; border-top: 1px solid rgba(255,255,255,0.05);">
            Made with ❤️ for Local Communities & Planet Earth. &copy; 2026 ZeroWaste Inc.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
