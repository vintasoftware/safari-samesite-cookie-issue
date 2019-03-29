import os

from .settings import *

DEBUG = False

import django_heroku
django_heroku.settings(locals())

CSRF_COOKIE_SAMESITE = os.environ.get('CSRF_COOKIE_SAMESITE', None)
SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', None)

REDIRECT_TARGET_URL = os.environ['REDIRECT_TARGET_URL']
