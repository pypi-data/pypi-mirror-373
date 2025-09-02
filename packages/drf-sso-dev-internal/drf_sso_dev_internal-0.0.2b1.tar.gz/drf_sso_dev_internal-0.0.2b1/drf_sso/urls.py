from django.urls import path
from .providers import get_provider_urls
from .views import login_methods, get_tokens_from_handover

app_name = 'drf_handover_sso'

urlpatterns = get_provider_urls() + [
    path("tokens/", get_tokens_from_handover, name="exchange-handover"),
    path("methods/", login_methods, name="login-methods")
]