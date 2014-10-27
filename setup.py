from setuptools import setup

def long_description():
    try:
       import pypandoc
       return pypandoc.convert('README.md', 'rst')
    except (IOError, ImportError):
       return open('README.md').read()

setup(
    name = 'django-http-auth',
    version = '0.1a1',
    description = ('An implementation of HTTP Authentication for Django.'),
    long_description = long_description(),
    author = 'Yaron Tal',
    author_email = 'nopped@gmail.com',
    url = 'https://github.com/nopped/django-http-auth',
    packages = ['django_http_auth'],
    license = 'MIT',
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved ::MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
     ],
)