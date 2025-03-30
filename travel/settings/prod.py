from .common import *  # noqa

# Timur settings

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS').split(',')
