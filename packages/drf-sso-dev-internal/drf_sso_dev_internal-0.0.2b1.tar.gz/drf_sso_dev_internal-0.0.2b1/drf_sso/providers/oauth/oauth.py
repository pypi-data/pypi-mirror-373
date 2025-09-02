from pathlib import Path
from urllib.parse import urlencode
import json, requests

class OAuthImpl:
    def __init__(self, conf: Path|dict):
        if isinstance(conf, Path):
            with open(conf, 'r') as file:
                self._load_conf(json.load(file))
        else:
            self._load_conf(conf)
            
    def _load_conf(self, conf: dict):
        self.client_id = conf['client_id']
        self.client_secret = conf['client_secret']
        self.authorization_url = conf['authorization_url']
        self.token_url = conf['token_url']
        self.redirect_uri = conf['redirect_uri']
        self.user_info_url = conf['user_info_url']
        self.scopes = conf.get('scopes', ['openid', 'profile', 'email'])
        self.extra_authorzation = conf.get('extra_authorization', None)
        
    def get_login_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
        }
        if self.extra_authorzation is not None:
            params.append(self.extra_authorzation)
        return f"{self.authorization_url}?{urlencode(params)}"
    
    def exchange_code(self, code: str):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_userinfo(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()