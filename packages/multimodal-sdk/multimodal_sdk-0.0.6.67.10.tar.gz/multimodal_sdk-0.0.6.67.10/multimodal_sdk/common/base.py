import os
from dotenv import load_dotenv

class BaseMultiModalRag:
    def __init__(self, base_url=None):
        load_dotenv()
        self.base_url = base_url if base_url else os.getenv('BASE_URL', 'https://192.168.20.20/api/v1')
        self.oauth_url = os.getenv('OAUTH_URL', 'https://192.168.20.20/api/v1/auth')
        self.authz_url = os.getenv('AUTHZ_URL', 'https://192.168.20.20/api/v1/authz')

        self.access_token = None
        self.refresh_token = None
        self.username = None
        self.password = None
        self.user_id = None
    
    def set_tokens(self, access_token, refresh_token, username, password, user_id):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.username = username
        self.password = password
        self.user_id = user_id
    
    def clear_tokens(self):
        self.access_token = None
        self.refresh_token = None
        self.username = None
        self.password = None
        self.user_id = None
    
    def check_auth(self):
        if not self.access_token or not self.refresh_token or not self.username or not self.password or not self.user_id:
            self.clear_tokens()
            return False
        return True