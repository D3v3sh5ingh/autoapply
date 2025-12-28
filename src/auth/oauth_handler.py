"""
Production OAuth handler for JobPulse Agent.
Real Google and GitHub OAuth with proper callback handling.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session
import json

load_dotenv()

class ProductionOAuthHandler:
    """Production OAuth with real Google/GitHub integration."""
    
    def __init__(self):
        # OAuth credentials from environment
        self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.github_client_id = os.getenv("GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        
        # Redirect URI (must match OAuth app settings)
        self.redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8501")
        
        # OAuth endpoints
        self.google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        self.github_auth_url = "https://github.com/login/oauth/authorize"
        self.github_token_url = "https://github.com/login/oauth/access_token"
        self.github_userinfo_url = "https://api.github.com/user"
        
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return ('user_email' in st.session_state and 
                st.session_state.user_email is not None and
                'oauth_provider_id' in st.session_state)
        
    def get_current_user(self) -> dict:
        """Get current authenticated user info."""
        if not self.is_authenticated():
            return None
        return {
            'email': st.session_state.get('user_email'),
            'name': st.session_state.get('user_name'),
            'provider': st.session_state.get('oauth_provider', 'unknown'),
            'provider_id': st.session_state.get('oauth_provider_id')
        }
        
    def logout(self):
        """Clear user session."""
        keys_to_clear = ['user_email', 'user_name', 'oauth_provider', 'oauth_provider_id', 'user_id', 'oauth_token']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def google_login(self):
        """Initiate Google OAuth flow."""
        if not self.google_client_id or not self.google_client_secret:
            st.error("⚠️ Google OAuth not configured. Add credentials to .env")
            return False
        
        # Check if we're handling a callback
        query_params = st.query_params
        if 'code' in query_params and 'state' in query_params:
            # OAuth callback - exchange code for token
            if st.session_state.get('oauth_state') == query_params['state']:
                self._handle_google_callback(query_params['code'])
                return True
        
        # Generate OAuth URL
        if st.button("🔐 Sign in with Google", key="google_login", use_container_width=True):
            auth_url = self._get_google_auth_url()
            st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
            return True
    
    def github_login(self):
        """Initiate GitHub OAuth flow."""
        if not self.github_client_id or not self.github_client_secret:
            st.error("⚠️ GitHub OAuth not configured. Add credentials to .env")
            return False
        
        # Check if we're handling a callback
        query_params = st.query_params
        if 'code' in query_params and 'state' in query_params:
            # OAuth callback - exchange code for token
            if st.session_state.get('oauth_state') == query_params['state']:
                self._handle_github_callback(query_params['code'])
                return True
        
        # Generate OAuth URL
        if st.button("🔐 Sign in with GitHub", key="github_login", use_container_width=True):
            auth_url = self._get_github_auth_url()
            st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
            return True
    
    def _get_google_auth_url(self):
        """Generate Google OAuth authorization URL."""
        import secrets
        state = secrets.token_urlsafe(16)
        st.session_state.oauth_state = state
        
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        from urllib.parse import urlencode
        return f"{self.google_auth_url}?{urlencode(params)}"
    
    def _get_github_auth_url(self):
        """Generate GitHub OAuth authorization URL."""
        import secrets
        state = secrets.token_urlsafe(16)
        st.session_state.oauth_state = state
        
        params = {
            'client_id': self.github_client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'read:user user:email',
            'state': state
        }
        
        from urllib.parse import urlencode
        return f"{self.github_auth_url}?{urlencode(params)}"
    
    def _handle_google_callback(self, code: str):
        """Handle Google OAuth callback and fetch user info."""
        import requests
        
        # Exchange code for access token
        token_data = {
            'client_id': self.google_client_id,
            'client_secret': self.google_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            token_response = requests.post(self.google_token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Fetch user info
            headers = {'Authorization': f"Bearer {tokens['access_token']}"}
            user_response = requests.get(self.google_userinfo_url, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # Store in session
            st.session_state.user_email = user_info.get('email')
            st.session_state.user_name = user_info.get('name', user_info.get('email'))
            st.session_state.oauth_provider = 'google'
            st.session_state.oauth_provider_id = user_info.get('id')  # Google's unique user ID
            st.session_state.oauth_token = tokens['access_token']
            
            # Clear OAuth state
            if 'oauth_state' in st.session_state:
                del st.session_state.oauth_state
            
            # Clear query params
            st.query_params.clear()
            st.success(f"✅ Signed in as {st.session_state.user_email}")
            st.rerun()
            
        except Exception as e:
            st.error(f"OAuth failed: {e}")
            return False
    
    def _handle_github_callback(self, code: str):
        """Handle GitHub OAuth callback and fetch user info."""
        import requests
        
        # Exchange code for access token
        token_data = {
            'client_id': self.github_client_id,
            'client_secret': self.github_client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        
        headers = {'Accept': 'application/json'}
        
        try:
            token_response = requests.post(self.github_token_url, data=token_data, headers=headers)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Fetch user info
            auth_headers = {
                'Authorization': f"Bearer {tokens['access_token']}",
                'Accept': 'application/json'
            }
            user_response = requests.get(self.github_userinfo_url, headers=auth_headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # GitHub email might be private, fetch separately if needed
            email = user_info.get('email')
            if not email:
                email_response = requests.get(f"{self.github_userinfo_url}/emails", headers=auth_headers)
                emails = email_response.json()
                primary_email = next((e['email'] for e in emails if e['primary']), emails[0]['email'] if emails else None)
                email = primary_email or f"{user_info['login']}@github.user"
            
            # Store in session
            st.session_state.user_email = email
            st.session_state.user_name = user_info.get('name', user_info.get('login'))
            st.session_state.oauth_provider = 'github'
            st.session_state.oauth_provider_id = str(user_info.get('id'))  # GitHub's unique user ID
            st.session_state.oauth_token = tokens['access_token']
            
            # Clear OAuth state
            if 'oauth_state' in st.session_state:
                del st.session_state.oauth_state
            
            # Clear query params
            st.query_params.clear()
            st.success(f"✅ Signed in as {st.session_state.user_email}")
            st.rerun()
            
        except Exception as e:
            st.error(f"OAuth failed: {e}")
            return False

# Alias for backward compatibility
OAuthHandler = ProductionOAuthHandler

def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        auth = OAuthHandler()
        if not auth.is_authenticated():
            st.warning("🔒 Please log in to access this feature")
            return None
        return func(*args, **kwargs)
    return wrapper
