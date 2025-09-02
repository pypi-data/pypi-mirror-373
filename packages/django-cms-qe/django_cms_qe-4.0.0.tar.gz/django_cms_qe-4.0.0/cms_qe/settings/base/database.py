"""
Database settings, used PostgreSQL without auth by default.
"""

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# https://pypi.org/project/python-environ/
#   Supported types / db_url

from .env import ENV

# Database
DATABASES = {
    "default": ENV.db("DATABASE_URL", default='postgres://qe_user:password@/cms_qe'),
}
