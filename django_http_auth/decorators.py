from django_http_auth import HTTPBasicAuthenticator

def http_basic_auth(func):
    def auth_wrap(request, *args, **kwargs):
        # Only authenticated users can get access
        if HTTPBasicAuthenticator.check(request):
            # Authentication was successful - continue execution as normal
            return func(request, *args, **kwargs)
        # No authentication was made - provide HTTP Basic Authentication challenge
        return HTTPBasicAuthenticator.challenge(request)
    return auth_wrap