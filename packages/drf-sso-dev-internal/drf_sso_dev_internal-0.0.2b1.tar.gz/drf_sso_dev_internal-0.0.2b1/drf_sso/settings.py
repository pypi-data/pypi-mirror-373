from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

DEFAULTS = {
    "MODULE_BASE_URL": None,
    "FRONTEND_CALLBACK_URL": None,
    "PROVIDERS": {}
}

class DRFSSOSettings:
    def __init__(self):
        user_settings = getattr(django_settings, 'DRF_SSO', {})
        
        for setting, default in DEFAULTS.items():
            setattr(self, setting, user_settings.get(setting, default))
            
        if self.MODULE_BASE_URL is None:
            raise ImproperlyConfigured("DRF_SSO['MODULE_BASE_URL'] n'est pas défini.")
        
        if self.FRONTEND_CALLBACK_URL is None:
            raise ImproperlyConfigured("DRF_SSO['FRONTEND_CALLBACK_URL'] n'est pas défini.")

        if not isinstance(self.PROVIDERS, dict):
            raise ImproperlyConfigured("DRF_SSO['PROVIDERS'] doit être un dictionnaire.")
        
        if not isinstance(self.MODULE_BASE_URL, str):
            raise ImproperlyConfigured("DRF_SSO['MODULE_BASE_URL'] doit être une string.")
        
        if not isinstance(self.FRONTEND_CALLBACK_URL, str):
            raise ImproperlyConfigured("DRF_SSO['FRONTEND_CALLBACK_URL'] doit être une string.")

api_settings = DRFSSOSettings()