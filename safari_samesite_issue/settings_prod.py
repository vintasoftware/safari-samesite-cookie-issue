from .settings import *

DEBUG = False

import django_heroku
django_heroku.settings(locals())