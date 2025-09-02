from .oidc import OIDC
from .auth_provider import AuthProvider

class OIDCProvider(AuthProvider):
    def __init__(self, title: str, name: str, conf: dict):
        super().__init__(title, name, conf.get('populate_user', 'drf_sso.providers.user_population.base_user_population'))
        self._init_provider_api(conf['config'])

    def _init_provider_api(self, config: dict):
        config['redirect_uri'] = f"{self.base_url}callback/"
        self.provider = OIDC(config)
    
    def get_login_url(self):
        return self.provider.get_login_url()
    
    def validate_response(self, request):
        return self.provider.get_id_token(request.query_params.get('code'))