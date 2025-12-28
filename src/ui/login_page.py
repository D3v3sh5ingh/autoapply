"""
Login page UI for JobPulse Agent.
Clean OAuth login interface.
"""
import streamlit as st
from src.auth import OAuthHandler

def show_login_page():
    """Display the login page with OAuth options."""
    
    # Hide sidebar on login page
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered login container
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🤖 JobPulse Agent")
        st.markdown("### Your AI-Powered Job Search Assistant")
        st.markdown("<br>", unsafe_allow_html=True)
        
        auth = OAuthHandler()
        
        st.markdown("#### Sign in to continue")
        st.caption("Your personalized job search dashboard awaits")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Google login button
        col_g1, col_g2, col_g3 = st.columns([0.5, 2, 0.5])
        with col_g2:
            auth.google_login()
        
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        
        # GitHub login button  
        col_gh1, col_gh2, col_gh3 = st.columns([0.5, 2, 0.5])
        with col_gh2:
            auth.github_login()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Info section
        with st.expander("ℹ️ About OAuth Login"):
            st.markdown("""
            **🔐 Secure Authentication:**
            - No passwords to remember
            - Your data stays private and isolated
            - Works with your existing Google/GitHub account
            
            **📊 Why Sign In:**
            - Access your saved jobs and application history
            - Track your progress over time
            - Get personalized job recommendations
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("🔒 Privacy-first • 100% open source • Your data, your control")
