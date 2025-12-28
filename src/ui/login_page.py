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
                background-color: #0F172A;
            }
            
            [data-testid="stSidebar"] { display: none; }
            
            .login-wrapper {
                display: flex;
                justify-content: center;
                align-items: center;
                padding-top: 5rem;
            }
            
            .login-card {
                width: 100%;
                max-width: 450px;
                background: #1E293B;
                padding: 3.5rem 2.5rem;
                border-radius: 20px;
                border: 1px solid #334155;
                text-align: center;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }
            
            .login-logo { font-size: 4rem; margin-bottom: 1.5rem; }
            
            .login-title {
                color: #F8FAFC !important;
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
            
            .auth-btn {
                display: block;
                width: 100%;
                padding: 1.1rem;
                margin-bottom: 1rem;
                border-radius: 10px;
                font-weight: 601;
                text-decoration: none;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                border: 1px solid #334155;
                background-color: #0F172A;
                color: #F1F5F9 !important;
                text-align: center;
            }
            
            .auth-btn:hover {
                border-color: #38BDF8;
                color: #38BDF8 !important;
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.2);
            }
            
            .guest-link {
                display: inline-block;
                margin-top: 1.5rem;
                color: #64748B;
                font-size: 0.95rem;
                text-decoration: none;
                transition: color 0.2s;
            }
            .guest-link:hover { color: #38BDF8; }
            
            .card-footer {
                margin-top: 3.5rem;
                padding-top: 1.5rem;
                border-top: 1px solid #334155;
                color: #475569;
                font-size: 0.8rem;
                letter-spacing: 0.05em;
            }
        </style>
    """, unsafe_allow_html=True)
    
    auth = OAuthHandler()
    google_url = auth._get_google_auth_url()
    github_url = auth._get_github_auth_url()

    # We use a single markdown block for the entire UI to ensure layout stability
    st.markdown(f"""
        <div class="login-wrapper">
            <div class="login-card">
                <div class="login-logo">🤖</div>
                <h1 class="login-title">JobPulse</h1>
                <p class="login-subtitle">Premium Job Intelligence</p>
                
                <a href="{google_url}" target="_self" class="auth-btn">🔐 Sign in with Google</a>
                <a href="{github_url}" target="_self" class="auth-btn">🔐 Sign in with GitHub</a>
                
                <p style="margin-top: 1rem;">
                    <a href="?guest=true" class="guest-link">⚡ Skip & Continue as Guest</a>
                </p>
                
                <div class="card-footer">
                    INDUSTRIAL VERSION v1.1.2 • SECURE SESSION
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Handle the guest query parameter if clicked
    if st.query_params.get("guest") == "true":
        st.query_params.clear()
        auth.guest_login()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # DIAGNOSTICS in a standard Streamlit expander below the card
    with st.expander("⚙️ System Diagnostics"):
        st.code(f"Endpoint: {auth.redirect_uri}")
        st.code(f"Env: {os.getenv('ENV', 'production')}")
        st.info("Ensure the Endpoint matches your OAuth App configurations.")
