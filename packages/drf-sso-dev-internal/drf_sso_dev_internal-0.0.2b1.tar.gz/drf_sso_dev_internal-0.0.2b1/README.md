# DRF-SSO

Library for implementing SSO on full-stack applications using Django Rest Framework as backend.

## Supported SSO Methods

- CAS - Supported
- SAMLv2 - Supported (except SLS, SP Initiated Only)
- OAuth - Supported
- OIDC - Supported

## Configuration

Installation in settings.py example

```python
DRF_SSO = {
    "FRONTEND_CALLBACK_URL": os.getenv("SSO_FRONT", "http://localhost:5173/access"),
    "MODULE_BASE_URL": os.getenv("SSO_BACK", "http://localhost:8000/sso/"),
    "PROVIDERS": {
        "oauth": {
            "title": "oidc_provider",
            "type": "OIDC",
            "populate_user": "core.utils.populate_from_m365",
            "config": {
                "client_id": os.getenv("M365_ID"),
                "client_secret": os.getenv("M365_SECRET"),
                "manifest_uri": "https://login.microsoftonline.com/organizations/v2.0/.well-known/openid-configuration",
            }
        },
        "cas": {
            "title": "cas_provider",
            "type": "CAS",
            "populate_user": "core.utils.populate_from_cas",
            "config": {
                "login_url": "https://mycas.com/login",
                "validate_url": "https://mycas.com/serviceValidate"
            }
        }
    }
}
```

## Frontend Integration

The library exposes views that perform redirections to SSO services for authentication. It handles the retrieval of user attributes from Identity Providers and triggers a callback method with these attributes as parameters. The developer must define how to populate their user records from the retrieved attributes.

Once user processing is complete, a frontend callback is invoked with a handover token (short-lived JWT token, expires in 5 minutes) and optionally additional attributes. This callback must be implemented to perform a POST request to an endpoint exposed by the library (`<Installation path URL>/tokens/`), exchanging the handover token for the user's access and refresh JWT tokens.

The handover token serves as a secure bridge between the SSO completion and the frontend authentication flow, ensuring that sensitive user data and tokens are never exposed in URL parameters or browser history. The frontend receives this temporary token and immediately exchanges it for production tokens through a secure API call, maintaining the security of the authentication process while providing a seamless user experience.

## User Population Methods

There are two ways to populate users:

### Custom Method Implementation

You can add the `populate_user` key to a provider configuration and specify the path to your custom method.

The method signature must be:
```python
def user_population(payload: dict, name: str) -> tuple[User, dict]:
    """
    Args:
        payload: User information from the provider (e.g., ID Token payload for OIDC)
        name: Provider name
    
    Returns:
        tuple: (User model instance, additional data dictionary)
    """
    user, created = User.objects.get_or_create(email=payload['email'])
    user.first_name = payload.get('given_name', '')
    user.last_name = payload.get('family_name', '')
    user.save()
    
    # Additional data to pass to frontend callback
    extra_data = {'department': payload.get('department'), 'new': created}
    
    return user, extra_data
```

After calling this method, the library invokes the frontend callback as follows: 
`<URL>/<handover_token>?department=IT&new=False`

### Built-in Configuration Method

You can add the `populate_user_conf` key to a provider configuration with the following format:

```python
{
    "lookup_field": ("email", "email"),  # (model_field, payload_key)
    "mappings": {
        "first_name": "given_name",        # Direct mapping
        "last_name": "family_name",        # Direct mapping
        "is_staff": lambda p: p.get('role') == 'admin'  # Callable mapping
    }
}
```

This method will get or create a user based on the `lookup_field`, then update the user model for each mapping key using either `payload[str]` or `callable(payload)`.

### Error Handling

You can and shoud surround your method with a try/except and you should raise drf_sso.exception.PopulationException, the library catch this exception when populating user.
Then redirect to frontend callback with an "err" query parameter containing the details

Example:

```python
if payload.get('department') != "HR":
    raise PopulationException("Only HR are authorized to login on this application.")
```

will redirect to: `https://myfront.com/callback/?err=Only%20HR%20are%20authorized%20to%20login%20on%20this%20application.`