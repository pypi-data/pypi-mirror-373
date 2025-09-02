from pathlib import Path
from urllib.parse import urlencode
import jwt.algorithms
import json, requests, jwt

from logging import getLogger

logger = getLogger(__name__)

class OIDCImpl:
    def __init__(self, conf: Path|dict):
        if isinstance(conf, Path):
            with open(conf, 'r') as file:
                self._load_conf(json.load(file))
        else:
            self._load_conf(conf)
        self._load_from_manifest()
        self._load_public_keys()
            
    def _load_conf(self, conf: dict):
        self.redirect_uri = conf['redirect_uri']
        self.client_id = conf['client_id']
        self.client_secret = conf['client_secret']
        self.manifest_uri = conf['manifest_uri']
        self.scopes = conf.get('scopes', ['openid', 'profile', 'email'])
        
    def _load_from_manifest(self):
        response = requests.get(self.manifest_uri)
        response.raise_for_status()
        response = response.json()
        self.jwks_uri = response["jwks_uri"]
        self.authorization_url = response["authorization_endpoint"]
        self.token_url = response["token_endpoint"]
        
    def _load_public_keys(self):
        response = requests.get(self.jwks_uri)
        response.raise_for_status
        keys = response.json()["keys"]
        self.public_keys = {}
        for jwk in keys:
            kid = jwk['kid']
            self.public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
            
    def _verify_token(self, token, retried=False):
        try:
            kid = jwt.get_unverified_header(token).get('kid')
            key = self.public_keys.get(kid)
            if key is None: raise KeyError(f"Unkown kid: {kid}")
            return jwt.decode(token, key=key, algorithms=['RS256'], audience=self.client_id)
        except (KeyError, jwt.InvalidSignatureError, jwt.DecodeError) as e:
            if retried: raise
            logger.warning("Failed to verify token (reason: %s). Reloading keys and retrying...", type(e).__name__)
            self._load_public_keys()
            return self._verify_token(token, True)
        except jwt.InvalidTokenError as e:
            logger.error("Token verification failed: %s", e)
            raise
        
    def get_login_url(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
            "response_type": "code",
        }
        return f"{self.authorization_url}?{urlencode(params)}"
    
    def get_id_token(self, code: str):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.token_url, data=data, headers=headers)
        try:
            response.raise_for_status()
        except:
            logger.debug(f"Error response from OIDC IdP: {response.json()}")
            raise
        token = response.json()['id_token']
        return self._verify_token(token)