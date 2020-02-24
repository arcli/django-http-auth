# django-http-auth

django-http-auth provides an implementation of HTTP Basic Authentication for Django. Implementation is based on RFC2617 (https://www.ietf.org/rfc/rfc2617.txt) and includes a simple brute-force protection mechanism.

Digest authentication will be added soon, stay tuned!

## Installation

From Git repository
```
1. git clone https://github.com/nopped/django-http-auth.git
2. python setup.py install
```

## Usage

Authentication can be applied by middleware, to protect all project's URLs, or a decorator that can be applied to any view functions.

* #### Middleware
 
 You can protect all URLs with authentication mechanism by adding django_http_auth to MIDDLEWARE_CLASSES in your Django settings file:
 
 * Basic Authentication
   
   ```python
   MIDDLEWARE_CLASSES = (
	#...
    'django_http_auth.middleware.HttpBasicAuthMiddleware',
)
```

* #### Decorator

 If you want to protect specific URLs, you can do so using django_http_auth decorator as follow:
 
 * Basic Authentication

   ```python
   from django_http_auth.decorators import http_basic_auth
  
   @http_basic_auth
   def someview(request):
           # do some work
           #...
   ```
   
* #### Brute-force protection

  In order to avoid abuse from potentioal attackers to try and brute force user's passwords, a simple protection mechanism is being used by default, if more than 10 attempts occurs during 30 seconds, the attacker's session is being blocked for 10 minutes.
  
  You can disable or customize the mechanism using the following variables in your Django settings file:
  
  #### HTTP_BASIC_AUTH_BF_ENABLED
  Enable/Disable brute-force protection mechanism
  
  **Default:**
  
  ```
  HTTP_BASIC_AUTH_BF_ENABLED = True
  ```
  
  #### HTTP_BASIC_AUTH_BF_ATTEMPTS
  Number of failed authentication attempts allow during HTTP_BASIC_AUTH_BF_MONITOR_WINDOW period
  
  **Default:**
  
  ```
  HTTP_BASIC_AUTH_BF_ATTEMPTS = 10
  ```
  
  #### HTTP_BASIC_AUTH_BF_MONITOR_WINDOW
  The duration (in seconds) of the check period for failed authentication attempts
  
  **Default:**
  
  ```
  HTTP_BASIC_AUTH_BF_MONITOR_WINDOW = 30
  ```
  
  #### HTTP_BASIC_AUTH_BF_BLOCK_PERIOD
  The duration (in seconds) of how long the attacker be blocked
  
  **Default:**
  
  ```
  HTTP_BASIC_AUTH_BF_ATTEMPTS = 60 * 10
  ```
  
## Compatiblity

Tested with:

* Django 1.6.x
* Django 2.2.x
