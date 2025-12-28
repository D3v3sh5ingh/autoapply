"""
Login page UI for JobPulse Agent.
Clean OAuth login interface.
"""
import streamlit as st
from src.auth import OAuthHandler

def show_login_page():
    """Display the login page with OAuth options."""
    
    # Premium styling for login page
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }
            
            [data-testid="stSidebar"] {
                display: none;
            }
            
            .login-card {
                background: rgba(255, 255, 255, 0.05);
                padding: 3rem;
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(20px);
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            
            .login-title {
                background: linear-gradient(90deg, #FF61D2 0%, #FE9090 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
                font-size: 2.5rem !important;
                margin-bottom: 0px;
            }
            
            .stButton>button {
                border-radius: 12px;
                height: 3rem;
                font-weight: 600;
                transition: all 0.3s ease;
                border: none;
                background: linear-gradient(45deg, #6366f1, #a855f7);
                color: white;
            }
            
            .stButton>button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered login container
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">🤖 JobPulse Agent</h1>', unsafe_allow_html=True)
        st.markdown("<p style='opacity: 0.8; font-size: 1.1rem;'>Your AI-Powered Job Search Assistant</p>", unsafe_allow_html=True)
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
        
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        
        # Guest login button
        col_gst1, col_gst2, col_gst3 = st.columns([0.5, 2, 0.5])
        with col_gst2:
            if st.button("⚡ Skip & Use as Guest", key="guest_login", use_container_width=True):
                auth.guest_login()
        
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
        st.markdown('</div>', unsafe_allow_html=True)
