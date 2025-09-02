#Django imports
from django.urls import path
from django.shortcuts import redirect

# Django Rest Framework imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Standard library imports
from abc import ABC, abstractmethod
from importlib import import_module
from urllib.parse import urlencode

# Local imports
from drf_sso.handover import handover_from_user
from drf_sso.settings import api_settings
from drf_sso.exception import PopulationException

def import_function(path: str):
    module_path, function_name = path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, function_name)

class AuthProvider(ABC):
    def __init__(self, title: str, name: str, populate_user: str):
        if self.__class__ == AuthProvider:
            raise TypeError("Vous ne pouvez pas instancier la classe abstraite AuthProvider")
        middle_separator = '' if api_settings.MODULE_BASE_URL.endswith('/') else '/'
        self.base_url = f"{api_settings.MODULE_BASE_URL}{middle_separator}{name}/"
        self.frontend_url = api_settings.FRONTEND_CALLBACK_URL
        self.title = title
        self.name = name
        self.populate_user = import_function(populate_user)
        
    @abstractmethod
    def get_login_url(self) -> str:
        pass
    
    @abstractmethod
    def validate_response(self, request) -> dict:
        pass

    def get_routes(self):        
        @api_view(["GET"])
        @permission_classes([AllowAny])
        def callback_view(request):
            payload = self.validate_response(request)
            query_params = {}
            #Création/Maj utilisateur
            try:
                user, params = self.populate_user(payload, self.name)
                query_params.update(params or {})
                #Création du token de handover
                handover = handover_from_user(user)
            except PopulationException as e:
                handover = ""
                query_params['err'] = e.details
                
            return redirect(f"{self.frontend_url}/{handover}?{urlencode(query_params)}")
        
        return [path(f"{self.name}/callback/", callback_view, name=f"sso-{self.name}-validate")]