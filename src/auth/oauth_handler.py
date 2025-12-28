"""
OAuth authentication handler for JobPulse Agent.
Supports Google and GitHub OAuth flows using Streamlit.
"""
import streamlit as st
import os
from dotenv import load_dotenv
import hashlib
import time

load_dotenv()

class OAuthHandler:
    """Manages OAuth flows and session state for user authentication."""
    
    def __init__(self):
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return 'user_email' in st.session_state and st.session_state.user_email is not None
        
    def get_current_user(self) -> dict:
        """Get current authenticated user info."""
        if not self.is_authenticated():
            return None
        return {
            'email': st.session_state.get('user_email'),
            'name': st.session_state.get('user_name'),
            'provider': st.session_state.get('oauth_provider', 'unknown')
        }
        
    def logout(self):
        """Clear user session."""
        keys_to_clear = ['user_email', 'user_name', 'oauth_provider', 'user_id']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                
    def google_login(self):
        """Initiate Google OAuth flow or use demo mode."""
        # Demo mode is default - no setup needed for personal use
        if st.button("🔐 Sign in with Google (Demo Mode)", key="google_demo", use_container_width=True):
            self._demo_login("google")
            return True
            
    def github_login(self):
        """Initiate GitHub OAuth flow or use demo mode."""
        # Demo mode is default - no setup needed for personal use
        if st.button("🔐 Sign in with GitHub (Demo Mode)", key="github_demo", use_container_width=True):
            self._demo_login("github")
            return True
            
    def _demo_login(self, provider: str):
        """Demo login for development/testing without real OAuth."""
        # Generate a unique demo user based on timestamp
        user_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        st.session_state.user_email = f"demo_{user_id}@{provider}.com"
        st.session_state.user_name = f"Demo User ({provider.title()})"
        st.session_state.oauth_provider = provider
        st.session_state.user_id = None  # Will be set by DB layer
        
        st.success(f"✅ Demo login successful as {st.session_state.user_email}")
        st.rerun()
        

def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        auth = OAuthHandler()
        if not auth.is_authenticated():
            st.warning("🔒 Please log in to access this feature")
            return None
        return func(*args, **kwargs)
    return wrapper
