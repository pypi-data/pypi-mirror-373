from .auth_provider import AuthProvider
from .cas import CAS

class CASProvider(AuthProvider):
    def __init__(self, title: str, name: str, conf: dict):
        super().__init__(title, name, conf.get('populate_user', 'drf_sso.providers.user_population.base_user_population'))
        self._init_provider_api(conf['config'])
        
    def _init_provider_api(self, config: dict):
        config['service_url'] = f"{self.base_url}callback/"
        self.provider = CAS(config)
        
    def get_login_url(self):
        return self.provider.get_login_url()
    
    def validate_response(self, request):
        return self.provider.validate_ticket(request.query_params.get('ticket'))