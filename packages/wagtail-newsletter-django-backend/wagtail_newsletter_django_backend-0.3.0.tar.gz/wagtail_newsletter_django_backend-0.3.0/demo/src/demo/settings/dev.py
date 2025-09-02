from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-gqi@n!k!b#mlxc5*&bt2c73j7ate#bwsky07rkcf-84nr^-^p%"

PII_HASHING_SALT = 'INSECURE SALT'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

STATIC_URL = "/static/"
MEDIA_URL = "/media/"


try:
    from .local import *
except ImportError:
    pass
