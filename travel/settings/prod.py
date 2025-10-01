from .common import *  # noqa

# Timur settings

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS').split(',')

CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(',')
