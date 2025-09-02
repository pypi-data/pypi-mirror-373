from enum import Enum, auto
from .cas_provider import CASProvider
from .saml_provider import SAMLProvider
from .oauth_provider import OAuthProvider
from .oidc_provider import OIDCProvider

class Provider(Enum):    
    OAUTH = auto()
    OIDC = auto()
    SAML = auto()
    CAS = auto()
    
class ProviderConfigurationError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        
provider_class_map = {
    Provider.CAS: CASProvider,
    Provider.SAML: SAMLProvider,
    Provider.OAUTH: OAuthProvider,
    Provider.OIDC: OIDCProvider
}
        
def from_config(name: str, conf: dict):
        type = conf.get('type')
        if type is None:
            raise ProviderConfigurationError("Type de provider manquant dans la configuration")
        if type.upper() not in [provider.name for provider in Provider]:
            raise ProviderConfigurationError("Type de provider inconnu dans la configuration")
        title = conf.get('title')
        if title is None:
            raise ProviderConfigurationError("Titre de provider manquant dans la configuration")
        
        provider_type = Provider[type.upper()]
        provider_cls = provider_class_map[provider_type]
        return provider_cls(title, name, conf)