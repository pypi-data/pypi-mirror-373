"""
Configuration for development.

Disables all security options.
"""

import os
from pathlib import Path

from .base import *  # noqa: F401,F403 pylint: disable=wildcard-import,unused-wildcard-import
from .base.env import ENV

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

DEBUG = True

META_SITE_PROTOCOL = 'http'

SECRET_KEY = ENV.str("SECRET_KEY", default='secret')

SESSION_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS += [  # noqa: F405
    'debug_toolbar',
    'django_extensions',
]

ROOT_URLCONF = "cms_qe.urls"

MIDDLEWARE += [  # noqa: F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

site_resolver = Path(__file__).resolve()

PROJECT_DIR = site_resolver.parent.parent.parent
RUN_SITE_DIR = os.environ.get("VENV_PATH", PROJECT_DIR)

STATIC_ROOT = ENV.str("STATIC_ROOT", default=os.path.join(PROJECT_DIR, 'staticfiles'))
MEDIA_ROOT = ENV.str("MEDIA_ROOT", default=os.path.join(RUN_SITE_DIR, 'media'))

# Caching
CACHES = {
    "default": ENV.cache("CACHE_URL", default=f'filecache://{os.path.join(RUN_SITE_DIR, "django_cache")}')
}

# Database
database_path = os.path.join(RUN_SITE_DIR, 'db.sqlite3')
database_url_default = f"sqlite:///{database_path}"  # pylint: disable=C0103
DATABASES = {"default": ENV.db("DATABASE_URL", default=database_url_default)}

EMAIL_BACKEND = 'cms_qe_test.mail_filebased_backend.EmlEmailBackend'
EMAIL_FILE_PATH = ENV.str("EMAIL_FILE_PATH", default=os.path.join(RUN_SITE_DIR, 'django_mails'))

ALDRYN_FORMS_SUBMISSION_LIST_DISPLAY_FIELD = "aldryn_forms.admin.display_form_submission_data"

SITE_API_ROOT = "/api/v1/"

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'cms_qe.api.utils.exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# API views: [("path/", "module.api.views.RecordViewSet", "api-records"), ...]
API_VIEWS = [
    ('aldryn-forms/forms', 'aldryn_forms.api.views.FormViewSet', 'aldryn-forms-form'),
    ('aldryn-forms/submitssions', 'aldryn_forms.api.views.SubmissionsViewSet', 'aldryn-forms-submitssions'),
]
