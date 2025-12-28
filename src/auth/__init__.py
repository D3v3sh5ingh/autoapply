"""Authentication module for JobPulse Agent."""
from .oauth_handler import OAuthHandler, require_auth

__all__ = ['OAuthHandler', 'require_auth']
