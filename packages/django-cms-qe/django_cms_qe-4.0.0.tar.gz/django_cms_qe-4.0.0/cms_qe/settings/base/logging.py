"""
Logging settings with base formatters and handlers.
"""
from .env import ENV

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/

SERVER_EMAIL = 'django_cms_qe@localhost'

ADMINS = (
    ('Root', 'root@localhost'),
)
MANAGERS = ADMINS


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'short': {
            'format': '%(levelname)s [%(filename)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
        'long': {
            'format': '[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'short'
        },
        'mailadmins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'handlers': ['mailadmins'],
            'propagate': True,
        },
        'cms_qe*': {
            'level': 'WARNING',
            'handlers': ['mailadmins'],
            'propagate': True,
        },
        '': {
            'level': ENV.str("LOGGER", default="ERROR"),
            'handlers': ['console'],
        },
    }
}
