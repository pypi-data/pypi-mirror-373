# IMPORTING LIBRARIES
import streamlit as st
from urllib.parse import urlencode
import requests
from typing import Dict, Any

# Google OAuth endpoints
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

class GoogleAuthService:
    """Google OAuth authentication service."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        self.client_id = config["client_id"]
        self.client_secret = config["client_secret"]
        self.redirect_uri = config["redirect_uri"]

    def authenticate(self, env: str = "Prod"):
        """Generate authentication URL for Google OAuth."""
        st.write("Authentication required.")
        st.write("Please sign in with your Pointr Account.")

        # Generate the Google OAuth2 authentication URL
        auth_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': env
        }
        auth_url = f"{AUTHORIZATION_URL}?{urlencode(auth_params)}"
        # Create a button that triggers the authentication process
        if st.button("Sign In with Google", on_click=lambda: st.rerun):
            # Redirect the user to the Google authentication URL
            st.markdown(f'<meta http-equiv="refresh" content="0;URL={auth_url}">', unsafe_allow_html=True)

    def exchange_code_for_token(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        token_data = {
            'code': auth_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
        }
        response = requests.post(TOKEN_URL, data=token_data)
        token_info = response.json()
        return token_info

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information using access token."""
        headers = {'Authorization': f"Bearer {access_token}"}
        user_response = requests.get(USERINFO_URL, headers=headers)
        user_info = user_response.json()
        return user_info


# Legacy functions for backward compatibility
def authenticate(config: Dict[str, str], env: str = "Prod"):
    """Legacy function for backward compatibility."""
    service = GoogleAuthService(config)
    return service.authenticate(env)

def exchange_code_for_token(config: Dict[str, str], auth_code: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    service = GoogleAuthService(config)
    return service.exchange_code_for_token(auth_code)

def get_user_info(access_token: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility."""
    headers = {'Authorization': f"Bearer {access_token}"}
    user_response = requests.get(USERINFO_URL, headers=headers)
    user_info = user_response.json()
    return user_info 