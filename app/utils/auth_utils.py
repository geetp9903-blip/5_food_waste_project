import hashlib
import streamlit as st
from app.utils.db_utils import execute_query, execute_dml

# Static salt for simplicity in this project scope
SALT = "zerowaste_salt_2026!"

def hash_password(password: str) -> str:
    """Hashes a password with a static salt using SHA-256."""
    return hashlib.sha256((password + SALT).encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifies a password against a hash."""
    return hash_password(password) == hashed

def create_user(username: str, password: str, display_name: str) -> int:
    """Creates a new user in the database."""
    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters long.")
    
    hashed_pwd = hash_password(password)
    query = """
    INSERT INTO Users (Username, Password_Hash, Display_Name)
    VALUES (?, ?, ?);
    """
    try:
        return execute_dml(query, (username, hashed_pwd, display_name))
    except Exception as e:
        if 'UNIQUE constraint failed: Users.Username' in str(e):
            raise ValueError("Username already exists. Please choose a different one.")
        raise e

def authenticate_user(username: str, password: str) -> dict | None:
    """Authenticates a user and returns their info if successful."""
    query = "SELECT User_ID, Username, Password_Hash, Display_Name FROM Users WHERE Username = ?;"
    df = execute_query(query, (username,))
    
    if df.empty:
        return None
    
    user_row = df.iloc[0]
    if verify_password(password, user_row['Password_Hash']):
        return {
            'User_ID': int(user_row['User_ID']),
            'Username': str(user_row['Username']),
            'Display_Name': str(user_row['Display_Name'])
        }
    return None

def login_user(user_data: dict):
    """Logs in a user by saving their info to session state."""
    st.session_state['current_user'] = user_data
    st.session_state['current_page'] = "Home (Understand)" # Default page after login

def get_current_user() -> dict | None:
    """Returns the currently logged-in user from session state."""
    return st.session_state.get('current_user')

def is_logged_in() -> bool:
    """Checks if a user is currently logged in and verifies they exist in the database."""
    if 'current_user' not in st.session_state or st.session_state['current_user'] is None:
        return False
    
    user_id = st.session_state['current_user'].get('User_ID')
    if user_id is not None:
        try:
            # Query the database to ensure the user still exists
            query = "SELECT 1 FROM Users WHERE User_ID = ?;"
            df = execute_query(query, (int(user_id),))
            if df.empty:
                # Automatically log out if the user no longer exists (e.g. database was reset)
                st.session_state['current_user'] = None
                st.session_state['current_page'] = None
                return False
            return True
        except Exception:
            return False
    return False

def logout():
    """Logs out the current user."""
    st.session_state['current_user'] = None
    st.session_state['current_page'] = None
