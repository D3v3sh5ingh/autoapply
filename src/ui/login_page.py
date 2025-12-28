"""
Login page UI for JobPulse Agent.
Clean OAuth login interface.
"""
import os
import streamlit as st
from src.auth import OAuthHandler

def show_login_page():
    """Display the login page with OAuth options."""
    
    # Premium styling for login page
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
                background-color: #0f172a;
            }
            
            [data-testid="stSidebar"] {
                display: none;
            }
            
            /* Professional Container Styling */
            [data-testid="stHeader"] {
                background: rgba(0,0,0,0);
            }
            
            .login-card {
                background-color: #1e293b;
                padding: 3rem;
                border-radius: 16px;
                border: 1px solid #334155;
                text-align: center;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 500px;
                margin: auto;
            }

            .login-title {
                color: #f8fafc;
                font-weight: 700;
                font-size: 2.25rem !important;
                margin-top: 0;
                margin-bottom: 0.5rem;
                letter-spacing: -0.025em;
            }
            
            .login-subtitle {
                color: #94a3b8;
                font-size: 1rem;
                margin-bottom: 2rem;
            }

            .stButton>button {
                border-radius: 8px;
                height: 3.5rem;
                font-weight: 600;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid #334155;
                background-color: #0f172a;
                color: #f8fafc;
                width: 100%;
            }
            
            .stButton>button:hover {
                border-color: #6366f1;
                color: #6366f1;
                background-color: #0f172a;
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered login container
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # We use a container to apply the card styling via CSS
    # targeted at the column block
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">🤖 JobPulse Agent</h1>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Professional AI-Powered Job Search</p>', unsafe_allow_html=True)
        
        st.write("---")
        st.write("**Sign in to continue**")
        st.caption("Your personalized job search dashboard awaits")
        st.markdown("<br>", unsafe_allow_html=True)
        
        auth = OAuthHandler()
        
        # Google/GitHub login buttons
        auth.google_login()
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        auth.github_login()
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        
        if st.button("⚡ Skip & Use as Guest", key="guest_login", use_container_width=True):
            auth.guest_login()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Info section
        with st.expander("ℹ️ About OAuth Login"):
            st.markdown("""
            - **🔐 Secure:** No passwords stored
            - **🔒 Private:** Data isolation per user
            - **🚀 Fast:** One-click integration
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("🔒 Privacy-first • 100% open source")
        st.markdown('</div>', unsafe_allow_html=True)
