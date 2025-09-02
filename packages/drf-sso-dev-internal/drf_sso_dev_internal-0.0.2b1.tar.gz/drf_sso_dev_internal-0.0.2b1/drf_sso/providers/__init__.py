from drf_sso.settings import api_settings
from .auth_provider import AuthProvider
from .registry import from_config

setattr(AuthProvider, "from_config", from_config)

def get_providers():
    return [
        AuthProvider.from_config(name, conf)
        for name, conf in api_settings.PROVIDERS.items()
    ]

def get_provider_urls():
    urlpatterns = []
    for provider in get_providers():
        urlpatterns += provider.get_routes()
    return urlpatterns