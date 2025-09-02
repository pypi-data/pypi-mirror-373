from django.contrib.auth import get_user_model
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .handover import user_from_handover

User = get_user_model()

from .providers import get_providers

@api_view(["GET"])
@permission_classes([AllowAny])
def login_methods(request):
    routes = [
        {
            "title": provider.title,
            "url": provider.get_login_url()
        }
        for provider in get_providers()
    ]
    return Response(routes)

    
@api_view(['POST'])
@permission_classes([AllowAny])
def get_tokens_from_handover(request):
    handover = request.data.get("handover", None)
    if handover is None:
        return Response({"detail": "Aucun handover token fourni."}, status=400)
    
    try:
        user = user_from_handover(handover)
    except (ExpiredSignatureError,InvalidSignatureError,User.DoesNotExist):
        return Response({"detail": "Le handover token fourni est invalide."})
        
    tokens = RefreshToken.for_user(user)
    
    return Response({
        "access": str(tokens.access_token),
        "refresh": str(tokens)
    })
