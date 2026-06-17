import streamlit as st
from app.utils.auth_utils import create_user, authenticate_user, login_user

def render_auth_page():
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <span style="font-size: 4rem;">🌱</span>
            <h1 style="margin-top: 0; margin-bottom: 0;">ZeroWaste</h1>
            <p style="color: #94a3b8; font-size: 1.1rem;">Local Food Redistribution System</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "✨ Sign Up"])
        
        with tab1:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("Welcome Back")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Log In", use_container_width=True)
                
                if submit_login:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        user = authenticate_user(username, password)
                        if user:
                            login_user(user)
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("Create an Account")
            with st.form("signup_form"):
                new_username = st.text_input("Username *", help="Must be unique.")
                display_name = st.text_input("Display Name *", help="How you will be known on the platform.")
                new_password = st.text_input("Password *", type="password", help="Minimum 4 characters.")
                confirm_password = st.text_input("Confirm Password *", type="password")
                
                submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit_signup:
                    if not new_username or not display_name or not new_password or not confirm_password:
                        st.error("Please fill in all required fields (*).")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters long.")
                    else:
                        try:
                            create_user(new_username, new_password, display_name)
                            # Auto login
                            user = authenticate_user(new_username, new_password)
                            if user:
                                login_user(user)
                                st.success("Account created successfully! Logging you in...")
                                st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
