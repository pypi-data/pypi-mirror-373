from .auth_provider import AuthProvider
from .oauth import OAuth

class OAuthProvider(AuthProvider):
    def __init__(self, title: str, name: str, conf: dict):
        super().__init__(title, name, conf.get('populate_user', 'drf_sso.providers.user_population.base_user_population'))
        self._init_provider_api(conf['config'])

    def _init_provider_api(self, config: dict):
        config['redirect_uri'] = f"{self.base_url}callback/"
        self.provider = OAuth(config)

    def get_login_url(self):
        return self.provider.get_login_url()
    
    def validate_response(self, request):
        code = request.query_params.get('code')
        if code is None:
            raise ValueError("Code d'autorisation manquant dans la réponse")
        token = self.provider.exchange_code(code)
        if token is None:
            raise ValueError("Échec de l'échange du code d'autorisation")
        return self.provider.get_userinfo()