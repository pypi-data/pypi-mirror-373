import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

def handover_from_user(user, duration=5):
    
    if user is None or user.__class__ != User:
        raise Exception("User is not a valid django user model")
    
    payload = {
        "exp": datetime.now().timestamp() + duration,
        "sub": str(user.pk)
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def user_from_handover(token):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'], options={
        "require": ['sub', 'exp']
    })
    
    return User.objects.get(pk=payload['sub'])