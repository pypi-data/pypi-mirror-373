from django.contrib.auth import get_user_model
from drf_sso.settings import api_settings
from django.core.exceptions import ImproperlyConfigured
from drf_sso.exception import PopulationException

User = get_user_model()
def base_user_population(payload, name):
    try:
        try:
            populate_user_conf = api_settings.PROVIDERS[name]['populate_user_conf']
            (db_lookup, payload_lookup) = populate_user_conf['lookup_field']
            mappings = populate_user_conf['mappings']
        except KeyError:
            raise ImproperlyConfigured(f'Provider "{name}" is using default user population method but doesn\'t provide a valid configuration.')
        
        payload_lookup = payload_lookup(payload) if callable(payload_lookup) else payload[payload_lookup]
        if callable(payload_lookup):
            payload_lookup = payload_lookup(payload)
        
        user, created = User.objects.get_or_create(**{db_lookup: payload_lookup})
        for db_field, payload_field in mappings.items():
            payload_field = payload_field(payload) if callable(payload_field) else payload_field
            setattr(user, db_field, payload_field)
        user.save()
        return user, {"created": created}
    except:
        raise PopulationException('Error populating user from payload.')