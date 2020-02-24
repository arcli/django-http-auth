import time
import base64
from datetime import datetime
from datetime import timedelta

from django.conf         import settings
from django.shortcuts    import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login

class HTTPBasicAuthenticator(object):
    S_FAILURE_COUNT        = 'http_basic_auth_failure_count'
    S_IS_BLOCKED           = 'http_basic_auth_block'
    S_LAST_CHECK_TIMESTAMP = 'http_basic_auth_last_check_timestamp'

    REALM             = getattr(settings, 'HTTP_BASIC_AUTH_REALM',             '')
    BF_ENABLED        = getattr(settings, 'HTTP_BASIC_AUTH_BF_ENABLED',        True)    # Brute Force Protection
    BF_ATTEMPTS       = getattr(settings, 'HTTP_BASIC_AUTH_BF_ATTEMPTS',       10)      # Requests
    BF_MONITOR_WINDOW = getattr(settings, 'HTTP_BASIC_AUTH_BF_MONITOR_WINDOW', 30)      # Seconds
    BF_BLOCK_PERIOD   = getattr(settings, 'HTTP_BASIC_AUTH_BF_BLOCK_PERIOD',   60 * 10) # Seconds

    @staticmethod
    def check(request):
        # Check if user already authenticated, if so, skip HTTP Basic authentication
        try:
            if request.user.is_authenticated():
                return True
        except TypeError:
            if request.user.is_authenticated:
                return True

        # Perform anti-brute force process
        if HTTPBasicAuthenticator._anti_bruteforce(request):
            return False

        # Get authorization HTTP header
        if request.META.get('HTTP_AUTHORIZATION', False):
            # Extract authentication type and credentials from header
            auth_type, credentials_base64 = request.META['HTTP_AUTHORIZATION'].split(' ')
            # Decode credentials using Base64
            credentials = base64.b64decode(credentials_base64)
            # Get username and password from decoded credentials
            username, password = credentials.split(':')
            # Try to authenticate username and password to allow access
            user_object = authenticate(username = username, password = password)
            # If we found a match and user is active, allow access
            if user_object is not None and user_object.is_active:
                login(request, user_object)
                return True

        # Failed to get authorization HTTP header or to authenticate user
        return False

    @staticmethod
    def challenge(request):
        # If we detect an attempt to brute force, we disable access of the attacker for an hour
        if HTTPBasicAuthenticator._is_blocked(request):
            # Build HTTPResponse with Service Unavailable error
            response = HttpResponse("Service Unavailable", status = 503)
            return response
        # Build HTTPResponse with authentication challenge
        response = HttpResponse("Authentication Required", status = 401)
        response['WWW-Authenticate'] = 'Basic realm="%s"' % HTTPBasicAuthenticator.REALM
        return response

    @staticmethod
    def _anti_bruteforce(request):
        # Update http basic authentication failure count
        try:
            # Increment by one every time we have a new request
            request.session[HTTPBasicAuthenticator.S_FAILURE_COUNT] += 1
        except KeyError:
            # New session, create session variables to be used for our anti brute-force mechanism
            request.session[HTTPBasicAuthenticator.S_IS_BLOCKED]           = False
            request.session[HTTPBasicAuthenticator.S_FAILURE_COUNT]        = 0
            request.session[HTTPBasicAuthenticator.S_LAST_CHECK_TIMESTAMP] = time.time()

        # Get the last check timestamp of the current session
        last_check_timestamp = datetime.fromtimestamp(request.session[HTTPBasicAuthenticator.S_LAST_CHECK_TIMESTAMP])

        # If last check timestamp is older than BF_BLOCK_PERIOD, reset last check timestamp
        if datetime.now() - last_check_timestamp > timedelta(seconds = HTTPBasicAuthenticator.BF_BLOCK_PERIOD):
            request.session[HTTPBasicAuthenticator.S_IS_BLOCKED]           = False
            request.session[HTTPBasicAuthenticator.S_FAILURE_COUNT]        = 0
            request.session[HTTPBasicAuthenticator.S_LAST_CHECK_TIMESTAMP] = time.time()
        else:
            # If we have more than BRUTE_FORCE_ATTEMPTS attempts in the last BF_MONITOR_WINDOW seconds,
            # block for BF_BLOCK_PERIOD seconds
            if request.session[HTTPBasicAuthenticator.S_FAILURE_COUNT] > HTTPBasicAuthenticator.BF_ATTEMPTS and \
               (datetime.now() - last_check_timestamp < timedelta(seconds = HTTPBasicAuthenticator.BF_MONITOR_WINDOW)):
                # Too many requests, it's time to block for BRUTE_FORCE_BLOCK_PERIOD
                request.session[HTTPBasicAuthenticator.S_IS_BLOCKED]           = True
                request.session[HTTPBasicAuthenticator.S_LAST_CHECK_TIMESTAMP] = time.time()

        # Return whether session is currently blocked or not
        return request.session[HTTPBasicAuthenticator.S_IS_BLOCKED]

    @staticmethod
    def _is_blocked(request):
        if request.session[HTTPBasicAuthenticator.S_IS_BLOCKED]:
            # Get the last check timestamp of the current session
            last_check_timestamp = datetime.fromtimestamp(request.session[HTTPBasicAuthenticator.S_LAST_CHECK_TIMESTAMP])
            # If we have been blocking the session for more than BF_BLOCK_PERIOD seconds - remove block
            if datetime.now() - last_check_timestamp >= timedelta(seconds = HTTPBasicAuthenticator.BF_BLOCK_PERIOD):
                request.session[HTTPBasicAuthenticator.S_IS_BLOCKED]           = False
                request.session[HTTPBasicAuthenticator.S_LAST_CHECK_TIMESTAMP] = time.time()
                return False

            # Session is still blocked
            return True

        # Session is currently not blocked
        return False