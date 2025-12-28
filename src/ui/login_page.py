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
    
    # Centered layout using columns
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.5, 1])
    
    with col2:
        # Use native container for stability
        with st.container(border=True):
            st.markdown('<h1 class="login-title">🤖 JobPulse Agent</h1>', unsafe_allow_html=True)
            st.markdown('<center>Professional AI-Powered Job Search</center>', unsafe_allow_html=True)
            st.divider()
            
            st.markdown("<div style='text-align: center'><b>Sign in to continue</b><br><span style='color: #64748b; font-size: 0.9em'>Your personalized job search awaits</span></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            auth = OAuthHandler()
            
            # Generate URLs (state is handled internally by generating fresh tokens)
            google_url = auth.get_google_auth_url_only()
            github_url = auth.get_github_auth_url_only()
            
            # Custom button styles
            st.markdown("""
            <style>
                .oauth-btn {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    background-color: #0f172a;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    color: #f8fafc;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.2s;
                }
                .oauth-btn:hover {
                    border-color: #6366f1;
                    color: #6366f1;
                    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Google Login via standard HTML link (target="_top" escapes iframe sandbox)
            if google_url:
                st.markdown(f'<a href="{google_url}" target="_top" class="oauth-btn">🔐 Sign in with Google</a>', unsafe_allow_html=True)
            else:
                st.error("Google OAuth not configured")
                
            # GitHub Login
            if github_url:
                st.markdown(f'<a href="{github_url}" target="_top" class="oauth-btn">🔐 Sign in with GitHub</a>', unsafe_allow_html=True)
            else:
                st.error("GitHub OAuth not configured")
                
            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)
            
            # Guest Login (still needs to be a button because it's an action, not a link)
            if st.button("⚡ Skip & Use as Guest", key="guest_login", use_container_width=True):
                auth.guest_login()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("ℹ️ About OAuth Login"):
                st.markdown("- **Secure:** No passwords stored\n- **Private:** Isolated data per user")
            
            st.caption("🔒 Privacy-first • 100% open source")
