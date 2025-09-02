"""
Mailing settings, by default app looks for smtp server.
"""
from .env import ENV

EMAIL_HOST = ENV.str("EMAIL_HOST", default="localhost")
EMAIL_HOST_USER = ENV.str("EMAIL_USER", default="")
EMAIL_HOST_PASSWORD = ENV.str("EMAIL_PASSWORD", default="")
EMAIL_PORT = ENV.int("EMAIL_PORT", default=587)  # TLS uses usually 587, not 22
EMAIL_USE_TLS = ENV.bool("EMAIL_USE_TLS", default=False)
EMAIL_SUBJECT_PREFIX = ENV.str("EMAIL_SUBJECT_PREFIX", default="")  # Remove Django default prefix
DEFAULT_FROM_EMAIL = ENV.str("DEFAULT_FROM_EMAIL", default="django_cms_qe@localhost")
