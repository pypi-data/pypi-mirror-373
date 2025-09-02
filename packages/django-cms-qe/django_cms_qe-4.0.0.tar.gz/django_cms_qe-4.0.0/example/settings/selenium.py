import os

from .dev import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'db_selenium.sqlite3'),  # noqa: F405
    }
}
