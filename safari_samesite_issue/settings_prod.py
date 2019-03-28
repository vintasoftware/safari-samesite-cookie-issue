import os

from .settings import *

DEBUG = False

import django_heroku
django_heroku.settings(locals())

REDIRECT_TARGET_URL = os.environ['REDIRECT_TARGET_URL']
