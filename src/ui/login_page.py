"""
Login page UI for JobPulse Agent.
Clean OAuth login interface.
"""
import streamlit as st
from src.auth import OAuthHandler

def show_login_page():
    """Display the login page with OAuth options."""
    
    # Industrial styling for login page
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
                background-color: #0F172A; /* Slate-950 */
                color: #E2E8F0;
            }
            
            [data-testid="stSidebar"] {
                display: none;
            }
            
            .login-container {
                max-width: 500px;
                margin: 4rem auto;
                padding: 3rem;
                background: #1E293B; /* Slate-800 */
                border-radius: 16px;
                border: 1px solid #334155; /* Slate-700 */
                text-align: center;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
            }
            
            .login-logo {
                font-size: 3.5rem;
                margin-bottom: 1rem;
            }
            
            .login-title {
                color: #F8FAFC;
                font-weight: 800;
                font-size: 2.5rem !important;
                margin-bottom: 0.5rem;
                letter-spacing: -0.025em;
            }
            
            .login-subtitle {
                color: #94A3B8;
                font-size: 1.1rem;
                margin-bottom: 3rem;
            }
            
            /* Industrial Buttons */
            .stButton>button, .stLinkButton>a {
                border-radius: 8px !important;
                height: 3.5rem !important;
                font-weight: 600 !important;
                transition: all 0.2s !important;
                border: 1px solid #334155 !important;
                background-color: #0F172A !important;
                color: #F1F5F9 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                text-decoration: none !important;
            }
            
            .stButton>button:hover, .stLinkButton>a:hover {
                border-color: #38BDF8 !important;
                color: #38BDF8 !important;
                transform: translateY(-1px) !important;
                background-color: rgba(56, 189, 248, 0.05) !important;
                box-shadow: 0 4px 12px rgba(56, 189, 248, 0.1) !important;
            }
            
            /* Remove default streamlit button container gaps */
            .element-container { margin-bottom: 0px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered design using st.columns for outer padding
    _, main_col, _ = st.columns([1, 2, 1])
    
    with main_col:
        # Wrap the header in a styled div
        st.markdown("""
            <div class="login-container">
                <div class="login-logo">🤖</div>
                <h1 class="login-title">JobPulse Agent</h1>
                <p class="login-subtitle">AI-Driven Job Search Intelligence</p>
        """, unsafe_allow_html=True)
        
        auth = OAuthHandler()
        
        # PROVIDER BUTTONS
        auth.google_login("🔐 Sign in with Google")
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        auth.github_login("🔐 Sign in with GitHub")
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        
        # GUEST BUTTON
        if st.button("⚡ Continue as Guest", key="guest_login", use_container_width=True):
            auth.guest_login()
            
        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
        
        # UTILITIES
        with st.expander("🛡️ Enterprise Security"):
            st.markdown("""
            - **Industry Standard:** Secure OAuth 2.0 flow
            - **Data Isolation:** User-specific local database
            - **Privacy First:** No tracking or data resale
            """)
            
        with st.expander("⚙️ System Diagnostics"):
            st.caption("Deployment Node: Streamlit Cloud")
            st.code(f"Callback: {auth.redirect_uri}")
            st.info("Ensure the Callback URI above matches your Cloud Console settings.")

        st.markdown("""
                <div style="margin-top: 3rem; border-top: 1px solid #334155; padding-top: 1rem;">
                    <span style="color: #64748B; font-size: 0.8rem;">System Version v1.1.0-STABLE</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
