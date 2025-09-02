from cms_qe.settings.dev import *  # noqa: F403

INSTALLED_APPS += [  # noqa: F405
    'example',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

ROOT_URLCONF = 'example.urls'
WSGI_APPLICATION = 'example.wsgi.application'

SESSION_COOKIE_NAME = ENV.str("SESSION_COOKIE_NAME", default="sessionid_example")  # noqa: F405
