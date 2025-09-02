"""
Configuration for unit testing.
"""

from .dev import *  # noqa: F401,F403 pylint: disable=wildcard-import,unused-wildcard-import

# It's needed by django-pytest.
ROOT_URLCONF = 'cms_qe.urls'

# Use base template.
ALDRYN_BOILERPLATE_NAME = 'legacy'

# Speed up creating users in unittests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

TEST_MAILCHIMP_USERNAME = 'cms-qe-test'
TEST_MAILCHIMP_API_KEY = '4b1f852f66a317a500a5ae711a9181be-us16'
TEST_MAILCHIMP_LIST_ID = 'b6b91697ec'
