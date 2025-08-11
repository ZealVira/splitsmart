from .base import *
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://localhost:5432/mysite',
        conn_max_age=600
    )
}

# Static files storage
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')
