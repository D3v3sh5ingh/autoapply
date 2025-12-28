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
        """Initiate Google OAuth flow using Streamlit's experimental auth."""
        # Using Streamlit's experimental OAuth (simplified approach)
        # For production, integrate with actual OAuth library
        
        if not self.google_client_id:
            st.error("⚠️ Google OAuth not configured. Add GOOGLE_CLIENT_ID to .env file.")
            return False
            
        # Streamlit experimental connection approach
        try:
            # This is a placeholder for Streamlit's OAuth integration
            # In practice, you'd use st.experimental_connection or a proper OAuth library
            st.info("🔄 Google OAuth integration pending. Using demo mode for now.")
            
            # DEMO MODE: Simulate login for development
            if st.button("🧪 Demo Login (Google)", key="google_demo"):
                self._demo_login("google")
                return True
                
        except Exception as e:
            st.error(f"Google login failed: {e}")
            return False
            
    def github_login(self):
        """Initiate GitHub OAuth flow."""
        if not self.github_client_id:
            st.error("⚠️ GitHub OAuth not configured. Add GITHUB_CLIENT_ID to .env file.")
            return False
            
        try:
            st.info("🔄 GitHub OAuth integration pending. Using demo mode for now.")
            
            # DEMO MODE
            if st.button("🧪 Demo Login (GitHub)", key="github_demo"):
                self._demo_login("github")
                return True
                
        except Exception as e:
            st.error(f"GitHub login failed: {e}")
            return False
            
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
