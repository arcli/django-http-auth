from django_http_auth import HTTPBasicAuthenticator

class HttpBasicAuthMiddleware(object):
    def process_request(self, request):
        # Only authenticated users can get access
        if HTTPBasicAuthenticator.check(request):
            # Authentication was successful - continue execution as normal
            return
        # No authentication was made - provide HTTP Basic Authentication challenge
        return HTTPBasicAuthenticator.challenge(request)
